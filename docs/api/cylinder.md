# cylinder

Create a cylinder centred at the origin along the Y axis.

## Signature
```python
forge3d.cylinder(
    radius: float,
    height: float,
    segments: int = 32,
    bevel: float = 0.0,
    material: Material | None = None,
    name: str = "cylinder"
) -> Mesh
```

## Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `radius` | float | required | Base/top radius in metres. |
| `height` | float | required | Total height in metres. |
| `segments` | int | 32 | Circumferential divisions. |
| `bevel` | float | 0.0 | Top and bottom edge bevel radius. |

## Example
```python
pillar = f3.cylinder(0.05, 1.2, bevel=0.005, material=f3.marble())
```
