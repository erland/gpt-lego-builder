#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

HEADER_RE = re.compile(r"^0\s+!LDRAW_ORG\s+(\S+)(?:\s+(.*))?$", re.IGNORECASE)
NAME_RE = re.compile(r"^0\s+Name:\s+(.+?)\s*$", re.IGNORECASE)
COLOUR_RE = re.compile(r"^0\s+!COLOUR\s+(\S+)\s+CODE\s+(\d+)\b", re.IGNORECASE)

ALLOWED_TYPES = {"part", "shortcut"}


@dataclass(frozen=True)
class SourceFile:
    path: str
    data: bytes


def _canonical_path(name: str) -> str:
    return name.replace("\\", "/").lstrip("./")


def _part_relative(path: str) -> str | None:
    p = _canonical_path(path)
    marker = "/parts/"
    if p.startswith("parts/"):
        rel = p[len("parts/"):]
    elif marker in p:
        rel = p.split(marker, 1)[1]
    else:
        return None
    if "/" in rel:
        return None
    if not rel.lower().endswith(".dat"):
        return None
    return rel.lower()


def iter_source_files(source: Path) -> Iterator[SourceFile]:
    if source.is_file() and zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as zf:
            for info in sorted(zf.infolist(), key=lambda i: i.filename.lower()):
                rel = _part_relative(info.filename)
                if rel is None or info.is_dir():
                    continue
                yield SourceFile(path=rel, data=zf.read(info))
        return

    if source.is_dir():
        candidates = []
        for p in source.rglob("*.dat"):
            rel = _part_relative(p.relative_to(source).as_posix())
            if rel is not None:
                candidates.append((rel, p))
        for rel, p in sorted(candidates):
            yield SourceFile(path=rel, data=p.read_bytes())
        return

    raise ValueError(f"Source must be an LDraw directory or zip archive: {source}")


def _read_named_file(source: Path, filename: str) -> bytes | None:
    wanted = filename.lower()
    if source.is_file() and zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as zf:
            matches = [i for i in zf.infolist() if not i.is_dir() and _canonical_path(i.filename).split("/")[-1].lower() == wanted]
            if not matches:
                return None
            matches.sort(key=lambda i: (len(_canonical_path(i.filename).split("/")), _canonical_path(i.filename).lower()))
            return zf.read(matches[0])
    if source.is_dir():
        matches = [p for p in source.rglob("*") if p.is_file() and p.name.lower() == wanted]
        if not matches:
            return None
        matches.sort(key=lambda p: (len(p.relative_to(source).parts), p.as_posix().lower()))
        return matches[0].read_bytes()
    return None


def source_fingerprint(files: Iterable[SourceFile], color_data: bytes | None = None) -> str:
    h = hashlib.sha256()
    for item in files:
        h.update(item.path.encode("utf-8"))
        h.update(b"\0")
        h.update(hashlib.sha256(item.data).digest())
        h.update(b"\n")
    if color_data is not None:
        h.update(b"LDConfig.ldr\0")
        h.update(hashlib.sha256(color_data).digest())
        h.update(b"\n")
    return "sha256:" + h.hexdigest()


def parse_header(data: bytes, fallback_name: str) -> dict:
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()[:40]
    description = ""
    library_type = ""
    qualifiers: list[str] = []
    declared_name = None

    for line in lines:
        if not description and line.startswith("0 ") and not line.startswith("0 !") and not line.lower().startswith("0 name:"):
            description = line[2:].strip()
        m = NAME_RE.match(line)
        if m:
            declared_name = m.group(1).strip().replace("\\", "/").split("/")[-1].lower()
        m = HEADER_RE.match(line)
        if m:
            library_type = m.group(1)
            rest = (m.group(2) or "").split()
            qualifiers = [t for t in rest if t.upper() not in {"ORIGINAL", "UPDATE"} and not re.fullmatch(r"\d{4}-\d{2}", t)]
            break

    if not description:
        raise ValueError(f"Missing description header in {fallback_name}")
    if not library_type:
        raise ValueError(f"Missing !LDRAW_ORG header in {fallback_name}")
    if declared_name and declared_name != fallback_name.lower():
        raise ValueError(f"Header Name mismatch for {fallback_name}: {declared_name}")

    usable = library_type.lower() in ALLOWED_TYPES
    return {
        "description": description,
        "library_type": library_type,
        "qualifiers": qualifiers,
        "usable_as_model_part": usable,
    }


def parse_colors(data: bytes) -> dict[str, dict]:
    colors: dict[str, dict] = {}
    text = data.decode("utf-8", errors="replace")
    for line in text.splitlines():
        m = COLOUR_RE.match(line)
        if not m:
            continue
        name, code_text = m.groups()
        code = str(int(code_text))
        if code in colors:
            raise ValueError(f"Duplicate LDraw color code in LDConfig.ldr: {code}")
        colors[code] = {"name": name.replace("_", " ")}
    if not colors:
        raise ValueError("No !COLOUR definitions found in LDConfig.ldr")
    return dict(sorted(colors.items(), key=lambda item: int(item[0])))


def build_catalog(source: Path, release: str, canonical_url: str, kind: str = "official_release") -> dict:
    files = list(iter_source_files(source))
    if not files:
        raise ValueError("No top-level parts/*.dat files found in source")
    color_data = _read_named_file(source, "LDConfig.ldr")
    if color_data is None:
        raise ValueError("LDConfig.ldr is required to build a verified color index")

    parts: dict[str, dict] = {}
    for item in files:
        if item.path in parts:
            raise ValueError(f"Duplicate normalized part reference: {item.path}")
        parts[item.path] = parse_header(item.data, item.path)

    colors = parse_colors(color_data)
    usable = sum(1 for item in parts.values() if item["usable_as_model_part"])
    return {
        "schema_version": "1.1",
        "source": {
            "name": "LDraw.org Official Parts Library",
            "kind": kind,
            "release": release,
            "fingerprint": source_fingerprint(files, color_data),
            "canonical_url": canonical_url,
        },
        "statistics": {
            "indexed_files": len(parts),
            "usable_parts": usable,
            "colors": len(colors),
        },
        "colors": colors,
        "parts": dict(sorted(parts.items())),
    }


def load_catalog(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def lookup_part(catalog: dict, part_ref: str) -> dict | None:
    return catalog.get("parts", {}).get(part_ref.replace("\\", "/").split("/")[-1].lower())


def validate_part_reference(catalog: dict, part_ref: str) -> tuple[bool, str]:
    entry = lookup_part(catalog, part_ref)
    if entry is None:
        return False, f"Unknown LDraw part: {part_ref}"
    if not entry.get("usable_as_model_part", False):
        return False, f"LDraw file is not approved as a top-level model part: {part_ref}"
    return True, "verified"


def validate_color_code(catalog: dict, color: int) -> tuple[bool, str]:
    if isinstance(color, bool) or not isinstance(color, int):
        return False, f"LDraw color code must be an integer: {color!r}"
    entry = catalog.get("colors", {}).get(str(color))
    if entry is None:
        return False, f"Unknown LDraw color code: {color}"
    return True, entry.get("name", "verified")
