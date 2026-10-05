# Builds the wooden artist-mannequin (mesh + armature) and exports library/mannequin.glb + .blend
# Run:  blender -b -P library/build_mannequin.py
import bpy, bmesh, os
from math import radians
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)

# Joint positions in metres, Z up, figure faces -Y. Height 1.75 (8 heads of 0.22).
# ponytail: every bone is a short stub pointing up, so all rest rotations are identity and a pose is
# plain x/y/z angles in body axes. Re-orient bones along the limbs if Blender-side IK is ever needed.
J = {'hips': (0, 0, .95), 'spine': (0, 0, 1.06), 'neck': (0, 0, 1.47)}
PARENT = {'spine': 'hips', 'neck': 'spine'}
for S, sx in (('L', 1), ('R', -1)):
    J['arm' + S] = (sx * .205, 0, 1.42);  PARENT['arm' + S] = 'spine'
    J['elbow' + S] = (sx * .205, 0, 1.13); PARENT['elbow' + S] = 'arm' + S
    J['hand' + S] = (sx * .205, 0, .88);  PARENT['hand' + S] = 'elbow' + S
    J['leg' + S] = (sx * .09, 0, .90);    PARENT['leg' + S] = 'hips'
    J['knee' + S] = (sx * .09, 0, .48);   PARENT['knee' + S] = 'leg' + S
    J['foot' + S] = (sx * .09, 0, .08);   PARENT['foot' + S] = 'knee' + S
J['prop'] = (0, 0, 0)              # free bone carrying a computer mouse; hidden (scale 0) unless an exercise uses it
NAMES = list(J)

bm = bmesh.new()
dl = bm.verts.layers.deform.verify()
bm.loops.layers.uv.verify()
WOOD, JOINT, PLASTIC = 0, 1, 2

def finish(verts, bone, mat, loc):
    for v in verts:
        v.co += Vector(loc)
        v[dl][NAMES.index(bone)] = 1.0
    for f in {f for v in verts for f in v.link_faces}:
        f.material_index = mat; f.smooth = True

def ball(bone, loc, r, scale=(1, 1, 1), taper=0, mat=WOOD, tilt=0):
    """Ellipsoid. taper>0 = wider at the top, <0 = wider at the bottom. tilt<0 swings the bottom forward."""
    verts = bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=18, radius=1, calc_uvs=True)['verts']
    rot = Matrix.Rotation(radians(tilt), 3, 'X')
    for v in verts:
        f = 1 + taper * v.co.z
        v.co = rot @ Vector((v.co.x * f * r * scale[0], v.co.y * f * r * scale[1], v.co.z * r * scale[2]))
    finish(verts, bone, mat, loc)

def limb(bone, top, bottom, r_top, r_bottom):
    """Tapered cylinder between two joint centres."""
    top, bottom = Vector(top), Vector(bottom)
    verts = bmesh.ops.create_cone(bm, cap_ends=True, calc_uvs=True, segments=24, radius1=r_bottom, radius2=r_top,
                                  depth=(top - bottom).length)['verts']
    finish(verts, bone, WOOD, (top + bottom) / 2)

ball('hips', (0, 0, .955), .1, (1.35, .9, 1.0), taper=.28)             # pelvis, narrows to the crotch
ball('spine', J['spine'], .062, mat=JOINT)                              # waist ball
ball('spine', (0, 0, 1.285), .2, (.86, .52, 1.0), taper=.3)            # chest, wide at the shoulders
ball('neck', J['neck'], .04, mat=JOINT)
limb('neck', (0, 0, 1.56), (0, 0, 1.45), .03, .034)
ball('neck', (0, -.012, 1.638), .114, (.7, .84, 1.0), taper=.3, tilt=-24)  # egg head, chin forward, top at 1.75
for S, sx in (('L', 1), ('R', -1)):
    x = sx * .205
    ball('arm' + S, J['arm' + S], .046, mat=JOINT)
    limb('arm' + S, (x, 0, 1.40), (x, 0, 1.15), .04, .03)
    ball('elbow' + S, J['elbow' + S], .034, mat=JOINT)
    limb('elbow' + S, (x, 0, 1.11), (x, 0, .90), .031, .023)
    ball('hand' + S, J['hand' + S], .026, mat=JOINT)
    ball('hand' + S, (x, 0, .795), .075, (.5, .22, 1.0), taper=.25)   # mitten hand, tip at 0.72
    x = sx * .09
    ball('leg' + S, J['leg' + S], .06, mat=JOINT)
    limb('leg' + S, (x, 0, .88), (x, 0, .50), .06, .044)
    ball('knee' + S, J['knee' + S], .047, mat=JOINT)
    limb('knee' + S, (x, 0, .46), (x, 0, .10), .043, .03)
    ball('foot' + S, J['foot' + S], .034, mat=JOINT)
    ball('foot' + S, (x, -.065, .034), .034, (1.25, 3.4, 1.0), taper=-.2)  # foot, sole on z=0

ball('prop', (0, 0, .02), .02, (1.6, 3.0, 1.0), mat=PLASTIC)   # computer mouse, bottom on the bone head

mesh = bpy.data.meshes.new('mannequin'); bm.to_mesh(mesh); bm.free()
body = bpy.data.objects.new('mannequin', mesh)
bpy.context.scene.collection.objects.link(body)
for n in NAMES: body.vertex_groups.new(name=n)
wood_img = bpy.data.images.load(os.path.join(HERE, 'wood.png'))   # from make_wood.py: light natural maple
for name, rough in (('wood', .5), ('wood_joint', .42), ('plastic', .35)):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    if name == 'plastic':
        b.inputs['Base Color'].default_value = (.06, .06, .07, 1)
    else:
        tex = m.node_tree.nodes.new('ShaderNodeTexImage'); tex.image = wood_img
        m.node_tree.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    mesh.materials.append(m)

arm = bpy.data.objects.new('rig', bpy.data.armatures.new('rig'))
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
for n in NAMES:
    b = arm.data.edit_bones.new(n)
    b.head = J[n]; b.tail = Vector(J[n]) + Vector((0, 0, .06)); b.roll = 0
    if n in PARENT: b.parent = arm.data.edit_bones[PARENT[n]]
bpy.ops.object.mode_set(mode='OBJECT')
body.parent = arm
body.modifiers.new('rig', 'ARMATURE').object = arm

prop = body.vertex_groups['prop'].index
zs = [v.co.z for v in mesh.vertices if not any(e.group == prop for e in v.groups)]
assert abs(min(zs)) < .002 and abs(max(zs) - 1.75) < .01, (min(zs), max(zs))   # sole on floor, 1.75 tall

bpy.ops.file.pack_all()                      # the wood texture travels inside the .blend
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'mannequin.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(HERE, 'mannequin.glb'), export_format='GLB',
                          export_animations=False, export_image_format='JPEG', export_jpeg_quality=88)
print('OK height', round(max(zs) - min(zs), 3))
