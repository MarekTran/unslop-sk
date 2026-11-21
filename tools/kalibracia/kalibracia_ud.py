#!/usr/bin/env python3
"""Kalibrácia metriky.py na ľudských textoch z Universal Dependencies.

Meria falošné poplachy: podiel ľudských úsekov, kde skript hlási nález P0 alebo P1,
a ktoré položky slova.md ich spúšťajú. Citlivosť na AI text nemeria.

Dáta (UD Slovak-SNK, CC BY-SA 4.0; do repozitára nepatria) stiahnite z GitHubu
UniversalDependencies:
  UD_Slovak-SNK/sk_snk-ud-train.conllu, sk_snk-ud-dev.conllu, sk_snk-ud-test.conllu

SNK je výber viet z dokumentov (blogy, publicistika, beletria, Wikipédia), nie súvislé
texty: úsek spája vety toho istého dokumentu, ktoré v ňom nemusia ísť hneď po sebe.
Čísla o slovách a frázach sú preto spoľahlivé, čísla o rytme, reťaziach spájacích
výrazov a zámenách v susedných vetách len orientačné.

Režimy:
  --gold          zlatá anotácia z CoNLL-U namiesto modelu UDPipe (lemy, slovné druhy,
                  závislosti). Položky slova.md sa lematizujú slovníkom tvar → lema
                  zo zadaných súborov (a z --slovnik), takže párovanie je približné.
  --udpipe CESTA  model UDPipe ako v bežnej prevádzke.
  bez oboch       režim bez modelu.

Príklad:
  python3 tools/kalibracia/kalibracia_ud.py sk_snk-ud-train.conllu
  python3 tools/kalibracia/kalibracia_ud.py --gold --slovnik sk_snk-ud-dev.conllu \\
      sk_snk-ud-train.conllu
"""
import argparse
import collections
import json
import os
import re
import sys

KOREN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(KOREN, "plugins", "unslop-sk", "skills", "unslop-sk", "scripts"))
import metriky  # noqa: E402


HRANICE = "dokument"   # dokument | zdroj | ziadne (prepína --hranice)


def nacti_conllu(cesta):
    """Vráti zoznam dokumentov; dokument = zoznam viet; veta = (text, tokeny, mwt).
    Hranicu dokumentu dáva „# newdoc“, alebo zmena dokumentu v sent_id (SNK:
    „zdroj:dokument:veta“)."""
    docs, doc, text, toks, mwt = [], [], None, [], []
    akt_doc = None
    with open(cesta, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# newdoc"):
                if doc:
                    docs.append(doc)
                doc = []
            elif line.startswith("# sent_id = ") and line.count(":") >= 2:
                d = line[12:].rsplit(":", 1)[0]
                if HRANICE == "zdroj":
                    d = d.split(":", 1)[0]
                elif HRANICE == "ziadne":
                    d = ""
                if akt_doc is not None and d != akt_doc and doc:
                    docs.append(doc)
                    doc = []
                akt_doc = d
            elif line.startswith("# text = "):
                text = line[9:]
            elif not line:
                if toks:
                    doc.append((text, toks, mwt))
                text, toks, mwt = None, [], []
            elif not line.startswith("#"):
                c = line.split("\t")
                if "-" in c[0]:
                    a, b = map(int, c[0].split("-"))
                    mwt.append((a, b, c[1]))
                elif "." not in c[0]:
                    toks.append(c)
    if toks:
        doc.append((text, toks, mwt))
    if doc:
        docs.append(doc)
    return docs


def featy(s):
    out = {}
    if s != "_":
        for f in s.split("|"):
            if "=" in f:
                k, v = f.split("=", 1)
                out[k] = v
    return out


class GoldUD:
    """Náhrada za metriky.UDPipe: pre registrované úseky vracia zlatú anotáciu."""

    def __init__(self, slovnik):
        self.slovnik = slovnik      # tvar → (lema, upos, feats)
        self.useky = {}             # text úseku → zoznam viet (text, tokeny, mwt)

    def registruj(self, text, vety):
        self.useky[text] = vety

    def _zarovnej(self, text, vety):
        vys, kurzor = [], 0
        for _, toks, mwt in vety:
            povrch = {}
            for a, b, form in mwt:
                for i in range(a, b + 1):
                    povrch[i] = form
            akt, mwt_rozsah = [], {}
            for c in toks:
                i = int(c[0])
                form = povrch.get(i, c[1])
                if i in povrch and form in mwt_rozsah:
                    s, e = mwt_rozsah[form]
                else:
                    s = text.find(form, kurzor)
                    if s < 0 or s - kurzor > 40:
                        continue
                    e = s + len(form)
                    kurzor = e
                    if i in povrch:
                        mwt_rozsah = {form: (s, e)}
                akt.append(metriky.Tok(c[1], c[2], c[3], featy(c[5]),
                                       int(c[6]) if c[6].isdigit() else 0, c[7], s, e,
                                       len(akt)))
            if akt:
                vys.append(akt)
        return vys

    def zpracuj(self, text, presegmented=False):
        if text in self.useky:
            return self._zarovnej(text, self.useky[text])
        # položky slova.md a neznáme úseky: pravidlá + slovník tvar → lema
        vety = []
        radky = text.split("\n") if presegmented else [text]
        pos = 0
        for r in radky:
            toks = metriky.tokeny_pravidla(text, pos, pos + len(r))
            for i, t in enumerate(toks):
                lem, upos, ft = self.slovnik.get(t.form.lower(), (t.form.lower(), "", {}))
                if not upos:
                    upos = "PUNCT" if not any(ch.isalnum() for ch in t.form) else "X"
                t.lemma, t.upos, t.feats, t.idx = lem, upos, dict(ft), i
            vety.append(toks)
            pos += len(r) + 1
        return vety


def slovnik_z(cesty):
    cet = collections.defaultdict(collections.Counter)
    for c in cesty:
        for doc in nacti_conllu(c):
            for _, toks, _ in doc:
                for t in toks:
                    cet[t[1].lower()][(t[2], t[3], t[5])] += 1
    return {k: (v.most_common(1)[0][0][0], v.most_common(1)[0][0][1],
                featy(v.most_common(1)[0][0][2])) for k, v in cet.items()}


def useky(docs, slov):
    """Úseky po aspoň `slov` slovách, neprekračujú hranice dokumentu."""
    for doc in docs:
        akt, n = [], 0
        for v in doc:
            akt.append(v)
            n += sum(1 for t in v[1] if t[3] != "PUNCT")
            if n >= slov:
                yield akt
                akt, n = [], 0
        if n >= slov * 0.6:
            yield akt


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("conllu", nargs="+")
    ap.add_argument("--gold", action="store_true")
    ap.add_argument("--udpipe")
    ap.add_argument("--slovnik", action="append", default=[],
                    help="ďalší CoNLL-U len pre slovník tvar → lema (režim --gold)")
    ap.add_argument("--slova", default=metriky.vychozi_slova())
    ap.add_argument("--profil", default="blog")
    ap.add_argument("--slov", type=int, default=190)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hranice", choices=["dokument", "zdroj", "ziadne"], default="dokument",
                    help="kde sa úsek nesmie pretiahnuť: cez dokument (predvolené), cez zdroj "
                         "(prvá časť sent_id; využije aj dokumenty s pár vetami), alebo nikde")
    a = ap.parse_args(argv)
    global HRANICE
    HRANICE = a.hranice

    gold = GoldUD(slovnik_z(a.conllu + a.slovnik)) if a.gold else None
    model = metriky.nacti_udpipe(a.udpipe) if a.udpipe else None
    vysledky = {}
    for cesta in a.conllu:
        jm = os.path.basename(cesta).replace(".conllu", "")
        poc_useku, slov_celkem = 0, 0
        s_nalezem = collections.Counter()
        polozky = collections.Counter()
        p2 = collections.Counter()
        hodnoty = collections.defaultdict(list)
        boh = collections.Counter()
        s_akymkolvek = 0
        for u in useky(nacti_conllu(cesta), a.slov):
            text = " ".join(v[0] for v in u)
            if gold:
                gold.registruj(text, u)
            an = metriky.Analyza(text, a.profil, gold or model, a.slova).spust()
            poc_useku += 1
            slov_celkem += an.doc.pocet_slov()
            kat = set()
            for n in an.nalezy:
                if n.zavaznost in ("P0", "P1"):
                    kat.add((n.zavaznost, n.metrika, n.kategorie))
                    if n.zdroj:
                        polozky[(n.zavaznost, n.zdroj)] += 1
                elif n.zavaznost == "P2":
                    p2[(n.metrika, n.kategorie)] += 1
                elif n.metrika == "bohemizmy" and n.zdroj:
                    boh[n.zdroj] += 1
            s_akymkolvek += bool(kat)
            for k in kat:
                s_nalezem[k] += 1
            m = an.metriky
            for klic, cesta_m in (
                    ("ktory_na_1000", ("sudrznost", "ktory_na_1000_slov")),
                    ("co_na_100", ("sudrznost", "co_na_100_viet")),
                    ("cisla_na_1000", ("konkretnost", "cisla_na_1000_slov")),
                    ("vlastne_mena_na_1000", ("konkretnost", "vlastne_mena_na_1000_slov")),
                    ("castice_mod_na_1000", ("postoj", "modalne_na_1000_slov")),
                    ("oslabujuce_na_1000", ("postoj", "oslabujuce_na_1000_slov")),
                    ("zamena_2os_na_1000", ("postoj", "osoba2_zamena_na_1000_slov")),
                    ("otazniky_na_100", ("postoj", "otazniky_na_100_viet")),
                    ("tento_na_zaciatku", ("sudrznost", "tento_na_zaciatku_podiel_viet"))):
                x = m.get(cesta_m[0], {}).get(cesta_m[1])
                if x is not None:
                    hodnoty[klic].append(x)
        vysledky[jm] = {
            "usekov": poc_useku, "slov": slov_celkem,
            "p0p1_aspon_jeden": round(s_akymkolvek / poc_useku, 3) if poc_useku else 0,
            "p0p1_podiel_usekov": {f"{z} {me}/{ka}": round(c / poc_useku, 3)
                                   for (z, me, ka), c in s_nalezem.most_common()},
            "p0p1_polozky": {f"{z} {zd}": c for (z, zd), c in polozky.most_common()},
            "p2_vyskyty": {f"{me}/{ka}": c for (me, ka), c in p2.most_common(15)},
            "info_bohemizmy": {zd: c for zd, c in boh.most_common(15)},
            "mediany": {k: sorted(v)[len(v) // 2] for k, v in hodnoty.items() if v},
            "priemery": {k: round(sum(v) / len(v), 2) for k, v in hodnoty.items() if v},
        }
    if a.json:
        print(json.dumps(vysledky, ensure_ascii=False, indent=1))
        return
    for jm, r in vysledky.items():
        print(f"== {jm}: {r['usekov']} úsekov, {r['slov']} slov")
        print(f"  úseky s aspoň jedným nálezom P0/P1: {r['p0p1_aspon_jeden']:.1%}")
        print("  podiel úsekov s nálezom P0/P1 podľa kategórie:")
        for k, v in r["p0p1_podiel_usekov"].items():
            print(f"    {v:6.1%}  {k}")
        if r["p0p1_polozky"]:
            print("  položky slova.md s P0/P1 (počet výskytov):")
            for k, v in r["p0p1_polozky"].items():
                print(f"    {v:3d}×  {k}")
        print("  najčastejšie P2:", ", ".join(f"{k} {v}" for k, v in r["p2_vyskyty"].items()))
        if r["info_bohemizmy"]:
            print("  rozšírené bohemizmy (info):",
                  ", ".join(f"{k} {v}" for k, v in r["info_bohemizmy"].items()))
        if r["mediany"]:
            print("  mediány:", r["mediany"])
            print("  priemery:", r["priemery"])


if __name__ == "__main__":
    main()
