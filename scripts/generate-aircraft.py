"""Original simplified 1:400 aircraft nets, shared PDF/SVG/preview geometry."""
from pathlib import Path
import json, math, html, shutil
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/kits/aircraft'; OUT.mkdir(parents=True,exist_ok=True)
PDF=ROOT/'output/pdf/aircraft-a4.pdf'
C='#ced9df'; DARK='#536a7c'; BLUE='#315eea'; GLUE='#eee8f6'; GREEN='#b8c4ae'
def face(points,fill=C):return {'points':points,'fill':fill}
def part(id,name,faces,folds=[],art=[],mesh=[]):return dict(id=id,name=name,faces=faces,folds=folds,art=art,mesh=mesh)
def rect(x,y,w,h):return [[x,y],[x+w,y],[x+w,y+h],[x,y+h]]
def flat(poly,z=0):return [[x,y,z] for x,y in poly]
def body(id,L,profile,a,b,w,depth,color):
    mirror=lambda p:[[x,-w-y] for x,y in p]
    roof=rect(a,-w,b-a,w)
    folds=[[[a,0],[b,0]],[[a,-w],[b,-w]]]
    # Two shaped sides hinge down from the narrow roof; open underside glues to wing/deck.
    meshes=[face([[x,-w/2,depth-y] for x,y in profile],color),face([[x,w/2,depth-y] for x,y in profile],color),face([[a,-w/2,depth],[b,-w/2,depth],[b,w/2,depth],[a,w/2,depth]],color)]
    windows=[[[4,2.1],[7,1],[10,1],[10,2.8],[5,3.3]]] if id=='M2' else [[[3,3],[6,1.5],[8,1.5],[8,4],[3,5]],[[9,1.5],[12,1],[13,4],[9,4]]]
    art=[face(p,DARK) for p in windows]+[face(mirror(p),DARK) for p in windows]
    for p in windows:
        meshes += [face([[x,-w/2-.02,depth-y] for x,y in p],DARK),face([[x,w/2+.02,depth-y] for x,y in p],DARK)]
    return part(id,'Folded fuselage',[face(profile,color),face(mirror(profile),color),face(roof,color)],folds,art,meshes)
L=43.25; S=29.975
half=[[0,0],[8,-1.5],[16,-3],[26,-S/2],[32,-S/2],[29,-4],[35,-4],[40,-9],[L,-9],[41,-2],[L,-2],[L,0]]
wing=half+[[x,-y] for x,y in reversed(half[1:-1])]
mig=[part('M1','Wing and tailplane',[face(wing)],art=[face(rect(18,-3,18,6),'#b9c6cf')],mesh=[face(flat(wing)),face(flat(rect(18,-3,18,6),.02),'#b9c6cf')]),body('M2',L,[[0,3.5],[0,3],[5,1],[8,0],[29,0],[L,1.5],[L,3.5]],8,29,3,3.5,C)]
for id,y in [('M3',-2.4),('M4',2.4)]:
    fin=[[0,0],[3,-5],[6,-5],[7,0]]
    mig.append(part(id,'Port fin' if y<0 else 'Starboard fin',[face(fin),face(rect(0,0,7,1.5),GLUE)],[[[0,0],[7,0]]],mesh=[face([[34+x,y,-v] for x,v in fin]),face(flat(rect(34,y-1.5 if y<0 else y,7,1.5)))]))
profile=[[0,8],[0,5],[3,2],[7,0],[20,0],[23,3],[38,5],[42,1],[43.75,1],[43.75,8],[23,8],[18,10],[4,10]]
heli=[body('H1',43.75,profile,7,20,3,10,GREEN)]
for id,sign in [('H2',-1),('H3',1)]:
    p=[[0,0],[1,6.8125],[5,6.8125],[6,0]]
    heli.append(part(id,'Port stub wing' if sign<0 else 'Starboard stub wing',[face(p,GREEN),face(rect(0,-1.5,6,1.5),GLUE)],[[[0,0],[6,0]]],mesh=[face([[14+x,sign*(1.5+y),5] for x,y in p],GREEN)]))
tail=[[-2,-6],[2,-6],[2,6],[-2,6]]
heli.append(part('H4','Tailplane',[face(tail,GREEN)],mesh=[face([[35+x,y,2] for x,y in tail],GREEN)]))
# Single five-blade star: all tips lie on the 21.625 mm rotor radius.
rotor=[]
for i in range(5):
    a=2*math.pi*i/5
    for r,t in [(1.6,a-.34),(21.625,a-.032),(21.625,a+.032),(1.6,a+.34)]:rotor.append([r*math.cos(t),r*math.sin(t)])
heli.append(part('H5','Five-blade main rotor',[face(rotor,DARK)],mesh=[face([[14+x,y,12] for x,y in rotor],DARK)]))
# Open-bottom 2 mm mast cube, top plus four hinged sides. Glue their lower edges onto roof.
faces=[face(rect(0,0,2,2),GREEN),face(rect(0,-2,2,2),GREEN),face(rect(0,2,2,2),GREEN),face(rect(-2,0,2,2),GREEN),face(rect(2,0,2,2),GREEN)]
folds=[[[0,0],[2,0]],[[0,2],[2,2]],[[0,0],[0,2]],[[2,0],[2,2]]]
heli.append(part('H6','Rotor mast',faces,folds,mesh=[face([[13,-1,10],[15,-1,10],[15,-1,12],[13,-1,12]],GREEN),face([[13,-1,12],[15,-1,12],[15,1,12],[13,1,12]],GREEN),face([[15,-1,10],[15,1,10],[15,1,12],[15,-1,12]],GREEN)]))
tr=[]
for i in range(3):
    a=2*math.pi*i/3
    for r,t in [(1,a-.4),(4.5,a-.11),(4.5,a+.11),(1,a+.4)]:tr.append([r*math.cos(t),r*math.sin(t)])
heli.append(part('H7','Tail rotor',[face(tr,DARK)],mesh=[face([[41+x,1.7,7+y] for x,y in tr],DARK)]))
# Mounting marks are printed on both body sides, with the mast guide on the roof.
for shape in [rect(14,4.9,6,.2),rect(34.7,7.6,.6,.4),rect(40.7,2.7,.6,.6)]:
    heli[0]['art'].extend([face(shape,BLUE),face([[x,-3-y] for x,y in shape],BLUE)])
heli[0]['art'].append(face(rect(13,-2.5,2,2),GLUE))
models=[dict(id='mig',name='MiG-29K',label='Carrier fighter',size='43.25 mm long · 29.98 mm wingspan',count=6,parts=mig),dict(id='hind',name='Mil Mi-24',label='Custom display addition',size='43.75 mm fuselage · 43.25 mm rotor diameter',count=2,parts=heli)]
# All browser coordinates and print paths are generated from these same parts.
(ROOT/'src/data/aircraft.json').write_text(json.dumps(models,indent=2)+'\n')
W,H=297,210
c=canvas.Canvas(str(PDF),pagesize=(W*mm,H*mm),invariant=1)
c.setTitle('Paper Craft - MiG-29K and Mil Mi-24 - 1:400')
svg=[]
def poly(p,fill,stroke='#334155',width=.16):
    path=c.beginPath();path.moveTo(p[0][0]*mm,(H-p[0][1])*mm)
    for x,y in p[1:]:path.lineTo(x*mm,(H-y)*mm)
    path.close();c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke));c.setLineWidth(width*mm);c.drawPath(path,fill=1,stroke=bool(width))
    svg.append(f'<polygon points="{" ".join(f"{x:.4f},{y:.4f}" for x,y in p)}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
def line(a,b,color='#334155',dash=False,width=.16):
    c.setStrokeColor(HexColor(color));c.setLineWidth(width*mm);c.setDash([.8*mm,.55*mm] if dash else []);c.line(a[0]*mm,(H-a[1])*mm,b[0]*mm,(H-b[1])*mm);c.setDash([])
    svg.append(f'<path d="M{a[0]} {a[1]} L{b[0]} {b[1]}" stroke="{color}" stroke-width="{width}" fill="none"'+(' stroke-dasharray=".8 .55"' if dash else '')+'/>')
def text(x,y,s,size=2.7,color='#536a7c'):
    c.setFont('Helvetica',size*mm);c.setFillColor(HexColor(color));c.drawString(x*mm,(H-y)*mm,s)
    svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial" font-size="{size}">{html.escape(s)}</text>')
def bounds(p):
    pts=[v for f in p['faces'] for v in f['points']]
    return min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)
def drawpart(p,x,y):
    x0,y0,x1,y1=bounds(p);move=lambda pts:[[a+x-x0,b+y-y0] for a,b in pts]
    assert x>=10 and y>=25 and x+x1-x0<=287 and y+y1-y0<=180
    for f in p['faces']:poly(move(f['points']),f['fill'],width=0)
    for f in p['faces']:
        pts=f['points']
        for a,b in zip(pts,pts[1:]+pts[:1]):
            if any((a==v and b==u) or (a==u and b==v) for u,v in p['folds']):continue
            line(*move([a,b]))
    for a,b in p['folds']:line(*move([a,b]),BLUE,True)
    for f in p['art']:poly(move(f['points']),f['fill'],width=0)
    text(x,y+y1-y0+3,p['id'],2.2)
    return (x,y,x+x1-x0,y+y1-y0+3)
def pagehead(title,subtitle,page):
    text(12,12,'PAPER CRAFT / AIRCRAFT COLLECTION',3,BLUE);text(12,20,title,4.5);text(12,27,subtitle,2.5)
    text(242,12,f'1:400  /  A4  /  {page} of 2',2.7)
def footer():
    line([12,187],[285,187], '#ced9df');text(12,194,'Solid: cut   |   Blue dashed: fold   |   Lilac: glue foot   |   Score before cutting.',2.6)
    text(12,200,'Print single-sided at 100% / Actual size. No Fit to page. Use 160-200 gsm card.',2.6)
    text(12,205,'Simplified display miniatures. Trial-build one before making the fleet. Guide: /aircraft',2.4)
    line([235,201],[285,201]);line([235,199],[235,203]);line([285,199],[285,203]);text(251,198,'50 mm check',2.4)
def savepage(n):
    (OUT/f'sheet-{n}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210"><rect width="297" height="210" fill="white"/>'+''.join(svg)+'</svg>')
    c.showPage();svg.clear()
pagehead('MiG-29K / six carrier fighters','Four pieces per aircraft. Wings stay spread in this edition. Blue lines on M1 locate the fuselage and fin feet; do not fold M1.',1)
for row in range(2):
    for col in range(3):
        x=12+col*94;y=35+row*75
        text(x,y,f'AIRCRAFT {row*3+col+1:02d}',2.4,BLUE)
        boxes=[drawpart(mig[0],x,y+5),drawpart(mig[1],x,y+43),drawpart(mig[2],x+56,y+8),drawpart(mig[3],x+70,y+8)]
        # Printed mounting guides for fuselage rails and both fin feet.
        for v in [-1.5,1.5]:line([x+8,y+5+S/2+v],[x+29,y+5+S/2+v],BLUE,True,.12)
        for v in [-2.4,2.4]:line([x+34,y+5+S/2+v],[x+41,y+5+S/2+v],BLUE,True,.12)
        for i,a in enumerate(boxes):
            for b in boxes[i+1:]:assert a[2]<b[0] or b[2]<a[0] or a[3]<b[1] or b[3]<a[1],('overlap',a,b)
footer();savepage(1)
pagehead('Mil Mi-24 / two display helicopters','Custom addition to the carrier display; not a Vikramaditya air-group aircraft. Seven pieces per helicopter.',2)
for n in range(2):
    x=14+n*140;y=38;text(x,y,f'HELICOPTER {n+1:02d}',2.5,BLUE)
    positions=[(x,y+8),(x+62,y+8),(x+79,y+8),(x+97,y+8),(x,y+58),(x+63,y+60),(x+88,y+60)]
    boxes=[drawpart(p,*pos) for p,pos in zip(heli,positions)]
    text(x+61,y+87,'H6: fold four sides down.',2.5);text(x+61,y+92,'Glue lower edges to H1 roof.',2.5)
    text(x+61,y+99,'H5: glue centre onto H6.',2.5);text(x+61,y+106,'H7: glue to the tail side.',2.5)
    for i,a in enumerate(boxes):
        for b in boxes[i+1:]:assert a[2]<b[0] or b[2]<a[0] or a[3]<b[1] or b[3]<a[1],('overlap',a,b)
footer();savepage(2);c.save();shutil.copy(PDF,OUT/PDF.name)
r=PdfReader(PDF);assert len(r.pages)==2
for p in r.pages:assert abs(float(p.mediabox.width)/mm-297)<.001 and abs(float(p.mediabox.height)/mm-210)<.001
assert max(x for x,y in wing)-min(x for x,y in wing)==43.25
assert abs(max(y for x,y in wing)-min(y for x,y in wing)-29.975)<1e-8
assert all(abs(math.hypot(*rotor[i])-21.625)<1e-8 for i in range(len(rotor)) if i%4 in [1,2])
print('PASS: two exact A4 pages; 6 x 4 + 2 x 7 = 38 parts; margins and part separation; 1:400 dimensions; shared SVG/PDF geometry.')
