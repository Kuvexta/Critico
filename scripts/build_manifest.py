"""MANIFEST.json reproducible del artefacto Crítico (CRITICO-SKILL-02, punto 3).

Lista ORDENADA de rutas relativas (POSIX, orden de bytes) con el sha256 de cada
archivo y un hash agregado = sha256 de las líneas «<sha256>  <ruta>\\n» en ese
orden (el mismo formato que `sha256sum`). Ese hash agregado es el
`bundle_sha256` del `artifact_binding`.

Incluye: skills/critico/**, plataformas/*/critico/**, 04_critic.config.yaml y los
prompts del sistema (prompts/critico_system.md y prompts/critic_system.en.md).
Excluye: .git, _tmp_pruebas y cachés (__pycache__, .pytest_cache, *.pyc).
No depende de git, de la fecha ni del sistema operativo.

Uso:
  python3 -B scripts/build_manifest.py --write    # regenera MANIFEST.json
  python3 -B scripts/build_manifest.py --check    # rc 1 si MANIFEST.json no coincide (sin escribir)
  python3 -B scripts/build_manifest.py --binding  # imprime el artifact_binding (head/tree vía git si existe)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parents[1]
MANIFEST = BASE / "MANIFEST.json"
INCLUDE_GLOBS = ("skills/critico/**/*", "plataformas/*/critico/**/*")
INCLUDE_FILES = ("04_critic.config.yaml", "prompts/critico_system.md", "prompts/critic_system.en.md")
EXCLUDED_PARTS = {".git", "_tmp_pruebas", "__pycache__", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
AGGREGATE_RULE = "sha256 de las líneas '<sha256>  <ruta>\\n' ordenadas por ruta (formato sha256sum)"


def _included(path: Path) -> bool:
    rel = path.relative_to(BASE)
    return path.is_file() and not path.is_symlink() and not (set(rel.parts) & EXCLUDED_PARTS) \
        and path.suffix not in EXCLUDED_SUFFIXES


def collect() -> list[str]:
    paths = set()
    for pattern in INCLUDE_GLOBS:
        paths.update(p.relative_to(BASE).as_posix() for p in BASE.glob(pattern) if _included(p))
    for name in INCLUDE_FILES:
        p = BASE / name
        if not p.is_file():
            raise SystemExit(f"falta un archivo obligatorio del manifest: {name}")
        paths.add(name)
    return sorted(paths, key=lambda s: s.encode("utf-8"))


def entries() -> list[dict]:
    return [{"path": p, "sha256": hashlib.sha256((BASE / p).read_bytes()).hexdigest()} for p in collect()]


def aggregate(items: list[dict]) -> str:
    return hashlib.sha256("".join(f"{e['sha256']}  {e['path']}\n" for e in items).encode("utf-8")).hexdigest()


def build() -> bytes:
    items = entries()
    data = {
        "id": "critico-artifact-manifest",
        "algorithm": "sha256",
        "include": list(INCLUDE_GLOBS) + list(INCLUDE_FILES),
        "exclude": sorted(EXCLUDED_PARTS) + ["*" + s for s in sorted(EXCLUDED_SUFFIXES)],
        "aggregate_rule": AGGREGATE_RULE,
        "count": len(items),
        "files": items,
        "aggregate_sha256": aggregate(items),
    }
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=BASE, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "no_comprobado"


def binding() -> dict:
    cfg = yaml.safe_load((BASE / "04_critic.config.yaml").read_text(encoding="utf-8"))
    return {"head": _git("rev-parse", "HEAD"), "tree": _git("rev-parse", "HEAD^{tree}"),
            "bundle_sha256": json.loads(build())["aggregate_sha256"],
            "config_hash": cfg.get("config_hash"), "critic_version": cfg.get("critic_version")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--binding", action="store_true")
    args = parser.parse_args()
    if args.binding:
        print(json.dumps({"artifact_binding": binding()}, ensure_ascii=False))
        return 0
    data = build()
    if args.write:
        if not MANIFEST.exists() or MANIFEST.read_bytes() != data:
            MANIFEST.write_bytes(data)
        print("MANIFEST_OK", json.loads(data)["count"], "bundle_sha256", json.loads(data)["aggregate_sha256"])
        return 0
    if not MANIFEST.exists() or MANIFEST.read_bytes() != data:
        print("MANIFEST_STALE: regenera con scripts/build_manifest.py --write", file=sys.stderr)
        return 1
    print("MANIFEST_OK", json.loads(data)["count"], "bundle_sha256", json.loads(data)["aggregate_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
