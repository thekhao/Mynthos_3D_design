"""Scene-graph traversal shared by the GLB exporter and the preview renderer."""
from __future__ import annotations
import numpy as np


def iter_instances(obj, parent=None):
    """Yield (mesh, world_matrix_4x4) for every mesh instance under obj."""
    from .mesh import Mesh
    if parent is None:
        parent = np.eye(4)
    if isinstance(obj, Mesh):
        yield obj, parent
        return
    if hasattr(obj, "roots"):
        for r in obj.roots:
            yield from iter_instances(r, parent)
        return
    M = parent
    if hasattr(obj, "local_matrix"):
        M = parent @ obj.local_matrix()
    if getattr(obj, "mesh", None) is not None:
        yield obj.mesh, M
    for ch in getattr(obj, "children", []) or []:
        yield from iter_instances(ch, M)


def scene_bounds(obj):
    """(min_xyz, max_xyz) over all mesh instances."""
    lo = np.full(3, np.inf)
    hi = np.full(3, -np.inf)
    for mesh, M in iter_instances(obj):
        if not len(mesh.positions):
            continue
        p = mesh.positions.astype(np.float64) @ M[:3, :3].T + M[:3, 3]
        lo = np.minimum(lo, p.min(axis=0))
        hi = np.maximum(hi, p.max(axis=0))
    if not np.all(np.isfinite(lo)):
        lo = np.zeros(3); hi = np.zeros(3)
    return lo, hi
