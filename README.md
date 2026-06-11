# Forge3D

**Code-first 3D assets for the web.** Forge3D is a Python library + CLI that builds detailed, PBR-textured, web-ready 3D models (GLB) entirely from scripts — geometry, materials, procedural textures, lighting and an interactive viewer snippet included.

Where code-CAD tools (OpenSCAD, CadQuery, ForgeCAD) target machining and 3D printing, Forge3D targets **browsers**: colors, PBR materials, reflections and smooth organic shapes are first-class citizens, and the output is an optimized `.glb` you can drop into three.js in one line.

> Status: under active construction — core implemented and smoke-tested, examples/docs/CI landing commit by commit.

## Why Forge3D

| | OpenSCAD / CadQuery | Forge3D |
|---|---|---|
| Output | STL / STEP (no color) | Optimized GLB (web native) |
| Materials | none / preview-only | Full PBR + presets (gold, glass, clearcoat...) |
| Textures | none | Procedural (wood, marble, noise, scratches...) with color + normal + roughness maps |
| Reflections | none | Environment-ready, HDRI included |
| Target | CNC, printing | Browser games, product viewers, interactive scenes |

## Quickstart (zero dependencies beyond numpy + Pillow)

```bash
git clone https://github.com/thekhao/Mynthos_3D_design.git
cd Mynthos_3D_design
export PYTHONPATH=src
python -m forge3d build examples/01_wooden_crate.py --out out
python -m forge3d validate out/crate.glb
```

```python
import forge3d as f3

crate = f3.box(0.5, rounding=0.02, material=f3.wood("oak"))
scene = f3.Scene("demo")
scene.add(crate)
scene.export("crate.glb")    # web-ready binary glTF
scene.preview("crate.png")   # 3-angle render, no GPU needed
```

## Conventions (one choice, everywhere)

- Units: **meters**. Angles: **degrees**. Up axis: **+Y** (glTF convention).
- Colors: linear RGB in [0, 1]. One mesh = one material.
- All primitives are **centered at the origin** (`.place_on_ground()` to rest on y=0).
- Errors tell you **what** failed, **where**, and **how to fix it**.

See `DECISIONS.md` for the architecture log, `BENCHMARK.md` for research notes and measured performance, `TODO.md` for the live roadmap.
