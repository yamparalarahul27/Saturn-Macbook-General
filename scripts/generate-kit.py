"""Generate matched millimetre-accurate PDF and SVG nets from the model dimensions."""
from pathlib import Path
import json, math, html, shutil
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader
from surface_art import artwork

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'src/data/vikramaditya.json').read_text())
OUT = ROOT / 'public/kits/vikramaditya'
OUT.mkdir(parents=True, exist_ok=True)
PDF = ROOT / 'output/pdf/vikramaditya-a4.pdf'
PDF.parent.mkdir(parents=True, exist_ok=True)
# Physical dimensions are millimetres at the selected print scale. Artwork and
# the isometric renderer use a stable illustration coordinate system.
K=DATA['illustrationScale']/DATA['scale']
ILLUSTRATION=json.loads(json.dumps(DATA))
for key in ['length','beam','split']:ILLUSTRATION[key]/=K
for kind in ['deck','hull']:ILLUSTRATION[kind]['outline']=[[v/K for v in pt] for pt in DATA[kind]['outline']]
ILLUSTRATION['hull']['height']/=K
for obj in [ILLUSTRATION['ramp'],*ILLUSTRATION['parts']]:
 for key in ['x','y','z','w','d','h']:obj[key]/=K
ART=artwork(ILLUSTRATION)
(ROOT/'src/data/surface-art.json').write_text(json.dumps(ART, separators=(',', ':'))+'\n')
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
 def __init__(self,c,compact=False): self.c=c; self.svg=[]; self.compact=compact
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
  assert x0>=10-1e-6 and y0>=(10 if d.compact else 28)-1e-6 and x1<=287+1e-6 and y1<=(191 if d.compact else 183)+1e-6,(self.id,self.bounds)
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
 ids=', '.join(f'{p["id"]:02}' for p in DATA['parts'] if p['sheet']==num)
 title=f'{ids} / {title}'
 if d.compact:
  d.text(12,7,f'Paper Craft / {title}',3,bold=True)
  d.text(285,7,f'INS Vikramaditya | 1:400 | v{DATA["version"]} | {num}/{DATA["sheets"]}',2.5,anchor='end')
 else:
  d.text(12,13,'Paper Craft',5,bold=True)
  d.text(285,13,f'INS Vikramaditya / 1:400 / v{DATA["version"]} / {num} of {DATA["sheets"]}',2.8,anchor='end')
  d.line((12,18),(285,18),'#d5dbe3',.2);d.text(12,24,title,3.3,bold=True)

def footer(d):
 d.line((12,194),(22,194),width=.32);d.text(25,195,'Cut outline',2.3)
 d.line((61,194),(71,194),BLUE,.22,[1.6,.9]);d.text(74,195,'Fold away from print',2.3)
 d.poly(rect(132,191.8,8,4.2),GLUE,INK,.2);d.text(143,195,'Glue tab',2.3)
 d.text(12,203,'A4 landscape | 100% / Actual size | Single-sided | No fit-to-page',2.5,bold=True)
 d.line((235,201),(285,201),width=.3)
 for x in [235,285]:d.line((x,199),(x,203),width=.3)
 d.text(260,197,'Check: exactly 50 mm',2.3,anchor='middle')

def notes(d,x,y,lines):
 for i,line in enumerate(lines): d.text(x,y+i*4.5,line,2.7,color=MUTED)

def placement(d,x,y,w,h,id):
 for a,b in edges(rect(x,y,w,h)): d.line(a,b,'#8e99a8',.16,[.5,1.1])
 d.text(x+w/2,y+h/2+1,f'{id}',3.5,'#7c899b',True,'middle')

def part_crop(d,net,start):
 x0,y0,x1,y1=net.bounds; subset=Drawing(d.c); subset.svg=d.svg[start:]; subset.save(f'part-{net.id}.svg',(x0-3,y0-3,x1-x0+6,y1-y0+6))


def section(points,lo,hi):
 result=points[:]
 for boundary,sign in [(lo,1),(hi,-1)]:
  output=[]
  for a,b in edges(result):
   da=(a[0]-boundary)*sign;db=(b[0]-boundary)*sign
   if da>=-1e-8:output.append(tuple(a))
   if da<0<db or db<0<da:output.append(add(a,mul(sub(b,a),da/(da-db))))
  result=output
 return result

def hull(d,id):
 p=DATA['parts'][id-1];n=Net(id);h=DATA['hull']['height']
 world=section(DATA['hull']['outline'],p['x'],p['x']+p['w'])
 # Centre each complete tray net on A4, including its full-height end walls.
 ox=(W-p['w'])/2-p['x'];oy=100.25-(min(y for x,y in world)+max(y for x,y in world))/2
 ring=[(x+ox,y+oy) for x,y in world];n.face(ring,TOP)
 for i,(a,b) in enumerate(edges(ring)):
  u=mul(sub(b,a),1/dist(a,b));v=(u[1],-u[0]);n.face([a,b,add(b,mul(v,h)),add(a,mul(v,h))],PAPER);n.fold(a,b)
  n.tab(add(b,mul(v,h*.55)),add(b,mul(v,h-1)),u,f'{id}{chr(65+i)}')
  pt=add(add(a,mul(u,min(5,dist(a,b)/2))),mul(v,h*.75));n.labels.append((*pt,f'{id}{chr(65+(i-1)%len(ring))}',1.65))
  if dist(a,b)>15:n.tab(add(add(a,mul(v,h)),mul(u,4)),add(add(b,mul(v,h)),mul(u,-4)),v,'DECK')
 start=len(d.svg);n.draw(d)
 for i,(a,b) in enumerate(edges(ring)):
  u=mul(sub(b,a),1/dist(a,b));v=(u[1],-u[0]);draw_art(d,f'hull-{id}-{i}',add(a,mul(v,h)),u,mul(v,-1))
 index=DATA['hullParts'].index(id);label=f'{id:02} / {p["name"].upper()}'
 d.text(148.5,97,label,3.2,bold=True,anchor='middle')
 d.text(148.5,103,'Print down; fold walls up.',2.5,anchor='middle')
 d.text(148.5,108,'Hull order: 1 - 2 - 15 - 16',2.5,anchor='middle')
 for local_x,neighbor in [(p['x'],DATA['hullParts'][index-1] if index else None),(p['x']+p['w'],DATA['hullParts'][index+1] if index<3 else None)]:
  if neighbor:
   ys=[y for x,y in world if abs(x-local_x)<1e-6]
   d.text(local_x+ox+(-h/2 if local_x==p['x'] else h/2),sum(ys)/len(ys)+oy,f'JOIN {neighbor}',2.5,BLUE,True,'middle',90)
 # Each rib has a clearly identified attachment line inside its corresponding tray.
 rib=DATA['parts'][DATA['ribParts'][index]-1]
 for ya,yb in [(rib['y']+oy,91),(113,rib['y']+rib['d']+oy)]:
  if yb>ya:d.line((rib['x']+ox,ya),(rib['x']+ox,yb),'#a7b2bf',.15,[.5,1])
 d.text(rib['x']+ox+3,rib['y']+oy+5,f'Support {rib["id"]}',2.2,MUTED)
 part_crop(d,n,start);return n

def draw_art(d,name,origin=(0,0),u=(1,0),v=(0,1)):
 def point(x,y):return add(origin,add(mul(u,x*K),mul(v,y*K)))
 for a in ART[name]:
  op=a['op'];x,y=a['x'],a['y'];stroke=a['stroke'];width=a['width']
  if op=='line':d.line(point(x,y),point(a['x2'],a['y2']),stroke,width*K,[v*K for v in a['dash']])
  else:
   if op=='rect':pts=[point(px,py) for px,py in rect(x,y,a['w'],a['h'])]
   else:pts=[point(x+a['r']*math.cos(i*math.tau/24),y+a['r']*math.sin(i*math.tau/24)) for i in range(24)]
   fill=a.get('fill','none');d.poly(pts,None if fill=='none' else fill,stroke,width*K)

def clipped_art(d,name,ring,origin,clip_id):
 d.c.saveState();path=d.c.beginPath();path.moveTo(ring[0][0]*mm,(H-ring[0][1])*mm)
 for x,y in ring[1:]:path.lineTo(x*mm,(H-y)*mm)
 path.close();d.c.clipPath(path,stroke=0,fill=0)
 pts=' '.join(f'{x},{y}' for x,y in ring)
 d.svg.append(f'<defs><clipPath id="{clip_id}"><polygon points="{pts}"/></clipPath></defs><g clip-path="url(#{clip_id})">')
 draw_art(d,name,origin)
 d.svg.append('</g>');d.c.restoreState()

def deck(d,id):
 p=DATA['parts'][id-1];n=Net(id);ox,oy=12-p['x'],29
 ring=[(x+ox,y+oy) for x,y in section(DATA['deck']['outline'],p['x'],p['x']+p['w'])]
 n.face(ring,'#dce2e8');start=len(d.svg);n.draw(d);clipped_art(d,'deck',ring,(ox,oy),f'deck-{id}')
 def segment(a,b):
  dx=b[0]-a[0];lo,hi=0,1
  if abs(dx)<1e-9:
   if not p['x']<=a[0]<=p['x']+p['w']:return
  else:
   t0,t1=sorted(((p['x']-a[0])/dx,(p['x']+p['w']-a[0])/dx));lo=max(lo,t0);hi=min(hi,t1)
  if hi>=lo:d.line(add(add(a,mul(sub(b,a),lo)),(ox,oy)),add(add(a,mul(sub(b,a),hi)),(ox,oy)),'#7f8d9e',.2,[.6,1.2])
 for target in [7,6,14]:
  t=DATA['parts'][target-1]
  for a,b in edges(rect(t['x'],t['y'],t['w'],t['d'])):segment(a,b)
  tx=t['x']+t['w']/2
  if p['x']<=tx<p['x']+p['w']:d.text(tx+ox,t['y']+t['d']/2+oy+1,str(target),3.5,MUTED,True,'middle')
 if id==3:d.text(36*K+ox,19*K+oy,'R33',4*K,'#84919e',True,'middle')
 part_crop(d,n,start);return n

def box(d,p,x,y):
 w,h,deep=p['w'],p['d'],p['h']; id=p['id']; n=Net(id); roof=rect(x,y,w,h); n.face(roof,TOP)
 for i,(a,b) in enumerate(edges(roof)):
  u=mul(sub(b,a),1/dist(a,b)); v=(u[1],-u[0]); n.face([a,b,add(b,mul(v,deep)),add(a,mul(v,deep))],PAPER); n.fold(a,b)
  n.tab(add(b,mul(v,3)),add(b,mul(v,deep-2)),u,f'{id}{chr(65+i)}')
  pt=add(add(a,mul(u,3)),mul(v,deep/2)); n.labels.append((*pt,f'{id}{chr(65+(i-1)%4)}',1.65))
  n.tab(add(add(a,mul(v,deep)),mul(u,2)),add(add(b,mul(v,deep)),mul(u,-2)),v,str(id))
 start=len(d.svg); n.draw(d)
 # Surface coordinates match the folded model, including the forward end.
 draw_art(d,f'{id}-side',(x,y+h))
 draw_art(d,f'{id}-side',(x,y),(1,0),(0,-1))
 draw_art(d,f'{id}-end',(x+w,y+h),(0,-1),(1,0))
 draw_art(d,f'{id}-end',(x,y),(0,1),(-1,0))
 for child_id in {7:[11,9],8:[10],10:[12]}.get(id,[]):
  child=DATA['parts'][child_id-1]
  left=max(0,child['x']-p['x']);top=max(0,child['y']-p['y'])
  right=min(w,child['x']+child['w']-p['x']);bottom=min(h,child['y']+child['d']-p['y'])
  placement(d,x+left,y+top,right-left,bottom-top,child_id)
 if id==9:
  d.poly(rect(x+2*K,y+2*K,w-4*K,h-4*K),'#7a8591')
  for xx in range(3,int(w/K)-2,2):d.line((x+xx*K,y+2*K),(x+xx*K,y+h-2*K),'#526574',.25*K)
  d.text(x+w/2,y+h+12*K,'R33',3*K,'#627181',True,'middle')
 elif id==14:d.poly(rect(x+2*K,y+2*K,w-4*K,h-4*K),'#acbac6','#8295a7',.2*K)
 # Keep corner matching codes legible where surface artwork passes underneath.
 for lx,ly,label,size in n.labels:
  if not label[-1:].isalpha():continue
  point=(lx,ly)
  on_wall=any(color==PAPER and all((1 if area(face)>0 else -1)*cross(sub(b,a),sub(point,a))>=-1e-7 for a,b in edges(face)) for face,color in n.faces)
  if on_wall:
   tw=stringWidth(label,'Helvetica',size)
   d.poly(rect(lx-tw/2-.25,ly-size,tw+.5,size+.3),PAPER)
   d.text(lx,ly,label,size,BLUE,anchor='middle')
 part_crop(d,n,start);return n

def strip(d,id,x,y):
 p=DATA['parts'][id-1];n=Net(id);n.face(rect(x,y,p['w'],p['d']),GLUE);start=len(d.svg);n.draw(d)
 d.line((x+10,y),(x+10,y+p['d']),'#8896aa',.15,[.5,1])
 d.text(x+10,y+p['d']/2,f'{id:02} / {p["name"]}',2.5,INK,True,'middle',90)
 part_crop(d,n,start);return n

def ramp(d,x=28,y=61):
 n=Net(6);p=DATA['ramp'];run,rise,w=p['w'],p['h'],p['d'];L=math.hypot(run,rise);t=run*run/L;alt=run*rise/L
 n.face(rect(x,y,L,w),'#dce2e8')
 for sign,yy in [(-1,y),(1,y+w)]:
  a=(x,yy);b=(x+L,yy);v=(x+t,yy+sign*alt);n.face([a,b,v],PAPER);n.fold(a,b)
  u=mul(sub(v,a),1/run);normal=(sign*-u[1],sign*u[0]);n.tab(add(a,mul(u,4)),add(v,mul(u,-2)),normal,'6')
 n.face(rect(x+L,y,rise,w),PAPER);n.fold((x+L,y),(x+L,y+w));n.tab((x+L+rise,y+3),(x+L+rise,y+w-3),(1,0),'6')
 start=len(d.svg);n.draw(d);d.line((x,y+w/2),(x+L,y+w/2),'#b69b4b',.9*K,[3*K,2*K]);part_crop(d,n,start);return n


def plate(d,id,x,y):
 p=DATA['parts'][id-1];n=Net(id);n.face(rect(x,y,p['w'],p['d']),TOP);start=len(d.svg);n.draw(d)
 d.poly(rect(x+.6,y+.6,p['w']-1.2,p['d']-1.2),None,'#a1afbc',.2)
 child=DATA['parts'][7 if id==11 else 12]
 placement(d,x+child['x']-p['x'],y+child['y']-p['y'],child['w'],child['d'],child['id'])
 d.text(x+1.4,y+2.7,str(id),1.8,MUTED)
 part_crop(d,n,start);return n

def screen(d,x,y):
 p=DATA['parts'][12];n=Net(13);n.face(rect(x,y,p['w'],p['h']),PAPER)
 n.face(rect(x,y+p['h'],p['w'],p['d']),GLUE);n.fold((x,y+p['h']),(x+p['w'],y+p['h']))
 start=len(d.svg);n.draw(d);draw_art(d,'radar',(x,y));d.text(x+p['w']/2,y+p['h']+2.8,'13',1.8,BLUE,True,'middle')
 part_crop(d,n,start);return n


def rib(d,id,x,y):
 p=DATA['parts'][id-1];n=Net(id);w,h=p['d'],p['h'];n.face(rect(x,y,w,h),TOP)
 n.tab((x+1,y),(x+w-1,y),(0,-1),'DECK')
 n.tab((x+1,y+h),(x+w-1,y+h),(0,1),'BASE')
 start=len(d.svg);n.draw(d)
 d.text(x+w/2,y+h/2,f'{id} / SUPPORT',2.6,INK,True,'middle')
 d.text(x+w/2,y+h/2+5,f'Hull {DATA["hullParts"][DATA["ribParts"].index(id)]}',2.5,MUTED,anchor='middle')
 part_crop(d,n,start);return n

c=canvas.Canvas(str(PDF),pagesize=(W*mm,H*mm),invariant=1)
c.setTitle('INS Vikramaditya - 71 cm paper model - 1:400 - A4');c.setAuthor('Paper Craft')
allnets=[]
def page(num,compact=False):
 d=Drawing(c,compact);header(d,num,DATA['sheetNames'][num-1]);return d
def finish(d,num):footer(d);d.save(f'sheet-{num}.svg');c.showPage()
for num,id in enumerate(DATA['hullParts'],1):
 d=page(num,True);allnets.append(hull(d,id));finish(d,num)
for num,id in enumerate(DATA['deckParts'],5):
 d=page(num);allnets.append(deck(d,id))
 if num<8:
  join=DATA['joinParts'][num-5];allnets.append(strip(d,join,207,36))
  notes(d,237,44,['Keep flat.','10 mm of strip','under each','deck panel.','Butt edges;','do not overlap.'])
 else:notes(d,209,44,['BOW / panel 18','Deck order:','3 - 4 - 17 - 18','','Join with strips','5, 19 and 20.','','Match all three','deck seams to','the hull seams.'])
 finish(d,num)
d=page(9);allnets.append(box(d,DATA['parts'][6],74,72));notes(d,23,156,['07 / Island: fold walls down, match corner letters, then fold base tabs inward.', 'Glue base tabs to deck guide 7. Gallery guide 11 faces the bow; funnel guide 9 faces the stern.']);finish(d,9)
d=page(10)
for id,x,y in [(8,48,76),(9,192,76)]:allnets.append(box(d,DATA['parts'][id-1],x,y))
notes(d,23,160,['08 / Bridge mounts on gallery 11 (sheet 12). Keep its 3.5 mm gallery rim visible.', '09 / Funnel mounts on island guide 9. Printed grilles remain uncut.']);finish(d,10)
d=page(11)
for id,x,y in [(10,56,83),(14,194,83)]:allnets.append(box(d,DATA['parts'][id-1],x,y))
notes(d,23,166,['10 / Foremast fits bridge guide 10. Platform 12 (sheet 12) caps the foremast.', '14 / Aft tower fits deck guide 14. Fold walls down and base tabs inward.']);finish(d,11)
d=page(12);allnets.append(ramp(d))
allnets.append(plate(d,11,179,35));allnets.append(plate(d,12,179,106));allnets.append(screen(d,239,106))
notes(d,17,170,['06 / High end toward bow. 11 / Gallery centred on island; bridge on guide 8.', '12 / Platform centred on foremast. 13 / Fold foot away; glue printed foot to guide 13.', 'Radar screen stands on port edge of guide 13, with its foot pointing toward starboard.']);finish(d,12)
d=page(13)
for id,x,y in [(21,23,38),(22,23,115),(23,171,38),(24,171,115)]:allnets.append(rib(d,id,x,y))
notes(d,127,106,['Fold both tabs away from print.', 'The printed BASE tab glues down;', 'the printed DECK tab glues up.'])
finish(d,13);c.save()
reader=PdfReader(PDF);assert len(reader.pages)==DATA['sheets']
for p in reader.pages:assert abs(float(p.mediabox.width)/mm-W)<.001 and abs(float(p.mediabox.height)/mm-H)<.001
for i,a in enumerate(allnets):
 for b in allnets[i+1:]:
  if DATA['parts'][a.id-1]['sheet']==DATA['parts'][b.id-1]['sheet']:
   ax,ay,ar,ab=a.bounds;bx,by,br,bb=b.bounds
   assert ar<=bx or br<=ax or ab<=by or bb<=ay,('separate pieces overlap',a.id,b.id)
for kind,ids in [('hull',DATA['hullParts']),('deck',DATA['deckParts'])]:
 parts=[DATA['parts'][id-1] for id in ids]
 assert parts[0]['x']==0 and parts[-1]['x']+parts[-1]['w']==DATA['length']
 for a,b in zip(parts,parts[1:]):
  boundary=a['x']+a['w'];assert boundary==b['x']
  seam=[]
  for part in [a,b]:
   pts=section(DATA[kind]['outline'],part['x'],part['x']+part['w'])
   seam.append(sorted(round(y,6) for x,y in pts if abs(x-boundary)<1e-6))
  assert seam[0]==seam[1],('mismatched seam',kind,boundary)
for id in DATA['ribParts']:
 p=DATA['parts'][id-1];ys=[]
 for a,b in edges(DATA['hull']['outline']):
  if min(a[0],b[0])<=p['x']<=max(a[0],b[0]) and a[0]!=b[0]:ys.append(a[1]+(b[1]-a[1])*(p['x']-a[0])/(b[0]-a[0]))
 assert abs(p['y']-min(ys))<1e-6 and abs(p['d']-(max(ys)-min(ys)))<1e-6,('rib fit',id)
 assert p['h']==DATA['hull']['height']
assert abs(DATA['length']-284000/DATA['scale'])<.001
assert abs(DATA['beam']-60000/DATA['scale'])<.001
assert abs(math.degrees(math.atan(DATA['ramp']['h']/DATA['ramp']['w']))-14)<.01
parts={p['id']:p for p in DATA['parts']}
for child_id,parent_id in [(11,7),(8,11),(10,8),(12,10),(13,12)]:
 child,parent=parts[child_id],parts[parent_id]
 assert abs(child['z']-(parent['z']+parent['h']))<1e-6,('floating mount',child_id)
 if child_id in [11,12]:assert abs(child['y']+child['d']/2-parent['y']-parent['d']/2)<1e-6
 if child_id==12:assert abs(child['x']+child['w']/2-parent['x']-parent['w']/2)<1e-6
 if child_id in [8,10,13]:
  assert child['x']>=parent['x'] and child['y']>=parent['y']
  assert child['x']+child['w']<=parent['x']+parent['w'] and child['y']+child['d']<=parent['y']+parent['d']
assert sorted(n.id for n in allnets)==[p['id'] for p in DATA['parts']]
shutil.copy2(PDF,OUT/'vikramaditya-a4.pdf')
print('PASS: 13 exact A4 landscape sheets; 24 cut pieces; 710 mm at 1:400; margins and net overlap; four hull/deck sections; three matched seams; rib fit; stacked mounts.')
print('Prototype: real-paper assembly remains untested.')
print(PDF)
