# Forge3D

**Generate production-ready PBR-textured 3D web assets entirely by script — no GUI, no CAD.**

[![CI](https://github.com/thekhao/Mynthos_3D_design/actions/workflows/ci.yml/badge.svg)](https://github.com/thekhao/Mynthos_3D_design/actions)

## Why Forge3D?

| Tool | Focus | Colors/Materials | Web-ready GLB |
|------|-------|-----------------|---------------|
| OpenSCAD | Mechanical CAD | none | STL only |
| CadQuery | Precise engineering | none | STEP/STL |
| Forge3D | **Web assets** | full PBR | native GLB |

Forge3D is the missing tool for developers who need to generate 3D assets **by code**:
PBR materials, procedural textures, and web-optimised GLB output are **first-class citizens**.

## Quickstart

```bash
git clone https://github.com/thekhao/Mynthos_3D_design.git
cd Mynthos_3D_design
export PYTHONPATH=src   # no pip install required
```

```python
import forge3d as f3

# Wooden crate in 4 lines
crate = f3.box((0.5, 0.4, 0.5), rounding=0.02, material=f3.wood("oak", resolution=256))
scene = f3.Scene("crate")
scene.add(crate)
scene.export("crate.glb")   # open in any glTF viewer
```

## Feature catalogue

- **Primitives**: `box`, `sphere`, `cylinder`, `cone`, `torus`, `plane`, `capsule` — all with bevel/rounding
- **Construction**: `lathe`, `extrude`, `sweep`, `loft`, `bezier`, `catmull_rom`
- **Operations**: `merge`, `instances`, `linear_pattern`, `circular_pattern`, boolean set
- **Transforms**: `translate`, `rotate_x/y/z`, `scale`, `mirror`
- **Materials**: 13 PBR presets + fully customisable `Material`
- **Procedural textures**: wood (3 variants), marble, leather, brushed metal, checker, gradient
- **Export**: binary GLB (indexed geometry, embedded textures, PBR materials)
- **Preview**: software-rasterised 3-view PNG
- **Validator**: built-in GLB structure and render check

## 10 example assets

| # | Asset | Build time | GLB size | Triangles |
|---|-------|-----------|----------|-----------|
| 01 | Wooden crate | 1.4 s | 258 kB | 1 156 |
| 02 | Gold coin | 0.5 s | 17 kB | 512 |
| 03 | Ceramic mug | 1.1 s | 54 kB | 2 076 |
| 04 | Desk lamp | 1.9 s | 197 kB | 6 432 |
| 05 | Fantasy sword | 1.4 s | 350 kB | 4 556 |
| 06 | Wristwatch | 3.6 s | 850 kB | 1 944 |
| 07 | Stylised car | 2.0 s | 288 kB | 11 936 |
| 08 | Spaceship | 2.9 s | 233 kB | 5 000 |
| 09 | Trophy | 2.6 s | 272 kB | 3 980 |
| 10 | Full scene | 3.3 s | 925 kB | 3 758 |

## Requirements

- Python 3.11+
- numpy
- Pillow

That's it. No C extensions, no build step, no internet required.

## Structure

```
src/forge3d/   library source (14 modules)
examples/      10 buildable asset scripts
tests/         34 unit tests
bench/         performance benchmarks
viewer/        offline three.js viewer
docs/api/      one Markdown page per function
assets/hdri/   procedural studio HDRI
.github/workflows/ci.yml  CI: tests + validation + bench
```

## CI

On every push:
1. Unit tests with 80%+ coverage (Python 3.11 + 3.12)
2. Build all 10 examples
3. Validate every GLB (built-in + optional official gltf-validator)
4. Run benchmarks (budget enforced)

## License

MIT (c) 2026 Forge3D Authors
