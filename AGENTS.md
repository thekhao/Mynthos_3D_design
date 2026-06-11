# AGENTS.md — Forge3D Quick-Start for AI Agents

Forge3D is a zero-dependency Python library (numpy + Pillow only) for generating
PBR-textured 3D assets as GLB files, ready to load in any web browser.

## Clone and install
```bash
git clone https://github.com/thekhao/Mynthos_3D_design.git forge3d
cd forge3d
# no pip install needed — add src/ to PYTHONPATH
export PYTHONPATH=src
```

## Your first asset (2 minutes)
```python
import forge3d as f3

# Gold coin
profile = [[0.0,0.0],[0.03,0.0],[0.03,0.004],[0.0,0.002]]
coin = f3.lathe(profile, segments=64, material=f3.gold())

scene = f3.Scene("my_coin")
scene.add(coin)
stats = scene.export("coin.glb")
scene.preview("coin.png")
print(stats)  # => {'bytes': ..., 'meshes': 1, 'triangles': ...}
```

## API surface

### Primitives
```python
f3.box(size, rounding=0.0, material=None, name="box")
f3.sphere(radius, segments=32, rings=16, material=None)
f3.cylinder(radius, height, segments=32, bevel=0.0, material=None)
f3.cone(radius_bottom, radius_top, height, segments=32, bevel=0.0, material=None)
f3.torus(radius, tube_radius, segments=48, tube_segments=24, material=None)
f3.plane(width, depth, material=None)
f3.capsule(radius, height, segments=32, rings=16, material=None)
```

### Construction
```python
f3.lathe(profile_2d, segments=64, cap=True, material=None)
f3.extrude(profile_2d, height, bevel=0.0, cap=True, material=None)
f3.sweep(profile_2d, path_3d, cap=True, material=None)
f3.loft(rings_list, smooth=True, material=None)
f3.bezier(control_points, segments=32)  # returns 2D numpy array
f3.circle_profile(radius, segments=32)  # returns 2D numpy array
f3.rounded_rect_profile(w, h, radius, corner_segments=4)  # returns 2D numpy array
```

### Transforms (chainable)
```python
mesh.translate(x, y, z)
mesh.rotate_x(deg); mesh.rotate_y(deg); mesh.rotate_z(deg)
mesh.scale(factor_or_xyz)
mesh.mirror(axis)   # axis in ('x','y','z')
mesh.copy()         # deep copy
mesh.linear_pattern(count, offset_xyz)
mesh.circular_pattern(count, axis='y')
f3.merge([mesh1, mesh2, ...])
f3.instances(mesh, positions_list)
```

### Materials (all PBR metallic-roughness)
```python
f3.gold(); f3.chrome(); f3.brushed_metal(color=(0.7,0.7,0.7))
f3.plastic(color, glossy=True); f3.ceramic(color)
f3.rubber(); f3.glass(tint=(1,1,1), roughness=0.0)
f3.neon(color, strength=3.0)  # emissive
f3.car_paint(color)  # clearcoat
f3.wood(variant='oak', resolution=256)
f3.marble(resolution=256)
f3.leather(color=(0.4,0.2,0.1), resolution=256)
f3.checker_textures(resolution=256, tiles=8)
# Custom:
f3.Material(name, base_color=(r,g,b,a), metallic=0.0, roughness=0.5,
            emissive=(0,0,0), emissive_strength=1.0, transmission=0.0,
            ior=1.5, clearcoat=0.0, textures=None)
```

### Scene
```python
scene = f3.Scene("scene_name")
scene.add(mesh1, mesh2, ...)
stats = scene.export("output.glb")    # returns dict
scene.preview("output.png")            # 3-view PNG render
```

## Units
- All distances in **metres**
- All angles in **degrees**
- Colors in linear [0,1] range
- +Y up coordinate system

## Run tests
```bash
PYTHONPATH=src python -m unittest tests.test_primitives -v
```

## Run benchmarks
```bash
python bench/bench.py
```

## Build all 10 examples
```bash
mkdir -p out
for s in examples/*.py; do PYTHONPATH=src FORGE3D_OUT=out python $s; done
```

## Open the viewer (offline)
Open `viewer/index.html` in any browser that supports ES modules (Chrome, Firefox, Safari).
If you get CORS errors, serve with: `python -m http.server 8080`
