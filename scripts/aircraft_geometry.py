"""Faceted aircraft shells. Every printed triangle unfolds an actual mesh triangle."""
import math
from collections import Counter
GREY='#b4c1c8'; GREEN='#859479'; GLASS='#506f7d'; GLUE='#ece7f5'
def sub(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return math.sqrt(dot(a,a))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def distance(a,b):return norm(sub(a,b))
def face(p,c,detail=False,cull=False):return dict(points=p,fill=c,detail=detail,cull=cull)
def makepart(id,name):return dict(id=id,name=name,faces=[],folds=[],art=[],mesh=[],checks=[])
def shade(c,t):
    return '#'+''.join(f'{max(0,min(255,round(int(c[i:i+2],16)*t))):02x}' for i in (1,3,5))
def third(a,b,ra,rb,side):
    d=distance(a,b);u=[(b[i]-a[i])/d for i in range(2)]
    x=(ra*ra-rb*rb+d*d)/(2*d);h=math.sqrt(max(0,ra*ra-x*x))
    return [a[0]+x*u[0]-side*h*u[1],a[1]+x*u[1]+side*h*u[0]]
def side(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def tab(p,a,b,inside,depth=.65):
    d=distance(a,b)
    if d<.3:return
    u=[(b[i]-a[i])/d for i in range(2)];s=-1 if side(a,b,inside)>0 else 1
    n=[-u[1]*s,u[0]*s];bevel=min(d*.24,.22)
    q=[a,b,[b[i]-u[i]*bevel+n[i]*depth for i in range(2)],[a[i]+u[i]*bevel+n[i]*depth for i in range(2)]]
    p['faces'].append(face(q,GLUE));p['folds'].append([a,b])
def ring(s,cy=0,n=8):
    x,ry,rz,zc=s
    return [[x,cy+ry*math.cos(-math.pi/2+2*math.pi*i/n),zc+rz*math.sin(-math.pi/2+2*math.pi*i/n)] for i in range(n)]
def shell(id,name,s0,s1,color,cy=0,join=False,glass=False,upper=False):
    p=makepart(id,name);A=ring(s0,cy);B=ring(s1,cy)
    if upper:A=A[2:7];B=B[2:7]
    n=4 if upper else 8
    v={**{f'a{i}':A[i%len(A)] for i in range(n+1)},**{f'b{i}':B[i%len(B)] for i in range(n+1)}}
    triangles=[]
    for i in range(n):triangles.extend([[f'a{i}',f'b{i}',f'b{i+1}'],[f'a{i}',f'b{i+1}',f'a{i+1}']])
    xy={'a0':[0.,0.],'b0':[distance(A[0],B[0]),0.]};prev=None;edgecount=Counter()
    for j,ids in enumerate(triangles):
        known=[i for i in ids if i in xy];new=next(i for i in ids if i not in xy);a,b=known
        sign=1
        if prev:
            other=next(k for k in prev if k not in (a,b));sign=-1 if side(xy[a],xy[b],xy[other])>0 else 1
            p['folds'].append([xy[a],xy[b]])
        xy[new]=third(xy[a],xy[b],distance(v[a],v[new]),distance(v[b],v[new]),sign)
        flat=[xy[i] for i in ids];mesh=[v[i] for i in ids]
        panel=j//2+(2 if upper else 0)
        c=GLASS if glass and panel in [2,3,4,5] else shade(color, [0.8,.88,.98,1.07,1.1,1,.9,.82][panel])
        # Triangles wound outward, based on radial vector at this station.
        normal=cross(sub(mesh[1],mesh[0]),sub(mesh[2],mesh[0]));mid=[sum(k[i] for k in mesh)/3 for i in range(3)]
        if dot(normal,[0,mid[1]-cy,mid[2]-(s0[3]+s1[3])/2])<0:mesh=list(reversed(mesh))
        p['faces'].append(face(flat,c));p['mesh'].append(face(mesh,c,cull=True))
        for k in range(3):
            assert abs(distance(flat[k],flat[(k+1)%3])-distance(v[ids[k]],v[ids[(k+1)%3]]))<1e-6
        prev=ids
    # Close the underside seam. Front tabs attach each section to its predecessor.
    tab(p,xy[f'a{n}'],xy[f'b{n}'],xy[f'b{n-1}'],.65)
    if upper:tab(p,xy['a0'],xy['b0'],xy['b1'],.65)
    if join:
        for i in range(n):tab(p,xy[f'a{i}'],xy[f'a{i+1}'],xy[f'b{i+1}'],.55)
    p['checks']=[dict(kind='shell',front=A,back=B,frontStation=s0,backStation=s1)]
    return p

def flatpart(id,name,poly,project,color,root=None):
    p=makepart(id,name);p['faces']=[face(poly,color)];p['mesh']=[face([project(*v) for v in poly],color)]
    if root:tab(p,root[0],root[1],root[2],.8)
    return p

def art(p,poly,project,color):
    p['art'].append(face(poly,color));p['mesh'].append(face([project(*v) for v in poly],color,True))
def circle(x,y,r):return [[x+r*math.cos(i*math.pi/8),y+r*math.sin(i*math.pi/8)] for i in range(16)]
def strips(prefix,names,stations,color,cy=0,glass_indices=(),upper=False):
    return [shell(f'{prefix}{i+1:02}',names[i],stations[i],stations[i+1],color,cy,i>0,i in glass_indices,upper) for i in range(len(stations)-1)]
def step(title,parts,text):return dict(title=title,ids=[p['id'] for p in parts],text=text)
COMMON='Print at 100%, check the 50 mm ruler, and use 100–120 gsm paper. Score lightly before cutting. Grey diagonals are gentle facet folds; blue dashed lines are tab folds. These very small prototype shells need a trial build. '
SHELL='Form each numbered skin around an eight-sided cross-section. Close its long underside seam with the lilac tab. Then join in numerical order: tuck the next section’s small front tabs inside the previous section, matching all eight panel edges. Keep the underside seams aligned. Do not flatten the body. '
def models():
    # Independent dimensions inferred from public recognition drawings and photographs,
    # anchored to nominal lengths/spans, not a claimed production blueprint.
    ms=[(0,.08,.08,3.0),(5,1.15,.85,3.2),(10,1.65,1.15,3.45),(17,2,1.4,3.3),(27,2.1,1.15,3.0),(36,1.65,.75,2.75),(43.25,.5,.35,2.5)]
    fus=strips('M',['Radome','Forward fuselage','Cockpit fuselage','Centre fuselage','Aft fuselage','Tail fairing'],ms,GREY)
    for p in fus[:1]:
        for f in p['faces']:
            if f['fill']!=GLUE:f['fill']='#75848b'
        for f in p['mesh']:f['fill']='#75848b'
    wings=[]
    for sign,id in [(-1,'M07'),(1,'M08')]:
        poly=[[12,2],[18,4],[25.6,14.9875],[29.1,14.9875],[30.8,4],[33,2]]
        project=lambda x,y,sign=sign:[x,sign*y,3.03]
        p=flatpart(id,'Port wing and leading-edge root' if sign<0 else 'Starboard wing and leading-edge root',poly,project,GREY,([33,2],[12,2],[25,8]))
        for r,c in [(.7,'#c18451'),(.46,'#eee8df'),(.24,'#6b8363')]:art(p,circle(26.4,10,r),project,c)
        wings.append(p)
    engines=[]
    for prefix,cy in [('L',-3.05),('R',3.05)]:
        engines+=strips(prefix,['Intake duct','Engine nacelle','Tapered exhaust'],[(16,1.05,1,2.25),(24,1.3,1.2,2.35),(39.5,1.05,1,2.15),(43.25,.9,.85,2.15)],'#98aab5',cy)
    tails=[]
    for sign,id in [(-1,'M09'),(1,'M10')]:
        poly=[[33,2.4],[38,8],[41.5,8],[40,2.4]];project=lambda x,y,sign=sign:[x,sign*y,2.8]
        tails.append(flatpart(id,'Port stabilizer' if sign<0 else 'Starboard stabilizer',poly,project,GREY,([40,2.4],[33,2.4],[38,6])))
    fins=[]
    for sign,id in [(-1,'M11'),(1,'M12')]:
        poly=[[31.7,0],[35.5,6.5],[37.5,6.3],[39.5,0]]
        project=lambda x,z,sign=sign:[x,sign*(3.05+z*.10),3.15+z]
        p=flatpart(id,'Port fin' if sign<0 else 'Starboard fin',poly,project,GREY,([39.5,0],[31.7,0],[36,3]))
        for row,col in enumerate(['#c18451','#eee8df','#6b8363']):art(p,[[35.5,4.2+row*.35],[36.9,4.2+row*.35],[36.9,4.5+row*.35],[35.5,4.5+row*.35]],project,col)
        fins.append(p)
    canopy=strips('C',['Canopy front','Canopy rear'],[(7.2,.7,.3,4.2),(10.6,1.12,.85,4.9),(15,.8,.2,4.6)],'#657e8b',glass_indices=(0,1),upper=True)
    mp=fus+wings+engines+tails+fins+canopy
    mg=[step('Prepare the rebuilt fighter',mp,COMMON+'One fighter uses 20 pieces. The cockpit and engine pods are tapered shells, not boxes.'),step('Form the tapered fuselage',fus,SHELL+'M01 is the dark nose. M06 is the narrow tail fairing. The front remains a tiny point-sized opening; close it with a dot of glue.'),step('Add the swept wings',wings,'Fold each root tab gently underneath its wing. Glue M07 and M08 symmetrically to the fuselage sides, level with its centre line. The long root extends from 12 to 33 mm behind the nose. Leave the wings spread; their leading-edge extensions run forward beside the cockpit.'),step('Build both engine pods',engines,SHELL+'Make L01–L03 and R01–R03 separately. Keep their inlet and exhaust openings open. Glue the pods beneath the wing roots, centred 3.05 mm either side of the centreline, with their exhausts flush with the tail at 43.25 mm.'),step('Add separate tail surfaces',tails+fins,'Attach M09/M10 below the fins, with their roots from 33 to 40 mm behind the nose. Fold the fin feet outward and glue M11/M12 along the tops of the engine pods. The swept leading edges face forward; cant the fins slightly outward. Use small glue fillets where flat feet meet curved pods.'),step('Shape the rounded canopy',canopy,SHELL+'The canopy is an open-bottom half-shell. Join C01 to C02, glazing facing outward. The small front end points forward. Place this canopy over the upper fuselage between 7.2 and 15 mm behind the nose. Fold its lower edge tabs inward and glue them along the upper fuselage; do not squash its rounded upper profile.'),step('Compare the completed silhouette',mp,'Check the pointed nose, broad swept wings, two separate stabilizers, outward-canted fins and paired open exhausts. This is a reference-informed faceted prototype, not a dimension-certified replica. Landing gear is omitted. Trial-build before repeating the other five fighters.')]
    # Hind stations reproduce a stepped cockpit, deep cabin and rising narrow boom.
    hs=[(0,.1,.15,2.8),(2.7,1.05,1.6,3.7),(5.4,1.55,1.75,4.1),(7,1.75,1.65,4.1),(9.6,2.1,2.55,4.9),(13,2.45,2.9,5.0),(20,2.45,2.85,5.05),(24,1.55,1.5,5.6),(37.8,.4,.55,6.1),(40,.25,.35,6.2)]
    hf=strips('H',['Nose chin','Front cockpit','Cockpit step','Rear cockpit','Cabin front','Main cabin','Cabin taper','Tail boom','Boom tip'],hs,GREEN,glass_indices=(1,3))
    hw=[]
    for sign,id in [(-1,'H10'),(1,'H11')]:
        poly=[[15,2.35],[17,8.3125],[20,8.3125],[20.5,2.35]];project=lambda x,y,sign=sign:[x,sign*y,5.8-(y-2.35)*.18]
        hw.append(flatpart(id,'Port drooping stub wing' if sign<0 else 'Starboard drooping stub wing',poly,project,GREEN,([20.5,2.35],[15,2.35],[18,6])))
    tp=flatpart('H12','Tailplane',[[34,-4.3],[36,-4.3],[36,4.3],[34,4.3]],lambda x,y:[x,y,5.9],GREEN)
    fin=flatpart('H13','Swept tail fin',[[37.8,6],[39.6,6],[43.75,11.1],[42.3,11.5]],lambda x,z:[x,0,z],GREEN,([37.8,6],[39.6,6],[42,10]))
    # Rotor mast is another octagonal sleeve, oriented vertically by rotating its mesh.
    mast=shell('H14','Rotor mast',(0,.55,.55,0),(1.5,.55,.55,0),'#738279')
    for f in mast['mesh']:f['points']=[[15+z,y,9.3+x] for x,y,z in f['points']]
    ro=[]
    for i in range(5):
        a=i*2*math.pi/5
        ro += [[r*math.cos(a+t),r*math.sin(a+t)] for r,t in [(1.3,-.4),(21.625,-.032),(21.625,.032),(1.3,.4)]]
    rotor=flatpart('H15','Five-blade main rotor',ro,lambda x,y:[15+x,y,10.8],'#4d6065')
    for i in range(5):
        a=i*2*math.pi/5;poly=[[r*math.cos(a+t),r*math.sin(a+t)] for r,t in [(20,-.031),(21.5,-.031),(21.5,.031),(20,.031)]]
        art(rotor,poly,lambda x,y:[15+x,y,10.81],'#d6bd6f')
    tr=[]
    for i in range(3):
        a=i*2*math.pi/3;tr += [[r*math.cos(a+t),r*math.sin(a+t)] for r,t in [(1,-.35),(4.5,-.10),(4.5,.10),(1,.35)]]
    tailrotor=flatpart('H16','Three-blade tail rotor',tr,lambda x,y:[42.3+x,-.35,10.3+y],'#4d6065')
    pods=[]
    for cy in [-1.2,1.2]:
        pods+=strips('E',['Engine intake','Engine fairing'],[(7.5,.7,.7,8.3),(11.5,1.05,1,8.5),(20,.8,.8,8.5)],'#76866d',cy)
    for i,p in enumerate(pods):p['id']=f'H{17+i}'
    hp=hf+hw+[tp,fin,mast,rotor,tailrotor]+pods
    hg=[step('Prepare the rebuilt Hind',hp,COMMON+'One helicopter uses 20 pieces. The cockpit steps and narrow tail boom are built into the shell sections.'),step('Build the stepped cockpit',hf[:4],SHELL+'H01–H04 make the chin and two cockpit bulges. Keep the blue glazing on top; the underside seams align below the chin.'),step('Form the cabin and tail boom',hf[4:],SHELL+'Continue with H05–H09. H06 is the wide cabin; H08 narrows sharply into the tail boom. Keep the boom rising toward the tail, as shown in Side view.'),step('Build the engine fairings',pods,SHELL+'H17–H18 form the left engine and H19–H20 the right. Glue the paired rounded pods along the cabin roof from 7.5 to 20 mm behind the nose. Centre them 1.2 mm either side of the centreline; the smaller intake ends face forward.'),step('Fit the drooping stub wings',hw,'Fold H10/H11 root tabs upward. Glue them to the cabin sides from 15 to 20.5 mm behind the nose. Their tips slope slightly downward, about 1 mm below the wing roots. Do not make them horizontal like the old edition.'),step('Build the tail assembly',[tp,fin,tailrotor],'Glue the centre of H12 across the tail boom at 35 mm behind the nose. Attach the H13 foot to the boom tip so the fin sweeps upward and aft. Glue H16 to the left side of the fin near its upper end. The three-blade rotor stays fixed.'),step('Add the main rotor',[mast,rotor],'Form H14 into an octagonal sleeve and glue its seam. Stand it upright between the engine fairings, 15 mm behind the nose. Glue its lower edges to the inner upper surfaces of the fairings; use a small glue fillet to bridge the curved contact. Glue only H15’s central hub to its top. Keep all five blades level. Its swept diameter is 43.25 mm; do not enlarge the rotor separately.'),step('Check the Hind profile',hp,'Compare Side and Top views: two stepped cockpit bulges, a deep cabin, downward-sloping stub wings and a much thinner rising tail boom. The Mi-24 remains a custom display addition to the carrier. This paper prototype still needs a physical fit test; landing gear and small equipment are omitted.')]
    return [dict(id='mig',name='MiG-29K',label='Carrier fighter',size='43.25 mm long · 29.98 mm wingspan',count=6,parts=mp,steps=mg,sheets=[1,2,3]),dict(id='hind',name='Mil Mi-24',label='Custom display addition',size='43.75 mm airframe · 43.25 mm rotor diameter',count=2,parts=hp,steps=hg,sheets=[4])]

def area(p):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2

def clip(s,c):
    out=s[:];sign=1 if area(c)>0 else -1
    for a,b in zip(c,c[1:]+c[:1]):
        inp=out;out=[]
        if not inp:break
        def val(p):return sign*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
        for p,q in zip(inp,inp[1:]+inp[:1]):
            vp,vq=val(p),val(q)
            if vp>=-1e-8:out.append(p)
            if (vp>1e-8 and vq<-1e-8) or (vp<-1e-8 and vq>1e-8):
                t=vp/(vp-vq);out.append([p[i]+t*(q[i]-p[i]) for i in range(2)])
    return out

def validate(built):
    for m in built:
        for p in m['parts']:
            if not p['checks']:continue
            for i,f in enumerate(p['faces']):
                for g in p['faces'][i+1:]:
                    overlap=abs(area(clip(f['points'],g['points'])))
                    assert overlap<1e-5,(p['id'],i,overlap)
    for model in built:
        chains=[model['parts'][:6]] if model['id']=='mig' else [model['parts'][:9]]
        if model['id']=='hind':chains += [model['parts'][-4:-2],model['parts'][-2:]]
        if model['id']=='mig':
            chains += [[p for p in model['parts'] if p['id'].startswith(prefix)] for prefix in ['L','R','C']]
        for chain in chains:
            for a,b in zip(chain,chain[1:]):
                assert a['checks'][0]['back']==b['checks'][0]['front'],('section mismatch',a['id'],b['id'])
    mig=[v for p in built[0]['parts'] for f in p['mesh'] for v in f['points']]
    assert abs(max(v[0] for v in mig)-min(v[0] for v in mig)-43.25)<1e-7
    assert abs(max(v[1] for v in mig)-min(v[1] for v in mig)-29.975)<1e-7
