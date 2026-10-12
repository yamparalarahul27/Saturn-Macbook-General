"""Faceted aircraft shells. Every printed triangle unfolds an actual mesh triangle."""
import math
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
def ring(s,cy=0,n=12):
    x,ry,rz,zc=s[:4]
    power=s[4] if len(s)>4 else 1
    def rounded(v):return math.copysign(abs(v)**power,v)
    return [[x,cy+ry*rounded(math.cos(-math.pi/2+2*math.pi*i/n)),zc+rz*rounded(math.sin(-math.pi/2+2*math.pi*i/n))] for i in range(n)]
def shell(id,name,s0,s1,color,cy=0,join=False,glass=False,upper=False):
    p=makepart(id,name);A=ring(s0,cy);B=ring(s1,cy)
    if upper:A=A[3:10];B=B[3:10]
    n=6 if upper else 12
    v={**{f'a{i}':A[i%len(A)] for i in range(n+1)},**{f'b{i}':B[i%len(B)] for i in range(n+1)}}
    triangles=[]
    for i in range(n):triangles.extend([[f'a{i}',f'b{i}',f'b{i+1}'],[f'a{i}',f'b{i+1}',f'a{i+1}']])
    xy={'a0':[0.,0.],'b0':[distance(A[0],B[0]),0.]};prev=None
    for j,ids in enumerate(triangles):
        known=[i for i in ids if i in xy];new=next(i for i in ids if i not in xy);a,b=known
        sign=1
        if prev:
            other=next(k for k in prev if k not in (a,b));sign=-1 if side(xy[a],xy[b],xy[other])>0 else 1
            p['folds'].append([xy[a],xy[b]])
        xy[new]=third(xy[a],xy[b],distance(v[a],v[new]),distance(v[b],v[new]),sign)
        flat=[xy[i] for i in ids];mesh=[v[i] for i in ids]
        panel=j//2+(3 if upper else 0)
        c=GLASS if glass and 3 <= panel <= 8 else shade(color, .94 + .13 * math.sin(-math.pi/2 + (panel+.5)*math.pi/6))
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
SHELL='Form each numbered skin around an twelve-sided cross-section. Close its long underside seam with the lilac tab. Then join in numerical order: tuck the next section’s small front tabs inside the previous section, matching all twelve panel edges. Keep the underside seams aligned. Do not flatten the body. '
def chain(prefix, name, stations, color, cy=0, upper=False):
    return strips(prefix,[f'{name} {i+1}' for i in range(len(stations)-1)],stations,color,cy,range(len(stations)-1) if upper else (),upper)

def landing(prefix, positions):
    parts=[]
    for i,(x,y,top,radius) in enumerate(positions):
        # Separate flat leg and wheel disc: practical at 1:400, not falsely volumetric.
        z=radius
        leg=flatpart(f'{prefix}{i+1}L','Landing gear leg',[[x-.23,z],[x+.23,z],[x+.23,top],[x-.23,top]],lambda x,z,y=y:[x,y,z],'#aeb8ba',([x-.23,top],[x+.23,top],[x,z]))
        wheel=flatpart(f'{prefix}{i+1}W','Wheel disc',circle(x,z,radius),lambda x,z,y=y:[x,y-.03,z],'#303b40')
        art(wheel,circle(x,z,radius*.38),lambda x,z,y=y:[x,y-.035,z],'#9aabad')
        parts += [leg,wheel]
    return parts

def models():
    # All stations are modelling estimates; only overall envelopes are dimension-anchored.
    ms=[(0,.035,.035,4.0),(1.5,.42,.36,4.05),(3.3,.8,.63,4.1),(5.3,1.15,.85,4.15),(7.5,1.4,1,4.2),(10,1.6,1.15,4.25),(13,1.8,1.22,4.2),(17,2.1,1.3,4.1),(22,2.4,1.25,3.95),(27,2.4,1.15,3.8),(32,2.1,.95,3.65),(36,1.6,.72,3.6),(40,.9,.45,3.55),(43.25,.15,.15,3.5)]
    fus=chain('F','Fuselage skin',ms,GREY)
    for p in fus[:3]:
        p['name']='Radome '+p['id']
        for f in p['faces']+p['mesh']:
            if f['fill']!=GLUE:f['fill']=shade('#78878e',1)
    wings=[]
    for sign,id in [(-1,'W01'),(1,'W02')]:
        # Broad root extension and swept outer wing, with small tip rail included in outline.
        poly=[[10.5,1.6],[15,2.8],[19.5,5],[25.8,14.65],[26,14.9875],[29.2,14.9875],[29.15,14.4],[31.1,5.1],[33,2.1]]
        project=lambda x,y,sign=sign:[x,sign*y,4.45-(y-2)*.015]
        p=flatpart(id,'Port wing / root extension' if sign<0 else 'Starboard wing / root extension',poly,project,GREY,([33,2.1],[10.5,1.6],[25,8]))
        for r,c in [(.7,'#c18451'),(.46,'#eee8df'),(.24,'#6b8363')]:art(p,circle(26.7,10,r),project,c)
        # Fold boundary is printed as surface detail, not a structural fold for spread wings.
        art(p,[[22.9,9.7],[30,9.7],[30,9.78],[22.9,9.78]],project,'#82959f')
        wings.append(p)
    engines=[]
    es=[(15.5,1.25,.95,3.35,.32),(18,1.4,1.15,3.15,.65),(23,1.42,1.2,3.15),(30,1.3,1.15,3.2),(36.8,1.1,1.02,3.2),(40.2,1.02,.98,3.2),(43.25,.85,.85,3.2)]
    for prefix,cy in [('L',-3.05),('R',3.05)]:
        pod=chain(prefix,'Engine duct',es,'#9cabb4',cy)
        for p in pod[-2:]:
            p['name']='Exhaust nozzle '+p['id']
            for f in p['faces']+p['mesh']:
                if f['fill']!=GLUE:f['fill']=shade(f['fill'],.7)
        engines+=pod
    tails=[]
    for sign,id in [(-1,'T01'),(1,'T02')]:
        poly=[[32.5,2.3],[37.8,8.2],[40.3,8.5],[41.3,7],[39.2,2.3]];project=lambda x,y,sign=sign:[x,sign*y,3.6]
        tails.append(flatpart(id,'Horizontal stabilizer',poly,project,GREY,([39.2,2.3],[32.5,2.3],[38,6])))
    fins=[]
    for sign,id in [(-1,'V01'),(1,'V02')]:
        poly=[[30.8,0],[34.2,5.8],[35.4,6.6],[37.3,6.35],[38.9,0]]
        project=lambda x,z,sign=sign:[x,sign*(3.05+z*.10),4.1+z]
        p=flatpart(id,'Canted vertical fin',poly,project,GREY,([38.9,0],[30.8,0],[35,3]))
        for row,col in enumerate(['#c18451','#eee8df','#6b8363']):art(p,[[35,4.4+row*.3],[36.5,4.4+row*.3],[36.5,4.65+row*.3],[35,4.65+row*.3]],project,col)
        fins.append(p)
    canopy=chain('C','Canopy section',[(7.4,.45,.12,5.18),(8.5,.87,.7,5.32),(10.2,1.04,1.03,5.4),(12.1,1,.98,5.43),(13.8,.8,.65,5.4),(15.1,.3,.08,5.4)],GLASS,upper=True)
    gear=landing('G',[(9,-.33,3.2,.58),(9,.33,3.2,.58),(27,-3.7,2.6,.9),(27,3.7,2.6,.9)])
    mp=fus+wings+engines+tails+fins+canopy+gear
    mg=[step('Prepare the precision fighter',mp,COMMON+f'One fighter has {len(mp)} pieces. Keep the F, L, R and C shell families separate. Cut tiny gear pieces last.'),step('Form the ogival nose and body',fus,SHELL+'F01–F03 form the radome. Continue through F13. The nose closes with a tiny dot of glue. Align every seam underneath; do not flatten the broad centre body.'),step('Fit the swept wings',wings,'Glue W01/W02 to the body sides, with leading-edge root extensions beginning 10.5 mm behind the nose and roots ending at 33 mm. Match both sides in Top view. The thin dark line denotes the wing-fold boundary; leave the wings spread.'),step('Form intakes and exhausts',engines,SHELL+'Join L01–L06 and R01–R06 separately. The dark final two segments are the exhaust nozzles. Keep both ends open. Mount beneath the wing roots at ±3.05 mm from the centreline, intake at 15.5 mm and exhaust at 43.25 mm behind the nose.'),step('Install the tail surfaces',tails+fins,'Glue T01/T02 at the rear fuselage, level at 3.6 mm above the wheel contact plane. Mount V01/V02 atop the engine pods, with the swept leading edge forward and a slight outward lean. Match the Top and Side previews before glue sets.'),step('Assemble the five-section canopy',canopy,'C01–C05 are open-bottom half-shells, not closed tubes. Join their front tabs in order. Fold the two lower-edge tabs inward. Glue over the fuselage from 7.4 to 15.1 mm behind the nose. The crown rises smoothly near C02/C03 and tapers aft; do not squash it.'),step('Add the landing gear',gear,'Each G family has a leg (L) and wheel disc (W). Glue the matching disc to the lower leg, then bend the top tab and attach beneath the body. G1/G2 make the paired nose wheels at 9 mm; G3/G4 are the main wheels at 27 mm and ±3.7 mm from centre. Double the discs with scrap paper if needed. Keep all wheel bottoms on a flat surface while drying.'),step('Check the completed fighter',mp,'Compare nose, canopy, wing sweep, twin nozzles and tail symmetry in all views. Flat paper wheels and unlined openings are scale simplifications. This is a reference-informed prototype; test one complete model before repeating it.')]
    # A smooth lower cockpit tub supports TWO separate raised canopy bubbles.
    hs=[(0,.08,.12,2.8),(1.3,.65,.65,2.95),(3,1.15,.95,3.15),(5,1.5,1.1,3.3),(7,1.8,1.25,3.6),(9.5,2.05,1.7,4.1),(12,2.35,2.35,4.55),(15,2.45,2.45,4.6),(19,2.4,2.4,4.65),(22,1.95,1.95,4.85),(25,1.35,1.25,5.25),(29,.95,.9,5.55),(33,.65,.65,5.8),(37.8,.38,.45,6.05),(40,.22,.28,6.2)]
    hf=chain('B','Body skin',hs,GREEN)
    front=chain('A','Forward canopy',[(.7,.35,.1,3.55),(1.8,.8,.8,3.85),(3.2,1.08,1.05,4.05),(4.6,1.1,.85,4.25),(6.2,.5,.08,4.5)],GLASS,upper=True)
    rear=chain('D','Raised rear canopy',[(5.8,.45,.1,4.8),(6.7,.9,.9,5.05),(8,1.15,1.25,5.35),(9.4,1.1,1.05,5.55),(10.8,.55,.08,5.95)],GLASS,upper=True)
    hw=[]
    for sign,id in [(-1,'W01'),(1,'W02')]:
        poly=[[14.5,2.35],[16.3,7.7],[17,8.17],[19.2,8.17],[20,2.35]]
        project=lambda x,y,sign=sign:[x,sign*y,5.65-(y-2.35)*math.tan(math.radians(12))]
        hw.append(flatpart(id,'Drooping stub wing',poly,project,GREEN,([20,2.35],[14.5,2.35],[18,6])))
    tail=[]
    for sign,id in [(-1,'T01'),(1,'T02')]:
        poly=[[33.9,.35],[34.4,4.1],[36,4.1],[35.8,.35]]
        tail.append(flatpart(id,'Tailplane half',poly,lambda x,y,sign=sign:[x,sign*y,5.9],GREEN,([35.8,.35],[33.9,.35],[35,3])))
    fin=flatpart('V01','Swept tail fin',[[37.5,6],[39.2,6],[43.75,11],[42.5,11.5],[41.5,10.4]],lambda x,z:[x,0,z],GREEN,([37.5,6],[39.2,6],[42,10]))
    pods=[]
    for prefix,cy in [('E',-1.15),('J',1.15)]:
        pods+=chain(prefix,'Engine fairing',[(8.2,.6,.6,7.3),(9.5,.9,.85,7.4),(12,1.1,1,7.5),(16,1.05,.95,7.5),(19,.85,.75,7.45),(21,.6,.5,7.1)],'#76866d',cy)
    mast=shell('R01','Rotor mast',(0,.45,.45,0),(1.4,.45,.45,0),'#738279')
    for f in mast['mesh']:f['points']=[[15+z,y,8.25+x] for x,y,z in f['points']]
    hub=flatpart('R02','Rotor hub',circle(0,0,1.15),lambda x,y:[15+x,y,9.65],'#64766b')
    blades=[]
    for i in range(5):
        a=i*2*math.pi/5;co,si=math.cos(a),math.sin(a)
        project=lambda x,y,co=co,si=si:[15+x*co-y*si,x*si+y*co,9.65]
        poly=[[.6,-.35],[3,-.6],[math.sqrt(21.625**2-.6**2),-.6],[math.sqrt(21.625**2-.6**2),.6],[3,.6],[.6,.35]]
        blade=flatpart(f'R{i+3:02}','Main rotor blade',poly,project,'#4d6065')
        art(blade,[[20.4,-.6],[math.sqrt(21.625**2-.6**2),-.6],[math.sqrt(21.625**2-.6**2),.6],[20.4,.6]],project,'#d6bd6f');blades.append(blade)
    tr=[]
    for i in range(3):
        a=i*2*math.pi/3;tr += [[r*math.cos(a+t),r*math.sin(a+t)] for r,t in [(1,-.35),(4.885,-.08),(4.885,.08),(1,.35)]]
    tailrotor=flatpart('R08','Tail rotor',tr,lambda x,y:[42.3+x,-.35,10.3+y],'#4d6065')
    gear=landing('G',[(5,-.35,2.35,.6),(5,.35,2.35,.6),(19,-2.6,3.2,.95),(19,2.6,3.2,.95)])
    hp=hf+front+rear+pods+hw+tail+[fin,mast,hub]+blades+[tailrotor]+gear
    hg=[step('Prepare the detailed Hind',hp,COMMON+f'One helicopter has {len(hp)} pieces. B is the body; A/D are the two canopies; E/J are engines; R is the rotor assembly.'),step('Build the rounded body and boom',hf,SHELL+'Join B01–B14 from nose to tail. The centre cabin is deepest, then narrows through several sections into the rising boom. Align all underside seams. The cockpit tub remains low to accept separate canopy bubbles.'),step('Build the two bubble canopies',front+rear,'A01–A04 form the forward canopy; D01–D04 form the raised rear canopy. These are open-bottom half-shells. Join each family in order and fold lower-edge tabs inward. Attach A from 0.7 to 6.2 mm behind the nose, and D from 5.8 to 10.8 mm. Keep the characteristic step between the two crowns; use small glue fillets at curved contact points.'),step('Add the twin engine housings',pods,SHELL+'Build E01–E05 and J01–J05 independently. Smaller intake ends face forward. Fit along the cabin roof from 8.2 to 21 mm behind the nose, centred ±1.15 mm. The rear tapers down toward the tail boom. Keep openings unfilled.'),step('Fit the drooping wings',hw,'Fold root tabs upward. Attach W01/W02 from 14.5 to 20 mm behind the nose. Set both tips about 1.2 mm below the roots (12 degrees downward). Check symmetry in the 3D view.'),step('Assemble the tail surfaces',tail+[fin,tailrotor],'Attach T01/T02 symmetrically to the boom at 34–36 mm. V01 sweeps upward and aft from the boom tip. Glue R08 to the left side near the fin tip. The tail rotor is fixed and remains clear of the tailplanes.'),step('Build the five-blade rotor',[mast,hub]+blades,'Roll R01 into a twelve-sided mast and glue its seam. Mount vertically between the engine fairings at 15 mm behind the nose. Glue hub R02 flat on top. Glue the inner 0.6–1.15 mm of each R03–R07 blade beneath the hub, spacing the five blades evenly at 72 degrees. Their tips reach 21.625 mm from the hub. Keep blades level while drying; use Top view as a placement reference.'),step('Fit the landing gear',gear,'G1/G2 are the paired nose wheels at 5 mm. G3/G4 are main wheels at 19 mm and ±2.6 mm. Glue each W disc to its L leg, bend the top tab and glue to the lower body. Reinforce flat discs with scrap paper if desired. Set on a flat surface so all wheels touch.'),step('Inspect the finished helicopter',hp,'Check two distinct canopy bubbles, a deep rounded cabin, paired engine housings, five separate rotor blades, drooping wings and rising tail. This represents a Mi-24D-style external silhouette. Equipment and cross-sections remain simplified and inferred; a physical trial build is still required.')]
    return [dict(id='mig',name='MiG-29K',label='Carrier fighter',size='43.25 mm long · 29.98 mm wingspan',count=6,parts=mp,steps=mg,sheets=[1,2,3]),dict(id='hind',name='Mil Mi-24',label='Custom display · Mi-24D-style',size='43.75 mm airframe · 43.25 mm rotor diameter',count=2,parts=hp,steps=hg,sheets=[4])]

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
        ids=[p['id'] for p in m['parts']]
        assert len(ids)==len(set(ids)), 'Duplicate part ID'
        assembly_ids=[id for step in m['steps'][1:-1] for id in step['ids']]
        assert set(assembly_ids)==set(ids), ('Uncovered assembly pieces',set(ids)-set(assembly_ids))
        assert len(assembly_ids)==len(set(assembly_ids)), 'Part repeated across construction steps'
        for p in m['parts']:
            if not p['checks']:continue
            for i,f in enumerate(p['faces']):
                for g in p['faces'][i+1:]:
                    overlap=abs(area(clip(f['points'],g['points'])))
                    assert overlap<1e-5,(p['id'],i,overlap)
    for model in built:
        prefixes=['F','L','R','C'] if model['id']=='mig' else ['B','A','D','E','J']
        chains=[[p for p in model['parts'] if p['id'].startswith(prefix)] for prefix in prefixes]
        for chain in chains:
            for a,b in zip(chain,chain[1:]):
                assert a['checks'][0]['back']==b['checks'][0]['front'],('section mismatch',a['id'],b['id'])
    mig=[v for p in built[0]['parts'] for f in p['mesh'] for v in f['points']]
    assert abs(max(v[0] for v in mig)-min(v[0] for v in mig)-43.25)<1e-7
    assert abs(max(v[1] for v in mig)-min(v[1] for v in mig)-29.975)<1e-7
