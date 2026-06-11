# box

Create a rectangular box centred at the origin.

## Signature
```python
forge3d.box(
    size: tuple[float,float,float] | float,
    rounding: float = 0.0,
    segments: int = 1,
    material: Material | None = None,
    name: str = "box"
) -> Mesh
```

## Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `size` | tuple(w,h,d) or float | required | Width, height, depth in metres. Single float = cube. |
| `rounding` | float | 0.0 | Edge bevel radius in metres. |
| `segments` | int | 1 | Face subdivisions. |
| `material` | Material | None | PBR material. |
| `name` | str | "box" | GLB scene node name. |

## Example
```python
import forge3d as f3
crate = f3.box((0.5, 0.4, 0.5), rounding=0.02, material=f3.wood("oak"))
scene = f3.Scene("s")
scene.add(crate)
scene.export("crate.glb")
```
