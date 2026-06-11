# Materials

All material presets return a `Material` with glTF 2.0 PBR metallic-roughness parameters.

## Presets
```python
f3.gold()                              # metallic=1.0, roughness=0.1, gold tint
f3.chrome()                            # metallic=1.0, roughness=0.05, silver
f3.polished_metal(color=(0.8,0.8,0.8)) # metallic=1.0, roughness=0.08
f3.brushed_metal(color=(0.7,0.7,0.7))  # metallic=1.0, anisotropic roughness texture
f3.plastic(color, glossy=True)         # metallic=0.0, roughness=0.15 or 0.6
f3.ceramic(color=(0.95,0.92,0.88))     # metallic=0.0, roughness=0.2
f3.rubber()                            # metallic=0.0, roughness=0.9
f3.glass(tint=(1,1,1), roughness=0.0)  # transmission=1.0, ior=1.5
f3.neon(color, strength=3.0)           # emissive material
f3.car_paint(color)                    # clearcoat=1.0
f3.wood(variant='oak', resolution=256) # color+normal+roughness texture
f3.marble(resolution=256)              # color+normal+roughness texture
f3.leather(color=(0.4,0.2,0.1), resolution=256)
f3.checker_textures(resolution=256, tiles=8)
```

## Custom Material
```python
mat = f3.Material(
    name="custom",
    base_color=(0.8, 0.2, 0.1, 1.0),  # RGBA linear [0,1]
    metallic=0.0,
    roughness=0.4,
    emissive=(0.0, 0.0, 0.0),
    emissive_strength=1.0,
    transmission=0.0,
    ior=1.5,
    clearcoat=0.0,
    textures=None
)
```

## PBR parameter guide
| Parameter | 0.0 | 1.0 |
|-----------|-----|-----|
| `metallic` | dielectric (plastic/ceramic) | metal |
| `roughness` | mirror-smooth | fully diffuse |
| `transmission` | opaque | fully transparent |
| `clearcoat` | no coat | full lacquer |
