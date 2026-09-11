#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, unicodedata
from pathlib import Path

DEFAULT_ENVELOPES = {
    "vehicle": (10, 20, 8),
    "building": (20, 16, 16),
    "furniture": (12, 8, 10),
    "animal": (10, 16, 12),
    "generic": (12, 16, 12),
}
SUBJECT_CLASSES = {
    "vehicle": ["bil", "traktor", "lastbil", "buss", "tåg", "tag", "motorcykel", "fordon", "car", "tractor", "truck", "bus", "train"],
    "building": ["hus", "stuga", "byggnad", "torn", "slott", "garage", "house", "cabin", "building", "tower", "castle"],
    "furniture": ["bord", "stol", "pall", "soffa", "table", "chair", "stool", "sofa"],
    "animal": ["hund", "katt", "häst", "hast", "fågel", "fagel", "djur", "dog", "cat", "horse", "bird", "animal"],
}
COLOR_ALIASES = {
    "svart": "Black", "black": "Black", "blå": "Blue", "bla": "Blue", "blue": "Blue",
    "grön": "Green", "gron": "Green", "green": "Green", "röd": "Red", "rod": "Red", "red": "Red",
    "gul": "Yellow", "yellow": "Yellow", "vit": "White", "white": "White",
    "ljusgrå": "Light Grey", "ljusgra": "Light Grey", "light grey": "Light Grey", "light gray": "Light Grey"
}

def norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s).lower().strip()

def color_index(catalog: dict) -> dict[str, tuple[int,str]]:
    out = {}
    for code, meta in catalog.get("colors", {}).items():
        name = meta.get("name")
        if name:
            out[norm(name)] = (int(code), name)
    return out

def classify(text: str) -> str:
    for cls, words in SUBJECT_CLASSES.items():
        if any(re.search(r"\b" + re.escape(w) + r"\b", text) for w in words):
            return cls
    return "generic"

def infer_subject(text: str) -> str:
    m = re.search(r"(?:bygg|build|gör|gor|make)\s+(?:en|ett|a|an)?\s*([\wåäöÅÄÖ-]+(?:\s+[\wåäöÅÄÖ-]+){0,3})", text, re.I)
    if m:
        s = re.split(r"[,.;]|\b(?:med|max|ungefär|ungefar|cirka|about|approximately)\b", m.group(1), maxsplit=1, flags=re.I)[0].strip()
        if s: return s
    return "LEGO-modell"

def interpret(prompt: str, catalog: dict) -> dict:
    t = norm(prompt)
    cls = classify(t)
    assumptions, constraints, questions = [], [], []

    if re.search(r"\b(display|displaymodell|utställning|utstallning|prydnad)\b", t): usage = "display"
    elif re.search(r"\b(leksak|lekbar|för lek|for lek|playable|toy)\b", t): usage = "play"
    else: usage = "unspecified"

    if re.search(r"\b(enkel|enkelt|simple|för barn|for barn)\b", t): detail = "simple"
    elif re.search(r"\b(detaljerad|detaljerat|mycket detaljer|detailed|high detail)\b", t): detail = "detailed"
    else:
        detail = "balanced"
        assumptions.append("Detaljnivå saknades; balanced används som konservativ standard.")

    max_parts = None
    m = re.search(r"(?:max(?:imalt)?|högst|hogst|inte mer än|inte mer an|under|at most|max)\s*(\d+)\s*(?:delar|bitar|parts|pieces)", t)
    if m:
        max_parts = int(m.group(1)); constraints.append(f"Max {max_parts} delar.")

    ci = color_index(catalog); colors=[]; seen=set()
    for alias, canonical in sorted(COLOR_ALIASES.items(), key=lambda kv: -len(kv[0])):
        if re.search(r"\b" + re.escape(alias) + r"\b", t) and canonical not in seen:
            hit = ci.get(norm(canonical))
            if hit:
                colors.append({"ldraw_code": hit[0], "name": hit[1], "source": "explicit"}); seen.add(canonical)
    # Full W x D x H form.
    triple = re.search(r"(\d+(?:[.,]\d+)?)\s*[x×]\s*(\d+(?:[.,]\d+)?)\s*[x×]\s*(\d+(?:[.,]\d+)?)\s*(?:studs?|knoppar)?", t)
    default = list(DEFAULT_ENVELOPES[cls]); source = "inferred"
    if triple:
        env = [float(x.replace(',', '.')) for x in triple.groups()]; source="explicit"
    else:
        env = default
        # Named single dimensions. Swedish "lång" and English "long" map to depth.
        patterns = [
            (0, r"(\d+(?:[.,]\d+)?)\s*(?:studs?|knoppar)?\s*(?:bred|wide)\b"),
            (1, r"(\d+(?:[.,]\d+)?)\s*(?:studs?|knoppar)?\s*(?:lång|lang|long)\b"),
            (2, r"(\d+(?:[.,]\d+)?)\s*(?:studs?|knoppar)?\s*(?:hög|hog|high|tall)\b"),
        ]
        explicit_count=0
        for idx, pat in patterns:
            mm=re.search(pat,t)
            if mm:
                env[idx]=float(mm.group(1).replace(',','.')); explicit_count += 1
        if explicit_count:
            source="partially_explicit"
            assumptions.append(f"Ospecificerade dimensioner härleddes från standardprofilen för {cls}.")
        else:
            assumptions.append(f"Storlek saknades; standard-envelope för {cls} används som startpunkt.")

    # A strict physical size in cm cannot be mapped confidently without choosing orientation/scale.
    cm = re.search(r"(\d+(?:[.,]\d+)?)\s*cm\b", t)
    if cm and source == "inferred":
        questions.append({
            "id":"physical-size-axis", "question":"Vilken huvudriktning ska den angivna cm-storleken avse?",
            "reason":"En ensam fysisk längd kan avse bredd, djup eller höjd och ändrar modellens skala väsentligt.", "blocking": True
        })

    if not colors:
        assumptions.append("Ingen verifierbar explicit färg hittades; färgsättning bestäms senare med få kataloggiltiga färger.")

    return {
        "schema_version":"1.0", "source_prompt":prompt, "subject":infer_subject(prompt), "model_usage":usage,
        "detail_level":detail, "max_parts":max_parts, "preferred_colors":colors,
        "target_envelope_studs":{"width":env[0],"depth":env[1],"height":env[2],"source":source},
        "constraints":constraints, "assumptions":assumptions, "open_questions":questions
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("prompt"); ap.add_argument("--catalog", default="catalog/catalog.json"); ap.add_argument("--output")
    a=ap.parse_args(); catalog=json.loads(Path(a.catalog).read_text(encoding="utf-8")); result=interpret(a.prompt,catalog)
    text=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.output: Path(a.output).write_text(text,encoding="utf-8")
    else: print(text,end="")
if __name__ == "__main__": main()
