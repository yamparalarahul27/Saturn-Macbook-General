"""Generate matched millimetre-accurate PDF and SVG nets from the model dimensions."""
from pathlib import Path
import json, math, html, shutil
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'src/data/vikramaditya.json').read_text())
OUT = ROOT / 'public/kits/vikramaditya'
OUT.mkdir(parents=True, exist_ok=True)
PDF = ROOT / 'output/pdf/vikramaditya-a4.pdf'
PDF.parent.mkdir(parents=True, exist_ok=True)
W,H=297,210
INK='#263243'; BLUE='#315eea'; PAPER='#e5eaf0'; TOP='#f0f3f7'; GLUE='#eeebf7'; MUTED='#66758a'

def add(a,b): return (a[0]+b[0],a[1]+b[1])
def mul(a,n): return (a[0]*n,a[1]*n)
def sub(a,b): return (a[0]-b[0],a[1]-b[1])
def dot(a,b): return a[0]*b[0]+a[1]*b[1]
def cross(a,b): return a[0]*b[1]-a[1]*b[0]
def dist(a,b): return math.hypot(*sub(a,b))
def edges(p): return zip(p,p[1:]+p[:1])
def rect(x,y,w,h): return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]

class Drawing:
 def __init__(self,c): self.c=c; self.svg=[]
 def poly(self,p,fill=None,stroke=None,width=.2):
  c=self.c; path=c.beginPath(); path.moveTo(p[0][0]*mm,(H-p[0][1])*mm)
  for x,y in p[1:]: path.lineTo(x*mm,(H-y)*mm)
  path.close(); c.setLineWidth(width*mm)
  if fill: c.setFillColor(HexColor(fill))
  if stroke: c.setStrokeColor(HexColor(stroke))
  c.drawPath(path,stroke=bool(stroke),fill=bool(fill))
  pts=' '.join(f'{x:.3f},{y:.3f}' for x,y in p)
  self.svg.append(f'<polygon points="{pts}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}"/>')
 def line(self,a,b,color=INK,width=.2,dash=None):
  c=self.c; c.setStrokeColor(HexColor(color)); c.setLineWidth(width*mm); c.setDash([v*mm for v in dash] if dash else [])
  c.line(a[0]*mm,(H-a[1])*mm,b[0]*mm,(H-b[1])*mm); c.setDash([])
  ds=f' stroke-dasharray="{" ".join(map(str,dash))}"' if dash else ''
  self.svg.append(f'<line x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}" stroke="{color}" stroke-width="{width}"{ds}/>')
 def text(self,x,y,text,size=2.7,color=INK,bold=False,anchor='start',angle=0):
  c=self.c; c.saveState(); c.translate(x*mm,(H-y)*mm); c.rotate(-angle); c.setFillColor(HexColor(color)); c.setFont('Helvetica-Bold' if bold else 'Helvetica',size*mm)
  {'start':c.drawString,'middle':c.drawCentredString,'end':c.drawRightString}[anchor](0,0,text); c.restoreState()
  self.svg.append(f'<text x="{x:.3f}" y="{y:.3f}" transform="rotate({angle} {x} {y})" font-family="Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{html.escape(text)}</text>')
 def circle(self,x,y,r,stroke=INK,fill=None,width=.2):
  c=self.c; c.setStrokeColor(HexColor(stroke)); c.setLineWidth(width*mm)
  if fill: c.setFillColor(HexColor(fill))
  c.circle(x*mm,(H-y)*mm,r*mm,stroke=1,fill=bool(fill))
  self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill or "none"}" stroke="{stroke}" stroke-width="{width}"/>')
 def save(self,name,view=None):
  view=view or (0,0,W,H); x,y,w,h=view
  (OUT/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="{x} {y} {w} {h}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white"/>'+''.join(self.svg)+'</svg>')

class Net:
 def __init__(self,id): self.id=id; self.faces=[]; self.folds=[]; self.labels=[]; self.bounds=None
 def face(self,p,color): self.faces.append((p,color))
 def fold(self,a,b): self.folds.append((a,b))
 def tab(self,a,b,n,label):
  u=mul(sub(b,a),1/dist(a,b)); bevel=min(1.8,dist(a,b)/4); deep=4.5
  p=[a,b,add(add(b,mul(u,-bevel)),mul(n,deep)),add(add(a,mul(u,bevel)),mul(n,deep))]
  self.face(p,GLUE); self.fold(a,b)
  mid=add(mul(add(a,b),.5),mul(n,2.9)); self.labels.append((*mid,label,1.7))
 def draw(self,d):
  for p,color in self.faces: d.poly(p,fill=color)
  # Remove shared hinges from the cut outlines, including partial tab hinges.
  for p,_ in self.faces:
   for a,b in edges(p):
    v=sub(b,a); ll=dot(v,v); intervals=[(0.,1.)]
    for f,g in self.folds:
     if abs(cross(v,sub(f,a)))>1e-6 or abs(cross(v,sub(g,a)))>1e-6: continue
     lo,hi=sorted((dot(sub(f,a),v)/ll,dot(sub(g,a),v)/ll)); new=[]
     for l,r in intervals:
      if hi<=l+1e-7 or lo>=r-1e-7: new.append((l,r))
      else:
       if lo>l+1e-7: new.append((l,lo))
       if hi<r-1e-7: new.append((hi,r))
     intervals=new
    for l,r in intervals: d.line(add(a,mul(v,l)),add(a,mul(v,r)),width=.32)
  for a,b in self.folds: d.line(a,b,BLUE,.22,[1.6,.9])
  for x,y,t,s in self.labels: d.text(x,y,t,s,BLUE,anchor='middle')
  pts=[p for face,_ in self.faces for p in face]; self.bounds=(min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts))
  x0,y0,x1,y1=self.bounds
  assert x0>=10 and y0>=25 and x1<=287 and y1<=183,(self.id,self.bounds)
  # Every polygon must be non-degenerate. Pairwise convex clipping catches overlapping faces/tabs.
  for i,(p,_) in enumerate(self.faces):
   assert abs(area(p))>.05
   for q,_ in self.faces[i+1:]:
    overlap=clip(p,q)
    assert abs(area(overlap))<.005,(self.id,'net overlap',abs(area(overlap)))

def area(p): return sum(cross(a,b) for a,b in edges(p))/2 if len(p)>2 else 0

def clip(subject,clipper):
 out=subject[:]; sign=1 if area(clipper)>0 else -1
 for a,b in edges(clipper):
  inp=out; out=[]
  if not inp: break
  for s,e in edges(inp):
   ds=sign*cross(sub(b,a),sub(s,a)); de=sign*cross(sub(b,a),sub(e,a))
   if de>=-1e-8:
    if ds< -1e-8: out.append(add(s,mul(sub(e,s),ds/(ds-de))))
    out.append(e)
   elif ds>=-1e-8: out.append(add(s,mul(sub(e,s),ds/(ds-de))))
 return out

def header(d,num,title):
 d.text(12,14,'Paper Craft',5,bold=True); d.text(285,13,f'INS Vikramaditya  /  Sheet {num} of 5',3,anchor='end')
 d.line((12,19),(285,19),'#d5dbe3',.2); d.text(12,25,title,3.3,bold=True)

def footer(d):
 d.line((12,188),(285,188),'#d5dbe3',.2)
 d.line((12,194),(22,194),width=.32); d.text(25,195,'Cut: bold outline',2.5)
 d.line((66,194),(76,194),BLUE,.22,[1.6,.9]); d.text(79,195,'Fold away from print',2.5)
 d.poly(rect(138,191.5,9,4.5),GLUE,INK,.2); d.text(150,195,'Glue tabs',2.5)
 d.text(12,202,'A4 landscape | Actual size / 100% | Single-sided | No fit-to-page',2.7,bold=True)
 d.line((235,199),(285,199),width=.3)
 for x in [235,285]: d.line((x,197),(x,201),width=.3)
 d.text(260,195,'This line must measure 50 mm',2.3,anchor='middle')

def notes(d,x,y,lines):
 for i,line in enumerate(lines): d.text(x,y+i*4.5,line,2.7,color=MUTED)

def placement(d,x,y,w,h,id):
 for a,b in edges(rect(x,y,w,h)): d.line(a,b,'#8e99a8',.16,[.5,1.1])
 d.text(x+w/2,y+h/2+1,f'{id}',3.5,'#7c899b',True,'middle')

def part_crop(d,net,start):
 x0,y0,x1,y1=net.bounds; subset=Drawing(d.c); subset.svg=d.svg[start:]; subset.save(f'part-{net.id}.svg',(x0-3,y0-3,x1-x0+6,y1-y0+6))


def splitpoly(p,forward):
 """Clip any polygon against one vertical split plane, preserving exact matching seam."""
 out=[]; x=DATA['split']
 for a,b in edges(p):
  da=(a[0]-x)*(1 if forward else -1); db=(b[0]-x)*(1 if forward else -1)
  if da>=-1e-8: out.append(tuple(a))
  if (da<0<db) or (db<0<da): out.append(add(a,mul(sub(b,a),da/(da-db))))
 return out

def hull(d,id):
 n=Net(id); forward=id==2; shift=DATA['split'] if forward else 0; ring=[(x-shift+43,y+47) for x,y in splitpoly(DATA['hull']['outline'],forward)]; h=DATA['hull']['height']; n.face(ring,TOP)
 for i,(a,b) in enumerate(edges(ring)):
  u=mul(sub(b,a),1/dist(a,b)); v=(u[1],-u[0]); n.face([a,b,add(b,mul(v,h)),add(a,mul(v,h))],PAPER); n.fold(a,b)
  # Narrow corner tabs begin far enough from each obtuse shoulder to stay in the unfolded gap.
  n.tab(add(b,mul(v,13)),add(b,mul(v,h-1)),u,f'{id}{chr(65+i)}')
  pt=add(add(a,mul(u,min(5,dist(a,b)/2))),mul(v,18)); n.labels.append((*pt,f'{id}{chr(65+(i-1)%len(ring))}',1.65))
  if dist(a,b)>15:
   n.tab(add(add(a,mul(v,h)),mul(u,4)),add(add(b,mul(v,h)),mul(u,-4)),v,'DECK')
 start=len(d.svg); n.draw(d)
 d.text(140,88,f'{id:02} / {"FORWARD" if forward else "AFT"} HULL UNDERSIDE',3.4,bold=True,anchor='middle')
 d.text(140,94,'Printed side down. Fold walls up, rim tabs inward.',2.5,anchor='middle')
 d.text(140,99,'The straight middle end joins the other hull half.',2.5,anchor='middle')
 # Identify the full-height joining bulkhead, not a tab.
 seamx=43 if forward else 43+DATA['split']
 d.text(seamx+(-12 if forward else 12),91,'JOIN',2.3,BLUE,True,'middle',90)
 part_crop(d,n,start); return n

def deck(d,id):
 n=Net(id); forward=id==4; shift=DATA['split'] if forward else 0; ox,oy=23-shift,34; ring=[(x+ox,y+oy) for x,y in splitpoly(DATA['deck']['outline'],forward)]; n.face(ring,'#dce2e8'); start=len(d.svg); n.draw(d)
 # Clip printed deck markings to this half. They are decoration, never cut lines.
 def segment(a,b,color,width,dash=None):
  xmin=DATA['split'] if forward else 0; xmax=DATA['length'] if forward else DATA['split']
  dx=b[0]-a[0]; lo,hi=0,1
  if abs(dx)<1e-9:
   if not xmin<=a[0]<=xmax:return
  else:
   t0,t1=sorted(((xmin-a[0])/dx,(xmax-a[0])/dx));lo=max(lo,t0);hi=min(hi,t1)
  if hi>=lo: d.line(add(add(a,mul(sub(b,a),lo)),(ox,oy)),add(add(a,mul(sub(b,a),hi)),(ox,oy)),color,width,dash)
 # Angled landing area and take-off centreline, schematic placement based on reference photography.
 for yy in [30,57]: segment((3,yy),(245,yy+12),'#ffffff',.8)
 segment((3,43.5),(245,55.5),'#ffffff',.45,[5,3])
 segment((82,54),(335,36),'#b69b4b',.9,[3,2]); segment((335,36),(403,36),'#b69b4b',.9,[3,2])
 for xx in [48,64,80]: segment((xx,31+xx*.044),(xx,58+xx*.044),'#7c8895',.35)
 for xx in [15,100,150,280,310]:
  segment((xx,13),(xx+18,13),'#a57865',.25); segment((xx,13),(xx,19),'#a57865',.25)
 for xx,yy in [(105,9),(156,7)]:
  for a,b in edges(rect(xx,yy,17,15)):segment(a,b,'#a9b2bd',.3)
 # Visible placement guides are only at mounting surfaces.
 for id2 in [7,6]:
  p=DATA['parts'][id2-1]; poly=rect(p['x'],p['y'],p['w'],p['d'])
  for a,b in edges(poly):segment(a,b,'#7f8d9e',.16,[.5,1.1])
  tx=p['x']+p['w']/2
  if (tx>=DATA['split'])==forward:d.text(tx+ox,p['y']+p['d']/2+oy+1,str(id2),3,'#7f8d9e',True,'middle')
 if not forward: d.text(36+ox,19+oy,'R33',4,'#84919e',True,'middle')
 part_crop(d,n,start);return n

def box(d,p,x,y):
 w,h,deep=p['w'],p['d'],p['h']; id=p['id']; n=Net(id); roof=rect(x,y,w,h); n.face(roof,TOP)
 for i,(a,b) in enumerate(edges(roof)):
  u=mul(sub(b,a),1/dist(a,b)); v=(u[1],-u[0]); n.face([a,b,add(b,mul(v,deep)),add(a,mul(v,deep))],PAPER); n.fold(a,b)
  n.tab(add(b,mul(v,3)),add(b,mul(v,deep-2)),u,f'{id}{chr(65+i)}')
  pt=add(add(a,mul(u,3)),mul(v,deep/2)); n.labels.append((*pt,f'{id}{chr(65+(i-1)%4)}',1.65))
  n.tab(add(add(a,mul(v,deep)),mul(u,2)),add(add(b,mul(v,deep)),mul(u,-2)),v,str(id))
 start=len(d.svg); n.draw(d)
 if id==7:
  # Bridge intentionally overhangs island by 2 mm on either side. Mark only its supported contact footprint.
  placement(d,x+48,y,30,18,8);placement(d,x+17,y+2,20,14,9)
  for xx in range(5,80,10):
   for yy in [y-7,y+h+3]:d.poly(rect(x+xx,yy,5,3),'#6c7e90')
 elif id==8:
  placement(d,x+8,y+6,10,10,10)
  for xx in range(3,25,6):
   for yy in [y-7,y+h+3]:d.poly(rect(x+xx,yy,4.5,3),'#596f85')
  for yy in range(3,18,6):
   for xx in [x-7,x+w+3]:d.poly(rect(xx,y+yy,3,4.5),'#596f85')
 elif id==9:
  d.poly(rect(x+2,y+2,w-4,h-4),'#7a8591')
  d.text(x+w/2,y+h+12,'R33',3,'#627181',True,'middle')
 elif id==10:
  for yy in [y-20,y+h+5]:
   d.poly(rect(x+1,yy,8,10),'#a8b8c9','#7f92aa',.2)
   for j in range(1,5):d.line((x+1,yy+j*2),(x+9,yy+j*2),'#71849a',.16)
   for j in range(1,4):d.line((x+1+j*2,yy),(x+1+j*2,yy+10),'#71849a',.16)
 part_crop(d,n,start);return n

def strip(d):
 n=Net(5);n.face(rect(27,148,70,20),GLUE);start=len(d.svg);n.draw(d)
 d.line((27,158),(97,158),'#8896aa',.15,[.5,1]);d.text(62,155,'GLUE UNDER AFT DECK 3',2.1,anchor='middle');d.text(62,164,'GLUE UNDER FORWARD DECK 4',2.1,anchor='middle');part_crop(d,n,start);return n

def ramp(d):
 n=Net(6);x,y=42,135;p=DATA['ramp'];run,rise,w=p['w'],p['h'],p['d'];L=math.hypot(run,rise);t=run*run/L;alt=run*rise/L
 n.face(rect(x,y,L,w),'#dce2e8')
 for sign,yy in [(-1,y),(1,y+w)]:
  a=(x,yy);b=(x+L,yy);v=(x+t,yy+sign*alt);n.face([a,b,v],PAPER);n.fold(a,b)
  u=mul(sub(v,a),1/run);normal=(sign*-u[1],sign*u[0]);n.tab(add(a,mul(u,4)),add(v,mul(u,-2)),normal,'6')
 n.face(rect(x+L,y,rise,w),PAPER);n.fold((x+L,y),(x+L,y+w));n.tab((x+L+rise,y+3),(x+L+rise,y+w-3),(1,0),'6')
 start=len(d.svg);n.draw(d);d.line((x,y+w/2),(x+L,y+w/2),'#b69b4b',.9,[3,2]);part_crop(d,n,start);return n

# Emit a 5-sheet carrier kit, with no unprintable oversized part.
c=canvas.Canvas(str(PDF),pagesize=(W*mm,H*mm));c.setTitle('INS Vikramaditya - A4 paper model - approximately 1:700');c.setAuthor('Paper Craft')
allnets=[]
for num,title in [(1,'01  Aft hull'),(2,'02  Forward hull')]:
 d=Drawing(c);header(d,num,title);allnets.append(hull(d,num));notes(d,17,158,['Score blue dashed lines before cutting. Cut bold outer outlines only; keep all pale glue tabs.',f'Fold walls up with the printed base facing down. Glue matching {num}A, {num}B, etc. behind their marked edges.', 'Fold the DECK rim tabs inward. Glue the two straight JOIN end walls back-to-back; keep both bottoms level.', 'This is a simplified waterline model: the underwater hull, tiny fittings and weapons are omitted.']);footer(d);d.save(f'sheet-{num}.svg');c.showPage()
d=Drawing(c);header(d,3,'03  Aft flight deck     /     05  Joining strip');allnets.append(deck(d,3));allnets.append(strip(d));notes(d,121,145,['Keep deck pieces 3 and 4 flat. Do not fold their seam.', 'Place strip 5 under the two straight middle edges,', 'with 10 mm glued beneath each half. Butt the edges', 'together; match both the runway lines and the outline.', 'Then glue the joined deck onto the hull rim tabs.', 'Use 160-200 gsm paper to keep the broad deck firm.']);footer(d);d.save('sheet-3.svg');c.showPage()
d=Drawing(c);header(d,4,'04  Forward flight deck     /     06  Ski jump');allnets.append(deck(d,4));allnets.append(ramp(d));notes(d,124,143,['06 / Ski jump: fold both triangular sides downward.', 'Fold the tall end downward and all base tabs inward.', 'Glue its three base tabs to deck footprint 6.', 'The low edge faces the stern; the raised edge faces', 'the bow. The printed centreline follows the runway.', 'The ramp is a simple straight 14-degree wedge.']);footer(d);d.save('sheet-4.svg');c.showPage()
d=Drawing(c);header(d,5,'07  Island     /     08  Bridge     /     09  Funnel     /     10  Radar mast')
for id,x,y in [(7,39,54),(8,203,54),(9,50,139),(10,140,142)]:allnets.append(box(d,DATA['parts'][id-1],x,y))
notes(d,191,129,['Fold walls down, away from print.', 'Glue matching lettered corner tabs.', 'Fold the four base tabs inward.', '', '7 fits the starboard deck guide.', '8 fits box 8 on the island roof;', 'it overhangs each side by 2 mm.', '9 fits roof box 9, aft of the bridge.', '10 fits box 10 on the bridge.', 'Use a thin layer of PVA glue.']);footer(d);d.save('sheet-5.svg');c.showPage();c.save()
reader=PdfReader(PDF);assert len(reader.pages)==5
for page in reader.pages:assert abs(float(page.mediabox.width)/mm-W)<.001 and abs(float(page.mediabox.height)/mm-H)<.001
for i,a in enumerate(allnets):
 for b in allnets[i+1:]:
  if DATA['parts'][a.id-1]['sheet']==DATA['parts'][b.id-1]['sheet']:
   # Net faces are convex except for the deck. Different pieces are separated by their bounding boxes.
   ax,ay,ar,ab=a.bounds;bx,by,br,bb=b.bounds
   assert ar<=bx or br<=ax or ab<=by or bb<=ay,('Separate parts overlap',a.id,b.id)
# Both hull halves have the same joining wall; both decks share an identical butt joint.
for kind in ['hull','deck']:
 seam=[]
 for forward in [False,True]:
  pts=splitpoly(DATA[kind]['outline'],forward); seam.append(sorted(round(y,6) for x,y in pts if abs(x-DATA['split'])<1e-6))
 assert seam[0]==seam[1],('mismatched seam',kind)
assert abs(DATA['length']-284000/DATA['scale'])<.001
assert abs(DATA['beam']-60000/DATA['scale'])<.001
assert abs(math.degrees(math.atan(DATA['ramp']['h']/DATA['ramp']['w']))-14)<.01
shutil.copy2(PDF,OUT/'vikramaditya-a4.pdf')
print('PASS: 5 exact A4 landscape sheets; 10 nets; no face/tab overlaps; printable margins; matching hull/deck joints; 1:700 overall dimensions; 14-degree ramp.')
print('Prototype: real-paper assembly remains untested.')
print(PDF)
