"""Printable surface artwork, in local millimetres, shared with the SVG model.

These are schematic markings, not a survey of the real vessel. JSON is emitted
by generate-kit.py so the browser and PDF use exactly the same primitives.
"""
import math


def artwork(data):
    result = {}

    def surface(name):
        items = []
        result[name] = items
        def line(x, y, x2, y2, stroke='#8996a4', width=.18, dash=None):
            items.append(dict(op='line', x=x, y=y, x2=x2, y2=y2, stroke=stroke, width=width, dash=dash or []))
        def rect(x, y, w, h, fill='none', stroke='#8996a4', width=.18):
            items.append(dict(op='rect', x=x, y=y, w=w, h=h, fill=fill, stroke=stroke, width=width))
        def circle(x, y, r, stroke='#8996a4', width=.16):
            items.append(dict(op='circle', x=x, y=y, r=r, stroke=stroke, width=width))
        return line, rect, circle

    line, rect, circle = surface('deck')
    outline = data['deck']['outline']
    def inside(x,y):
        hit=False
        for a,b in zip(outline,outline[1:]+outline[:1]):
            if (a[1]>y)!=(b[1]>y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]: hit=not hit
        return hit
    # Tiny printed tie-downs on the parking areas; keep landing lanes clear.
    for x in range(12,400,10):
        for y in range(7,82,9):
            if not inside(x,y) or not inside(x,y-3) or not inside(x,y+3):continue
            if 28+x*.05 < y < 61+x*.05:continue
            if 170<x<264 and y<30:continue
            if 136<x<154 and 6<y<24:continue
            circle(x,y,.35,'#adb6be',.12)
            line(x-.6,y,x+.6,y,'#9da9b3',.12)
    # Subdued panel seams and deck-edge light marks.
    for x in range(25,400,25):
        for y in [5,77]:
            if inside(x,y) and inside(x+9,y):line(x,y,x+9,y,'#c5cdd4',.12)
    center=(202,42)
    for a,b in zip(outline,outline[1:]+outline[:1]):
        count=max(1,int(math.dist(a,b)/8))
        for n in range(1,count):
            x=a[0]+(b[0]-a[0])*n/count;y=a[1]+(b[1]-a[1])*n/count
            vx,vy=center[0]-x,center[1]-y;length=math.hypot(vx,vy)
            x+=vx/length*1.7;y+=vy/length*1.7
            circle(x,y,.32,'#b39966',.18)
    for y in [30,57]:line(3,y,245,y+12,'#ffffff',.8)
    line(3,43.5,245,55.5,'#ffffff',.45,[5,3])
    line(82,54,335,36,'#b69b4b',.9,[3,2]);line(335,36,403,36,'#b69b4b',.9,[3,2])
    for x in [44,58,72,86]:line(x,31+x*.044,x,58+x*.044,'#7c8895',.32)
    for x in [8,14,20,26]:
        line(x,32+x*.05,x+3,32+x*.05,'#ffffff',1)
        line(x,55+x*.05,x+3,55+x*.05,'#ffffff',1)
    for x in [15,100,150,280,310]:
        line(x,13,x+18,13,'#a57865',.25);line(x,13,x,19,'#a57865',.25)
    for x,y in [(105,9),(156,7)]:
        rect(x,y,17,15,'#d3dbe2','#9daab6',.25)
        rect(x+1,y+1,15,13,'none','#e8edf0',.25)
        line(x+8.5,y+1,x+8.5,y+14,'#aeb9c2',.16)
        for n in range(0,16,3):line(x+n,y,x+n+1.4,y,'#b59868',.45)
    # Box walls: windows, deck bands, access hatches, ventilation and ladders.
    for p in data['parts']:
        if p['type']!='box':continue
        for side,width in [('side',p['w']),('end',p['d'])]:
            line,rect,circle=surface(f"{p['id']}-{side}")
            h=p['h']
            line(.6,h-1,width-.6,h-1,'#8e9dab',.35)
            if p['id'] in [7,8]:
                for x in range(3,int(width)-3,7):
                    rect(x,3.5,4,2.7,'#637a90','#53697f',.15)
                    line(x,3.5,x+4,3.5,'#a9bdcc',.25)
                line(1,7.6,width-1,7.6,'#a1aebb',.22)
                if width>25:
                    rect(width-10,h-6,3,4.5,'#d4dce3','#8e9dab',.15)
                    circle(width-7.7,h-3.6,.2,'#687d90',.2)
                    for x in range(12,int(width)-16,15):
                        rect(x,h-6,6,3,'#bac6cf','#899ba9',.15)
                        for j in range(1,5):line(x+j,h-5.6,x+j,h-3.4,'#8b9ca9',.14)
            else:
                for x in [.8,width-.8]:line(x,2,x,h-2,'#9cabb7',.18)
                if p['id'] in [10,14]:
                    rect(1.5,2,width-3,6,'#b2c0cd','#7c90a4',.18)
                    for y in range(3,8):line(1.5,y,width-1.5,y,'#7c90a4',.14)
                    for x in range(3,int(width)-2,2):line(x,2,x,8,'#7c90a4',.14)
                    for y in range(11,int(h)-2,2):line(width/2-1,y,width/2+1,y,'#899dab',.18)
                    for x in [width/2-1,width/2+1]:line(x,10,x,h-3,'#899dab',.18)
                if p['id']==9:
                    rect(2,2,width-4,3,'#adb9c3','#8b9ca9',.18)
                    for x in range(3,int(width)-2,2):line(x,2.3,x,4.7,'#758a9c',.2)
    # Hull side artwork follows each actual unfolded edge, excluding joining walls.
    for forward in [False, True]:
        ring=[];split=data['split']
        hull=data['hull']['outline']
        for a,b in zip(hull,hull[1:]+hull[:1]):
            da=(a[0]-split)*(1 if forward else -1);db=(b[0]-split)*(1 if forward else -1)
            if da>=-1e-8:ring.append(a)
            if da<0<db or db<0<da:
                t=da/(da-db);ring.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])])
        for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
            line,rect,circle=surface(f"hull-{2 if forward else 1}-{i}")
            width=math.dist(a,b)
            if width<20 or abs(a[0]-split)<1e-7 and abs(b[0]-split)<1e-7:continue
            line(1,22.5,width-1,22.5,'#8c9aa7',.4)
            line(1,3,width-1,3,'#c0cad3',.18)
            for x in range(14,int(width)-10,12):
                circle(x,5.5,.65,'#8e9eac',.2)
                line(x+5,8,x+5,21,'#c0cad3',.13)
            for x in range(32,int(width)-15,48):
                rect(x,10,7,9,'#cdd7df','#9dabb7',.18)
                line(x+3.5,10,x+3.5,19,'#a7b4bf',.15)
                for y in [12,15,18]:line(x+.5,y,x+1.5,y,'#879bab',.18)
    line,rect,circle=surface('radar')
    rect(.5,.5,13,7,'#afc1cc','#71879a',.22)
    for y in range(1,8):line(.5,y,13.5,y,'#71879a',.15)
    for x in range(1,14):line(x,.5,x,7.5,'#71879a',.15)
    return result
