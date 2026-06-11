"""Binary glTF 2.0 writer per the Khronos spec.

Layout: 12-byte header (magic 0x46546C67, version 2, total length)
+ JSON chunk (0x4E4F534A, space-padded to 4-byte align)
+ BIN chunk (0x004E4942, zero-padded).

Optimizations: shared-mesh instancing, material dedup,
uint16 indices when < 65536 vertices, POSITION min/max.
"""
from __future__ import annotations
import io, json, struct
from typing import Optional
import numpy as np
from .materials import Material
from .mesh import Mesh, MeshError

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN  = 0x004E4942
ARRAY_BUFFER = 34962
ELEMENT_ARRAY_BUFFER = 34963
GENERATOR = "Forge3D v0.1.0"


class _Bin:
    def __init__(self):
        self.parts = []; self.length = 0; self.views = []
    def add(self, data: bytes, target=None) -> int:
        pad = (-self.length) % 4
        if pad: self.parts.append(b"\x00"*pad); self.length += pad
        view = {"buffer": 0, "byteOffset": self.length, "byteLength": len(data)}
        if target is not None: view["target"] = target
        self.parts.append(data); self.length += len(data); self.views.append(view)
        return len(self.views) - 1
    def blob(self) -> bytes:
        b = b"".join(self.parts)
        return b + b"\x00" * ((-len(b)) % 4)


def _png_bytes(img) -> bytes:
    buf = io.BytesIO(); img.save(buf, format="PNG", optimize=True); return buf.getvalue()


def _material_json(mat: Material, tex_indices: dict) -> dict:
    pbr = {
        "baseColorFactor": [round(float(c), 6) for c in mat.base_color],
        "metallicFactor": round(float(mat.metallic), 6),
        "roughnessFactor": round(float(mat.roughness), 6),
    }
    j = {"name": mat.name, "pbrMetallicRoughness": pbr}
    ts = mat.textures
    if ts is not None:
        k = id(ts)
        if ts.has_color():   pbr["baseColorTexture"] = {"index": tex_indices[(k,"color")]}
        if ts.has_mr():      pbr["metallicRoughnessTexture"] = {"index": tex_indices[(k,"mr")]}
        if ts.has_normal():  j["normalTexture"] = {"index": tex_indices[(k,"normal")]}
        if ts.has_emissive(): j["emissiveTexture"] = {"index": tex_indices[(k,"emissive")]}
    em = np.array(mat.emissive, dtype=np.float64)
    strength = float(mat.emissive_strength)
    if em.max() > 1.0: strength *= float(em.max()); em = em/em.max()
    if em.max() > 0: j["emissiveFactor"] = [round(float(c),6) for c in em]
    if mat.alpha_mode != "OPAQUE":
        j["alphaMode"] = mat.alpha_mode
        if mat.alpha_mode == "MASK": j["alphaCutoff"] = mat.alpha_cutoff
    if mat.double_sided: j["doubleSided"] = True
    ext = {}
    if strength != 1.0 and em.max() > 0:
        ext["KHR_materials_emissive_strength"] = {"emissiveStrength": round(strength,4)}
    if mat.transmission > 0:
        ext["KHR_materials_transmission"] = {"transmissionFactor": round(mat.transmission,4)}
        if mat.thickness > 0:
            ext["KHR_materials_volume"] = {"thicknessFactor": round(mat.thickness,6)}
    if abs(mat.ior - 1.5) > 1e-9:
        ext["KHR_materials_ior"] = {"ior": round(mat.ior,4)}
    if mat.clearcoat > 0:
        ext["KHR_materials_clearcoat"] = {
            "clearcoatFactor": round(mat.clearcoat,4),
            "clearcoatRoughnessFactor": round(mat.clearcoat_roughness,4),
        }
    if ext: j["extensions"] = ext
    return j


def export_glb(obj, path: str) -> dict:
    """Export a Mesh, Node or Scene to .glb. Returns stats dict."""
    bin_w = _Bin()
    accessors, meshes_j, mats_j, images_j, textures_j = [], [], [], [], []
    samplers_j = [{"magFilter":9729,"minFilter":9987,"wrapS":10497,"wrapT":10497}]
    mesh_idx: dict = {}; mat_idx: dict = {}; tex_idx: dict = {}
    ext_used = set(); tri_total = 0

    def add_acc(view, ct, count, atype, vmin=None, vmax=None):
        a = {"bufferView":view,"componentType":ct,"count":int(count),"type":atype}
        if vmin is not None: a["min"]=vmin; a["max"]=vmax
        accessors.append(a); return len(accessors)-1

    def add_ts(ts):
        k = id(ts)
        for kind in ("color","normal","mr","emissive"):
            if (k,kind) in tex_idx: continue
            img = ts.image(kind)
            if img is None: continue
            v = bin_w.add(_png_bytes(img))
            images_j.append({"bufferView":v,"mimeType":"image/png"})
            textures_j.append({"sampler":0,"source":len(images_j)-1})
            tex_idx[(k,kind)] = len(textures_j)-1

    def add_mat(mat: Material) -> int:
        dk = mat.dedup_key()
        if dk in mat_idx: return mat_idx[dk]
        if mat.textures is not None: add_ts(mat.textures)
        mj = _material_json(mat, tex_idx)
        for e in (mj.get("extensions") or {}): ext_used.add(e)
        mats_j.append(mj); mat_idx[dk] = len(mats_j)-1; return mat_idx[dk]

    def add_mesh(mesh: Mesh) -> int:
        nonlocal tri_total
        if id(mesh) in mesh_idx: return mesh_idx[id(mesh)]
        if mesh.triangle_count == 0:
            raise MeshError(f"mesh '{mesh.name}' has 0 triangles.")
        tri_total += mesh.triangle_count
        pos = np.ascontiguousarray(mesh.positions, dtype=np.float32)
        nrm = np.ascontiguousarray(mesh.normals, dtype=np.float32)
        uv  = np.ascontiguousarray(mesh.uvs, dtype=np.float32)
        if mesh.vertex_count < 65536:
            idx = np.ascontiguousarray(mesh.indices, dtype=np.uint16); comp = 5123
        else:
            idx = np.ascontiguousarray(mesh.indices, dtype=np.uint32); comp = 5125
        vp = bin_w.add(pos.tobytes(), ARRAY_BUFFER)
        vn = bin_w.add(nrm.tobytes(), ARRAY_BUFFER)
        vu = bin_w.add(uv.tobytes(), ARRAY_BUFFER)
        vi = bin_w.add(idx.tobytes(), ELEMENT_ARRAY_BUFFER)
        ap = add_acc(vp,5126,len(pos),"VEC3",[float(x) for x in pos.min(axis=0)],[float(x) for x in pos.max(axis=0)])
        an = add_acc(vn,5126,len(nrm),"VEC3")
        au = add_acc(vu,5126,len(uv),"VEC2")
        ai = add_acc(vi,comp,idx.size,"SCALAR")
        mi = add_mat(mesh.material)
        meshes_j.append({"name":mesh.name,"primitives":[{
            "attributes":{"POSITION":ap,"NORMAL":an,"TEXCOORD_0":au},
            "indices":ai,"material":mi,"mode":4}]})
        mesh_idx[id(mesh)] = len(meshes_j)-1; return mesh_idx[id(mesh)]

    nodes_j = []; lights_j = []

    def add_node(o) -> int:
        nd = {}
        if isinstance(o, Mesh):
            nd["name"] = o.name; nd["mesh"] = add_mesh(o)
        else:
            nd["name"] = getattr(o,"name","node")
            if hasattr(o,"local_matrix"):
                M = np.asarray(o.local_matrix(), dtype=np.float64)
                if not np.allclose(M, np.eye(4)):
                    nd["matrix"] = [float(x) for x in M.T.reshape(-1)]
            if getattr(o,"mesh",None) is not None:
                nd["mesh"] = add_mesh(o.mesh)
            if getattr(o,"light",None) is not None:
                lights_j.append(o.light)
                nd["extensions"] = {"KHR_lights_punctual":{"light":len(lights_j)-1}}
                ext_used.add("KHR_lights_punctual")
            kids = [add_node(c) for c in (getattr(o,"children",[]) or [])]
            if kids: nd["children"] = kids
        nodes_j.append(nd); return len(nodes_j)-1

    roots = obj.roots if hasattr(obj,"roots") else [obj]
    root_ids = [add_node(r) for r in roots]
    gltf = {
        "asset":{"version":"2.0","generator":GENERATOR},
        "scene":0,
        "scenes":[{"name":getattr(obj,"name","scene"),"nodes":root_ids}],
        "nodes":nodes_j, "meshes":meshes_j, "materials":mats_j,
        "accessors":accessors, "bufferViews":bin_w.views,
        "buffers":[{"byteLength":len(bin_w.blob())}],
    }
    if images_j: gltf["images"]=images_j; gltf["textures"]=textures_j; gltf["samplers"]=samplers_j
    if lights_j:
        _ll = {"lights": lights_j}
        _lext = {"KHR_lights_punctual": _ll}
        gltf["extensions"] = _lext
    if ext_used: gltf["extensionsUsed"] = sorted(ext_used)
    jb = json.dumps(gltf,separators=(",",":")).encode("utf-8")
    jb += b" "*((-len(jb))%4)
    bb = bin_w.blob()
    total = 12+8+len(jb)+8+len(bb)
    with open(path,"wb") as f:
        f.write(struct.pack("<III",GLB_MAGIC,2,total))
        f.write(struct.pack("<II",len(jb),CHUNK_JSON)); f.write(jb)
        f.write(struct.pack("<II",len(bb),CHUNK_BIN)); f.write(bb)
    return {"bytes":total,"meshes":len(meshes_j),"materials":len(mats_j),
            "triangles":tri_total,"textures":len(textures_j)}


_SNIPPET = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>html,body{margin:0;height:100%;background:#15171c}#app{width:100%;height:100vh}</style>
</head><body><div id="app"></div>
<script type="importmap">
{"imports":{"three":"__THREE_DIR__/three.module.min.js","three/addons/":"__THREE_DIR__/addons/"}}
</script>
<script type="module">
import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {RGBELoader} from 'three/addons/loaders/RGBELoader.js';
const el=document.getElementById('app');
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(el.clientWidth,el.clientHeight);
renderer.toneMapping=THREE.ACESFilmicToneMapping;
el.appendChild(renderer.domElement);
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x15171c);
const camera=new THREE.PerspectiveCamera(40,el.clientWidth/el.clientHeight,0.001,100);
new RGBELoader().load('__HDRI__',(hdr)=>{
  hdr.mapping=THREE.EquirectangularReflectionMapping;
  scene.environment=hdr;
});
const controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;
new GLTFLoader().load('__GLB__',(gltf)=>{
  scene.add(gltf.scene);
  const box=new THREE.Box3().setFromObject(gltf.scene);
  const c=box.getCenter(new THREE.Vector3());
  const s=box.getSize(new THREE.Vector3()).length();
  camera.position.set(c.x+s*0.8,c.y+s*0.5,c.z+s*0.8);
  camera.near=s/100;camera.far=s*20;camera.updateProjectionMatrix();
  controls.target.copy(c);
});
renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera);});
</script></body></html>
"""


def threejs_snippet(glb_filename: str, three_dir: str = "./vendor",
                    hdri_filename: str = "./studio.hdr") -> str:
    """Ready-to-paste offline HTML + three.js snippet loading the GLB."""
    return (_SNIPPET
            .replace("__THREE_DIR__", three_dir)
            .replace("__HDRI__", hdri_filename)
            .replace("__GLB__", glb_filename))
