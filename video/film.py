# The promo film: set + big mannequin + tiny mannequin on the monitor, 19 shots timed to the narration.
#   blender -b -P video/film.py -- board <out-dir>          one low-res frame from the middle of every shot
#   blender -b -P video/film.py -- frames <out-dir> a b     full-quality PNG frames a..b (render in chunks)
# Times are seconds from the narration take (word timings: remotion/scripts/desk-break-promo.words.json).
import bpy, sys, os, math
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, r'C:\studio\tools\video-engine\blender')
import clay

FPS, END = 24, 29.5
F = lambda t: 1 + round(t * FPS)
args = sys.argv[sys.argv.index('--') + 1:]
MODE, OUT = args[0], args[1]

clay.reset(fps=FPS, frames=F(END))
sc = bpy.context.scene
clay.stage('cream')
bpy.data.objects['stage'].rotation_euler.z = math.pi           # curved wall behind the desk
# where the studio wall doesn't reach, the camera sees the world: make it the warm wall tone, not grey
w = sc.world; nt = w.node_tree; bg = next(n for n in nt.nodes if n.type == 'BACKGROUND')
seen = nt.nodes.new('ShaderNodeBackground'); seen.inputs['Color'].default_value = clay.rgb('#E9D0A6'); seen.inputs['Strength'].default_value = 1.0
lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac']); nt.links.new(bg.outputs['Background'], mix.inputs[1])
nt.links.new(seen.outputs['Background'], mix.inputs[2]); nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
wood_img = bpy.data.images.load(os.path.join(ROOT, 'library', 'wood.png'))


# ---------- materials & set ----------
def wood(name, tint=(1, 1, 1, 1), rough=.45, scale=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value = rough
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = wood_img
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale,) * 3
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], tex.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs['Fac'].default_value = 1
    mix.inputs['Color2'].default_value = tint
    nt.links.new(tex.outputs['Color'], mix.inputs['Color1']); nt.links.new(mix.outputs['Color'], b.inputs['Base Color'])
    return m


def box(name, size, at, mat, r=.012):
    o = clay.rounded_box(size, r=r, name=name, at=at)
    o.data.materials.clear(); o.data.materials.append(mat)
    return o


maple = wood('maple', scale=1.6)
walnut = wood('walnut', tint=(.55, .38, .24, 1), rough=.4, scale=2.2)
floor = bpy.data.objects['stage']; floor.data.materials.clear()
floor.data.materials.append(wood('floor', tint=(.97, .93, .88, 1), rough=.5, scale=1.4))

box('desk_top', (1.3, .66, .035), (0, -.78, .7225), maple)
for x in (-.6, .6):
    box('desk_leg', (.04, .6, .72), (x, -.78, .36), maple)
box('mon_stand', (.22, .16, .012), (0, -.98, .746), walnut)
box('mon_neck', (.05, .03, .2), (0, -1.0, .85), walnut)
box('monitor', (.66, .03, .4), (0, -.99, 1.13), walnut, r=.01)
box('keyboard', (.44, .14, .02), (-.03, -.6, .768), walnut, r=.008)
desk_mouse = clay.sphere(.03, name='desk_mouse', at=(.3, -.6, .765))
desk_mouse.scale = (1, 1.6, .55); desk_mouse.data.materials.clear(); desk_mouse.data.materials.append(walnut)
for nm, s, at in [('seat', (.46, .44, .04), (0, .12, .43)), ('back', (.46, .04, .5), (0, .34, .7))]:
    box('chair_' + nm, s, at, maple)
for x in (-.2, .2):
    for y in (.31, -.07):
        box('chair_leg', (.035, .035, .41), (x, y, .205), maple)

# screens: one plane per state, switched on and off over time
screens = {}
for i, nm in enumerate(['a', 'b', 'c', 'done']):
    m = bpy.data.materials.new('screen_' + nm); m.use_nodes = True
    nt = m.node_tree; nt.nodes.remove(nt.nodes['Principled BSDF'])
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.6
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(os.path.join(HERE, f'screen-{nm}.png'))
    nt.links.new(tx.outputs['Color'], em.inputs['Color']); nt.links.new(em.outputs['Emission'], nt.nodes['Material Output'].inputs['Surface'])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -.9735 + i * .0001, 1.13), rotation=(math.radians(90), 0, math.radians(180)))
    p = bpy.context.object; p.name = 'screen_' + nm; p.scale = (.62, .38, 1); p.data.materials.append(m)
    screens[nm] = p


def show_only(objs, t, on):
    """objs visible from time t when on=True, hidden when False (stepped, no fade)."""
    for o in objs:
        for attr in ('hide_render', 'hide_viewport'):
            setattr(o, attr, not on); o.keyframe_insert(attr, frame=F(t))


for nm, (t0, t1) in {'a': (0, 1.66), 'b': (1.66, 3.3), 'c': (3.3, 20.9), 'done': (20.9, END + 1)}.items():
    o = screens[nm]
    if t0 > 0:
        show_only([o], 0, False)
    show_only([o], t0, True); show_only([o], t1, False)

# ---------- the two mannequins ----------
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, 'library', '.check', 'video', 'exercises.glb'))
big = next(o for o in sc.objects if o.type == 'ARMATURE')
big_mesh = next(o for o in sc.objects if o.type == 'MESH' and o.parent == big)
for o in sc.objects:                                   # the library mouse prop is dark plastic; wood here
    if o.type == 'MESH' and 'plastic' in o.data.materials:
        o.data.materials[o.data.materials.find('plastic')] = walnut
mini = big.copy(); mini.data = big.data.copy(); sc.collection.objects.link(mini)
mini_mesh = big_mesh.copy(); sc.collection.objects.link(mini_mesh)
mini_mesh.parent = mini; mini_mesh.modifiers[0].object = mini
for rig in (big, mini):
    rig.animation_data_create(); rig.animation_data.action = None


def place(rig, t, loc, rot_z=0.0, scale=1.0):
    rig.location, rig.rotation_euler, rig.scale = loc, (0, 0, math.radians(rot_z)), (scale,) * 3
    for path in ('location', 'rotation_euler', 'scale'):
        rig.keyframe_insert(path, frame=F(t))


def acts(rig, plan):
    """plan: [(start_s, action, speed, play_from_s)] — each plays from its start until the next one begins."""
    tr = rig.animation_data.nla_tracks.new()
    for k, (t, name, speed, skip) in enumerate(plan):
        end = plan[k + 1][0] if k + 1 < len(plan) else END + 1
        a = bpy.data.actions[name]
        a0, a1 = a.frame_range
        s = tr.strips.new(name, F(t), a)
        s.action_frame_start = a0 + skip * FPS
        s.scale = 1 / speed
        length = (F(end) - F(t)) * speed
        loop = (a1 - s.action_frame_start)
        s.repeat = max(1.0, length / max(loop, 1)) if not name.startswith(('funny', 'v-slide')) else 1.0
        s.extrapolation = 'HOLD_FORWARD'
        if s.frame_end > F(end):
            s.frame_end = F(end)


STAND = ((.72, -.22, 0), -47)          # beside the desk corner, facing the monitor
acts(big, [(0, 'v-typing', 1, 0), (1.66, 'v-slump', 1, 0), (6.3, 'v-slide', .9, 0), (11.7, 'v-stand', 1, 0),
           (13.3, 'neck-side-tilt', 1.15, 0), (15.7, 'shoulder-rolls-back', 1, 0), (16.6, 'standing-side-bend-reach', 1.2, 0),
           (17.6, 'v-stand', 1, 0), (18.35, 'funny-dab', 1.3, .3), (18.9, 'funny-stage-dive', 1.05, .6),
           (21.7, 'funny-mouse-drop', 1.25, 0), (25.2, 'v-stand', 1, 0)])
place(big, 0, (0, 0, 0)); place(big, 11.7, STAND[0], STAND[1])
place(big, 18.9, (1.0, .55, 0), 90)          # the dive: open floor, facing +x, falls back towards the desk side
place(big, 21.7, STAND[0], STAND[1] + 25)
place(big, 24.7, (.5, .75, 0), 180)           # final: facing the camera, right third

MINI_AT = (.235, -.958, .935)
acts(mini, [(0, 'v-stand', 1, 0), (9.34, 'v-wave', 1, 0), (11.7, 'neck-side-tilt', 1.15, 0),
            (15.7, 'shoulder-rolls-back', 1, 0), (16.6, 'standing-side-bend-reach', 1.2, 0), (17.6, 'funny-dab', 1.3, .3),
            (18.9, 'v-stand', 1, 0), (20.9, 'v-wave', 1, 0)])
place(mini, 0, MINI_AT, 180, 0.0001); place(mini, 9.3, MINI_AT, 180, 0.0001)
place(mini, 9.5, MINI_AT, 180, .082); place(mini, 9.62, MINI_AT, 180, .07)      # pop: overshoot and settle
show_only([desk_mouse], 21.7, False)

# ---------- camera: hard cuts, one move per shot ----------
aim = clay.link(bpy.data.objects.new('aim', None))
cd = bpy.data.cameras.new('cam'); cam = clay.link(bpy.data.objects.new('cam', cd)); sc.camera = cam
tc = cam.constraints.new('TRACK_TO'); tc.target = aim; tc.track_axis, tc.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'
cd.dof.use_dof = True; cd.sensor_width = 36; cd.dof.focus_object = aim      # focus follows where the camera looks


def key(t, pos, look, lens, fstop, last=False):
    cam.location, aim.location = pos, look
    cd.lens, cd.dof.aperture_fstop = lens, fstop
    for o, p in ((cam, 'location'), (aim, 'location'), (cd, 'lens'), (cd.dof, 'aperture_fstop')):
        o.keyframe_insert(p, frame=F(t) - (1 if last else 0))


SHOTS = []
def shot(t0, t1, a, b, lens, fstop=2.8, lens1=None):
    """a, b = (camera, look-at) at the start and end of the shot."""
    SHOTS.append((t0, t1))
    key(t0, *a, lens, fstop); key(t1, *b, lens1 or lens, fstop, last=True)


def at(rig, bone, t, off=(0, 0, 0)):
    """where a bone is at time t (world), so cameras aim at the body, not at a guess"""
    sc.frame_set(F(t))
    return tuple(rig.matrix_world @ rig.pose.bones[bone].head + Vector(off))


add = lambda p, d, k=1.0: tuple(a + b * k for a, b in zip(p, d))
WORK, CORNER = (.19, -.974, 1.13), (MINI_AT[0], MINI_AT[1], MINI_AT[2] + .065)
FACING = (-.73, -.68, 0)                                     # where the standing mannequin looks (towards the monitor)
shot(0.0, .95, ((.2, -.4, 1.135), WORK), ((.19, -.47, 1.13), WORK), 40, 2.8)                              # S1 ECU "Working… 0:03"
H = at(big, 'neck', 1.3, (0, 0, .17))
shot(.95, 1.66, (add(H, (.62, -.78, -.08)), H), (add(H, (.56, -.7, -.08)), H), 50, 2.4)                      # S2 face, 3/4 from the screen side
shot(1.66, 3.3, ((0, -.35, 3.2), (0, -.4, .7)), ((0, -.35, 3.0), (0, -.4, .7)), 35, 5.6)                    # S3 top shot
H = at(big, 'neck', 4.5, (0, 0, .12))
shot(3.3, 6.3, (add(H, (-1.0, .1, .05)), H), (add(H, (-.78, .08, .04)), H), 50, 2.4)                        # S4 side CU, slow push-in
L = at(big, 'hips', 7.6)
shot(6.3, 9.2, ((-1.25, .95, .28), L), ((-1.05, .8, .25), at(big, 'hips', 8.8)), 30, 4.0)                    # S5 low angle, the slide
shot(9.2, 10.4, (add(CORNER, (.05, .82, .02)), CORNER), (add(CORNER, (.04, .7, .02)), CORNER), 100, 4.0)     # S6 macro corner, pop + wave
shot(10.4, 11.7, ((.38, .3, .42), CORNER), ((.36, .2, .44), CORNER), 50, 2.8)                              # S7 from the floor, past the big one, up at the mini
shot(11.7, 13.3, ((1.5, .32, 1.74), CORNER), ((1.44, .26, 1.72), CORNER), 45, 2.8)                            # S8 over the shoulder
shot(13.3, 14.6, ((2.5, -.45, 1.3), (.47, -.42, 1.15)), ((2.4, -.45, 1.3), (.47, -.42, 1.15)), 26, 5.6)     # S9 profile two-shot, both tilt
H = at(big, 'neck', 15.1, (0, 0, .15))
shot(14.6, 15.7, (add(H, FACING, 1.05), H), (add(H, FACING, .9), H), 50, 2.4)                               # S10 CU from the screen's point of view
C = at(big, 'spine', 16.1, (0, 0, .3))
shot(15.7, 16.6, (add(C, (.9, -.9, .05)), C), (add(C, (1.2, -.35, .1)), C), 50, 3.2)                        # S11 orbit, shoulders
B = at(big, 'spine', 17.1, (0, 0, .2))
shot(16.6, 17.6, (add(B, (1.15, -.8, -.35)), B), (add(B, (1.15, -.8, .65)), B), 26, 4.0)         # S12 crane up, side bend
shot(17.6, 18.35, (add(CORNER, (.05, .82, .02)), CORNER), (add(CORNER, (.04, .74, .02)), CORNER), 100, 4.0)  # S13 macro, mini dabs
C = at(big, 'spine', 18.6, (0, 0, .35))
shot(18.35, 18.9, ((1.4, -1.05, .45), C), ((1.3, -.95, .45), C), 24, 4.0)                                   # S14 low hero, big dabs
shot(18.9, 20.8, ((1.0, 2.7, .45), (1.0, .55, .8)), ((1.05, 2.5, .35), (.85, .55, .3)), 24, 4.0)              # S15 stage dive, side, low
shot(20.8, 21.7, ((.16, -.38, 1.135), (.15, -.974, 1.13)), ((.155, -.44, 1.13), (.15, -.974, 1.13)), 36, 2.8)                            # S16 ECU "Done"
C = at(big, 'spine', 22.6, (0, 0, .32))
shot(21.7, 23.4, (add(C, (-.1, -1.7, .05)), C), (add(C, (.08, -1.5, .1)), C), 30, 3.2)                    # S17 mouse up, and drop
M = at(big, 'prop', 24.2)
shot(23.4, 24.7, (add(M, (.34, -.26, .09)), M), (add(M, (.29, -.22, .07)), M), 85, 2.8)                      # S18 macro, the mouse lands
shot(24.7, END + .05, ((0, 3.5, 1.3), (.1, -.4, .95)), ((0, 4.3, 1.9), (.1, -.4, .9)), 36, 8.0)              # S19 crane back, wide

for o in (cam, aim, cd):
    ad = o.animation_data
    if ad and ad.action:
        from bpy_extras import anim_utils
        for fc in anim_utils.action_get_channelbag_for_slot(ad.action, ad.action.slots[0]).fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'; kp.easing = 'AUTO'
            for a, b in zip(fc.keyframe_points, fc.keyframe_points[1:]):
                if b.co.x - a.co.x <= 1.01:            # end of a shot -> next shot: a hard cut
                    a.interpolation = 'CONSTANT'

# ---------- light & render ----------
for L in clay.lights(scale=.6, sun=2.0, sun_soft=8):
    L.location.rotate(Euler((0, 0, math.pi))); L.rotation_euler.z += math.pi

if MODE == 'board':
    clay.render_settings('CYCLES', res=(1080, 1920), samples=24, exposure=-.1, blur=False)
    sc.render.resolution_percentage = 50
    os.makedirs(OUT, exist_ok=True)
    for i, (t0, t1) in enumerate(SHOTS):
        for part, t in (('a', t0 + .12), ('b', (t0 + t1) / 2), ('c', t1 - .12)):
            clay.still(os.path.join(OUT, f's{i + 1:02d}{part}.png'), frame=F(t))
    print('OK board', len(SHOTS))
else:
    a, b = int(args[2]), int(args[3])
    clay.render_settings('CYCLES', res=(1080, 1920), samples=96, exposure=-.1)
    sc.frame_start, sc.frame_end = a, b
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = os.path.join(OUT, 'f')
    sc.render.use_overwrite, sc.render.use_placeholder = False, True     # rerun = continue where it stopped
    bpy.ops.render.render(animation=True)
    print('OK frames', a, b)
