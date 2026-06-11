"""Forge3D CLI.

Usage:
    python -m forge3d build examples/crate.py [--out out/]
    python -m forge3d validate out/crate.glb [--no-render]
    python -m forge3d preview out/crate.glb [-o out/crate.png] [--size 512]
    python -m forge3d snippet out/crate.glb [-o viewer.html]
    python -m forge3d version
"""
from __future__ import annotations
import argparse, os, runpy, sys, time


def _build(args):
    if not os.path.isfile(args.script):
        print(f"error: not found: {args.script}",file=sys.stderr); return 2
    os.environ["FORGE3D_OUT"] = args.out
    os.makedirs(args.out, exist_ok=True)
    t0 = time.perf_counter()
    runpy.run_path(args.script, run_name="__main__")
    print(f"build ok: {args.script} in {time.perf_counter()-t0:.2f}s (out: {args.out})")
    return 0

def _validate(args):
    from .validate import GLBValidationError, validate_glb
    try:
        r = validate_glb(args.file, render_check=not args.no_render)
    except GLBValidationError as e:
        print(f"INVALID: {e}",file=sys.stderr); return 1
    print(f"valid: {args.file} | tri={r['triangles']} mat={r['materials']} tex={r['textures']} render_mean={r['render_mean']}")
    return 0

def _preview(args):
    from .render import preview
    from .validate import load_glb
    root,_ = load_glb(args.file)
    out = args.output or os.path.splitext(args.file)[0]+".png"
    preview(root, out, size=args.size)
    print(f"preview: {out}"); return 0

def _snippet(args):
    from .gltf import threejs_snippet
    html = threejs_snippet(os.path.basename(args.file),three_dir=args.three_dir,hdri_filename=args.hdri)
    out = args.output or os.path.splitext(args.file)[0]+".html"
    with open(out,"w",encoding="utf-8") as f: f.write(html)
    print(f"snippet: {out}"); return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="forge3d")
    sub = p.add_subparsers(dest="cmd",required=True)
    b = sub.add_parser("build"); b.add_argument("script"); b.add_argument("--out",default="out"); b.set_defaults(func=_build)
    v = sub.add_parser("validate"); v.add_argument("file"); v.add_argument("--no-render",action="store_true"); v.set_defaults(func=_validate)
    pr = sub.add_parser("preview"); pr.add_argument("file"); pr.add_argument("-o","--output"); pr.add_argument("--size",type=int,default=512); pr.set_defaults(func=_preview)
    sn = sub.add_parser("snippet"); sn.add_argument("file"); sn.add_argument("-o","--output"); sn.add_argument("--three-dir",default="./vendor"); sn.add_argument("--hdri",default="./studio.hdr"); sn.set_defaults(func=_snippet)
    sv = sub.add_parser("version"); sv.set_defaults(func=lambda a:(print(__import__("forge3d").__version__),0)[1])
    args = p.parse_args(argv)
    return args.func(args)

if __name__=="__main__":
    raise SystemExit(main())
