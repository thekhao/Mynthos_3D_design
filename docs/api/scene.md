# Scene

Container that groups meshes and exports them as a single GLB file.

## Signature
```python
class Scene:
    def __init__(self, name: str = "scene") -> None
    def add(self, *meshes: Mesh) -> Scene        # chainable
    def export(self, path: str) -> dict           # writes GLB, returns stats
    def preview(self, path: str) -> None          # writes 3-view PNG
```

## Export stats dict
```python
{
    "bytes": 258432,      # GLB file size in bytes
    "meshes": 3,          # number of mesh nodes
    "triangles": 1156,    # total triangle count
    "materials": 2        # unique material count
}
```

## Example
```python
scene = f3.Scene("product")
scene.add(body, lid, label)
stats = scene.export("out/product.glb")
scene.preview("out/product.png")
print(f"{stats['triangles']} tri, {stats['bytes']//1024} kB")
```
