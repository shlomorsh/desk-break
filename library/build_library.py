# Turns every exercises/*.json into an animation on the mannequin rig.
# Output: exercises.glb (mesh + rig + one animation per exercise), exercises.blend (the same, as Blender actions)
# and exercises.json (metadata).
# Run:  blender -b -P library/build_library.py                      (all categories -> library/)
#       blender -b -P library/build_library.py -- <category> <dir>  (one category -> <dir>, for checking)
#       blender -b -P library/build_library.py -- <file.json> <dir>  (any file in the same format, e.g. the video's moves)
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
#   "amount_en" / "steps_en": the English amount and instructions ("he" / "amount" / "steps" are Hebrew).
import bpy, json, glob, os, sys
import numpy as np
from math import radians
from mathutils import Euler, Matrix, Quaternion, Vector
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

# ---- Contacts: what touches the floor stays put ------------------------------------------------------------
# The keys turn and move the body around the pelvis, so on its own a foot on the floor slides or swings with
# it. settle() replays every frame: it re-grounds the body, slides the whole body so parts resting on the floor
# (back, knees, the seat) don't skid, and holds a foot or hand that touches the floor where it landed, bending
# the leg/arm to reach it (two-bone IK). It lets go when the keys lift it (LIFT_LO..LIFT_HI).
# Every vertex belongs to exactly one bone (rigid wooden segments), so skinning is one matrix per bone.
NAMES = [b.name for b in bones]
BI = {n: i for i, n in enumerate(NAMES)}
PARENT = [BI[b.parent.name] if b.parent else -1 for b in bones]
VB = np.array([BI[body.vertex_groups[v.groups[0].group].name] for v in body.data.vertices])
co = np.empty(len(VB) * 3); body.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
RESTI = np.array([np.linalg.inv(np.array(rig.data.bones[n].matrix_local)) for n in NAMES])
LOC = np.einsum('nij,nj->ni', RESTI[VB, :3, :3], co) + RESTI[VB, :3, 3]      # each vertex in its bone's frame
LIMBS = [(BI[u], BI[m], BI[e], s) for u, m, e, s in
         (('legL', 'kneeL', 'footL', 1), ('legR', 'kneeR', 'footR', 1), ('armL', 'elbowL', 'handL', -1), ('armR', 'elbowR', 'handR', -1))]
ENDV = {e: np.where(VB == e)[0] for _, _, e, _ in LIMBS}
STILL = BODY & ~np.isin(VB, list(ENDV))       # parts that rest on the floor without IK: back, pelvis, knees...
TOUCH, LIFT_LO, LIFT_HI, FADE, MAX_DROP, NEAR, SLIDE, SETTLED = 0.01, 0.012, 0.06, 8, 0.06, 0.01, 0.15, 0.15
HIPS = BI['hips']
smooth = lambda x: x * x * (3 - 2 * x)
QH = np.array(rig.data.bones['hips'].matrix_local)[:3, :3]


def skin(M, idx=slice(None)):
    return np.einsum('nij,nj->ni', M[VB[idx], :3, :3], LOC[idx]) + M[VB[idx], :3, 3]


def rotx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def swing(a, b):
    """Smallest rotation taking direction a to direction b."""
    a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)
    ax, c = np.cross(a, b), a @ b
    s = np.linalg.norm(ax)
    if s < 1e-9: return np.eye(3)
    k = ax / s
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + s * K + (1 - c) * K @ K


def reach(Mp, Bu, Bm, end_t, A, sign):
    """Two-bone IK: bend the middle joint (its x axis; knees bend +x, elbows -x), then swing the upper bone so
    the end joint lands on A. Returns the new upper/middle local matrices and where the end really got to."""
    H = (Mp @ Bu)[:3, 3]
    th = Matrix(Bm[:3, :3].tolist()).to_euler('YZX').x
    rest = rotx(-th) @ Bm[:3, :3]                 # the middle joint's twist, without its bend
    dist = lambda a: np.linalg.norm(rotx(a) @ rest @ end_t + Bm[:3, 3])
    want, lo, hi = np.linalg.norm(A - H), 0.0, 2.9 * sign
    if want >= dist(lo): hi = lo
    elif want > dist(hi):
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if dist(mid) > want else (lo, mid)
    Bm2 = Bm.copy(); Bm2[:3, :3] = rotx(hi) @ rest
    Mu = Mp @ Bu
    v = Mu[:3, :3] @ (Bm2[:3, :3] @ end_t + Bm2[:3, 3])
    R = swing(v, A - H)
    Bu2 = Bu.copy(); Bu2[:3, :3] = Mp[:3, :3].T @ R @ Mu[:3, :3]
    return Bu2, Bm2, H + R @ v


def settle(ex, F, lift):
    """Bake frames 1..F so contacts hold (see above). Returns {data_path: [F x n] values} to key."""
    seated, loop = ex.get('seated'), not ex.get('once')
    Ms, shift, hips_loc, anchored, resting = [], [], [], [], []
    off, prev = np.zeros(2), None
    for f in range(1, F + 1):                     # pass 1: the keyed pose, re-grounded, resting parts pinned
        scene.frame_set(f)
        M = np.array([np.array(b.matrix) for b in bones])
        V = skin(M)
        # the keys are grounded; between them only push up out of the floor (pulling down to meet a swinging
        # foot would make the body bob)
        dz = max(0, SEAT - V[PELVIS, 2].min() if seated else lift.evaluate(f) - V[BODY, 2].min())
        z = V[:, 2] + dz
        on = PELVIS & (z < SEAT + NEAR) if seated else STILL & (z < NEAR)
        if prev is not None and (common := on & prev[0]).any():
            off = (prev[1][common] - V[common, :2]).mean(0)
        prev = on, V[:, :2] + off
        Ms.append(M); shift.append([*off, dz]); hips_loc.append(np.array(bones['hips'].location))
        anchored.append(on.any())
        resting.append([((VB == u) | (VB == m)) @ (z < NEAR) > 0 for u, m, _, _ in LIMBS])
    shift = np.array(shift)
    if loop: shift[:, :2] -= np.outer(np.linspace(0, 1, F), shift[-1, :2] - shift[0, :2])   # close the loop

    fk = np.array([[Ms[i][e, :3, 3] + shift[i] for _, _, e, _ in LIMBS] for i in range(F)])   # keyed end joints
    spd = np.linalg.norm(np.diff(fk, axis=0, prepend=fk[:1]), axis=2) * FPS
    low = np.array([[(LOC[ENDV[e]] @ Ms[i][e, :3, :3].T)[:, 2].min() + fk[i, li, 2] for li, (_, _, e, _) in enumerate(LIMBS)]
                    for i in range(F)])                                                    # keyed lowest point
    state = [{'mode': 'free', 'air': 99} for _ in LIMBS]
    out = {}
    for rep in ((0, 1) if loop else (1,)):      # loops run twice so the first frame starts where the last ends
        quats, locs = {i: [] for u, m, e, _ in LIMBS for i in (u, m, e)}, []
        for i in range(F):
            M = Ms[i].copy(); M[:, :3, 3] += shift[i]
            goal = {}
            for li, (u, m, e, sign) in enumerate(LIMBS):
                st, Rfk, hfk = state[li], M[e, :3, :3], M[e, :3, 3]
                Be = np.linalg.inv(M[m]) @ M[e]
                zmin = (LOC[ENDV[e]] @ Rfk.T)[:, 2].min() + hfk[2]
                rel = (np.linalg.inv(M[HIPS]) @ [*hfk, 1])[:3]      # where the keys put it, seen from the pelvis
                speed = spd[i, li]
                st['air'] = 0 if zmin > LIFT_HI / 2 else st['air'] + 1
                # let go when the keys lift it, or when the limb itself drags it far along the floor (a heel
                # slide, a leg sliding out) - not when the body moved over it, nor when the limb only made up for that
                if st['mode'] == 'plant':
                    moved = hfk - st['fk0']
                    by_body = moved - M[HIPS, :3, :3] @ (rel - st['rel0'])
                    slid = (zmin < 2 * TOUCH and np.linalg.norm(moved) > SLIDE                # still on the floor
                            and np.linalg.norm(by_body) < 0.5 * np.linalg.norm(moved))
                    lifted = min(zmin, zmin - by_body[2])      # how high the leg itself raised it, not a body tilt
                    if lifted > LIFT_HI: st['mode'] = 'free'             # lifted: already eased back onto the keys
                    elif resting[i][li] or slid: st.update(mode='fade', k=0, dp=st['head'] - hfk, dq=st['R'] @ Rfk.T)
                R, h = Rfk, hfk
                if st['mode'] == 'fade':
                    st['k'] += 1
                    if st['k'] > FADE: st['mode'] = 'free'
                    else:
                        w = 1 - smooth(st['k'] / FADE)
                        R = np.array(Quaternion().slerp(Matrix(st['dq'].tolist()).to_quaternion(), w).to_matrix()) @ Rfk
                        h = hfk + w * st['dp']
                if st['mode'] != 'plant' and zmin < TOUCH and not resting[i][li] and speed < SETTLED:
                    W = LOC[ENDV[e]] @ R.T + h
                    st.update(mode='plant', Rref=R @ Be[:3, :3].T, W=W, C=W[:, 2] < W[:, 2].min() + .003,
                              fk0=hfk, rel0=rel)
                    lifted = zmin
                if st['mode'] == 'plant':
                    Rp = st['Rref'] @ Be[:3, :3]            # keep the planted angle; the key may still roll the foot
                    st['W'][:, 2] -= 0.3 * max(st['W'][:, 2].min(), 0)   # ease a hovering foot down onto the floor
                    j = (LOC[ENDV[e]] @ Rp.T)[:, 2].argmin()            # roll onto whatever point is lowest now
                    hp = [*st['W'][j, :2], st['W'][st['C'], 2].min()] - Rp @ LOC[ENDV[e]][j]
                    W = LOC[ENDV[e]] @ Rp.T + hp
                    st.update(W=W, C=W[:, 2] < W[:, 2].min() + .003)
                    # as the keys start lifting it, hand it back to them gradually
                    st['s'] = s = smooth(np.clip((LIFT_HI - lifted) / (LIFT_HI - LIFT_LO), 0, 1))
                    R = np.array(Matrix(Rfk.tolist()).to_quaternion().slerp(Matrix(Rp.tolist()).to_quaternion(), s).to_matrix())
                    h = hfk + s * (hp - hfk)
                if st['mode'] != 'plant' and st['air'] < 15 and speed > SETTLED:
                    # coming down while still moving: hover, and touch down where the keys bring it to rest
                    k = next((j for j in range(i, F) if spd[j, li] < SETTLED), F - 1)
                    up = min(0.6 * np.linalg.norm(fk[k, li, :2] - hfk[:2]), 0.06) - zmin
                    if up > 0 and low[k, li] < TOUCH: h = h + [0, 0, up]; goal[li] = R, h
                if st['mode'] != 'free': goal[li] = R, h
            drop = 0.0
            if not anchored[i] and not seated:            # standing: lower the pelvis a little so legs reach
                for li, (R, h) in goal.items():
                    u, m, e, _ = LIMBS[li]
                    if LIMBS[li][3] < 0: continue
                    H = M[u, :3, 3]
                    r = np.linalg.norm(M[m, :3, 3] - H) + np.linalg.norm(M[e, :3, 3] - M[m, :3, 3])
                    hor = np.linalg.norm((h - H)[:2])
                    if hor < r: drop = max(drop, (H[2] - h[2]) - np.sqrt(r * r - hor * hor) + 0.002)
                drop = min(drop, MAX_DROP)
                M[:, 2, 3] -= drop
            for li, (u, m, e, sign) in enumerate(LIMBS):
                st, p = state[li], PARENT[u]
                if li in goal:
                    R, h = goal[li]
                    Bu, Bm2, got = reach(M[p], np.linalg.inv(M[p]) @ M[u], np.linalg.inv(M[u]) @ M[m],
                                         (np.linalg.inv(M[m]) @ M[e])[:3, 3], h, sign)
                    M[u] = M[p] @ Bu; M[m] = M[u] @ Bm2
                    M[e, :3, :3], M[e, :3, 3] = R, got
                    if st['mode'] == 'plant' and st['s'] > .99:   # (out of reach: the foot/hand slides along)
                        st['W'] += got - h
                st.update(R=M[e, :3, :3].copy(), head=M[e, :3, 3].copy())
            for b in quats:
                q = Matrix((np.linalg.inv(M[PARENT[b]]) @ M[b])[:3, :3].tolist()).to_quaternion()
                if quats[b] and np.dot(quats[b][-1], q) < 0: q.negate()
                quats[b].append(list(q))
            locs.append(hips_loc[i] + QH.T @ (shift[i] - [0, 0, drop]))
        out = {f'pose.bones["{NAMES[b]}"].rotation_quaternion': np.array(v) for b, v in quats.items()}
        out['pose.bones["hips"].location'] = np.array(locs)
    return out
FILES = [ONLY] if ONLY and ONLY.endswith('.json') else sorted(glob.glob(os.path.join(HERE, 'exercises', (ONLY or '*') + '.json')))
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
                rig['lift'] = float(key.get('lift', 0)); rig.keyframe_insert('["lift"]', frame=frame)
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
        bag = anim_utils.action_get_channelbag_for_slot(act, act.slots[0])
        for fc in bag.fcurves:
            mode = 'CONSTANT' if fc.data_path.endswith('scale') else 'LINEAR' if ex.get('linear') else None
            if mode:
                for kp in fc.keyframe_points: kp.interpolation = mode
        lift = bag.fcurves.find('["lift"]')
        for path, vals in settle(ex, frame, lift).items():   # every frame keyed: contacts hold between keys
            for i in range(vals.shape[1]):
                kp = bag.fcurves.find(path, index=i).keyframe_points
                kp.clear(); kp.add(len(vals))
                kp.foreach_set('co', np.column_stack([np.arange(1, len(vals) + 1), vals[:, i]]).ravel())
                for k in kp: k.interpolation = 'LINEAR'
        bag.fcurves.remove(lift)
        meta.append({k: ex[k] for k in ('id', 'he', 'en', 'amount', 'amount_en', 'steps', 'steps_en', 'view', 'seated', 'once', 'bpm') if k in ex} |
                    {'category': cat['category']['id'], 'duration': round(t - ex['beat'], 3), 'keyTimes': times})
        if ex.get('once'): meta[-1]['duration'] = times[-1]
        print('built', ex['id'])

cats = {}
for path in FILES:
    c = json.load(open(path, encoding='utf-8'))['category']; cats[c['id']] = c

rig.animation_data.action = None
del rig['lift']
for b in bones: b.rotation_quaternion = (1, 0, 0, 0); b.location = (0, 0, 0)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, 'exercises.glb'), export_format='GLB',
                          export_animation_mode='ACTIONS', export_image_format='JPEG', export_jpeg_quality=88, export_force_sampling=True, export_frame_step=1)
if not ONLY:                                  # the full library also as a Blender file: rig + one action per exercise
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'exercises.blend'), compress=True, copy=True)
json.dump({'categories': list(cats.values()), 'exercises': meta},
          open(os.path.join(OUT, 'exercises.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
ids = [m['id'] for m in meta]
assert len(ids) == len(set(ids)), 'duplicate exercise ids'
print('OK', len(meta), 'exercises')
