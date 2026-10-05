# The video's set: wooden desk, monitor (Claude working), keyboard, chair, and the mannequin from the library.
# Look-dev:  blender -b -P video/set.py -- real|soft <out.png> [exercise-id] [frame]
import bpy, sys, math, os
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, r'C:\studio\tools\video-engine\blender')
import clay

args = sys.argv[sys.argv.index('--') + 1:]
LOOK, OUT = args[0], args[1]
EX, FRAME = (args + ['chair-rowing', '1'])[2:4]

clay.reset(fps=24, frames=48)
clay.stage('cream')

wood_img = bpy.data.images.load(os.path.join(ROOT, 'library', 'wood.png'))


def wood(name, tint=(1, 1, 1, 1), rough=.45, scale=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = wood_img
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale, scale)
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
dark = wood('walnut', tint=(.55, .38, .24, 1), rough=.4, scale=2.2)    # darker wood for the monitor, still wood
# desk in front of the figure (the figure faces -Y), top at 0.74
box('desk_top', (1.3, .66, .035), (0, -.78, .74 - .0175), maple)
for x in (-.6, .6):
    box('desk_leg', (.04, .6, .72), (x, -.78, .36), maple)
# monitor
box('mon_stand', (.22, .16, .012), (0, -.98, .746), dark)
box('mon_neck', (.05, .03, .2), (0, -1.0, .85), dark)
mon = box('monitor', (.66, .03, .4), (0, -.99, 1.13), dark, r=.01)
scr_img = bpy.data.images.load(os.path.join(HERE, 'screen-working.png'))
sm = bpy.data.materials.new('screen'); sm.use_nodes = True
nt = sm.node_tree; nt.nodes.remove(nt.nodes['Principled BSDF'])
em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.6
tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = scr_img
nt.links.new(tx.outputs['Color'], em.inputs['Color']); nt.links.new(em.outputs['Emission'], nt.nodes['Material Output'].inputs['Surface'])
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -.974, 1.13), rotation=(math.radians(90), 0, math.radians(180)))
scr = bpy.context.object; scr.scale = (.62, .38, 1); scr.data.materials.append(sm)
# keyboard + mouse on the desk
box('keyboard', (.44, .14, .02), (-.03, -.6, .768), dark, r=.008)
ms = clay.sphere(.03, name='mouse', at=(.3, -.6, .765)); ms.scale = (1, 1.6, .55); ms.data.materials.clear(); ms.data.materials.append(dark)
# chair (seat top 0.45, like the library's seated exercises), back behind the figure
for nm, s, at in [('seat', (.46, .44, .04), (0, .12, .43)), ('back', (.46, .04, .5), (0, .34, .7))]:
    box('chair_' + nm, s, at, maple)
for x in (-.2, .2):
    for y in (.31, -.07):
        box('chair_leg', (.035, .035, .41), (x, y, .205), maple)
# wooden floor
bpy.data.objects['stage'].rotation_euler.z = math.pi      # the curved wall goes behind the desk, where the camera looks
floor = bpy.data.objects['stage']; floor.data.materials.clear(); floor.data.materials.append(wood('floor', tint=(.97, .93, .88, 1), rough=.5, scale=1.4))

# mannequin with its library animation
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, 'library', 'exercises.glb'))
rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
rig.animation_data_create()
rig.animation_data.action = bpy.data.actions[EX]
for o in bpy.context.scene.objects:                    # the library mouse prop is dark plastic; wood here
    if o.type == 'MESH' and 'plastic' in o.data.materials:
        o.data.materials[o.data.materials.find('plastic')] = dark
if rig.animation_data.action_slot is None and bpy.data.actions[EX].slots:
    rig.animation_data.action_slot = bpy.data.actions[EX].slots[0]
bpy.context.scene.frame_set(int(FRAME))

# camera: vertical 9:16, 3/4 view from the front-left, mid shot
# over the shoulder from behind-left: the screen and the figure both read
cam_rig, cam = clay.camera(target=(0, -.45, .92), dist=3.6, elev=14, azim=140, lens=45)

if LOOK == 'real':
    for L in clay.lights(scale=.6, sun=2.0, sun_soft=8):  # the kit lights a camera at the front; ours looks from behind
        L.location.rotate(Euler((0, 0, math.pi)))
        L.rotation_euler.z += math.pi
    clay.render_settings('CYCLES', res=(1080, 1920), samples=128, exposure=-.1)
else:                                   # soft studio: no sun, no cast shadow, ambient from all around
    clay.lights(scale=.6, sun=0.0)
    w = bpy.context.scene.world
    next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND').inputs['Strength'].default_value = 1.1
    clay.render_settings('EEVEE', res=(1080, 1920), samples=64)
    bpy.context.scene.eevee.use_shadows = False
clay.still(OUT)
print('OK', OUT)
