# capsule

Create a capsule (cylinder with hemispherical caps) centred at the origin.

## Signature
```python
forge3d.capsule(
    radius: float,
    height: float,
    segments: int = 32,
    rings: int = 16,
    material: Material | None = None,
    name: str = "capsule"
) -> Mesh
```

## Notes
`height` is the total height including the two hemispherical caps.
The cylindrical mid-section height = `height - 2 * radius`.

## Example
```python
body = f3.capsule(0.04, 0.18, material=f3.rubber())
```
