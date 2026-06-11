# Forge3D — Benchmark & Auto-Evaluation

## Build performance (measured, v0.1.0)

| Asset | Script | Build time | GLB size | Meshes | Triangles |
|-------|--------|-----------|----------|--------|-----------|
| 01 Wooden crate | examples/01_wooden_crate.py | 1.4 s | 258 kB | 3 | 1 156 |
| 02 Gold coin | examples/02_gold_coin.py | 0.5 s | 17 kB | 1 | 512 |
| 03 Ceramic mug | examples/03_ceramic_mug.py | 1.1 s | 54 kB | 2 | 2 076 |
| 04 Desk lamp | examples/04_desk_lamp.py | 1.9 s | 197 kB | 5 | 6 432 |
| 05 Fantasy sword | examples/05_sword.py | 1.4 s | 350 kB | 4 | 4 556 |
| 06 Wristwatch | examples/06_wristwatch.py | 3.6 s | 850 kB | 6 | 1 944 |
| 07 Stylised car | examples/07_stylized_car.py | 2.0 s | 288 kB | 9 | 11 936 |
| 08 Spaceship | examples/08_spaceship.py | 2.9 s | 233 kB | 5 | 5 000 |
| 09 Trophy | examples/09_trophy.py | 2.6 s | 272 kB | 5 | 3 980 |
| 10 Full scene | examples/10_full_scene.py | 3.3 s | 925 kB | 6 | 3 758 |

## Budgets (enforced by CI)

| Budget | Limit | Status |
|--------|-------|--------|
| Simple asset build | < 2 s | PASS |
| Complex asset build | < 5 s | PASS |
| GLB file size | < 2 MB | PASS |

All 10/10 benchmarks PASS.

## glTF 2.0 spec compliance
- Indexed geometry: YES (UNSIGNED_SHORT for <65536 verts, UNSIGNED_INT otherwise)
- Binary chunk alignment: YES (4-byte aligned, zero-padded)
- Accessor byte offsets: YES (4-byte aligned)
- PBR metallic-roughness: YES (all material parameters)
- Normal maps (glTF Y+ convention): YES
- No required extensions: YES (no KHR_draco, no KHR_meshopt)

## Research summary (Phase 0)

### glTF 2.0 binary format
GLB = 12-byte header (magic 0x46546C67, version 2, total length) + JSON chunk + BIN chunk.
JSON chunk: scene graph, meshes, materials, accessors, bufferViews, textures.
BIN chunk: raw binary float32/uint16 geometry + RGBA texture data.
All accessors must be 4-byte aligned. BufferViews carry byteOffset + byteLength.

### PBR metallic-roughness model
`pbrMetallicRoughness.baseColorFactor` = [R,G,B,A] linear
`metallicFactor` = 0 (dielectric) to 1 (metal)
`roughnessFactor` = 0 (mirror) to 1 (matte)
`emissiveFactor` + `KHR_materials_emissive_strength` for neon effects
`KHR_materials_transmission` + `KHR_materials_ior` for glass
`KHR_materials_clearcoat` for car paint

### Procedural textures
All textures generated as 256x256 (configurable) RGBA images using numpy.
Wood: 2-octave Perlin-like noise warped along Y axis.
Marble: sin(x + turbulence) with greyscale gradient.
Brushed metal: anisotropic Gaussian noise along U axis.
Normal maps: finite difference of heightmap XY deltas to [128+dx, 128+dy, 255] RGB.

### Positioning vs OpenSCAD/CadQuery
OpenSCAD: CSG tree, STL export, no color, no UV, no PBR. Perfect for mechanical parts.
CadQuery: BREP/STEP, no texture support, engineering focus.
Forge3D: triangle meshes, GLB/glTF 2.0, full PBR, procedural textures, web-native.

## Visual quality auto-evaluation

- Normals: correct on all primitives (verified by render_mean check in validator)
- UVs: cylindrical/spherical/planar depending on primitive; 0-1 range, no overlap
- Textures: embedded as PNG in GLB (lossless), readable by three.js and Babylon.js
- Viewer test: all 10 GLBs load in viewer/index.html with correct lighting

## Known limits (roadmap v0.2)

1. No Draco/meshopt compression (add KHR_meshopt for 50% size reduction)
2. Booleans are assembly-only (add proper BSP for complex subtractions)
3. PNG textures (add JPEG fallback for <2MB colormaps)
4. No animation support (add TRS keyframes + morph targets)
5. No instanced rendering for repeated objects (add EXT_mesh_gpu_instancing)
6. Normal map strength is fixed (expose normalScale parameter)
7. HDRI resolution 256x128 (add 1k/2k option with tone-mapping)
