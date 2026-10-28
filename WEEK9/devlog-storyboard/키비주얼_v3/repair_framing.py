"""One-pass review repairs to the saved representative states."""
import bpy,math
from mathutils import Vector,Euler
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'LIMEN_개발로그_콘티_v3.blend'))
bpy.context.preferences.filepaths.save_version=0
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type!='CPU'
def fit(scene):
    bpy.context.window.scene=scene;bpy.context.view_layer.update();cam=scene.camera;inv=cam.matrix_world.inverted();pts=[]
    for obj in scene.objects:
        if obj.type not in {'MESH','CURVE','FONT'} or obj.name.startswith('Infinite charcoal'):continue
        pts.extend(inv@(obj.matrix_world@Vector(c)) for c in obj.bound_box)
    xx=[v.x for v in pts];yy=[v.y for v in pts]
    cam.location+=cam.rotation_euler.to_matrix()@Vector(((min(xx)+max(xx))/2,(min(yy)+max(yy))/2,0))
    cam.data.ortho_scale=max(cam.data.ortho_scale,max(max(xx)-min(xx),(max(yy)-min(yy))*1920/1080)*1.10)
def center(obj):
    return sum((obj.matrix_world@Vector(c) for c in obj.bound_box),Vector())/8
framed={'S03','S04','S06','S07','S09','S10','S11','S12','S13','S20','S21','S22','S23'}
for sid in list(framed)+['S16','S18']:
    scene=bpy.data.scenes[sid];bpy.context.window.scene=scene;bpy.context.view_layer.update()
    if sid=='S11':
        origin=Vector((-3.3,0,.8));turn=Euler((0,0,math.pi))
        for o in scene.objects:
            if o.name.startswith('Kinect side section'):
                delta=o.location-origin;delta.rotate(turn);o.location=origin+delta;o.rotation_euler.z+=math.pi
    if sid=='S16':
        for o in scene.objects:
            if o.type in {'CURVE','FONT'} and ('Raised FAIL frame' in o.name or 'Label FAIL' in o.name):
                c=center(o)
                if abs(c.x+2.57)<.15 and abs(c.y+1.52)<.15:o.location.z+=.32
    if sid=='S23':
        for o in scene.objects:
            if o.name.startswith('Occluded floor wedge'):
                o.data.vertices[1].co.x=-3.2;o.data.vertices[2].co.x=-2.1;o.data.update()
    if sid=='S18':
        cache={}
        for o in scene.objects:
            if o.type not in {'MESH','CURVE','FONT'} or o.name.startswith('Infinite charcoal'):continue
            c=center(o)
            if abs(c.x-1.01)<.94 and abs(c.y-.6053)<.55:continue
            for slot in o.material_slots:
                old=slot.material
                if not old:continue
                if old.name not in cache:
                    m=old.copy();m.name=old.name+' / S18 subdued';p=m.node_tree.nodes.get('Principled BSDF')
                    col=p.inputs['Base Color'].default_value
                    p.inputs['Base Color'].default_value=tuple(v*.24 for v in col[:3])+(col[3],)
                    p.inputs['Emission Strength'].default_value*=.2;cache[old.name]=m
                slot.material=cache[old.name]
    if sid in framed:fit(scene)
    scene.cycles.device='GPU';scene.render.filepath=str(P/(sid+'.png'))
    print('V3_REVIEW_RENDER',sid,flush=True);bpy.ops.render.render(write_still=True,scene=scene.name)
bpy.context.window.scene=bpy.data.scenes['S11']
bpy.ops.wm.save_as_mainfile(filepath=str(P/'LIMEN_개발로그_콘티_v3.blend'))
print('V3_REVIEW_COMPLETE',flush=True)
