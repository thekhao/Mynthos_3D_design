# Procedural Textures

Texture functions return a `Textures` object with PIL images for `color_map`, `normal_map`, and `roughness_map`. Embedded as PNG in the exported GLB.

## Functions
```python
f3.wood_textures(variant='oak', resolution=256)
# variant: 'oak' | 'pine' | 'dark'

f3.marble_textures(resolution=256)

f3.leather_textures(color=(0.4,0.2,0.1), resolution=256)

f3.checker_textures(resolution=256, tiles=8)

f3.brushed_metal_textures(color=(0.7,0.7,0.7), resolution=256)

f3.gradient_textures(color_a, color_b, resolution=256)

f3.noise_textures(scale=4.0, resolution=256)
```

## Usage with a custom material
```python
tex = f3.wood_textures('oak', resolution=512)
mat = f3.Material('oak_plank', base_color=(1,1,1,1), roughness=0.6, textures=tex)
crate = f3.box((0.5, 0.4, 0.5), material=mat)
```

## Notes
- Resolution must be a power of 2: 64, 128, 256, 512, 1024.
- Higher resolution = larger GLB. 256 is the default (good balance for web).
- Normal maps use the glTF Y+ convention (G channel = Y up).
