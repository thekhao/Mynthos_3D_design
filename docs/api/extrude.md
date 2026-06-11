# extrude

Extrude a closed 2D profile along the Y axis.

## Signature
```python
forge3d.extrude(
    profile: list[list[float]],
    height: float,
    bevel: float = 0.0,
    cap: bool = True,
    material: Material | None = None,
    name: str = "extrude"
) -> Mesh
```

## Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `profile` | list of [x, z] | required | Closed 2D profile in metres (XZ plane). |
| `height` | float | required | Extrusion height along Y in metres. |
| `bevel` | float | 0.0 | Edge bevel radius at top and bottom. |

## Example
```python
profile = f3.rounded_rect_profile(0.06, 0.06, radius=0.008)
gem = f3.extrude(profile, height=0.02, bevel=0.003, material=f3.glass())
```
