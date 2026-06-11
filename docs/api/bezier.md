# Curve utilities

Curve functions return numpy arrays for use as profiles or paths in `lathe`, `extrude`, `sweep`, `loft`.

## bezier
```python
forge3d.bezier(
    control_points: list[list[float]],  # Nx2 or Nx3
    segments: int = 32
) -> np.ndarray
```
Cubic Bezier (de Casteljau). Groups of 4 points = one cubic segment.

## catmull_rom
```python
forge3d.catmull_rom(
    points: list[list[float]],
    segments: int = 32
) -> np.ndarray
```
Catmull-Rom spline passing through all points.

## circle_profile
```python
forge3d.circle_profile(radius: float, segments: int = 32) -> np.ndarray  # (N, 2)
```

## rounded_rect_profile
```python
forge3d.rounded_rect_profile(
    w: float, h: float, radius: float, corner_segments: int = 4
) -> np.ndarray  # (N, 2)
```

## Example
```python
path = f3.bezier([[0,0.3,0],[0.05,0.25,0.05],[0.08,0.1,0]], segments=32)
profile = f3.circle_profile(0.01)
wire = f3.sweep(profile, path, material=f3.gold())
```
