# sphere

Create a UV sphere centred at the origin.

## Signature
```python
forge3d.sphere(
    radius: float,
    segments: int = 32,
    rings: int = 16,
    material: Material | None = None,
    name: str = "sphere"
) -> Mesh
```

## Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `radius` | float | required | Radius in metres. |
| `segments` | int | 32 | Longitudinal divisions (around equator). |
| `rings` | int | 16 | Latitudinal divisions. |
| `material` | Material | None | PBR material. |

## Example
```python
ball = f3.sphere(0.1, segments=64, material=f3.ceramic((1, 0.9, 0.8)))
```
