"""LIMEN documentary explainer / procedural Blender storyboard v3.
blender -b -t 8 --python render_3d.py -- S11 S27
No arguments renders all 31 representative frames and saves the editable blend.
"""
import bpy, math, random, json, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'scenes.json' if (ROOT/'scenes.json').exists() else ROOT.parent/'키비주얼_v2/manifest.json').read_text(encoding='utf-8'))
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
TARGETS=set(ARGS) if ARGS else {s['id'] for s in DATA}
bpy.ops.wm.read_factory_settings(use_empty=True)
GPU=False
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for device in prefs.devices:device.use=device.type!='CPU'
    GPU=any(d.use and d.type!='CPU' for d in prefs.devices)
    print('V3_GPU',[(d.name,d.type,d.use) for d in prefs.devices],flush=True)
except Exception as exc:print('V3_CPU_FALLBACK',str(exc),flush=True)

def rgba(h):
    rgb=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
def material(name,col,rough=.65,metal=.0,emission=0,alpha=1):
    m=bpy.data.materials.new(name);m.diffuse_color=rgba(col)[:3]+(alpha,);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba(col);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if emission:p.inputs['Emission Color'].default_value=rgba(col);p.inputs['Emission Strength'].default_value=emission
    if alpha<1:
        p.inputs['Alpha'].default_value=alpha
        if hasattr(m,'surface_render_method'):m.surface_render_method='DITHERED'
        m.use_transparency_overlap=False
    return m
M={
'ground':material('Studio / graphite','#1A2028',.85),
'slab':material('Architecture / chalk gray','#BBC4CC',.65),
'wall':material('Architecture / pale stone','#A5B0BA',.68),
'dark':material('Hardware / charcoal','#202935',.4,.15),
'black':material('Lens / black glass','#080E16',.18,.3),
'white':material('Porcelain / off white','#E7E7DF',.5),
'muted':material('Auxiliary / slate','#687B8A',.55),
'blue':material('Input A / cool blue','#4BA0DC',.4,.1,.12),
'blueghost':material('Sensing volume / cool blue','#3D8BBD',.85,0,0,.13),
'occluded':material('Occluded volume / charcoal','#17212C',.8,0,0,.22),
'bluefloor':material('Sensing footprint / blue','#24577B',.7),
'red':material('Error or LAN / vermilion','#F05A43',.5,0,.08),
'redghost':material('Lost identity / vermilion glass','#EB6753',.65,0,0,.24),
'green':material('Retained or accepted / sage green','#80D5A0',.5,0,.08),
'greenghost':material('Retained / transparent green','#66CA8A',.7,0,0,.18),
'teal':material('Projected image / petrol','#144D56',.8,0,.12),
'fly':material('Projected image / pale lime','#D4E989',.5,0,.5),
'beam':material('Projection volume / pale gray','#B6CED2',.8,0,0,.045),
'live':material('Live footage placeholder / slate','#252F3A',.8),
'ghostwall':material('Cutaway wall / transparent slate','#A4BAC3',.65,0,0,.08),
}
SC=None;CAM=None
def assign(o,mat):o.data.materials.append(M[mat] if isinstance(mat,str) else mat);return o
def box(name,loc,size,mat='white',bevel=.04,rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if rot:o.rotation_euler=rot
    assign(o,mat)
    if bevel:
        mod=o.modifiers.new('Soft manufactured edge','BEVEL');mod.width=bevel;mod.segments=3
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o
def sphere(name,loc,r,mat='white',scale=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=r,location=loc);o=bpy.context.object;o.name=name
    if scale:o.scale=scale
    assign(o,mat)
    for p in o.data.polygons:p.use_smooth=True
    return o
def curve(name,pts,mat='white',r=.014,smooth=False):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;c.resolution_u=20
    sp=c.splines.new('BEZIER' if smooth else 'POLY');sp.bezier_points.add(len(pts)-1) if smooth else sp.points.add(len(pts)-1)
    if smooth:
        for p,v in zip(sp.bezier_points,pts):p.co=v;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    else:
        for p,v in zip(sp.points,pts):p.co=tuple(v)+(1,)
    o=bpy.data.objects.new(name,c);SC.collection.objects.link(o);assign(o,mat);return o
def dashed(name,a,b,mat='muted',r=.012,n=12):
    a=Vector(a);b=Vector(b)
    for i in range(n):curve(name,[a.lerp(b,i/n),a.lerp(b,(i+.4)/n)],mat,r)
def rod(name,a,b,r=.06,mat='white'):
    a=Vector(a);b=Vector(b);d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();assign(o,mat)
    for p in o.data.polygons:p.use_smooth=True
    mod=o.modifiers.new('Round caps','BEVEL');mod.width=r*.65;mod.segments=3
    o.modifiers.new('Normal','WEIGHTED_NORMAL');return o
def mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);SC.collection.objects.link(o);assign(o,mat);return o
def ring(name,center,r,mat='green',thick=.018,start=0,end=math.tau,plane='XY'):
    x,y,z=center;pts=[]
    for i in range(65):
        a=start+(end-start)*i/64
        pts.append((x+r*math.cos(a),y+r*math.sin(a),z) if plane=='XY' else (x+r*math.cos(a),y,z+r*math.sin(a)))
    return curve(name,pts,mat,thick)
def label(t,loc,size=.22,mat='muted',billboard=True):
    c=bpy.data.curves.new('Label '+t,'FONT');c.body=t;c.align_x='CENTER';c.align_y='CENTER';c.size=size;c.extrude=.002;c.bevel_depth=.0005
    o=bpy.data.objects.new('Label '+t,c);SC.collection.objects.link(o);o.location=loc;assign(o,mat)
    if billboard:o.rotation_euler=(CAM.location-Vector(loc)).to_track_quat('Z','Y').to_euler()
    return o
def linebox(name,x0,x1,y0,y1,z,mat='green',r=.014):return curve(name,[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z),(x0,y0,z)],mat,r)
def mannequin(name,loc,mat='white',scale=1,rot=0,wire=False):
    ox,oy,oz=loc
    def p(x,y,z):return (ox+(x*math.cos(rot)-y*math.sin(rot))*scale,oy+(x*math.sin(rot)+y*math.cos(rot))*scale,oz+z*scale)
    if wire:
        pts=[(0,0,1.52),(0,0,1.25),(0,0,.9),(-.24,0,1.25),(.24,0,1.25),(-.33,0,.98),(.33,0,.98),(-.37,-.03,.74),(.37,-.03,.74),(-.13,0,.72),(.13,0,.72),(-.15,0,.38),(.15,0,.38),(-.16,-.04,.08),(.16,-.04,.08)]
        for a,b in [(0,1),(1,2),(1,3),(1,4),(3,5),(4,6),(5,7),(6,8),(2,9),(2,10),(9,11),(10,12),(11,13),(12,14)]:rod(name+' bone',p(*pts[a]),p(*pts[b]),.018*scale,mat)
        for q in pts:sphere(name+' joint',p(*q),.041*scale,mat)
    else:
        sphere(name+' head',p(0,0,1.51),.14*scale,mat)
        sphere(name+' torso',p(0,0,1.08),.25*scale,mat,(.83,.62,1.37))
        sphere(name+' pelvis',p(0,0,.76),.20*scale,mat,(1,.67,.8))
        for side in [-1,1]:
            rod(name+' thigh',p(side*.115,0,.72),p(side*.145,-.02,.40),.075*scale,mat)
            rod(name+' calf',p(side*.145,-.02,.40),p(side*.16,-.02,.10),.058*scale,mat)
            box(name+' shoe',p(side*.16,-.065,.055),(.13*scale,.23*scale,.1*scale),mat,.035*scale)
            rod(name+' upper arm',p(side*.21,0,1.25),p(side*.30,0,1.0),.056*scale,mat)
            rod(name+' forearm',p(side*.30,0,1.0),p(side*.34,-.03,.78),.045*scale,mat)
            sphere(name+' hand',p(side*.34,-.03,.75),.057*scale,mat)
        # A subtle nose establishes front/back without a realistic face.
        sphere(name+' face direction',p(0,-.126,1.51),.035*scale,mat,(.8,1.25,.8))
def hardware(name,pos,kind='sensor',scale=1,rot=0):
    made=[];x,y,z=pos
    if kind=='sensor':
        made+=[box(name,(x,y,z+.06),(.55,.13,.10),'dark',.025),box(name+' neck',(x,y,z-.12),(.055,.055,.27),'muted',.015),box(name+' foot',(x,y,z-.26),(.30,.2,.035),'dark',.02)]
        if z>.4:
            made.append(rod(name+' stand',(x,y,.04),(x,y,z-.28),.023,'muted'))
            made.append(box(name+' stand base',(x,y,.025),(.35,.26,.045),'dark',.02))
        for dx in [-.18,0,.18]:made.append(sphere(name+' lens',(x+dx,y-.071,z+.06),.032,'black',scale=(1,.3,1)))
    elif kind=='pc':
        made+=[box(name,pos,(.42,.65,.9),'dark',.05)]
        for zz in [.14,.23,.32]:made.append(box(name+' vent',(x,y-.33,z+zz),(.22,.013,.025),'muted',.006))
        made.append(sphere(name+' led',(x+.12,y-.337,z-.28),.018,'green'))
    elif kind=='laptop':
        made+=[box(name+' keyboard',pos,(.85,.55,.055),'dark',.02),box(name+' screen',(x,y+.22,z+.30),(.85,.045,.57),'dark',.02),box(name+' display',(x,y+.192,z+.30),(.76,.012,.47),'live',.008)]
        for i in range(4):made.append(box(name+' keys',(x,y-.10+i*.065,z+.035),(.65,.03,.012),'muted',.002))
    elif kind=='projector':
        made.append(box(name,pos,(.52,.34,.22),'white',.04));made.append(sphere(name+' lens',(x,y-.18,z),.082,'black',scale=(1,.25,1)))
        for dx in [-.13,-.08,-.03]:made.append(box(name+' vent',(x+dx,y-.172,z),(.018,.01,.12),'muted',.003))
    for o in made:
        delta=o.location-Vector(pos);delta.rotate(__import__('mathutils').Euler((0,0,rot)));o.location=Vector(pos)+delta*scale;o.scale*=scale;o.rotation_euler.z+=rot
    return made
def room(content=False,walls=True,grid=False,fold=False,ox=0,oy=0,k=1):
    def p(x,y,z):return (ox+x*k,oy+y*k,z*k)
    box('Room / 7.2 by 4 floor',p(0,0,-.13),(7.2*k,4*k,.26*k),'teal' if content else 'slab',.04*k)
    if walls:
        box('Room / front wall',p(0,2.04,1.3),(7.2*k,.10*k,2.6*k),'teal' if content else 'wall',.018*k)
        if fold:
            left=box('Room / left wall rising',p(-4.13,0,1.12),(.10*k,4*k,2.6*k),'wall',.018*k,rot=(0,-math.pi/6,0))
            right=box('Room / right wall rising',p(4.13,0,1.12),(.10*k,4*k,2.6*k),'wall',.018*k,rot=(0,math.pi/6,0))
        else:
            box('Room / left wall',p(-3.64,0,1.3),(.10*k,4*k,2.6*k),'teal' if content else 'wall',.018*k)
            box('Room / right cutaway wall',p(3.64,0,1.3),(.055*k,4*k,2.6*k),'ghostwall',.01*k)
            curve('Cutaway upper edge',[p(3.65,-2,2.6),p(3.65,2,2.6)],'muted',.009*k)
            curve('Cutaway front edge',[p(3.65,-2,0),p(3.65,-2,2.6)],'muted',.009*k)
    if grid:
        for x in range(-3,4):curve('Floor measuring grid',[p(x,-2,.015),p(x,2,.015)],'muted',.004*k)
        for y in range(-1,2):curve('Floor measuring grid',[p(-3.6,y,.015),p(3.6,y,.015)],'muted',.004*k)
    dashed('Open entrance',p(-3.6,-2.01,.03),p(3.6,-2.01,.03),'muted',.01*k,24)
    if content:
        rng=random.Random(404)
        for i in range(65):
            x=rng.uniform(-3.4,3.4);y=rng.uniform(-1.85,1.85);z=rng.uniform(.18,2.45)
            pos=p(x,y,.026) if i%3==0 else p(x,1.977,z) if i%3==1 else p(-3.577,y,z)
            sphere('Projected firefly',pos,rng.uniform(.018,.035)*k,'fly')
        curve('One continuous projected curve',[p(-3.57,-.5,1.7),p(-3.57,.1,.2),p(-2.5,.2,.03),p(-.6,-.7,.03),p(1.2,.2,.03),p(2.6,1.98,.2),p(1.9,1.98,1.4),p(.3,1.98,1.9)],'fly',.016*k,True)
def sensor_pair(two=True,frustum=True):
    for i,(x,a) in enumerate([(-3.35,-35),(3.35,35)][:2 if two else 1]):
        hardware('Kinect '+('A' if i==0 else 'B'),(x,-1.85,.65),rot=math.radians(180+a))
        label('A' if i==0 else 'B',(x,-2.23,.7),.18)
        if frustum:cone((x,-1.82,.72),math.radians(35 if i==0 else -35),4.5)
def cone(pos,angle=0,length=4.5):
    x,y,z=pos
    def p(a,r,zz=0):return (x+math.sin(angle+a)*r,y+math.cos(angle+a)*r,zz)
    # Diagram volume uses 70-degree horizontal aperture; vertical section is schematic.
    pts=[p(math.radians(-35+70*i/32),length,.025) for i in range(33)]
    # Crop the footprint to the physical room footprint.
    def clip(poly,axis,bound,less):
        out=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            ai=(a[axis]<=bound) if less else (a[axis]>=bound);bi=(b[axis]<=bound) if less else (b[axis]>=bound)
            if ai:out.append(a)
            if ai!=bi:
                t=(bound-a[axis])/(b[axis]-a[axis]);out.append(tuple(a[j]+(b[j]-a[j])*t for j in range(3)))
        return out
    foot=[(x,y,.025)]+pts
    for ax,b,less in [(0,-3.6,False),(0,3.6,True),(1,-2,False),(1,2,True)]:foot=clip(foot,ax,b,less)
    if len(foot)>2:
        mesh('Sensing footprint',foot,[tuple(range(len(foot)))],'bluefloor')
        curve('Sensing footprint perimeter',foot+[foot[0]],'blue',.009)
    for a in [-35,35]:
        end=p(math.radians(a),length,1.65)
        mesh('Transparent sensing slice',[(x,y,z),(end[0],end[1],.04),end],[(0,1,2)],'blueghost')
        curve('Sensing volume ray',[(x,y,z),end],'blue',.009)
def footage(name,x=0,y=0,z=.35,w=9.6,h=5.4,code='L3',success=False,dim=False):
    box(name+' frame',(x,y,z-.05),(w+.12,h+.12,.12),'green' if success else 'dark' if dim else 'muted',.045)
    box(name+' placeholder',(x,y,z+.025),(w,h,.05),'dark' if dim else 'live',.025)
    curve(name+' diagonal 1',[(x-w/2+.08,y-h/2+.08,z+.058),(x+w/2-.08,y+h/2-.08,z+.058)],'muted',.006)
    curve(name+' diagonal 2',[(x-w/2+.08,y+h/2-.08,z+.058),(x+w/2-.08,y-h/2+.08,z+.058)],'muted',.006)
    label(code,(x-w/2+.3,y-h/2+.27,z+.07),.19,'muted',False)
def stamp(x,y,z,scale=1,angle=0,success=False):
    c='green' if success else 'red';w=2.6 if success else 2.1;h=.66
    pts=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2),(-w/2,-h/2)]
    def p(x0,y0):return(x+(x0*math.cos(angle)-y0*math.sin(angle))*scale,y+(x0*math.sin(angle)+y0*math.cos(angle))*scale,z)
    curve('Raised '+('SUCCESS' if success else 'FAIL')+' frame',[p(a,b) for a,b in pts],c,.023*scale)
    o=label('SUCCESS' if success else 'FAIL',(x,y,z+.02),(.37 if success else .43)*scale,c,False);o.rotation_euler.z=angle
def cards(n,state):
    w=3.15 if n==2 else 2.4 if n==3 else 1.85;h=w*9/16;gap=.17
    for i in range(n*n):
        x=(i%n-(n-1)/2)*(w+gap);y=((n-1)/2-i//n)*(h+gap)
        target=n==4 and i==6;ok=state=='success' and target
        footage('Evidence panel '+str(i+1),x,y,.35,w,h,'L4' if ok else 'L3',ok,dim=state=='success' and not target)
        failed=state!='plain' and (n==2 or n==3 and i<7 or n==4 and not target)
        if failed:stamp(x,y,.77 if n==3 and i==6 else .45,.86 if n==2 else .62 if n==3 else .48,math.radians([-8,5,-3,7][i%4]))
        if ok:stamp(x,y,.5,.57,-.08,True)
        if n==2 and state=='plain':
            if i==0:
                ring('Misaligned calibration',(x-w*.37,y+h*.32,.46),.11,'white',.012);ring('Misaligned calibration',(x-w*.35,y+h*.30,.48),.11,'blue',.012)
            elif i==1:
                for j in range(3):sphere('Ant icon',(x-w*.37,y+h*.32+j*.055,.49),.037,'white')
            elif i==2:
                for dx in [-.035,.035]:box('Pause',(x-w*.36+dx,y+h*.32,.46),(.025,.16,.04),'white',.005)
            else:
                for dx,dy in [(-.08,0),(.08,0),(0,.1)]:sphere('Three people',(x-w*.36+dx,y+h*.32+dy,.48),.04,'white')
def axes(pos,angle=0,mat='white',k=.6):
    x,y,z=pos
    for a in [angle,angle+math.pi/2]:
        ex=x+math.cos(a)*k;ey=y+math.sin(a)*k
        curve('Coordinate axis',[(x,y,z),(ex,ey,z)],mat,.012)
        d=Vector((math.cos(a),math.sin(a),0));rod('Axis head',Vector((ex,ey,z))-d*.06,(ex,ey,z),.033,mat)
def fusion_points(x,y,mat='blue',angle=0,scale=1):
    pts=[(-.04,0,1.51),(.04,0,1.51),(0,0,1.34),(-.2,0,1.2),(.2,0,1.2),(0,0,1.1),(-.29,0,.95),(.29,0,.95),(-.33,0,.76),(.33,0,.76),(-.12,0,.73),(.12,0,.73),(-.14,0,.38),(.14,0,.38)]
    for a,b,z in pts:
        xx=x+(a*math.cos(angle)-b*math.sin(angle))*scale;yy=y+(a*math.sin(angle)+b*math.cos(angle))*scale
        sphere('Sensor observation point',(xx,yy,z*scale+.04),.055*scale,mat)
def branches(selected=False):
    rod('Original time line',(-7,0,.30),(-4.5,0,.30),.028,'white')
    sphere('Start',(-7,0,.30),.08,'white')
    for i in range(48):
        yy=(i-23.5)*.125;gy=(-1 if i<24 else 1)*1.65
        mat='red' if i%3==0 else 'muted'
        end=1.0 if selected else 7.3
        curve('Alternative hypothesis',[(-4.5,0,.30),(-2.8,gy,.3),(-.4,yy,.3),(end,yy,.3)],mat,.009 if selected else .015,True)
        if not selected:
            if i%4==0:
                for dx,dy in [(-.04,0),(.04,0),(0,.07)]:sphere('Three-person case',(7.55+dx,yy+dy,.32),.025,mat)
            elif i%4==1:ring('Ghost case',(7.55,yy,.32),.045,'red',.008)
            elif i%4==2:
                curve('Rejected case',[(7.51,yy-.04,.32),(7.59,yy+.04,.32)],'red',.012);curve('Rejected case',[(7.51,yy+.04,.32),(7.59,yy-.04,.32)],'red',.012)
            else:sphere('Case marker',(7.55,yy,.32),.03,mat)
    if selected:
        rod('Selected time line',(-4.5,0,.43),(7.5,0,.43),.035,'white')
        for yy in [-.45,.45]:box('Green clamp',(1.5,yy,.53),(.14,.13,.42),'green',.025)
        curve('Selection bracket',[(1.5,-.45,.75),(1.5,-.45,1.0),(1.5,.45,1.0),(1.5,.45,.75)],'green',.035)
        for xx in [4.2,6.0]:mannequin('Retained person',(xx,0,.45),'white',.5)
def structure(assembling=False):
    # All fusion operations live physically inside the open main-computer box.
    sx=-7.5;px=-5.4
    for yy,t in [(1.25,'A'),(-1.25,'B')]:
        hardware('Input Kinect '+t,(sx,yy,.62),scale=.8);label(t,(sx,yy-.18,1.02),.18)
        curve('Local sensor cable',[(sx+.3,yy,.55),(px-.3,yy,.55)],'muted',.017)
    hardware('Main computer',(px,1.25,.65),'pc')
    hardware('Sender notebook',(px,-1.25,.22),'laptop')
    box('Open main computer / fusion boundary',(-3.85,1.1,.38),(2.3,1.9,.12),'dark',.04)
    for x in [-4.85,-2.85]:rod('Main PC boundary post',(x,.22,.4),(x,.22,1.35),.018,'muted')
    curve('Main PC top boundary',[(-4.85,.22,1.35),(-4.85,1.95,1.35),(-2.85,1.95,1.35),(-2.85,.22,1.35)],'muted',.016)
    for x,y in [(-4.45,1.45),(-4.45,.75)]:sphere('Sensor input',(x,y,.62),.10,'blue')
    sphere('Merged observation',(-3.3,1.1,.72),.15,'white')
    for y in [.75,1.45]:curve('Fuse in main PC',[(-4.45,y,.62),(-3.9,y,.65),(-3.3,1.1,.72)],'blue',.024,True)
    curve('LAN cable',[(-5.6,-1.45,.26),(-6.6,-1.7,.2),(-6.4,.75,.22),(-5.55,1.18,.5)],'red',.027,True)
    label('LAN',(-6.45,-.7,.4),.17,'red')
    curve('Remote data into main PC',[(-5.0,-1.25,.3),(-4.45,-.65,.4),(-4.45,.75,.62)],'blue',.019,True)
    curve('Main content output',[(-3.3,1.1,.72),(-2,1.1,.72),(-1.25,0,.6)],'blue',.021,True)
    # Physical T-shaped image plate on a small pedestal.
    x0=0;y0=2.2 if assembling else 0;z=1.8 if assembling else .57
    box('Image / floor plate',(x0,y0,z),(1.44,.8,.06),'teal',.01)
    box('Image / front plate',(x0,y0+.8,z),(1.44,.8,.06),'teal',.01)
    for xx in [-1.12,1.12]:box('Image / side plate',(xx,y0,z),(.8,.8,.06),'teal',.01)
    curve('Image / continuity',[(-1.4,y0-.1,z+.05),(-.7,y0+.22,z+.05),(0,y0-.1,z+.05),(.7,y0+.1,z+.05),(1.4,y0-.2,z+.05)],'fly',.018,True)
    for i,yy in enumerate([1.5,.5,-.5,-1.5]):
        xx=3.2+(.4 if assembling and i%2 else 0);zz=1.7 if assembling else .75
        hardware('Projector '+str(i+1),(xx,yy,zz),'projector',scale=.85,rot=math.radians(90))
        label('P'+str(i+1),(xx,yy-.2,zz+.45),.16)
        if assembling:dashed('Assembly travel',(xx+2,yy,zz+1),(xx+.5,yy,zz+.15),'muted',.011,10)
        else:
            curve('Output branch',[(1.5,0,.58),(2.2,yy,.65),(xx-.2,yy,.75)],'blue',.018,True)
            mesh('Projector light cone',[(xx+.2,yy,.75),(6.3,yy*.52,.4),(6.7,yy*.52,1.5)],[(0,1,2)],'beam')
    room(content=True,ox=7.0,oy=.2,k=.36)
    if assembling:dashed('Room assembly travel',(8.8,2.0,2.0),(7.6,.8,1.3),'muted',.012,12)

def setup(sid,cam=(10,-14,11),target=(0,0,.6),ortho=12):
    global SC,CAM
    SC=bpy.data.scenes.new(sid);bpy.context.window.scene=SC
    SC.render.engine='CYCLES'
    SC.cycles.device='GPU' if GPU else 'CPU';SC.cycles.samples=32;SC.cycles.use_denoising=True;SC.cycles.max_bounces=5;SC.cycles.transparent_max_bounces=8
    SC.render.resolution_x=1920;SC.render.resolution_y=1080;SC.render.resolution_percentage=100
    SC.render.image_settings.file_format='PNG';SC.render.image_settings.color_mode='RGB';SC.render.film_transparent=False
    SC.view_settings.view_transform='AgX';SC.view_settings.look='AgX - Medium High Contrast'
    world=bpy.data.worlds.new(sid+' studio world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.14,.18,1);world.node_tree.nodes['Background'].inputs[1].default_value=.32;SC.world=world
    box('Infinite charcoal studio floor',(0,0,-.43),(200,200,.2),'ground',0)
    def area(name,loc,power,size,color):
        dat=bpy.data.lights.new(name,'AREA');dat.energy=power;dat.shape='DISK';dat.size=size;dat.color=color
        o=bpy.data.objects.new(name,dat);SC.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
    area('Large soft key',(-4,-6,12),1900,7,(1,.92,.82));area('Cool fill',(8,-1,8),1300,6,(.71,.84,1));area('Back edge',(-3,8,10),2200,5,(.82,.91,1))
    dat=bpy.data.cameras.new(sid+' camera');CAM=bpy.data.objects.new(sid+' camera',dat);SC.collection.objects.link(CAM);CAM.location=cam;CAM.rotation_euler=(Vector(target)-CAM.location).to_track_quat('-Z','Y').to_euler();dat.type='ORTHO';dat.ortho_scale=ortho;dat.lens=52;SC.camera=CAM
    SC.render.filepath=str(ROOT/(sid+'.png'))
def build(sid):
    rng=random.Random(sid)
    if sid in ['S01','S02']:
        setup(sid,(7,-11,12),(0,0,.2),12)
        if sid=='S01':
            box('Extruded cursor',(-2.6,1.4,.14),(.045,.4,.1),'white',.015)
            for row in range(7):
                x=-2.6
                for i in range(rng.randint(3,6)):
                    w=rng.uniform(.16,.8);box('Log strip',(x+w/2,1-row*.25,.1),(w,.035,.055),'white' if row==4 else 'muted',.01);x+=w+.1
        else:
            rod('Future floor front edge',(-4.5,-1.8,.08),(4.5,-1.8,.08),.022,'white')
            for i in range(45):
                x=rng.uniform(-4.4,4.4);y=rng.uniform(-1.5,2.3);z=rng.uniform(.12,1.8)
                box('Falling log strip',(x,y,z),(.035,.035,rng.uniform(.2,.85)),'muted' if i%3 else 'white',.01)
    elif sid=='S03':
        setup(sid,ortho=13.6);room(fold=True,grid=True)
        rod('Width dimension',(-3.6,-2.5,-.07),(3.6,-2.5,-.07),.008,'muted');label('7.2m',(0,-2.7,-.05),.22)
    elif sid=='S04':
        setup(sid,(8,-12,18),(0,0,0),18.8)
        for x,y,w,h in [(0,-1,7.2,4),(0,3,7.2,4),(-5.6,-1,4,4),(5.6,-1,4,4)]:box('Unfolded image plate',(x,y,0),(w,h,.12),'teal',.025)
        curve('Image across seams',[(-7.2,-1.7,.075),(-4.6,-.2,.075),(-2.4,-1.3,.075),(0,-.3,.075),(2.4,-1.8,.075),(5.2,-.1,.075),(7.4,-1,.075)],'fly',.022,True)
        curve('Image toward front',[(-.5,-.3,.075),(1,1,.075),(.6,2.8,.075),(-1.5,4.3,.075)],'fly',.022,True)
        for i in range(70):
            x=rng.uniform(-7.5,7.5);y=rng.uniform(-2.9,4.9)
            if y<.9 or abs(x)<3.5:sphere('Image point',(x,y,.085),rng.uniform(.018,.04),'fly')
        for x in [-3.6,3.6]:dashed('Hinge',(x,-3,.08),(x,1,.08),'muted',.012,20)
        dashed('Hinge',(-3.6,1,.08),(3.6,1,.08),'muted',.012,28)
    elif sid=='S05':
        setup(sid,(9,-15,13),(0,0,.4),17)
        footage('Single content image',-6,0,.35,2.1,1.18,'',False)
        for x in [-3.0,-.8,1.4]:
            box('Processing stage',(x,0,.55),(.58,.58,.58),'dark',.07);curve('Signal link',[(x-1.6,0,.6),(x-.35,0,.6)],'blue',.021)
            sphere('Data packet',(x-.6,0,.6),.07,'blue')
        for i,yy in enumerate([2.0,.67,-.67,-2.0]):
            curve('Four output paths',[(1.8,0,.6),(3,yy,.6),(4.4,yy,.6)],'blue',.02,True);hardware('P'+str(i+1),(4.7,yy,.6),'projector',rot=math.pi/2);label('P'+str(i+1),(4.7,yy-.35,1.0),.18)
            mesh('Projection beam',[(4.9,yy,.6),(6.5,yy-.4,.2),(6.5,yy+.4,.2)],[(0,1,2)],'beam')
    elif sid=='S06':
        setup(sid,ortho=12.8);room(content=True)
        for i,(x,y) in enumerate([(-2,-.5),(0,0),(1.6,-.3),(2.1,1.1)]):
            hardware('Ceiling projector '+str(i+1),(x,y,3.1),'projector',scale=.7)
            mesh('Projection light beam',[(x,y,3.0),(x-.8,y+.7,.04),(x+.8,y+1,.04)],[(0,1,2)],'beam')
        for x,y,z in [(-3.56,.3,1.3),(0,1.975,1.3),(0,0,.04),(3.56,.3,1.3)]:
            ring('Synchronized pulse',(x,y,z),.25,'white',.014,plane='XZ' if z>1 else 'XY')
    elif sid in ['S06L','S09L','S12L']:
        setup(sid,(1,-9,24),(0,0,.3),12.5);footage(sid,code={'S06L':'L5','S09L':'L6','S12L':'L7'}[sid])
        if sid=='S06L':
            for x in [-3,3]:curve('Live room corner',[(x,-2,.45),(x,2,.45),(x*.5,1,.46),(x*.5,-1,.46),(x,-2,.45)],'white',.015)
            linebox('Live front wall',-1.5,1.5,-1,1,.46,'white',.015)
            for x in [-3,3]:
                for y in [-2,2]:sphere('Mapping reference',(x,y,.47),.038,'white')
        elif sid=='S09L':
            for x,y in [(-3,-1.1),(3,1.0)]:ring('Hardware attachment',(x,y,.46),.17,'white',.017)
            curve('LAN overlay',[(-3,-1.1,.5),(-1.5,1.2,1.6),(1.5,1.8,1.3),(3,1,.5)],'red',.035,True)
        else:
            for x,y in [(-1.5,-.3),(2,.8)]:ring('Ghost error callout',(x,y,.5),.28,'red',.027)
    elif sid in ['S07','S09','S10','S12','S22','S23']:
        setup(sid,(9,-14,14) if sid!='S10' else (10,-14,6),(0,0,.5),12.7)
        room(grid=sid in ['S22','S23']);sensor_pair(two=sid!='S07')
        if sid=='S09':
            hardware('Main PC',(-4.3,-2.6,.5),'pc');hardware('Sender laptop',(4.3,-2.6,.0),'laptop')
            curve('Direct LAN',[(-4.2,-2.8,.1),(-2,-3.6,.05),(2,-3.6,.05),(4.1,-2.8,.1)],'red',.027,True);label('LAN',(0,-3.7,.12),.2,'red')
        if sid=='S12':
            for x,y in [(-.8,.2),(1,-.3)]:
                mannequin('Actual visitor',(x,y,.04),'white',.8);mannequin('Duplicate identity',(x+.48,y+.22,.04),'redghost',.8,wire=True)
                curve('One person split',[(x,y,1.3),(x+.48,y+.22,1.3)],'red',.014)
        if sid in ['S22','S23']:
            linebox('Safe zone',-3.05,3.05,-1.45,1.45,.055,'green',.025)
            if sid=='S22':
                for x,y in [(-1,.4),(1,-.5)]:mannequin('Visitor',(x,y,.04),'white',.8)
            else:
                # Foreground body lies on the ray B -> held position.
                mannequin('Occluding visitor',(1.2,-.5,.04),'white',.85)
                mannequin('Held last pose',(-.4,.5,.04),'greenghost',.85)
                ring('Held location',(-.4,.5,.065),.43,'green',.026);ring('Paused timer',(-.4,.5,.075),.55,'green',.025,0,math.pi*1.5)
                for dx in [-.10,.10]:box('Pause indicator',(-.4+dx,.5,.12),(.065,.30,.055),'green',.01)
                mesh('Occluded floor wedge',[(1.2,-.5,.04),(-3.2,1.9,.04),(-2.1,1.9,.04)],[(0,1,2)],'dark')
                curve('Blocked sight line',[(3.35,-1.82,.72),(1.2,-.5,.72)],'blue',.019)
    elif sid=='S08':
        setup(sid,(6,-12,7),(0,0,.8),9.2)
        box('Comparison platform',(0,0,-.08),(7,3,.16),'dark',.05)
        mannequin('Front-facing visitor',(-1.8,0,.03),'white',1.35)
        mannequin('Back-facing visitor',(1.5,0,.03),'white',1.35,math.pi)
        mannequin('Swapped observation',(1.73,0,.03),'red',1.35,wire=True)
        for x,t in [(-2.35,'L'),(-1.25,'R'),(.95,'R'),(2.15,'L')]:label(t,(x,-.28,1.08),.23,'blue' if x<0 else 'red')
        ring('Turn arrow',(0,0,2.25),.5,'muted',.025,0,math.pi*1.65)
        hardware('Kinect',(-3,0,.4),scale=.8)
    elif sid=='S11':
        setup(sid,(6,-12,4.5),(0,0,1.0),9.7)
        box('Side section base',(0,0,-.1),(8,3,.2),'slab',.04)
        hardware('Kinect side section',(-3.3,0,.8),rot=math.pi/2)
        mannequin('Foreground occluder',(-.4,0,.04),'white',1.2)
        mannequin('Occluded visitor',(2.15,0,.04),'redghost',1.2)
        mannequin('Missing observation',(2.15,0,.04),'red',1.2,wire=True)
        for z in [.25,.5,.75,1.0,1.3,1.65,2.0]:
            end=(-.70,0,z) if z<1.85 else (3.6,0,z+1.0)
            curve('Visibility ray',[(-3.1,0,.86),end],'blue',.009)
        mesh('Occluded shadow volume',[(-.4,-.22,.05),(-.4,.22,.05),(-.4,.22,1.94),(-.4,-.22,1.94),(3.7,-.5,.04),(3.7,.5,.04),(3.7,.5,3.45),(3.7,-.5,3.45)],[(0,1,5,4),(2,3,7,6),(0,3,7,4),(1,2,6,5)],'occluded')
        ring('Lost detection',(2.15,0,2.3),.22,'red',.02,plane='XZ')
    elif sid=='S13':
        setup(sid,(7,-12,14),(0,0,.5),13.7)
        footage('Older attempt',-3,1.0,.4,5.8,3.26,'L1');footage('Recent attempt',3.0,1.1,.7,6.9,3.88,'L2');footage('Current attempt',0,-.6,1.1,7.8,4.39,'L1')
        curve('Timeline',[(-5,-3.5,.0),(5,-3.5,.0)],'muted',.018)
        for x,t in [(-4,'10-12'),(-1.3,'10-15'),(1.4,'10-23'),(4.1,'10-28')]:rod('Timeline tick',(x,-3.65,.01),(x,-3.35,.01),.01,'white');label(t,(x,-3.95,.03),.19,'muted',False)
    elif sid in ['S14','S15','S16','S17','S18']:
        n=2 if sid in ['S14','S15'] else 3 if sid=='S16' else 4
        setup(sid,(1,-5,20),(0,0,.3),11.5);cards(n,'plain' if sid=='S14' else 'success' if sid=='S18' else 'fail')
    elif sid=='S19':
        setup(sid,(1,-6,22),(0,0,.5),12.2)
        for x,y in [(-5,2),(5,2),(-5,-2),(5,-2),(-2,3.8),(2,3.8)]:footage('Discarded attempt',x,y,.2,2.8,1.58,'L3')
        footage('Success evidence',0,0,1.6,7.9,4.44,'L4',True)
    elif sid in ['S20','S21']:
        setup(sid,(6,-9,6),(0,0,1.0),6.0)
        box('Calibration stage',(0,0,-.08),(4.5,3.5,.16),'dark',.06)
        axes((-1.7,-1.2,.05),0,'white');axes((1.6,-1.2,.05),0 if sid=='S21' else .44,'blue')
        fusion_points(-.35,0,'white')
        fusion_points(-.35 if sid=='S21' else .45,.03,'blue',0 if sid=='S21' else .44)
        if sid=='S20':
            curve('Calibration residual',[(-.35,-.45,.15),(.45,-.45,.15)],'red',.015)
            for x in [-.35,.45]:rod('Residual tick',(x,-.55,.15),(x,-.35,.15),.01,'muted')
        else:
            ring('Accepted calibration',(1,0,.1),.28,'green',.025);curve('Checkmark',[(.85,-.06,.13),(.97,-.14,.13),(1.18,.14,.13)],'green',.033)
    elif sid in ['S24','S25']:
        setup(sid,(4,-10,16),(0,0,.5),18.4);branches(sid=='S25')
    elif sid in ['S26','S27']:
        setup(sid,(10,-17,16),(0,0,.5),22.8);structure(sid=='S26')
    elif sid=='S28':
        setup(sid,(8,-13,12),(0,0,1.2),16.4)
        for i in range(180):
            x=rng.uniform(-4,6);y=rng.uniform(-1.0,2.5);z=rng.uniform(.5,2.7)+(x+4)*.12
            sphere('Structure becomes firefly',(x,y,z),rng.uniform(.015,.045),'fly' if x>0 else 'white')
        for a,b in [((-6,0,.5),(-3,0,.5)),((-3,0,.5),(-2,1,.5)),((-3,0,.5),(-2,-1,.5))]:dashed('Fading connection',a,b,'muted',.009,18)
    else:raise ValueError(sid)

def fit_camera(scene,margin=1.10):
    bpy.context.window.scene=scene;bpy.context.view_layer.update();cam=scene.camera;inv=cam.matrix_world.inverted();pts=[]
    for obj in scene.objects:
        if obj.type not in {'MESH','CURVE','FONT'} or obj.name.startswith('Infinite charcoal'):continue
        pts.extend(inv@(obj.matrix_world@Vector(c)) for c in obj.bound_box)
    xx=[p.x for p in pts];yy=[p.y for p in pts]
    cx=(min(xx)+max(xx))/2;cy=(min(yy)+max(yy))/2
    cam.location+=cam.rotation_euler.to_matrix()@Vector((cx,cy,0))
    needed=max(max(xx)-min(xx),(max(yy)-min(yy))*1920/1080)*margin
    cam.data.ortho_scale=max(cam.data.ortho_scale,needed)

for item in DATA:
    if item['id'] not in TARGETS:continue
    print('V3_BUILD',item['id'],flush=True);build(item['id'])
    if item['id'] in {'S03','S04','S06','S07','S09','S10','S11','S12','S13','S20','S21','S22','S23'}:fit_camera(SC)
    SC['scene_id']=item['id'];SC['start_seconds']=int(item['t'].split(':')[0])*60+int(item['t'].split(':')[1]);SC['duration_seconds']=item['d'];SC['status']='Storyboard visualization / not field validation'
    print('V3_RENDER',item['id'],flush=True);bpy.ops.render.render(write_still=True,scene=SC.name)
    print('V3_DONE',item['id'],flush=True)
if not ARGS:
    bpy.context.window.scene=bpy.data.scenes.get('S11') or SC
    for stored in list(bpy.data.scenes):
        if not len(stored.objects):bpy.data.scenes.remove(stored);continue
        stored.render.filepath='//'+stored.name+'.png'
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'LIMEN_개발로그_콘티_v3.blend'))
print('V3_COMPLETE',flush=True)
