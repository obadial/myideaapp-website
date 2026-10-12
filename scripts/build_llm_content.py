#!/usr/bin/env python3
"""Rend chaque page d'app lisible par les moteurs IA (ChatGPT, Perplexity…) et par Bing.

Pourquoi : ChatGPT est la 2e source de téléchargements du studio (App Store
Connect › Sources › Apps référentes, oct. 2026), et sa recherche web s'appuie sur
l'index de Bing. Or le site est servi en français et traduit en JavaScript : un
robot ne voit jamais l'anglais. Ce script injecte, depuis les descriptions App
Store déjà validées par Apple (source unique de vérité) :

1. un bloc anglais statique « About <App> (English) » dans chaque `<app>/index.html`,
   entre les marqueurs `<!-- llm-en:start -->` / `<!-- llm-en:end -->` ;
2. des champs JSON-LD SoftwareApplication (`alternateName`, `featureList`,
   `inLanguage`, `sameAs`) ;
3. `llms.txt` à la racine (index lisible par les LLM) ;
4. les `<lastmod>` du sitemap pour les pages touchées.

Idempotent : relancer après toute modification d'une description App Store.
    python3 scripts/build_llm_content.py
"""
import datetime
import html
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
APPS_ROOT = SITE.parent / "application"
TODAY = datetime.date.today().isoformat()

# dossier du site → dossier du projet Flutter
APPS = {
    "rhythm": "Rhythm-app", "runfree": "runfree", "myfoodbook": "MyCookbook",
    "hydrome": "HydroMe", "stockwatch": "StockWatch", "enjoymeal": "enjoymeal",
    "chapter": "Chapter", "nova": "nova", "mantrame": "MantraMe",
    "lunarest": "luna-rest", "inhale": "inhale", "budgetbrief": "BudgetBrief",
}
LANGUAGES = ["en", "fr", "de", "es", "it", "pt", "hi", "ar"]
START, END = "<!-- llm-en:start -->", "<!-- llm-en:end -->"
_facts_path = SITE / "data" / "apps.json"
FACTS = ({a["slug"]: a for a in json.loads(_facts_path.read_text(encoding="utf-8"))["apps"]}
         if _facts_path.exists() else {})


def read_meta(app_dir: str, locale: str, field: str) -> str:
    p = APPS_ROOT / app_dir / "fastlane" / "metadata" / locale / f"{field}.txt"
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


def linkify(text: str) -> str:
    # Les descriptions App Store citent parfois /index.html : on lie l'URL canonique.
    esc = re.sub(r"(https://myideapp\.com/[^\s<]*?)index\.html", r"\1", html.escape(text))
    return re.sub(r"(https://[^\s<]+)", r'<a href="\1">\1</a>', esc)


def description_to_html(desc: str) -> tuple[str, list[str]]:
    """Convertit la description App Store en HTML ; renvoie aussi les intitulés de fonctions."""
    out, items, features = [], [], []

    def flush():
        if items:
            out.append("<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")
            items.clear()

    for raw in desc.splitlines():
        line = raw.strip()
        if not line:
            continue
        head = re.fullmatch(r"-{2,}\s*(.+?)\s*-{2,}", line)
        if head:
            flush()
            out.append(f"<h3>{html.escape(head.group(1).capitalize())}</h3>")
        elif line.isupper() and len(line) <= 40:
            # Intertitre en capitales (Rhythm, EnjoyMeal) : c'est lui qui nomme la fonction.
            flush()
            out.append(f"<h3>{html.escape(line.capitalize())}</h3>")
            features.append(line.capitalize())
        elif line[0] in "•–-":
            body = line.lstrip("•–- ").strip()
            if not body:  # ligne de séparation (« --- ») : pas une puce
                flush()
                continue
            items.append(linkify(body))
            title = re.split(r"\s[—–-]\s|:", body, maxsplit=1)[0].strip().rstrip(".")
            # Une puce sans intitulé est une phrase, pas un nom de fonction.
            if title and not title.startswith("http") and len(title.split()) <= 6:
                features.append(title)
        else:
            flush()
            out.append(f"<p>{linkify(line)}</p>")
    flush()
    return "\n        ".join(out), features


def build_block(name: str, body: str) -> str:
    return f"""{START}
  <section class="section" id="english" lang="en">
    <div class="container" style="max-width:760px;">
      <details class="faq-item" style="border-bottom:1px solid rgba(128,128,128,0.18);padding:1.15rem 0;">
        <summary style="cursor:pointer;font-weight:600;">About {html.escape(name)} (English)</summary>
        <div class="llm-en" style="margin-top:1rem;line-height:1.6;">
        {body}
        </div>
      </details>
    </div>
  </section>
  {END}"""


def patch_jsonld(page: str, en_name: str, features: list[str], store_url: str) -> str:
    def fix(m):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            return m.group(0)
        if data.get("@type") != "SoftwareApplication":
            return m.group(0)
        data["alternateName"] = en_name
        data["inLanguage"] = LANGUAGES
        if features:
            data["featureList"] = features[:12]
        if store_url:
            data["sameAs"] = [store_url]
        return ('<script type="application/ld+json">\n'
                + json.dumps(data, ensure_ascii=False, indent=2) + "\n  </script>")
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix, page, flags=re.S)


def main():
    llms = ["# MyIdeApp", "",
            "> Independent studio publishing privacy-first iOS apps. Data stays on the "
            "device whenever possible; no social feeds. Free to download, optional "
            "subscription. Site: https://myideapp.com/", "", "## Apps", ""]
    touched = []
    for site_dir, app_dir in APPS.items():
        page_path = SITE / site_dir / "index.html"
        desc = read_meta(app_dir, "en-US", "description")
        if not page_path.exists() or not desc:
            print(f"skip {site_dir}")
            continue
        en_name = read_meta(app_dir, "en-US", "name")
        subtitle = read_meta(app_dir, "en-US", "subtitle")
        page = page_path.read_text(encoding="utf-8")
        store = re.search(r'"downloadUrl":\s*"([^"]+)"', page)
        store_url = store.group(1) if store else ""

        body, features = description_to_html(desc)
        block = build_block(en_name.split(" - ")[0], body)
        if START in page:
            page = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, page, flags=re.S)
        else:
            page = page.replace('  <footer class="footer">', block + '\n\n  <footer class="footer">', 1)
        page = patch_jsonld(page, en_name, features, store_url)
        page_path.write_text(page, encoding="utf-8")
        touched.append(f"https://myideapp.com/{site_dir}/")

        first = next((l for l in desc.splitlines() if l.strip() and not l.startswith("---")), "")
        llms += [f"### {en_name}", f"{subtitle}. {first.strip()}",
                 f"- Page: https://myideapp.com/{site_dir}/"]
        if store_url:
            llms.append(f"- App Store: {store_url}")
        if features:
            llms.append("- Key features: " + "; ".join(features[:8]))
        fact = FACTS.get(site_dir)
        if fact:
            pr = fact["price"]
            llms.append("- Price: free to download; " + (
                f"optional Premium ${pr['monthly_usd']}/month or ${pr['annual_usd']}/year (France €{pr['monthly_eur'].replace(',', '.')}/€{pr['annual_eur'].replace(',', '.')})"
                if fact.get("premium_available", True) else "Premium option coming soon"))
            llms.append("- Free: " + fact["free"]["en"])
            if fact.get("premium_available", True):
                llms.append("- Premium adds: " + fact["premium"]["en"])
            llms.append(f"- Data: stored on device only, no account required. iOS {fact['ios_min']}+. 9 languages.")
        llms += [f"- Privacy policy: https://myideapp.com/{site_dir}/privacy.html", ""]
        print(f"ok {site_dir}: {len(features)} features")

    (SITE / "llms.txt").write_text("\n".join(llms).rstrip() + "\n", encoding="utf-8")

    sm_path = SITE / "sitemap.xml"
    sm = sm_path.read_text(encoding="utf-8")
    for url in touched + ["https://myideapp.com/"]:
        sm = re.sub(r"(<loc>" + re.escape(url) + r"</loc>\s*<lastmod>)[^<]+", r"\g<1>" + TODAY, sm)
    sm_path.write_text(sm, encoding="utf-8")
    print(f"llms.txt + sitemap ({len(touched)} pages, lastmod {TODAY})")


if __name__ == "__main__":
    main()
