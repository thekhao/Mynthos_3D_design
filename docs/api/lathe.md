# lathe

Create a surface of revolution by rotating a 2D profile 360 degrees around the Y axis.

## Signature
```python
forge3d.lathe(
    profile: list[list[float]],
    segments: int = 64,
    cap: bool = True,
    material: Material | None = None,
    name: str = "lathe"
) -> Mesh
```

## Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `profile` | list of [r, y] | required | 2D profile in metres. r >= 0. |
| `segments` | int | 64 | Circumferential divisions. |
| `cap` | bool | True | Close open ends with flat disc caps. |

## Example
```python
profile = [[0, 0], [0.03, 0], [0.03, 0.004], [0, 0.002]]
coin = f3.lathe(profile, segments=64, material=f3.gold())
```
