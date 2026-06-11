# Export, Preview & Validate

## GLB export

`scene.export(path)` writes a spec-compliant GLB 2.0:
- **Header**: magic `0x46546C67`, version 2, total length (12 bytes)
- **JSON chunk**: scene graph, meshes, materials, accessors, bufferViews, textures, samplers
- **BIN chunk**: float32 positions/normals/UVs + uint16/uint32 indices + raw PNG texture bytes
- All accessors and bufferViews 4-byte aligned
- Indexed geometry throughout (UNSIGNED_SHORT < 65536 verts, else UNSIGNED_INT)
- Textures embedded as lossless PNG

## PNG preview

`scene.preview(path)` renders a 3-view orthographic PNG (front/side/top) using matplotlib.

## CLI
```bash
export PYTHONPATH=src

# Build a GLB:
python -m forge3d build examples/01_wooden_crate.py

# Preview only (no GLB written):
python -m forge3d preview examples/02_gold_coin.py

# Validate a GLB:
python -m forge3d validate out/01_wooden_crate.glb
```

## Built-in validator
```python
from forge3d.validate import validate_glb

result = validate_glb("out/01_wooden_crate.glb", render_check=True)
# Returns:
# {
#   'valid': True,
#   'triangles': 1156,
#   'meshes': 3,
#   'render_mean': 47.3   # mean pixel brightness; < 5 = likely black/broken
# }
```

## Viewer
Open `viewer/index.html` in any browser with ES module support.
For local files, serve with: `python -m http.server 8080`
