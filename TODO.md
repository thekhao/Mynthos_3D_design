# Forge3D TODO — v0.1.0

## Phase 0 — Research
- [x] glTF 2.0 / GLB binary format spec (header, chunks, accessors)
- [x] PBR metallic-roughness model
- [x] Procedural texture algorithms (Perlin noise, wood, marble)
- [x] Geometry algorithms (primitives, lathe, extrude, sweep, loft, bezier)
- [x] Competitor analysis (OpenSCAD, CadQuery) documented in BENCHMARK.md

## Phase 1 — API design
- [x] Dream scripts written (wooden crate, wristwatch, spaceship)
- [x] Full API surface defined
- [x] All 14 source modules stubbed

## Phase 2 — Core implementation
- [x] Primitives: box, sphere, cylinder, cone, torus, plane, capsule
- [x] Construction: lathe, extrude, sweep, loft
- [x] Curves: bezier, catmull_rom, circle_profile, rounded_rect_profile
- [x] Operations: merge, instances, linear_pattern, circular_pattern, mirror
- [x] Boolean approximation (subtract_cylinder helper)
- [x] Smooth normals (angle-weighted vertex normal averaging)
- [x] Materials: 13 PBR presets
- [x] Procedural textures: wood, marble, leather, checker, brushed_metal, gradient, noise
- [x] Normal map generation from heightmap
- [x] GLB binary writer (spec-compliant, indexed geometry)
- [x] PNG preview (matplotlib multi-view rasterizer)
- [x] CLI (forge3d build / preview / validate)
- [x] Validator (GLB structure + mesh + normals + render check)

## Phase 3 — Performance
- [x] Bench script written: bench/bench.py
- [x] 10/10 benchmarks PASS (SIMPLE <2s, COMPLEX <5s, all <2MB)

## Phase 4 — Tests
- [x] 34 unit tests written: tests/test_primitives.py
- [x] 34/34 tests PASS (stdlib unittest)
- [x] Built-in GLB validator

## Phase 5 — 10 example assets
- [x] 01 Wooden crate (258 kB, 1156 tri)
- [x] 02 Gold coin (17 kB, 512 tri)
- [x] 03 Ceramic mug (54 kB, 2076 tri)
- [x] 04 Desk lamp (197 kB, 6432 tri)
- [x] 05 Fantasy sword (350 kB, 4556 tri)
- [x] 06 Wristwatch (850 kB, 1944 tri)
- [x] 07 Stylised car (288 kB, 11936 tri)
- [x] 08 Spaceship (233 kB, 5000 tri)
- [x] 09 Trophy (272 kB, 3980 tri)
- [x] 10 Full scene (925 kB, 3758 tri)

## Phase 6 — GitHub + documentation
- [x] CI workflow (.github/workflows/ci.yml)
- [x] Viewer (viewer/index.html) with three.js vendored
- [x] Vendor files (three.module.min.js, three.core.min.js, all addons)
- [x] HDRI studio.hdr generated (131 kB, 256x128 RGBE)
- [x] docs/api/ (one page per function)
- [x] AGENTS.md
- [x] README.md (pitch, quickstart, benchmark table, comparison)
- [x] DECISIONS.md (20 architecture decisions)
- [x] BENCHMARK.md (measured results + research)
- [x] MIT license
- [x] All source commits pushed to GitHub
- [x] Vendor files pushed
- [x] Docs pushed
- [x] Tag v0.1.0

## Definition of Done
- [x] Offline install in one command
- [x] Full function catalogue implemented, tested, documented
- [x] 10 assets build, GLBs valid, PNG previews verified
- [x] All performance budgets met
- [x] Viewer loads all 10 assets with reflections
- [x] Test coverage > 80%, CI green
- [x] README + AGENTS.md + docs complete
- [x] Tag v0.1.0
