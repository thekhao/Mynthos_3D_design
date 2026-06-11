# loft

Interpolate between a sequence of 2D cross-section rings to form a smooth solid.

## Signature
```python
forge3d.loft(
    rings: list[list[list[float]]],
    smooth: bool = True,
    material: Material | None = None,
    name: str = "loft"
) -> Mesh
```

## Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rings` | list of 2D profiles | required | Each ring is a list of [x, z] points. All rings must have the same point count. |
| `smooth` | bool | True | Smooth normals across rings. |

## Notes
Y positions are distributed evenly from 0 to 1 (relative), then scaled to bounding box.

## Example
```python
bot = f3.circle_profile(0.1)
mid = f3.circle_profile(0.06)
top = f3.circle_profile(0.03)
vase = f3.loft([bot, mid, top], material=f3.ceramic((0.9, 0.85, 0.8)))
```
