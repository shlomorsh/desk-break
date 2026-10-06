# Writing exercises for the mannequin library

One category = one file: `library/exercises/<category-id>.json`. Blender turns every file into animations
(`build_library.py`); `gallery.html` shows them. Reference file with 42 checked exercises:
`exercises/neck-shoulders-arms.json` — read it first, copy its style.

## File shape

```json
{ "category": { "id": "back-spine", "he": "גב ועמוד שדרה", "en": "Back & spine" },
  "exercises": [
    { "id": "cat-cow-standing", "he": "חתול-פרה בעמידה", "en": "Standing cat-cow", "amount": "8 פעמים",
      "steps": ["...", "...", "..."], "beat": 1.2,
      "keys": [ {}, { "spine": [30, 0, 0], "hold": 1 } ] } ] }
```

- `id`: kebab-case English, unique. `he` / `en`: names. `amount`: short Hebrew ("10 פעמים", "30 שניות").
- `steps`: 2–4 short plain-Hebrew instructions, written for a beginner. A step starting with `!` is a caution
  (shown in orange), e.g. `"!אם הברך כואבת, יורדים רק חצי דרך."`.
- `beat`: seconds from one key to the next. `keys`: poses; the loop returns to key 0 by itself.

## Exercise options

| field | meaning |
|---|---|
| `"linear": true` | constant speed between keys (circles). Default eases in/out at every key. |
| `"once": true` | plays one time, no loop back (falls, a stage dive, dropping the mouse). |
| `"seated": true` | sits on a chair: pelvis bottom at 0.45 m, chair drawn by the gallery. |
| `"view"` | `"head"` close-up, `"upper"` chest-up, `"floor"` low side camera for floor work. Default full body. |
| `"bpm": 96` | the tempo a dance was written for. Use `beat = 60/bpm` (or 30/bpm for half-beats). |

## Key (pose) fields

Rotations are degrees `[x, y, z]` in the figure's own axes (x = towards its left, y = up, z = forward),
applied **y first (twist), then z (sideways), then x (forward/back)**. Every bone is identity at rest
(standing straight, arms down).

Bones: `hips` (root: rotates the WHOLE body), `spine` (one piece, waist to shoulders), `neck` (neck+head),
`armL/R`, `elbowL/R`, `handL/R`, `legL/R`, `kneeL/R`, `footL/R`.

- `"arm"`, `"leg"`, `"elbow"`, `"knee"`, `"hand"`, `"foot"` without L/R = both sides. Values for the right
  side are written exactly like the left; the builder mirrors them. `armL` / `armR` set one side.
- Rest pose added to every key: `arm [0,0,6]`, `elbow [-6,0,0]` (unless you set them).
- `"bone.pos": [x,y,z]` metres offset, e.g. `"arm.pos": [0, 0.05, 0]` = shrug (there is no collarbone).
  `"pos"` = whole body offset (x/z only matter; height is automatic).
- `"hold": s` stay on this key s extra seconds.
- `"lift": m` raise the body m metres above the floor (jumps, flips).
- `"prop": "handR"` the computer mouse is in the right hand; `"prop": [x, 0, z]` it lies on the floor there,
  `"propRot": [x,y,z]` its rotation; no `prop` on a key = mouse hidden.

**Grounding is automatic**: after posing, the whole body is moved up/down so its lowest point touches the
floor (or the pelvis sits on the chair when `seated`). Lying, kneeling and sitting on the floor just work —
pose the body, the floor finds it. **Contacts hold too**: a foot or hand that touches the floor stays where it
landed (the leg/arm bends to reach it) until the keys lift it, and parts resting on the floor (back, knees, the
seat) don't skid. So turning or tilting `hips` with the feet down moves the pelvis over planted feet, and a
`pos` shift is a weight shift, not a slide. A foot that the leg itself drags along the floor (a heel slide, a
leg sliding out) is let go and follows the keys.

## Directions that are verified (copy these)

| want | value |
|---|---|
| arm straight forward / overhead / back | `arm [-90,0,0]` / `[-170,0,8]` / `[40,0,0]` |
| arm out to the side (T) | `arm [0,0,88]` |
| W / goal-post (forearm up, elbow out) | `arm [0,90,88]` + `elbow [-90,0,0]` |
| arm across the chest | `arm [-90,0,-48]` |
| elbow bent 90 (forearm forward) | `elbow [-90,0,0]`; twist forearm `elbow [-90,±80,0]` |
| thigh forward (knee up) | `leg [-90,0,0]`, shin hangs: `knee [90,0,0]` (knee x>0 bends) |
| leg out to the side | `leg [0,0,30]` |
| bend forward / back / to the right / turn left | `spine [x>0]` / `[x<0]` / `[0,0,z>0]` / `[0,y>0,0]` |
| look down / turn head left / tilt to right ear | `neck [30,0,0]` / `[0,60,0]` / `[0,0,24]` |
| whole body: lie on the back (face up) | `hips [-90,0,0]` (+ `"view": "floor"`) |
| lie face down / on the left side | `hips [90,0,0]` / `hips [0,0,-90]` |
| sit on the floor, legs straight forward | `leg [-90,0,0]` (body stays upright, floor found automatically) |
| on hands and knees | `hips [90,0,0]`, `leg [-90,0,0]`, `knee [90,0,0]`, `arm [-90,0,0]`, `elbow [0,0,0]` |
| chair sitting (with `"seated": true`) | `leg [-90,0,4]`, `knee [90,0,0]` |
| feet: point toes / pull toes up | `foot [40,0,0]` / `foot [-30,0,0]` |

Careful: when a pose is rotated a lot (e.g. lying), arm/leg values are still relative to the body, not the
floor. Rotations between two keys take the short way round: keep each joint's change between neighbouring keys
under ~170° (a full flip = 4 keys of 90°).

## Check your work (always)

```
bash library/check.sh <category-id>
```

Builds only your file into `library/.check/<id>/` (~30 s) and photographs every exercise frozen on each of
its first four keys: `k0-*.png` … `k3-*.png` (an exercise with fewer keys repeats its last one; keys beyond 3
aren't photographed, so put the poses that matter early). Each `-0`, `-1`… is one screen of the gallery. Read the images and fix anything that looks wrong: limbs through the body,
feet sliding through the floor, a "squat" that looks like a fall, a pose that doesn't read as the exercise.
Repeat until it looks right. Do not edit `build_library.py`, `gallery.html`, `main.js` or the mannequin —
if you need something they can't do, say so in your report.
