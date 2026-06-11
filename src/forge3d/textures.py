"""Procedural textures (numpy + Pillow): noise, wood, marble, brushed metal,
leather, checker, scratches, grain, gradients.

glTF packing: mr map = [1, roughness, metallic] (G=roughness, B=metallic).
All color data linear [0,1]; PNG color/emissive are sRGB-encoded on export.
Default resolution: 512.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np
from PIL import Image


def _srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x**(1/2.4) - 0.055)


@dataclass
class TextureSet:
    """Bundle of optional texture maps for a Material.
    Fields (ndarray [0,1]): color(H,W,3), normal(H,W,3), roughness(H,W), metallic(H,W), emissive(H,W,3).
    """
    color: Optional[np.ndarray] = None
    normal: Optional[np.ndarray] = None
    roughness: Optional[np.ndarray] = None
    metallic: Optional[np.ndarray] = None
    emissive: Optional[np.ndarray] = None

    def has_color(self): return self.color is not None
    def has_normal(self): return self.normal is not None
    def has_mr(self): return self.roughness is not None or self.metallic is not None
    def has_emissive(self): return self.emissive is not None

    def array(self, kind: str):
        if kind == "color": return self.color
        if kind == "normal": return self.normal
        if kind == "emissive": return self.emissive
        if kind == "mr":
            if not self.has_mr(): return None
            ref = self.roughness if self.roughness is not None else self.metallic
            h, w = ref.shape[:2]
            out = np.ones((h, w, 3))
            if self.roughness is not None: out[:,:,1] = self.roughness
            if self.metallic is not None: out[:,:,2] = self.metallic
            return out
        raise ValueError(f"TextureSet.array: unknown kind '{kind}'.")

    def image(self, kind: str):
        a = self.array(kind)
        if a is None: return None
        if kind in ("color", "emissive"): a = _srgb(a)
        u8 = (np.clip(a, 0, 1) * 255).round().astype(np.uint8)
        return Image.fromarray(u8)


def noise(resolution: int = 512, scale=8, octaves: int = 4, seed: int = 0,
          persistence: float = 0.5) -> np.ndarray:
    """Tileable fractal value noise in [0,1]."""
    if np.isscalar(scale): scale = (int(scale), int(scale))
    sx, sy = max(int(scale[0]), 1), max(int(scale[1]), 1)
    out = np.zeros((resolution, resolution)); amp_total = 0.0
    for o in range(octaves):
        nx, ny = sx * 2**o, sy * 2**o
        rng = np.random.default_rng(seed * 1000003 + o)
        lattice = rng.random((ny+1, nx+1))
        lattice[-1,:] = lattice[0,:]; lattice[:,-1] = lattice[:,0]
        u = np.linspace(0, nx, resolution, endpoint=False)
        v = np.linspace(0, ny, resolution, endpoint=False)
        U, V = np.meshgrid(u, v)
        iu, iv = U.astype(int), V.astype(int)
        fu, fv = U - iu, V - iv
        fu = fu*fu*(3 - 2*fu); fv = fv*fv*(3 - 2*fv)
        a = lattice[iv, iu]; b = lattice[iv, iu+1]
        c = lattice[iv+1, iu]; d = lattice[iv+1, iu+1]
        amp = persistence**o
        out += amp * ((a*(1-fu) + b*fu)*(1-fv) + (c*(1-fu) + d*fu)*fv)
        amp_total += amp
    out /= amp_total
    lo, hi = out.min(), out.max()
    return (out - lo) / max(hi - lo, 1e-12)


def normal_from_height(height, strength: float = 2.0) -> np.ndarray:
    """Tangent-space normal map [0,1] from height field [0,1]."""
    gy, gx = np.gradient(height.astype(np.float64))
    res = max(height.shape)
    nx = -gx * strength * res / 64.0
    ny = gy * strength * res / 64.0
    nz = np.ones_like(nx)
    n = np.stack([nx, ny, nz], axis=2)
    n /= np.maximum(np.linalg.norm(n, axis=2, keepdims=True), 1e-12)
    return n * 0.5 + 0.5


def checker_textures(resolution=512, tiles=8,
                     color_a=(0.92,0.92,0.92), color_b=(0.15,0.15,0.15),
                     roughness_a=0.4, roughness_b=0.4) -> TextureSet:
    """Checkerboard color + roughness."""
    idx = np.arange(resolution) * tiles // resolution
    mask = ((idx[:,None] + idx[None,:]) % 2).astype(np.float64)
    color = np.asarray(color_a)*(1-mask[:,:,None]) + np.asarray(color_b)*mask[:,:,None]
    rough = roughness_a*(1-mask) + roughness_b*mask
    return TextureSet(color=color, roughness=rough)


def gradient_textures(resolution=512, top=(1.,1.,1.), bottom=(0.,0.,0.),
                      direction="v") -> TextureSet:
    """Linear color gradient. direction: 'v' or 'h'."""
    t = np.linspace(0, 1, resolution)
    T = (np.tile(t[:,None], (1,resolution)) if direction == "v"
         else np.tile(t[None,:], (resolution,1)))
    color = np.asarray(top)*(1-T[:,:,None]) + np.asarray(bottom)*T[:,:,None]
    return TextureSet(color=color)


def grain_textures(resolution=512, base_roughness=0.5, amount=0.25,
                   scale=96, seed=3) -> TextureSet:
    """Fine roughness grain."""
    g = noise(resolution, scale=scale, octaves=2, seed=seed)
    rough = np.clip(base_roughness + (g - 0.5)*2*amount, 0.02, 1.0)
    return TextureSet(roughness=rough, normal=normal_from_height(g, strength=0.4))


def scratches_textures(resolution=512, count=80, seed=7,
                       base_roughness=0.25, scratch_roughness=0.7) -> TextureSet:
    """Random fine scratches (roughness + normal)."""
    from PIL import ImageDraw, ImageFilter
    img = Image.new("F", (resolution, resolution), 0.0)
    draw = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    for _ in range(count):
        x0, y0 = rng.random(2) * resolution
        ang = rng.random() * 2 * np.pi
        length = (0.05 + 0.25*rng.random()) * resolution
        x1, y1 = x0 + np.cos(ang)*length, y0 + np.sin(ang)*length
        draw.line([(x0,y0),(x1,y1)], fill=float(0.4 + 0.6*rng.random()), width=1)
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    h = np.asarray(img, dtype=np.float64)
    h = h / max(h.max(), 1e-12)
    rough = np.clip(base_roughness + h*(scratch_roughness - base_roughness), 0, 1)
    return TextureSet(roughness=rough, normal=normal_from_height(-h, strength=1.2))


_WOOD_COLORS = {
    "oak": ((0.52,0.35,0.19),(0.36,0.22,0.11)),
    "walnut": ((0.26,0.15,0.08),(0.13,0.07,0.035)),
    "pine": ((0.66,0.47,0.24),(0.50,0.33,0.15)),
}


def wood_textures(kind="oak", resolution=512, rings=9.0, seed=11) -> TextureSet:
    """Procedural wood. kind: 'oak', 'walnut', 'pine'."""
    if kind not in _WOOD_COLORS:
        raise ValueError(f"wood_textures kind '{kind}' unknown. Use: {sorted(_WOOD_COLORS)}.")
    light, dark = (np.asarray(c) for c in _WOOD_COLORS[kind])
    turb = noise(resolution, scale=(4,16), octaves=4, seed=seed)
    fiber = noise(resolution, scale=(2,128), octaves=2, seed=seed+1)
    u = np.linspace(0,1,resolution)[None,:].repeat(resolution, axis=0)
    phase = u * rings + turb*2.2 + fiber*0.35
    ring = (0.5 + 0.5*np.sin(phase*2*np.pi))**1.5
    color = dark + (light - dark)*ring[:,:,None]
    color *= (0.92 + 0.16*fiber)[:,:,None]
    rough = np.clip(0.55 + 0.25*(1-ring) + 0.1*(fiber-0.5), 0.3, 1.0)
    nmap = normal_from_height(ring*0.6 + fiber*0.4, strength=1.4)
    return TextureSet(color=np.clip(color,0,1), normal=nmap, roughness=rough)


def marble_textures(base=(0.93,0.93,0.95), vein=(0.45,0.43,0.48),
                    resolution=512, vein_count=3.0, seed=5) -> TextureSet:
    """Veined marble."""
    base, vein = np.asarray(base), np.asarray(vein)
    turb = noise(resolution, scale=6, octaves=5, seed=seed)
    u = np.linspace(0,1,resolution)[None,:].repeat(resolution, axis=0)
    v = np.abs(np.sin((u*vein_count + turb*3.5)*np.pi))
    mask = np.clip((1-v)**6*1.6, 0, 1)
    cloud = noise(resolution, scale=12, octaves=3, seed=seed+2)*0.12
    color = base*(1-mask[:,:,None]) + vein*mask[:,:,None] - cloud[:,:,None]*0.3
    rough = np.clip(0.12 + 0.4*mask + 0.1*cloud, 0.05, 1.0)
    nmap = normal_from_height(-mask*0.5, strength=0.5)
    return TextureSet(color=np.clip(color,0,1), normal=nmap, roughness=rough)


def brushed_metal_textures(resolution=512, seed=9) -> TextureSet:
    """Anisotropic brushing streaks."""
    streaks = noise(resolution, scale=(2,180), octaves=3, seed=seed)
    fine = noise(resolution, scale=(8,256), octaves=2, seed=seed+1)
    h = streaks*0.7 + fine*0.3
    rough = np.clip(0.18 + 0.35*h, 0.1, 0.65)
    nmap = normal_from_height(h*0.5, strength=0.5)
    return TextureSet(roughness=rough, normal=nmap)


def leather_textures(base=(0.35,0.2,0.12), resolution=512, seed=13) -> TextureSet:
    """Grained leather."""
    base = np.asarray(base)
    pebble = noise(resolution, scale=48, octaves=3, seed=seed)
    folds = noise(resolution, scale=6, octaves=3, seed=seed+1)
    h = pebble*0.65 + folds*0.35
    color = base[None,None,:] * (0.8 + 0.35*h[:,:,None])
    rough = np.clip(0.6 + 0.3*(1-pebble), 0.4, 1.0)
    nmap = normal_from_height(h, strength=2.2)
    return TextureSet(color=np.clip(color,0,1), normal=nmap, roughness=rough)
