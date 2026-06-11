"""Scene graph: named groups, pivots, transforms, instancing, studio lighting.

Units: meters. Angles: degrees. +Y up.
"""
from __future__ import annotations
from typing import Optional, Sequence
import numpy as np
from .mesh import Mesh, MeshError, rotation_matrix, scale_matrix, translation_matrix


class Node:
    """Named transform node holding an optional Mesh, optional light, and children."""
    def __init__(self, mesh=None, name=None, children=None, light=None):
        self.mesh = mesh
        self.name = name or (mesh.name if mesh is not None else "node")
        self.children = list(children or [])
        self.matrix = np.eye(4)
        self.light = light

    def add(self, *objs):
        """Append children (Node or Mesh). Returns self."""
        for o in objs:
            if not isinstance(o, (Node, Mesh)):
                raise MeshError(f"Node.add expects Node or Mesh, got {type(o).__name__}.")
            self.children.append(o)
        return self

    def local_matrix(self): return self.matrix

    def translate(self, x=0., y=0., z=0.):
        self.matrix = translation_matrix((x, y, z)) @ self.matrix; return self

    def rotate(self, axis: str, angle_deg: float, pivot=None):
        R = rotation_matrix(axis, angle_deg)
        if pivot is not None:
            p = np.asarray(pivot, dtype=np.float64)
            R = translation_matrix(p) @ R @ translation_matrix(-p)
        self.matrix = R @ self.matrix; return self

    def scale(self, factor):
        if np.isscalar(factor): factor = (factor, factor, factor)
        self.matrix = scale_matrix(factor) @ self.matrix; return self

    def set_pivot_transform(self, matrix):
        M = np.asarray(matrix, dtype=np.float64)
        if M.shape != (4, 4):
            raise MeshError(f"set_pivot_transform expects 4x4, got {M.shape}.")
        self.matrix = M; return self


def group(name: str, *children) -> Node:
    """Named group node."""
    return Node(name=name, children=list(children))


def instances(mesh: Mesh, placements, name: str = "instances") -> Node:
    """Efficient GPU instancing: one Mesh shared, many placement nodes.
    placements: list of (x,y,z) or 4x4 matrices.
    """
    root = Node(name=name)
    for i, p in enumerate(placements):
        p = np.asarray(p, dtype=np.float64)
        child = Node(mesh=mesh, name=f"{name}_{i}")
        if p.shape == (4, 4): child.matrix = p
        elif p.shape == (3,): child.matrix = translation_matrix(p)
        else: raise MeshError(f"instances placement #{i}: expected (3,) or (4,4), got {p.shape}.")
        root.children.append(child)
    return root


def _aim_matrix(direction) -> np.ndarray:
    d = np.asarray(direction, dtype=np.float64)
    d /= max(np.linalg.norm(d), 1e-12)
    z = -d
    up = np.array([0.,1.,0.])
    if abs(np.dot(z, up)) > 0.999: up = np.array([1.,0.,0.])
    x = np.cross(up, z); x /= np.linalg.norm(x)
    y = np.cross(z, x)
    M = np.eye(4)
    M[:3,0], M[:3,1], M[:3,2] = x, y, z
    return M


def studio_lights(intensity: float = 1.0) -> Node:
    """3-point KHR_lights_punctual rig: warm key, cool fill, white rim."""
    rig = Node(name="studio_lights")
    for lname, direction, color, watts in [
        ("key", (-0.5,-0.8,-0.4), [1.0,0.96,0.9], 3.2),
        ("fill", (0.7,-0.3,-0.3), [0.85,0.9,1.0], 1.0),
        ("rim", (0.2,-0.4,0.9), [1.0,1.0,1.0], 1.6),
    ]:
        n = Node(name=f"light_{lname}", light={
            "type": "directional", "name": lname,
            "color": color, "intensity": round(watts*intensity, 3),
        })
        n.matrix = _aim_matrix(direction)
        rig.children.append(n)
    return rig


class Scene:
    """Root container. Call add(), then export() or preview()."""
    def __init__(self, name: str = "scene", lights: bool = True):
        self.name = name
        self.roots = []
        if lights: self.roots.append(studio_lights())

    def add(self, *objs):
        for o in objs:
            if not isinstance(o, (Node, Mesh)):
                raise MeshError(f"Scene.add expects Node or Mesh, got {type(o).__name__}.")
            self.roots.append(o)
        return self

    def export(self, path: str) -> dict:
        """Write optimized .glb. Returns stats."""
        from .gltf import export_glb
        return export_glb(self, path)

    def preview(self, path: str, size: int = 512,
                yaws=(30., 120., 250.), pitch: float = 18.) -> str:
        """3-angle PNG contact sheet."""
        from .render import preview
        return preview(self, path, size=size, yaws=yaws, pitch=pitch)
