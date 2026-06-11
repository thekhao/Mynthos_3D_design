# sweep

Sweep a 2D cross-section along a 3D path.

## Signature
```python
forge3d.sweep(
    profile: list[list[float]],
    path: list[list[float]],
    cap: bool = True,
    material: Material | None = None,
    name: str = "sweep"
) -> Mesh
```

## Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `profile` | list of [x, y] | required | 2D cross-section in local frame. |
| `path` | list of [x, y, z] | required | 3D spine path in metres. |
| `cap` | bool | True | Close the two open ends. |

## Example
```python
path = f3.bezier([[0,0,0],[0.05,0.05,0],[0.1,0,0]], segments=24)
profile = f3.circle_profile(0.008)
handle = f3.sweep(profile, path, material=f3.ceramic((0.95, 0.9, 0.85)))
```
