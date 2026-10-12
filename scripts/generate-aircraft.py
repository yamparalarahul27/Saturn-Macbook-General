"""Generate A4 nets from the same triangulated shells used by the browser."""
from pathlib import Path
import json, math, html, shutil
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from pypdf import PdfReader
from aircraft_geometry import models as build_models, distance, GLUE, validate
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/kits/aircraft';OUT.mkdir(parents=True,exist_ok=True)
PDF=ROOT/'output/pdf/aircraft-a4.pdf'
BLUE='#315eea'
models=build_models()
validate(models)
(ROOT/'src/data/aircraft.json').write_text(json.dumps(models,separators=(',',':'))+'\n')
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
    for a,b in p['folds']:
        is_tab=any(f['fill']==GLUE and f['points'][:2]==[a,b] for f in p['faces'])
        line(*move([a,b]),BLUE if is_tab else '#98a6ad',True,.12)
    for f in p['art']:poly(move(f['points']),f['fill'],width=0)
    text(x,y+y1-y0+3,p['id'],2.2)
    return (x,y,x+x1-x0,y+y1-y0+3)
def pagehead(title,subtitle,page):
    text(12,12,'PAPER CRAFT / AIRCRAFT COLLECTION / SHAPE STUDY',3,BLUE);text(12,20,title,4.5);text(12,27,subtitle,2.5)
    text(242,12,f'1:400  /  A4  /  {page} of 4',2.7)
def footer():
    line([12,187],[285,187], '#ced9df');text(12,194,'Outer outline: cut | Grey dashes: facets | Blue dashes: tabs | Lilac: glue.',2.6)
    text(12,200,'Print single-sided at 100% / Actual size. No Fit to page. Use 100-120 gsm paper.',2.6)
    text(12,205,'Simplified display miniatures. Trial-build one before making the fleet. Guide: /aircraft',2.4)
    line([235,201],[285,201]);line([235,199],[235,203]);line([285,199],[285,203]);text(251,198,'50 mm check',2.4)
def savepage(n):
    (OUT/f'sheet-{n}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210"><rect width="297" height="210" fill="white"/>'+''.join(svg)+'</svg>')
    c.showPage();svg.clear()

def modelcopy(model,x,y,label):
    text(x,y,label,2.5,BLUE)
    # Shelf pack one complete model in its own 130 x 146 mm area.
    cx=x;cy=y+7;rowheight=0;boxes=[]
    for p in model['parts']:
        x0,y0,x1,y1=bounds(p);w=x1-x0;h=y1-y0+4
        if cx+w>x+126:cx=x;cy+=rowheight+5;rowheight=0
        assert cy+h<182,(p['id'],'model block too tall',cy+h)
        boxes.append(drawpart(p,cx,cy));cx+=w+6;rowheight=max(rowheight,h)
    for i,a in enumerate(boxes):
        for b in boxes[i+1:]:assert a[2]<b[0] or b[2]<a[0] or a[3]<b[1] or b[3]<a[1],('page overlap',a,b)
for n in range(1,5):
    m=models[0] if n<4 else models[1]
    pagehead(m['name']+' / two complete models',f"{len(m['parts'])} pieces each. Segmented shells; join in number order. Use the updated online guide.",n)
    for i in range(2):modelcopy(m,12+i*140,35,f"{m['name']} {((n-1)*2+i+1) if n<4 else i+1:02d}")
    footer();savepage(n)
c.save();shutil.copy(PDF,OUT/PDF.name)
r=PdfReader(PDF);assert len(r.pages)==4
for page in r.pages:assert abs(float(page.mediabox.width)/mm-297)<.001 and abs(float(page.mediabox.height)/mm-210)<.001
for model in models:
    for p in model['parts']:
        for f in p['faces']:assert len(f['points'])>=3 and all(math.isfinite(v) for pt in f['points'] for v in pt)
        for a,b in p['folds']:
            count=sum(1 for f in p['faces'] for u,v in zip(f['points'],f['points'][1:]+f['points'][:1]) if (a==u and b==v) or (a==v and b==u))
            assert count==2,(p['id'],'unmatched fold',count)
print(f'PASS: 4 A4 sheets, {sum(len(m["parts"])*m["count"] for m in models)} pieces; unfolded triangle lengths match mesh; fold hinges and page separation checked.')
