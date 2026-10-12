#!/usr/bin/env python3
"""Récupère les derniers posts Instagram des apps du studio (API Graph de Meta).

Lancé chaque jour par .github/workflows/instagram.yml, puis build_instagram.py
régénère la page « Sur Instagram ». Écrit :
- data/instagram.json : pour chaque app, ses 6 derniers posts (lien, légende, date, type) ;
- assets/instagram/<app>/<id>.jpg : copie légère du visuel (720 px), pour que la page
  ne charge rien depuis Instagram. Les anciens visuels sont supprimés.

Jeton : variable d'environnement IG_ACCESS_TOKEN (secret GitHub, jamais dans le dépôt).
Un jeton de page Facebook ou d'utilisateur système Meta Business avec les droits
`instagram_basic` et `pages_show_list` suffit : les comptes Instagram professionnels
liés aux pages sont retrouvés par leur nom (champ `instagram` de data/apps.json).

    IG_ACCESS_TOKEN=… python3 scripts/fetch_instagram.py
"""
import datetime
import io
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
APPS = json.loads((SITE / "data/apps.json").read_text(encoding="utf-8"))["apps"]
GRAPH = "https://graph.facebook.com"
PER_ACCOUNT = 6
WIDTH = 720


def get(path, **params):
    params["access_token"] = os.environ["IG_ACCESS_TOKEN"]
    url = f"{GRAPH}/{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def ig_accounts():
    """Nom d'utilisateur Instagram → identifiant du compte professionnel."""
    found, url_params = {}, {"fields": "instagram_business_account{id,username}", "limit": 100}
    data = get("me/accounts", **url_params)
    while True:
        for page in data.get("data", []):
            ig = page.get("instagram_business_account")
            if ig and ig.get("username"):
                found[ig["username"].lower()] = ig["id"]
        nxt = data.get("paging", {}).get("next")
        if not nxt:
            return found
        with urllib.request.urlopen(nxt, timeout=30) as r:
            data = json.load(r)


def save_image(url, dest):
    from PIL import Image  # installé par le workflow (pip install pillow)
    with urllib.request.urlopen(url, timeout=60) as r:
        im = Image.open(io.BytesIO(r.read())).convert("RGB")
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / im.width)))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "JPEG", quality=78, optimize=True, progressive=True)


def main():
    if not os.environ.get("IG_ACCESS_TOKEN"):
        # Pas encore de jeton : la tâche quotidienne ne doit pas échouer (et envoyer un
        # e-mail d'erreur chaque jour) ; la page reste simplement non générée.
        print("IG_ACCESS_TOKEN absent : rien à récupérer")
        return
    ids = ig_accounts()
    out = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "accounts": {}}
    keep = set()
    for app in APPS:
        user = (app.get("instagram") or "").lower()
        if not user:
            continue
        if user not in ids:
            print(f"  {app['slug']} : compte @{user} introuvable avec ce jeton")
            continue
        media = get(f"{ids[user]}/media", fields="id,caption,media_type,media_url,thumbnail_url,permalink,timestamp",
                    limit=PER_ACCOUNT).get("data", [])
        posts = []
        for m in media:
            src = m.get("thumbnail_url") if m.get("media_type") == "VIDEO" else m.get("media_url")
            if not src:
                continue
            rel = f"assets/instagram/{app['slug']}/{m['id']}.jpg"
            dest = SITE / rel
            if not dest.exists():
                save_image(src, dest)
            keep.add(dest)
            posts.append({"id": m["id"], "type": m.get("media_type"), "permalink": m["permalink"],
                          "caption": m.get("caption", ""), "timestamp": m["timestamp"], "image": rel})
        out["accounts"][app["slug"]] = {"username": app["instagram"], "posts": posts}
        print(f"  {app['slug']} : {len(posts)} posts")
    for old in (SITE / "assets/instagram").glob("*/*.jpg"):
        if old not in keep:
            old.unlink()
    (SITE / "data/instagram.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
