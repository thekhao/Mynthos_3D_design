"""Strict GLB validator (glTF 2.0) - no external dependencies.

validate_glb(path) checks: binary container, spec fields, mesh data
(non-empty, indexed, unit normals, UVs, POSITION min/max), PBR materials,
image decodability, node graph validity, and a non-black render.
"""
from __future__ import annotations
import io, json, struct
from typing import Optional
import numpy as np
from .materials import Material
from .mesh import Mesh

_CSIZE = {5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}
_CDTYPE = {5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}
_TCOUNT = {"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4,"MAT4":16}


class GLBValidationError(Exception):
    pass


class _Ck:
    def __init__(self): self.errors=[]; self.warnings=[]
    def err(self,m): self.errors.append(m)
    def warn(self,m): self.warnings.append(m)
    def req(self,c,m):
        if not c: self.err(m)
        return bool(c)


def _parse(data, ck):
    if len(data)<12: raise GLBValidationError("file shorter than 12-byte header")
    magic,version,total = struct.unpack_from("<III",data,0)
    ck.req(magic==0x46546C67,f"bad magic 0x{magic:08X}")
    ck.req(version==2,f"version {version}, expected 2")
    ck.req(total==len(data),f"header total {total} != file {len(data)}")
    offset=12; chunks=[]
    while offset+8<=len(data):
        clen,ctype=struct.unpack_from("<II",data,offset)
        ck.req(clen%4==0,f"chunk at {offset} not 4-aligned")
        chunks.append((ctype,data[offset+8:offset+8+clen])); offset+=8+clen
    ck.req(len(chunks)>=1 and chunks[0][0]==0x4E4F534A,"first chunk must be JSON")
    binc = chunks[1][1] if len(chunks)>1 else b""
    try: gltf=json.loads(chunks[0][1].decode("utf-8"))
    except Exception as e: raise GLBValidationError(f"JSON parse error: {e}") from e
    return gltf,binc


def _acc(gltf,binc,idx,ck):
    a=gltf["accessors"][idx]; n=_TCOUNT[a["type"]]; dt=_CDTYPE[a["componentType"]]
    if "bufferView" not in a: ck.err(f"accessor {idx} missing bufferView"); return None
    bv=gltf["bufferViews"][a["bufferView"]]
    start=bv.get("byteOffset",0)+a.get("byteOffset",0)
    size=a["count"]*n*_CSIZE[a["componentType"]]
    if start+size>len(binc): ck.err(f"accessor {idx} overruns BIN"); return None
    arr=np.frombuffer(binc,dtype=dt,count=a["count"]*n,offset=start)
    return arr.reshape(a["count"],n) if n>1 else arr


def _check_mat(mi,mat,ck,nt):
    pbr=mat.get("pbrMetallicRoughness",{})
    bcf=pbr.get("baseColorFactor",[1,1,1,1])
    if not all(0<=v<=1 for v in bcf): ck.err(f"mat {mi}: baseColorFactor out of [0,1]")
    for k in ("metallicFactor","roughnessFactor"):
        v=pbr.get(k,1.0)
        if not 0<=v<=1: ck.err(f"mat {mi}: {k}={v} out of [0,1]")


def load_glb(path: str):
    """Parse a Forge3D GLB back into a Node tree (for validation render)."""
    from .scene import Node
    ck=_Ck()
    with open(path,"rb") as f: data=f.read()
    gltf,binc=_parse(data,ck)
    if ck.errors: raise GLBValidationError("; ".join(ck.errors))
    mats=[]
    for mat in gltf.get("materials",[]):
        pbr=mat.get("pbrMetallicRoughness",{})
        em=mat.get("emissiveFactor",[0,0,0])
        es=mat.get("extensions",{}).get("KHR_materials_emissive_strength",{}).get("emissiveStrength",1.0)
        mats.append(Material(
            name=mat.get("name","m"),
            base_color=tuple(pbr.get("baseColorFactor",[1,1,1,1])),
            metallic=pbr.get("metallicFactor",1.0),
            roughness=pbr.get("roughnessFactor",1.0),
            emissive=tuple(em),emissive_strength=es,
            double_sided=mat.get("doubleSided",False)))
    meshes=[]
    for mesh in gltf.get("meshes",[]):
        prims=[]
        for prim in mesh["primitives"]:
            pos=_acc(gltf,binc,prim["attributes"]["POSITION"],ck)
            nrm=_acc(gltf,binc,prim["attributes"]["NORMAL"],ck)
            uv=_acc(gltf,binc,prim["attributes"]["TEXCOORD_0"],ck)
            idx=_acc(gltf,binc,prim["indices"],ck)
            mat=mats[prim["material"]] if "material" in prim else None
            prims.append(Mesh(pos.astype(np.float32),nrm.astype(np.float32),
                              uv.astype(np.float32),idx.astype(np.uint32).reshape(-1,3),
                              material=mat,name=mesh.get("name","mesh")))
        meshes.append(prims)
    nodes=[]
    for nd in gltf.get("nodes",[]):
        node=Node(name=nd.get("name"))
        if "matrix" in nd:
            node.matrix=np.array(nd["matrix"],dtype=np.float64).reshape(4,4).T
        nodes.append(node)
    for ni,nd in enumerate(gltf.get("nodes",[])):
        for ci in nd.get("children",[]):
            nodes[ni].children.append(nodes[ci])
        if "mesh" in nd:
            for pm in meshes[nd["mesh"]]:
                nodes[ni].children.append(Node(mesh=pm))
    sc=gltf["scenes"][gltf.get("scene",0)]
    root=Node(name="root")
    for ni in sc["nodes"]: root.children.append(nodes[ni])
    return root,gltf


def validate_glb(path: str, render_check: bool = True, strict: bool = True) -> dict:
    """Validate a GLB. Raises GLBValidationError if errors found (strict=True).
    Returns report: {ok, errors, warnings, triangles, meshes, materials, textures, render_mean}.
    """
    ck=_Ck()
    with open(path,"rb") as f: data=f.read()
    gltf,binc=_parse(data,ck)
    asset=gltf.get("asset",{})
    ck.req(asset.get("version")=="2.0",f"asset.version {asset.get('version')!r} != '2.0'")
    bufs=gltf.get("buffers",[])
    if bufs:
        ck.req(len(bufs)==1 and "uri" not in bufs[0],"GLB must have one uri-less buffer")
        ck.req(abs(bufs[0]["byteLength"]-len(binc))<4,
               f"buffer byteLength {bufs[0]['byteLength']} != BIN {len(binc)}")
    tri_total=0
    for mi,mesh in enumerate(gltf.get("meshes",[])):
        for pi,prim in enumerate(mesh["primitives"]):
            w=f"mesh {mi} prim {pi}"
            attrs=prim.get("attributes",{})
            if not ck.req("POSITION" in attrs,f"{w}: no POSITION"): continue
            ck.req("NORMAL" in attrs,f"{w}: no NORMAL")
            ck.req("TEXCOORD_0" in attrs,f"{w}: no TEXCOORD_0")
            ck.req(prim.get("mode",4)==4,f"{w}: mode must be TRIANGLES")
            ck.req("indices" in prim,f"{w}: must be indexed")
            pos=_acc(gltf,binc,attrs["POSITION"],ck)
            if pos is None or not ck.req(len(pos)>0,f"{w}: empty"): continue
            acc=gltf["accessors"][attrs["POSITION"]]
            if "min" not in acc or "max" not in acc:
                ck.err(f"{w}: POSITION missing min/max")
            if "NORMAL" in attrs:
                nrm=_acc(gltf,binc,attrs["NORMAL"],ck)
                if nrm is not None:
                    ln=np.linalg.norm(nrm.astype(np.float64),axis=1)
                    if not np.allclose(ln,1.0,atol=5e-3):
                        ck.err(f"{w}: normals not unit (min {ln.min():.4f} max {ln.max():.4f})")
            if "indices" in prim:
                idx=_acc(gltf,binc,prim["indices"],ck)
                if idx is not None:
                    ck.req(len(idx)%3==0,f"{w}: index count not divisible by 3")
                    ck.req(int(idx.max())<len(pos),f"{w}: index out of range")
                    tri_total+=len(idx)//3
    ck.req(tri_total>0,"file has no triangles")
    for mi,mat in enumerate(gltf.get("materials",[])):
        _check_mat(mi,mat,ck,len(gltf.get("textures",[])))
    from PIL import Image
    n_img=0
    for ii,img in enumerate(gltf.get("images",[])):
        bv=gltf["bufferViews"][img["bufferView"]]
        blob=binc[bv.get("byteOffset",0):bv.get("byteOffset",0)+bv["byteLength"]]
        try:
            with Image.open(io.BytesIO(blob)) as im: im.verify()
            n_img+=1
        except Exception as e: ck.err(f"image {ii} decode error: {e}")
    # node graph sanity
    n_nd=len(gltf.get("nodes",[]))
    seen=set()
    for ni,nd in enumerate(gltf.get("nodes",[])):
        for c in nd.get("children",[]):
            ck.req(0<=c<n_nd,f"node {ni}: child {c} out of range")
            ck.req(c not in seen,f"node {c} has multiple parents")
            seen.add(c)
    rm=None
    if render_check and not ck.errors:
        from .render import render as _render
        root,_=load_glb(path)
        img=_render(root,size=128)
        rm=float(img.mean())
        ck.req(rm>6.0,f"render is black (mean={rm:.1f})")
    report={"ok":not ck.errors,"errors":ck.errors,"warnings":ck.warnings,
            "triangles":tri_total,"meshes":len(gltf.get("meshes",[])),
            "materials":len(gltf.get("materials",[])),"textures":n_img,"render_mean":rm}
    if strict and ck.errors:
        raise GLBValidationError(f"{path}: "+"; ".join(ck.errors))
    return report
