# cone

Create a truncated cone (frustum) centred at the origin.

## Signature
```python
forge3d.cone(
    radius_bottom: float,
    radius_top: float,
    height: float,
    segments: int = 32,
    bevel: float = 0.0,
    material: Material | None = None,
    name: str = "cone"
) -> Mesh
```

## Notes
- Set `radius_top=0` for a true cone.
- Set both radii equal for a cylinder.

## Example
```python
funnel = f3.cone(0.1, 0.02, 0.15, material=f3.plastic((0.8, 0.1, 0.1)))
```
