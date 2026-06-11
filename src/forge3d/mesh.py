"""Core indexed triangle mesh + transformations.

Conventions (whole library):
- Units: meters. Angles: degrees. Axes: glTF convention, +Y up, right-handed.
- Triangles are counter-clockwise when seen from outside.
- A Mesh holds exactly one Material; multi-material objects are Scenes/Groups
  of several meshes (this maps 1:1 to glTF primitives and keeps exports clean).
"""
from __future__ import annotations

import math
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

from .materials import Material


class MeshError(ValueError):
    """Raised on invalid mesh operations, with a fix hint."""


def _as_f32(a, shape_last, what: str) -> np.ndarray:
    arr = np.asarray(a, dtype=np.float32)
    if arr.ndim != 2 or arr.shape[1] != shape_last:
        raise MeshError(
            f"{what} must be an (N, {shape_last}) array, got shape {arr.shape}. "
            f"Fix: reshape your data to rows of {shape_last} floats."
        )
    return arr


def rotation_matrix(axis, angle_deg: float) -> np.ndarray:
    """4x4 rotation matrix. axis: 'x'|'y'|'z' or a 3-vector. angle in degrees."""
    if isinstance(axis, str):
        u = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}.get(axis.lower())
        if u is None:
            raise MeshError(f"rotation axis {axis!r} invalid. Fix: use 'x', 'y', 'z' or a 3-vector.")
        u = np.array(u, dtype=np.float64)
    else:
        u = np.asarray(axis, dtype=np.float64)
        n = np.linalg.norm(u)
        if n == 0:
            raise MeshError("rotation axis is the zero vector. Fix: pass a non-zero 3-vector.")
        u = u / n
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    x, y, z = u
    R = np.array([
        [c + x*x*(1-c), x*y*(1-c) - z*s, x*z*(1-c) + y*s, 0],
        [y*x*(1-c) + z*s, c + y*y*(1-c), y*z*(1-c) - x*s, 0],
        [z*x*(1-c) - y*s, z*y*(1-c) + x*s, c + z*z*(1-c), 0],
        [0, 0, 0, 1],
    ], dtype=np.float64)
    return R


def translation_matrix(offset) -> np.ndarray:
    M = np.eye(4)
    M[:3, 3] = np.asarray(offset, dtype=np.float64)
    return M


def scale_matrix(factors) -> np.ndarray:
    f = np.asarray(factors, dtype=np.float64)
    if f.ndim == 0:
        f = np.array([f, f, f])
    M = np.eye(4)
    M[0, 0], M[1, 1], M[2, 2] = f
    return M


class Mesh:
    """Indexed triangle mesh with positions, normals, UVs and one material."""

    def __init__(self, positions, normals, uvs, indices,
                 material=None, name: str = "mesh"):
        self.positions = _as_f32(positions, 3, f"Mesh '{name}' positions")
        self.normals = _as_f32(normals, 3, f"Mesh '{name}' normals")
        self.uvs = _as_f32(uvs, 2, f"Mesh '{name}' uvs")
        idx = np.asarray(indices, dtype=np.uint32)
        if idx.ndim != 2 or idx.shape[1] != 3:
            raise MeshError(
                f"Mesh '{name}' indices must be (M, 3), got {idx.shape}.")
        self.indices = idx
        n = len(self.positions)
        if len(self.normals) != n or len(self.uvs) != n:
            raise MeshError(
                f"Mesh '{name}': positions/normals/uvs must have same length.")
        if idx.size and idx.max() >= n:
            raise MeshError(
                f"Mesh '{name}': index {idx.max()} out of range ({n} vertices).")
        self.material = material if material is not None else Material()
        self.name = name

    @property
    def triangle_count(self): return len(self.indices)
    @property
    def vertex_count(self): return len(self.positions)

    def bounds(self):
        if not len(self.positions):
            z = np.zeros(3, dtype=np.float32); return z, z
        return self.positions.min(axis=0), self.positions.max(axis=0)

    def volume(self) -> float:
        p = self.positions.astype(np.float64)
        a, b, c = (p[self.indices[:, i]] for i in range(3))
        return float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)

    def surface_area(self) -> float:
        p = self.positions.astype(np.float64)
        a, b, c = (p[self.indices[:, i]] for i in range(3))
        return float(0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1).sum())

    def copy(self):
        return Mesh(self.positions.copy(), self.normals.copy(),
                    self.uvs.copy(), self.indices.copy(), self.material, self.name)

    def apply_matrix(self, M):
        M = np.asarray(M, dtype=np.float64)
        p = self.positions.astype(np.float64)
        self.positions = ((p @ M[:3, :3].T) + M[:3, 3]).astype(np.float32)
        NM = np.linalg.inv(M[:3, :3]).T
        nrm = self.normals.astype(np.float64) @ NM.T
        ln = np.linalg.norm(nrm, axis=1, keepdims=True); ln[ln == 0] = 1.0
        self.normals = (nrm / ln).astype(np.float32)
        if np.linalg.det(M[:3, :3]) < 0:
            self.indices = self.indices[:, ::-1].copy()
        return self

    def translate(self, x=0.0, y=0.0, z=0.0):
        self.positions = self.positions + np.array([x, y, z], dtype=np.float32)
        return self

    def rotate(self, axis, angle_deg: float, pivot=(0.0, 0.0, 0.0)):
        T1 = translation_matrix(-np.asarray(pivot, dtype=np.float64))
        T2 = translation_matrix(pivot)
        return self.apply_matrix(T2 @ rotation_matrix(axis, angle_deg) @ T1)

    def rotate_x(self, a): return self.rotate("x", a)
    def rotate_y(self, a): return self.rotate("y", a)
    def rotate_z(self, a): return self.rotate("z", a)

    def scale(self, factors):
        return self.apply_matrix(scale_matrix(factors))

    def mirror(self, axis: str = "x"):
        f = {"x": (-1,1,1), "y": (1,-1,1), "z": (1,1,-1)}.get(axis.lower())
        if f is None:
            raise MeshError(f"mirror axis {axis!r} invalid. Fix: use 'x', 'y' or 'z'.")
        return self.apply_matrix(scale_matrix(f))

    def center(self, x=True, y=True, z=True):
        lo, hi = self.bounds()
        c = (lo + hi) / 2
        self.translate(-c[0] if x else 0, -c[1] if y else 0, -c[2] if z else 0)
        return self

    def place_on_ground(self, ground_y: float = 0.0):
        lo, _ = self.bounds()
        return self.translate(0, ground_y - float(lo[1]), 0)

    def flip(self):
        self.indices = self.indices[:, ::-1].copy()
        self.normals = -self.normals
        return self

    def set_material(self, material):
        self.material = material; return self

    def face_normals(self) -> np.ndarray:
        p = self.positions.astype(np.float64)
        a, b, c = (p[self.indices[:, i]] for i in range(3))
        fn = np.cross(b - a, c - a)
        ln = np.linalg.norm(fn, axis=1, keepdims=True); ln[ln == 0] = 1.0
        return fn / ln

    def compute_flat_normals(self):
        fn = self.face_normals().astype(np.float32)
        idx = self.indices.reshape(-1)
        self.positions = self.positions[idx]
        self.uvs = self.uvs[idx]
        self.normals = np.repeat(fn, 3, axis=0)
        self.indices = np.arange(len(idx), dtype=np.uint32).reshape(-1, 3)
        return self

    def compute_smooth_normals(self, angle_deg: float = 180.0):
        p = self.positions.astype(np.float64)
        a, b, c = (p[self.indices[:, i]] for i in range(3))
        fn = np.cross(b - a, c - a)
        unit = fn / np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-20)
        pos_q = np.round(p[self.indices.reshape(-1)] * 1e5).astype(np.int64)
        if angle_deg >= 179.0:
            keys = pos_q
        else:
            cell = max(2, int(round(180.0 / max(angle_deg, 1.0))))
            n_q = np.floor((np.repeat(unit, 3, axis=0) * 0.5 + 0.5) * cell).astype(np.int64)
            keys = np.concatenate([pos_q, n_q], axis=1)
        uniq, inv = np.unique(keys, axis=0, return_inverse=True)
        acc = np.zeros((len(uniq), 3), dtype=np.float64)
        np.add.at(acc, inv, np.repeat(fn, 3, axis=0))
        ln = np.maximum(np.linalg.norm(acc, axis=1, keepdims=True), 1e-20)
        acc /= ln
        idx = self.indices.reshape(-1)
        self.positions = self.positions[idx]
        self.uvs = self.uvs[idx]
        self.normals = acc[inv].astype(np.float32)
        self.indices = np.arange(len(idx), dtype=np.uint32).reshape(-1, 3)
        return self.weld()

    def weld(self, tolerance: float = 1e-6):
        q = 1.0 / max(tolerance, 1e-12)
        key = np.concatenate([
            np.round(self.positions * q),
            np.round(self.normals * 1e3),
            np.round(self.uvs * 1e4),
        ], axis=1)
        uniq, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
        self.positions = self.positions[first]
        self.normals = self.normals[first]
        self.uvs = self.uvs[first]
        self.indices = inv[self.indices.reshape(-1)].astype(np.uint32).reshape(-1, 3)
        i = self.indices
        keep = (i[:,0] != i[:,1]) & (i[:,1] != i[:,2]) & (i[:,0] != i[:,2])
        self.indices = i[keep]
        return self

    def linear_pattern(self, count: int, offset):
        if count < 1:
            raise MeshError(f"linear_pattern count must be >= 1, got {count}.")
        off = np.asarray(offset, dtype=np.float32)
        copies = []
        for k in range(count):
            m = self.copy(); m.positions = m.positions + off * k; copies.append(m)
        return merge(copies, name=f"{self.name} x{count}", material=self.material)

    def circular_pattern(self, count: int, axis: str = "y",
                         start_angle: float = 0.0, end_angle: float = 360.0,
                         pivot=(0.0, 0.0, 0.0)):
        if count < 1:
            raise MeshError(f"circular_pattern count must be >= 1.")
        span = end_angle - start_angle
        full = abs(span % 360.0) < 1e-9
        steps = count if full else max(count - 1, 1)
        copies = []
        for k in range(count):
            ang = start_angle + span * k / steps
            copies.append(self.copy().rotate(axis, ang, pivot=pivot))
        return merge(copies, name=f"{self.name} circ x{count}", material=self.material)

    def grid_pattern(self, counts=(2,1,2), spacing=(0.1,0.1,0.1)):
        nx, ny, nz = (int(c) for c in counts)
        sx, sy, sz = spacing
        copies = []
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    m = self.copy()
                    m.positions = m.positions + np.array([i*sx, j*sy, k*sz], dtype=np.float32)
                    copies.append(m)
        return merge(copies, name=f"{self.name} grid", material=self.material)


def merge(meshes, name: str = "merged", material=None):
    ms = list(meshes)
    if not ms:
        raise MeshError("merge() needs at least one mesh.")
    offsets = np.cumsum([0] + [m.vertex_count for m in ms[:-1]])
    positions = np.concatenate([m.positions for m in ms])
    normals = np.concatenate([m.normals for m in ms])
    uvs = np.concatenate([m.uvs for m in ms])
    indices = np.concatenate([m.indices + np.uint32(o) for m, o in zip(ms, offsets)])
    return Mesh(positions, normals, uvs, indices,
                material=material or ms[0].material, name=name)


def grid_mesh(P, N, UV, wrap_u=False, wrap_v=False,
              material=None, name="grid", flip=False):
    rows, cols = P.shape[0], P.shape[1]
    quads_v = rows if wrap_v else rows - 1
    quads_u = cols if wrap_u else cols - 1
    r = np.arange(quads_v); c = np.arange(quads_u)
    rr, cc = np.meshgrid(r, c, indexing="ij")
    r1 = (rr + 1) % rows; c1 = (cc + 1) % cols
    i00 = (rr*cols + cc).ravel(); i01 = (rr*cols + c1).ravel()
    i10 = (r1*cols + cc).ravel(); i11 = (r1*cols + c1).ravel()
    t1 = np.stack([i00, i10, i11], axis=1)
    t2 = np.stack([i00, i11, i01], axis=1)
    tris = np.concatenate([t1, t2]).astype(np.uint32)
    pf = P.reshape(-1, 3).astype(np.float64)
    nf = N.reshape(-1, 3).astype(np.float64)
    a, b, c = pf[tris[:,0]], pf[tris[:,1]], pf[tris[:,2]]
    face_n = np.cross(b - a, c - a)
    vote = np.sum(face_n * (nf[tris[:,0]] + nf[tris[:,1]] + nf[tris[:,2]]))
    if vote < 0:
        tris = tris[:, ::-1].copy()
    if flip:
        tris = tris[:, ::-1].copy()
    return Mesh(P.reshape(-1, 3), N.reshape(-1, 3), UV.reshape(-1, 2), tris,
                material=material, name=name)
