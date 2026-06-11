"""PBR materials (glTF 2.0 metallic-roughness) and ready-to-use presets.

Every parameter maps 1:1 to glTF 2.0 core or a ratified Khronos extension.

Conventions (used across all of Forge3D):
- Colors are linear-space RGB(A) floats in [0, 1].
- roughness: 0.0 = perfect mirror, 1.0 = fully diffuse. Default 0.6.
- metallic: 0.0 = dielectric, 1.0 = metal. Default 0.0.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from .textures import TextureSet


class MaterialError(ValueError):
    """Raised when a material parameter is out of range, with a fix hint."""


def _check01(name: str, value: float, material: str) -> None:
    if not (0.0 <= float(value) <= 1.0):
        raise MaterialError(
            f"Material '{material}': parameter '{name}' is {value!r} but must be "
            f"in [0, 1]. Fix: pass a float between 0.0 and 1.0."
        )


@dataclass
class Material:
    """A physically based material, exported as glTF metallic-roughness."""
    name: str = "default"
    base_color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0)
    metallic: float = 0.0
    roughness: float = 0.6
    emissive: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    emissive_strength: float = 1.0
    alpha_mode: str = "OPAQUE"
    alpha_cutoff: float = 0.5
    double_sided: bool = False
    transmission: float = 0.0
    ior: float = 1.5
    thickness: float = 0.0
    clearcoat: float = 0.0
    clearcoat_roughness: float = 0.03
    textures: Optional["TextureSet"] = None

    def __post_init__(self) -> None:
        bc = tuple(float(c) for c in self.base_color)
        if len(bc) == 3:
            bc = bc + (1.0,)
        object.__setattr__(self, "base_color", bc)
        for comp, v in zip("rgba", bc):
            _check01(f"base_color.{comp}", v, self.name)
        for p in ("metallic", "roughness", "transmission", "clearcoat",
                  "clearcoat_roughness", "alpha_cutoff"):
            _check01(p, getattr(self, p), self.name)
        em = tuple(float(c) for c in self.emissive)
        object.__setattr__(self, "emissive", em)
        if self.alpha_mode not in ("OPAQUE", "MASK", "BLEND"):
            raise MaterialError(f"Material '{self.name}': alpha_mode must be OPAQUE/MASK/BLEND.")
        if not (1.0 <= self.ior <= 3.0):
            raise MaterialError(f"Material '{self.name}': ior {self.ior} out of [1.0, 3.0].")

    def with_(self, **changes) -> "Material":
        return dataclasses.replace(self, **changes)

    def dedup_key(self) -> tuple:
        return (
            self.base_color, self.metallic, self.roughness, self.emissive,
            self.emissive_strength, self.alpha_mode, self.alpha_cutoff,
            self.double_sided, self.transmission, self.ior, self.thickness,
            self.clearcoat, self.clearcoat_roughness, id(self.textures),
        )


def polished_metal(color=(0.95, 0.95, 0.97), name="polished metal") -> Material:
    """Mirror-like metal. roughness=0.05, metallic=1."""
    return Material(name=name, base_color=(*color, 1.0), metallic=1.0, roughness=0.05)

def brushed_metal(color=(0.84, 0.85, 0.88), resolution=512, name="brushed metal") -> Material:
    """Anisotropic brushed steel via procedural roughness+normal map."""
    from .textures import brushed_metal_textures
    return Material(name=name, base_color=(*color, 1.0), metallic=1.0, roughness=0.35,
                    textures=brushed_metal_textures(resolution=resolution))

def gold(name="gold") -> Material:
    """Polished gold. Linear base color from measured gold reflectance."""
    return Material(name=name, base_color=(1.0, 0.766, 0.336, 1.0), metallic=1.0, roughness=0.12)

def chrome(name="chrome") -> Material:
    return Material(name=name, base_color=(0.9, 0.9, 0.92, 1.0), metallic=1.0, roughness=0.03)

def plastic(color=(0.8, 0.1, 0.1), glossy=True, name="plastic") -> Material:
    return Material(name=name, base_color=(*color, 1.0), metallic=0.0,
                    roughness=0.25 if glossy else 0.7)

def glass(tint=(1.0, 1.0, 1.0), roughness=0.02, name="glass") -> Material:
    return Material(name=name, base_color=(*tint, 1.0), metallic=0.0,
                    roughness=roughness, transmission=1.0, ior=1.5, thickness=0.002)

def ceramic(color=(0.96, 0.96, 0.94), name="ceramic") -> Material:
    return Material(name=name, base_color=(*color, 1.0), metallic=0.0,
                    roughness=0.08, clearcoat=0.6, clearcoat_roughness=0.05)

def rubber(color=(0.05, 0.05, 0.05), name="rubber") -> Material:
    return Material(name=name, base_color=(*color, 1.0), metallic=0.0, roughness=0.9)

def neon(color=(0.1, 1.0, 0.6), strength=8.0, name="neon") -> Material:
    return Material(name=name, base_color=(0.02, 0.02, 0.02, 1.0), metallic=0.0,
                    roughness=0.4, emissive=tuple(color), emissive_strength=float(strength))

def car_paint(color=(0.7, 0.05, 0.05), name="car paint") -> Material:
    return Material(name=name, base_color=(*color, 1.0), metallic=0.4,
                    roughness=0.35, clearcoat=1.0, clearcoat_roughness=0.03)

def wood(kind="oak", resolution=512, name=None) -> Material:
    """Procedural wood. kind: 'oak', 'walnut', 'pine'."""
    from .textures import wood_textures
    return Material(name=name or f"wood {kind}", base_color=(1, 1, 1, 1), metallic=0.0,
                    roughness=0.8, textures=wood_textures(kind=kind, resolution=resolution))

def marble(color=(0.93, 0.93, 0.95), vein=(0.45, 0.43, 0.48), resolution=512, name="marble") -> Material:
    from .textures import marble_textures
    return Material(name=name, base_color=(1, 1, 1, 1), metallic=0.0, roughness=0.25,
                    textures=marble_textures(base=color, vein=vein, resolution=resolution))

def leather(color=(0.35, 0.2, 0.12), resolution=512, name="leather") -> Material:
    from .textures import leather_textures
    return Material(name=name, base_color=(1, 1, 1, 1), metallic=0.0, roughness=0.75,
                    textures=leather_textures(base=color, resolution=resolution))

PRESETS = {
    "polished_metal": polished_metal, "brushed_metal": brushed_metal,
    "gold": gold, "chrome": chrome, "plastic": plastic, "glass": glass,
    "ceramic": ceramic, "rubber": rubber, "neon": neon, "car_paint": car_paint,
    "wood": wood, "marble": marble, "leather": leather,
}
