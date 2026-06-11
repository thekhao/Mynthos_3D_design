"""Forge3D - code-first 3D asset generation for the web.

Detailed, PBR-textured GLB assets from pure Python scripts (numpy + Pillow
only). Geometry, materials, procedural textures, scene graph, optimized GLB
export, PNG previews and a ready-to-paste three.js snippet.

Quickstart:
    import forge3d as f3
    crate = f3.box(0.5, rounding=0.02, material=f3.wood("oak"))
    scene = f3.Scene("demo")
    scene.add(crate)
    scene.export("crate.glb")
    scene.preview("crate.png")

Units: meters. Angles: degrees. Colors: linear RGB in [0, 1]. +Y is up.
"""

__version__ = "0.1.0"

from .mesh import (
    Mesh, MeshError, merge, grid_mesh,
    rotation_matrix, translation_matrix, scale_matrix,
)
from .primitives import box, sphere, cylinder, cone, torus, plane, capsule
from .construct import (
    bezier, catmull_rom, arc_points, circle_profile,
    rounded_rect_profile, star_profile, triangulate_polygon,
    lathe, extrude, sweep, loft,
)
from .ops import union, subtract, intersect, round_edges, shell, subdivide
from .materials import (
    Material, MaterialError, PRESETS,
    polished_metal, brushed_metal, gold, chrome, plastic, glass,
    ceramic, rubber, neon, car_paint, wood, marble, leather,
)
from .textures import (
    TextureSet, noise, normal_from_height, checker_textures,
    gradient_textures, grain_textures, scratches_textures,
    wood_textures, marble_textures, brushed_metal_textures, leather_textures,
)
from .scene import Scene, Node, group, instances, studio_lights
from .gltf import export_glb, threejs_snippet
from .render import render, preview
from .validate import validate_glb, load_glb, GLBValidationError

__all__ = [
    "__version__",
    "Mesh", "MeshError", "merge", "grid_mesh",
    "rotation_matrix", "translation_matrix", "scale_matrix",
    "box", "sphere", "cylinder", "cone", "torus", "plane", "capsule",
    "bezier", "catmull_rom", "arc_points", "circle_profile",
    "rounded_rect_profile", "star_profile", "triangulate_polygon",
    "lathe", "extrude", "sweep", "loft",
    "union", "subtract", "intersect", "round_edges", "shell", "subdivide",
    "Material", "MaterialError", "PRESETS",
    "polished_metal", "brushed_metal", "gold", "chrome", "plastic", "glass",
    "ceramic", "rubber", "neon", "car_paint", "wood", "marble", "leather",
    "TextureSet", "noise", "normal_from_height", "checker_textures",
    "gradient_textures", "grain_textures", "scratches_textures",
    "wood_textures", "marble_textures", "brushed_metal_textures", "leather_textures",
    "Scene", "Node", "group", "instances", "studio_lights",
    "export_glb", "threejs_snippet", "render", "preview",
    "validate_glb", "load_glb", "GLBValidationError",
]
