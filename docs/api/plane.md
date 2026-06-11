# plane

Create a flat rectangle in the XZ plane, centred at the origin.

## Signature
```python
forge3d.plane(
    width: float,
    depth: float,
    material: Material | None = None,
    name: str = "plane"
) -> Mesh
```

## Example
```python
floor = f3.plane(2.0, 2.0, material=f3.marble())
```
