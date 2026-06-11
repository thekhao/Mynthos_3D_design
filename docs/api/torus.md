# torus

Create a torus centred at the origin in the XZ plane.

## Signature
```python
forge3d.torus(
    radius: float,
    tube_radius: float,
    segments: int = 48,
    tube_segments: int = 24,
    material: Material | None = None,
    name: str = "torus"
) -> Mesh
```

## Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `radius` | float | required | Distance from centre to tube centre, in metres. |
| `tube_radius` | float | required | Tube cross-section radius in metres. |
| `segments` | int | 48 | Divisions around the main ring. |
| `tube_segments` | int | 24 | Divisions around the tube cross-section. |

## Example
```python
ring = f3.torus(0.02, 0.004, material=f3.gold())
```
