#!/usr/bin/env python3
"""Prépare les données de la page « Sur Instagram » depuis data/instagram_posts.txt.

Choix de Lucas (2026-10-12) : pas de mise à jour automatique ; on relève les
derniers posts à la main (dans Chrome, sur les profils) quand on met le site à
jour, puis on relance ce script et build_instagram.py.

Pour chaque post listé :
- la date vient du code du post (l'identifiant Instagram contient l'heure de
  publication : (id >> 23) millisecondes depuis le 24/08/2011) ;
- le visuel est la copie publique du post (/p/<code>/media/?size=l, couverture
  pour un Reel), réduite à 720 px dans assets/instagram/<app>/<code>.jpg.
  Les anciens visuels qui ne sont plus listés sont supprimés.
Écrit data/instagram.json, lu par build_instagram.py.

    python3 scripts/import_instagram.py
"""
import datetime
import json
import re
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
APPS = {a["slug"]: a for a in json.loads((SITE / "data/apps.json").read_text(encoding="utf-8"))["apps"]}
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
IG_EPOCH_MS = 1314220021721
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15"


def posted_at(code):
    media_id = 0
    for ch in code:
        media_id = media_id * 64 + ALPHABET.index(ch)
    ms = (media_id >> 23) + IG_EPOCH_MS
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).isoformat(timespec="seconds")


def download(code, dest):
    req = urllib.request.Request(f"https://www.instagram.com/p/{code}/media/?size=l", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        if not r.headers.get("Content-Type", "").startswith("image/"):
            raise SystemExit(f"{code} : pas d'image (post supprimé ou privé ?)")
        raw = r.read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
        tmp.write(raw)
        tmp.flush()
        subprocess.run(["sips", "-Z", "720", "-s", "format", "jpeg", "-s", "formatOptions", "78", tmp.name, "--out", str(dest)],
                       check=True, capture_output=True)


def main():
    out = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "accounts": {}}
    keep = set()
    for line in (SITE / "data/instagram_posts.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        m = re.match(r"(\w+)\s+([pr])\s+([\w-]+)\s*\|\s*(.*)$", line)
        if not m:
            raise SystemExit(f"ligne illisible : {line}")
        slug, kind, code, cap = m.groups()
        if slug not in APPS or not APPS[slug].get("instagram"):
            raise SystemExit(f"{slug} : app inconnue ou sans compte Instagram")
        user = APPS[slug]["instagram"]
        rel = f"assets/instagram/{slug}/{code}.jpg"
        dest = SITE / rel
        if not dest.exists():
            download(code, dest)
            time.sleep(1)  # 48 requêtes d'affilée : on reste poli avec Instagram
        keep.add(dest)
        out["accounts"].setdefault(slug, {"username": user, "posts": []})["posts"].append({
            "id": code, "type": "VIDEO" if kind == "r" else "IMAGE",
            "permalink": f"https://www.instagram.com/{user}/{'reel' if kind == 'r' else 'p'}/{code}/",
            "caption": cap.replace("�", "").strip(), "timestamp": posted_at(code), "image": rel})
    for acc in out["accounts"].values():
        acc["posts"].sort(key=lambda p: p["timestamp"], reverse=True)
    for old in (SITE / "assets/instagram").glob("*/*.jpg"):
        if old not in keep:
            old.unlink()
    (SITE / "data/instagram.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n = sum(len(a["posts"]) for a in out["accounts"].values())
    print(f"{n} posts de {len(out['accounts'])} comptes importés")


if __name__ == "__main__":
    main()
