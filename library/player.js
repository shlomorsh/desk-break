// Shared by gallery.html and the desktop app: cameras, the chair prop and lights for the mannequin library.
// The page must map the bare specifier 'three' in an importmap.
import * as THREE from 'three';

// camera position, look-at target — per exercise "view" (see AUTHORING.md)
export const VIEWS = {
  full: [[1.6, 1.25, 4.6], [0, 0.92, 0]],
  head: [[0.5, 1.72, 1.45], [0, 1.58, 0]],
  upper: [[0.9, 1.45, 2.6], [0, 1.25, 0.1]],
  floor: [[2.3, 1.9, 2.7], [0, 0.25, 0]],
};

const wood = new THREE.TextureLoader().load(new URL('./wood.png', import.meta.url).href);
wood.colorSpace = THREE.SRGBColorSpace;
wood.wrapS = wood.wrapT = THREE.RepeatWrapping;
const propMat = new THREE.MeshStandardMaterial({ map: wood, color: 0xd9c7ad, roughness: .6 });

export function chair() {              // seat top at 0.45 (the "seated" height in build_library.py)
  const g = new THREE.Group();
  const box = (w, h, d, x, y, z) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), propMat); m.position.set(x, y, z); g.add(m); };
  box(.46, .04, .44, 0, .43, -.12); box(.46, .5, .04, 0, .7, -.34);
  for (const x of [-.2, .2]) for (const z of [-.31, .07]) box(.035, .41, .035, x, .205, z);
  return g;
}

export function lights(scene) {
  scene.add(new THREE.HemisphereLight(0xfff6ea, 0x8a7560, 1.9));
  const sun = new THREE.DirectionalLight(0xfff1dc, 2.1); sun.position.set(2, 3, 4); scene.add(sun);
}
