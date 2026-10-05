# Turns every exercises/*.json into an animation on the mannequin rig.
# Output: exercises.glb (mesh + rig + one animation per exercise) and exercises.json (metadata).
# Run:  blender -b -P library/build_library.py                      (all categories -> library/)
#       blender -b -P library/build_library.py -- <category> <dir>  (one category -> <dir>, for checking)
#
# Pose format (degrees, the figure's own axes: x = right->left, y = up, z = forward):
#   bone: [x, y, z] rotation, applied y (twist) then z (sideways) then x (forward/back).
#   arms/legs: x<0 swings forward, z>0 moves out to the side. spine/neck: x>0 bends forward,
#   y>0 turns left, z>0 bends right. elbow x<0 bends, knee x>0 bends.
#   "arm", "leg"... without L/R = both sides. Right side values are written like the left and mirrored.
#   "bone.pos": [x, y, z] metres offset ("pos" = whole body). "hold": extra seconds to stay on this key.
#   "view": "head" | "upper" | "floor" on an exercise = camera hint for players (default full body).
#   Every key is grounded automatically: the lowest point of the body touches the floor.
#   "seated": true on an exercise = grounded on a chair instead: bottom of the pelvis at seat height.
#   "once": true = plays one time (no loop back to the first key), e.g. a stage dive.
#   key "lift": metres above the floor after grounding (jumps, flips).
#   key "prop": "handL" | "handR" = the computer mouse is held in that hand; [x, y, z] = mouse lies there (world,
#   metres, y up, z forward); "propRot": [x, y, z] its rotation. No "prop" on a key = mouse hidden.
#   "bpm": tempo the moves were written for (dances); players can speed it up to a song's tempo.
import bpy, json, glob, os, sys
import numpy as np
from math import radians
from mathutils import Euler, Vector
from bpy_extras import anim_utils

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
REST = {'arm': [0, 0, 6], 'elbow': [-6, 0, 0]}
SIDED = ('arm', 'elbow', 'hand', 'leg', 'knee', 'foot')
SEAT = 0.45
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ONLY, OUT = (args + [None, HERE])[:2]

bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, 'mannequin.blend'))
scene = bpy.context.scene
scene.render.fps = FPS
rig, body = bpy.data.objects['rig'], bpy.data.objects['mannequin']
bones = rig.pose.bones
for b in bones: b.rotation_mode = 'QUATERNION'
rig.animation_data_create()


def expand(key):
    """Shorthand key -> {bone: (rot, pos)} with mirroring for the right side."""
    rot, pos = {}, {}
    for k, v in {**REST, **key}.items():
        if k in ('hold', 'lift', 'prop', 'propRot'): continue
        if k == 'pos': k = 'hips.pos'
        name, is_pos = (k[:-4], True) if k.endswith('.pos') else (k, False)
        sides = [(name + 'L', False), (name + 'R', True)] if name in SIDED else [(name, name.endswith('R') and name[:-1] in SIDED)]
        for bone, mirror in sides:
            if bone not in bones: raise KeyError(f'unknown bone {bone}')
            if is_pos: pos[bone] = (-v[0], v[1], v[2]) if mirror else tuple(v)
            else: rot[bone] = (v[0], -v[1], -v[2]) if mirror else tuple(v)
    # specific sides win over "both sides"
    for k, v in key.items():
        if k[:-1] in SIDED and k[-1] in 'LR':
            rot[k] = (v[0], -v[1], -v[2]) if k[-1] == 'R' else tuple(v)
    return rot, pos


PELVIS = None


def lowest_point(only_pelvis=False):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    me = ev.to_mesh()
    co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', co)
    ev.to_mesh_clear()
    m = np.array(ev.matrix_world)
    z = co.reshape(-1, 3) @ m[2, :3] + m[2, 3]
    return float(z[PELVIS if only_pelvis else BODY].min())


def pose(key, seated=False):
    rot, pos = expand(key)
    for b in bones:
        r = rot.get(b.name, (0, 0, 0))
        b.rotation_quaternion = Euler([radians(a) for a in r], 'YZX').to_quaternion()
        b.location = Vector(pos.get(b.name, (0, 0, 0)))
    bpy.context.view_layer.update()
    if seated:
        bones['hips'].location.y -= lowest_point(True) - SEAT    # hips local y = up
        bpy.context.view_layer.update()
        if lowest_point() < -0.01: print(f'WARNING {key} goes below the floor while seated')
    else:
        bones['hips'].location.y -= lowest_point()
    bones['hips'].location.y += key.get('lift', 0)
    p = bones['prop']
    p.scale = (1, 1, 1) if 'prop' in key else (0, 0, 0)
    if isinstance(key.get('prop'), str):                       # held: follow the hand
        bpy.context.view_layer.update()
        h = bones[key['prop']].matrix                             # armature space (Blender axes)
        grip = h @ Vector((0, -0.07, 0.03))
        p.location = Vector((grip.x, grip.z, -grip.y))            # Blender -> figure axes (y up, z forward)
        p.rotation_quaternion = h.to_quaternion()
    elif 'prop' in key:
        p.location = Vector(key['prop'])
        p.rotation_quaternion = Euler([radians(a) for a in key.get('propRot', (0, 0, 0))], 'YZX').to_quaternion()


g = body.vertex_groups['hips'].index
PELVIS = np.array([any(e.group == g and e.weight > .5 for e in v.groups) for v in body.data.vertices])
g = body.vertex_groups['prop'].index
BODY = np.array([not any(e.group == g for e in v.groups) for v in body.data.vertices])
FILES = sorted(glob.glob(os.path.join(HERE, 'exercises', (ONLY or '*') + '.json')))
assert FILES, f'no exercises/{ONLY}.json'

meta = []
for path in FILES:
    cat = json.load(open(path, encoding='utf-8'))
    for ex in cat['exercises']:
        act = bpy.data.actions.new(ex['id'])
        act.use_fake_user = True
        rig.animation_data.action = act
        prev, t, times = {}, 0.0, []
        first = {k: v for k, v in ex['keys'][0].items() if k != 'hold'}
        for key in ex['keys'] + ([] if ex.get('once') else [first]):   # close the loop
            for dt in ([0, key.get('hold', 0)] if key.get('hold') else [0]):
                t += dt
                try: pose(key, ex.get('seated'))
                except Exception as e: raise SystemExit(f"ERROR in {ex['id']}: {e}")
                frame = 1 + round(t * FPS)
                for b in bones:
                    q = b.rotation_quaternion
                    if b.name in prev and prev[b.name].dot(q) < 0: q.negate()   # shortest path
                    prev[b.name] = q.copy()
                    b.keyframe_insert('rotation_quaternion', frame=frame)
                    b.keyframe_insert('location', frame=frame)
                    if b.name == 'prop': b.keyframe_insert('scale', frame=frame)
            times.append(round(t, 3))
            t += ex['beat']
        if not ex.get('once'): times.pop()                  # the closing key is key 0 again
        for fc in anim_utils.action_get_channelbag_for_slot(act, act.slots[0]).fcurves:
            mode = 'CONSTANT' if fc.data_path.endswith('scale') else 'LINEAR' if ex.get('linear') else None
            if mode:
                for kp in fc.keyframe_points: kp.interpolation = mode
        meta.append({k: ex[k] for k in ('id', 'he', 'en', 'amount', 'steps', 'view', 'seated', 'once', 'bpm') if k in ex} |
                    {'category': cat['category']['id'], 'duration': round(t - ex['beat'], 3), 'keyTimes': times})
        if ex.get('once'): meta[-1]['duration'] = times[-1]
        print('built', ex['id'])

cats = {}
for path in FILES:
    c = json.load(open(path, encoding='utf-8'))['category']; cats[c['id']] = c

rig.animation_data.action = None
for b in bones: b.rotation_quaternion = (1, 0, 0, 0); b.location = (0, 0, 0)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'exercises.glb'), export_format='GLB',
                          export_animation_mode='ACTIONS', export_image_format='JPEG', export_jpeg_quality=88, export_force_sampling=True, export_frame_step=1)
json.dump({'categories': list(cats.values()), 'exercises': meta},
          open(os.path.join(OUT, 'exercises.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
ids = [m['id'] for m in meta]
assert len(ids) == len(set(ids)), 'duplicate exercise ids'
print('OK', len(meta), 'exercises')
