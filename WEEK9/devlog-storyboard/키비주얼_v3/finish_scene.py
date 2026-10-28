"""Finalize the occlusion diagram after the framing review."""
import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'LIMEN_개발로그_콘티_v3.blend'))
bpy.context.preferences.filepaths.save_version=0
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type!='CPU'
s=bpy.data.scenes['S23'];bpy.context.window.scene=s
for obj in s.objects:
    if obj.name.startswith('Occluded floor wedge'):
        obj.data.vertices[1].co.x=-3.2;obj.data.vertices[2].co.x=-2.1;obj.data.update()
s.cycles.device='GPU';s.render.filepath=str(P/'S23.png')
bpy.ops.render.render(write_still=True,scene=s.name)
q=P/'검수';q.mkdir(exist_ok=True)
checks={}
for sid in ['S03','S04','S06','S07','S09','S10','S11','S12','S13','S20','S21','S22','S23']:
    scene=bpy.data.scenes[sid];bpy.context.window.scene=scene;bpy.context.view_layer.update()
    cam=scene.camera;inv=cam.matrix_world.inverted();pts=[]
    for obj in scene.objects:
        if obj.type not in {'MESH','CURVE','FONT'} or obj.name.startswith('Infinite charcoal'):continue
        pts.extend(inv@(obj.matrix_world@Vector(c)) for c in obj.bound_box)
    width=cam.data.ortho_scale;height=width*1080/1920
    ok=all(abs(p.x)<width/2 and abs(p.y)<height/2 for p in pts);checks[sid]=ok
assert all(checks.values()),checks
(q/'3D_프레이밍검수.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
bpy.context.window.scene=bpy.data.scenes['S11']
for stored in list(bpy.data.scenes):
    if not len(stored.objects):bpy.data.scenes.remove(stored);continue
    stored.render.filepath='//'+stored.name+'.png'
assert len(bpy.data.scenes)==31,len(bpy.data.scenes)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'LIMEN_개발로그_콘티_v3.blend'))
print('V3_FINAL_COMPLETE',flush=True)
