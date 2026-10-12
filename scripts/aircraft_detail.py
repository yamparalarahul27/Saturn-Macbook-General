"""Construction and surface detail shared by the printed and assembled aircraft."""
import math

def enrich(mig, heli, face, part, rect, flat):
    ink='#687e89'; glass='#739cac'; light='#aecbd4'; olive='#7f916e'; tan='#d1c4a0'
    def circle(x,y,r):return [[x+r*math.cos(i*math.pi/12),y+r*math.sin(i*math.pi/12)] for i in range(24)]
    def strip(a,b,w=.10):
        dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy);nx,ny=-dy/n*w/2,dx/n*w/2
        return [[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]]
    def add(p,poly,color,project):
        p['art'].append(face(poly,color)); f=face([project(x,y) for x,y in poly],color);f['detail']=True;p['mesh'].append(f)
    def plane(p,poly,color,z=.03):add(p,poly,color,lambda x,y:[x,y,z])
    def side(p,poly,color,depth,width=3):
        for sign in [-1,1]:
            net=poly if sign<0 else [[x,-width-y] for x,y in poly]
            p['art'].append(face(net,color)); f=face([[x,sign*(width/2+.03),depth-y] for x,y in poly],color);f['detail']=True;p['mesh'].append(f)
    def cap(id,name,l,w,h,x,y,z,color):
        faces=[face(rect(0,0,l,w),color),face(rect(0,-h,l,h),color),face(rect(0,w,l,h),color),face(rect(-h,0,h,w),color),face(rect(l,0,h,w),color)]
        folds=[[[0,0],[l,0]],[[0,w],[l,w]],[[0,0],[0,w]],[[l,0],[l,w]]]
        maps=[lambda a,b:[x+a,y+b,z+h],lambda a,b:[x+a,y,z+h+b],lambda a,b:[x+a,y+w,z+h-(b-w)],lambda a,b:[x,y+b,z+h+a],lambda a,b:[x+l,y+b,z+h-(a-l)]]
        meshes=[face([maps[i](*v) for v in f['points']],f['fill']) for i,f in enumerate(faces)]
        p=part(id,name,faces,folds,mesh=meshes)
        # The two end panels are inlet / exhaust faces, not cut-out holes.
        add(p,rect(-h+.15,.15,h-.3,w-.3),'#344953',maps[3])
        add(p,rect(l+.15,.15,h-.3,w-.3),'#46545b',maps[4])
        for a in [l*.3,l*.65]:add(p,rect(a,0,.10,w),ink,maps[0])
        return p,maps
    # Wing hinge/aileron lines, walkways, airframe roundels and leading-edge accents.
    for sign in [-1,1]:
        for a,b in [((20,6),(30,6)),((25,12.8),(30.5,12.8)),((37,6.5),(42,6.5)),((16,3),(26,14))]:
            plane(mig[0],strip([a[0],sign*a[1]],[b[0],sign*b[1]]),ink)
        for r,col in [(.85,'#c77e4f'),(.58,'#f3eee6'),(.30,'#668766')]:plane(mig[0],circle(27.7,sign*9.5,r),col)
        plane(mig[0],rect(17,sign*3.2 if sign>0 else -3.65,7,.45),'#81949e')
    for poly,color in [([[.5,3.4],[4,1.6],[4,3.4]],'#8e9ea6'),(rect(18,1.2,7,.12),ink),(rect(20,2.5,9,.12),ink)]:side(mig[1],poly,color,3.5)
    for x in [18,19,20,21,22]:side(mig[1],rect(x,.55,.22,.55),ink,3.5)
    # Upright fin stripes and rudder hinges, transformed to their installed positions.
    for i,p in enumerate(mig[2:4]):
        y=-2.4 if i==0 else 2.4
        project=lambda x,v,y=y:[34+x,y-.025,1.5-v]
        for a,b in [([5.6,-4.7],[6.7,-.5]),([1,-.65],[6.5,-.65])]:add(p,strip(a,b),ink,project)
        for row,col in enumerate(['#c77e4f','#f3eee6','#668766']):add(p,rect(3.4,-4.1+row*.4,1.7,.4),col,project)
        # Fin feet now sit on the engine roofs.
        for f in p['mesh']:
            if not f.get('detail'):f['points']=[[x,y,z+1.5] for x,y,z in f['points']]
    for id,y in [('M5',-4.1),('M6',1.9)]:
        p,maps=cap(id,'Port engine housing' if id=='M5' else 'Starboard engine housing',18,2.2,1.5,25.25,y,0,'#aebfc9')
        # Fin foot guide: left fold lies 1.7 mm across roof, right at .5 mm.
        v=1.7 if id=='M5' else .5
        add(p,rect(8.75,v,7,.1),'#315eea',maps[0])
        for x in [14.4,15.1,15.8,16.5,17.2]:add(p,rect(x,.12,.13,1.96),ink,maps[0])
        mig.append(p)
    p,maps=cap('M7','Raised cockpit canopy',8,2.4,1.1,8,-1.2,3.5,'#536a7c')
    for poly in [rect(.35,.25,2.25,1.9),rect(2.9,.25,4.75,1.9)]:add(p,poly,glass,maps[0])
    add(p,rect(3.1,.38,4.3,.3),light,maps[0])
    for y,idx in [(-.95,1),(2.55,2)]:
        for x,w in [(.35,2.25),(2.9,4.75)]:add(p,rect(x,y,w,.65),glass,maps[idx])
    mig.append(p)
    # Hind camouflage patches stay inside the side profile. The livery is illustrative.
    for poly,col in [([[14,.3],[18,.3],[22,3.5],[20,4.6],[16,3.7]],olive),([[4,7],[9,6],[14,7.8],[12,9.6],[5,9.6]],tan),([[23,4],[28,4.7],[30,6],[26,7.7],[23,7.6]],olive),([[33,5.2],[36,5.5],[38,5.8],[38,7.7],[33,7.7]],tan),([[41,3.5],[43.4,2.1],[43.4,5.8],[41.4,6.5]],olive)]:side(heli[0],poly,col,10)
    # Inset glazing leaves dark frames around the original cockpit windows.
    for poly in [[[3.4,3.2],[5.8,2],[7.6,1.9],[7.6,3.65],[3.4,4.5]],[[9.4,1.8],[11.7,1.45],[12.5,3.6],[9.4,3.6]]]:side(heli[0],poly,glass,10)
    for a,b in [([5.4,2.1],[5.4,4.1]),([10.7,1.7],[10.7,3.5])]:side(heli[0],strip(a,b,.15),ink,10)
    # Cabin door, glazing, access panels, vents and tail reinforcement bands.
    for a,b in [([13.5,4.5],[19.6,4.5]),([19.6,4.5],[19.6,8.6]),([19.6,8.6],[13.5,8.6]),([13.5,8.6],[13.5,4.5]),([23.5,6.4],[38,6.4]),([6,8.8],[11,8.8])]:side(heli[0],strip(a,b,.10),ink,10)
    for x in [14.1,16.8]:side(heli[0],rect(x,5.35,1.8,1.25),glass,10)
    side(heli[0],rect(18.3,7,.8,.18),ink,10)
    for x in [20.8,21.25,21.7,22.15]:side(heli[0],rect(x,5,.18,1.8),ink,10)
    for x in [30.5,37]:side(heli[0],rect(x,5.15 if x<35 else 5.6,.15,2.5 if x<35 else 2.05),ink,10)
    for i,p in enumerate(heli[1:3]):
        sign=-1 if i==0 else 1
        project=lambda x,y,sign=sign:[14+x,sign*(1.5+y),5.03]
        add(p,[[1,1],[4,2],[4.7,5.7],[2,5.4]],olive,project)
        add(p,strip([1.3,5.8],[4.7,5.8]),ink,project)
    for i in range(5):
        a=i*2*math.pi/5
        p=[[r*math.cos(a+t),r*math.sin(a+t)] for r,t in [(20,-.032),(21.45,-.032),(21.45,.032),(20,.032)]]
        add(heli[4],p,'#d9bd69',lambda x,y:[14+x,y,12.03])
        p=[[r*math.cos(a+t),r*math.sin(a+t)] for r,t in [(3,-.02),(19.6,-.02),(19.6,-.005),(3,-.005)]]
        add(heli[4],p,'#8d9c9b',lambda x,y:[14+x,y,12.03])
    add(heli[4],circle(0,0,1.1),'#819094',lambda x,y:[14+x,y,12.04])
    for i in range(3):
        a=i*2*math.pi/3
        p=[[r*math.cos(a+t),r*math.sin(a+t)] for r,t in [(3.6,-.105),(4.4,-.105),(4.4,.105),(3.6,.105)]]
        add(heli[6],p,'#ded8bf',lambda x,y:[41+x,1.73,7+y])
    for id,y in [('H8',-1.4),('H9',.2)]:
        p,maps=cap(id,'Port engine cover' if id=='H8' else 'Starboard engine cover',4.5,1.2,1.2,8,y,10,olive)
        for x in [1,1.5,2,2.5,3]:add(p,rect(x,.2,.15,.8),ink,maps[0])
        heli.append(p)
