#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Slovný diff po vetách a kontrola tichej straty pri prepise slovenského textu.

    python3 diff.py pred.txt po.txt [--format md|json|oboje] [--metriky]
                    [--profil blog] [--udpipe cesta] [--prisne]

Len štandardná knižnica. Nezávisí od locale ani od gitu. Vety, maskovanie kódu a citácií
a kmene pre skloňované mená berie z metriky.py v tom istom priečinku.

Výstup md: slovný diff (len zmenené vety, značky [-zmazané-] a {+pridané+}), oddiel
Tichá strata a s --metriky riadok metrík pred → po. Výstup json: zmeny, straty, metriky.
Návratový kód je 0; s --prisne 1, keď straty nie sú prázdne.

Kontrola straty porovnáva počty výskytov v zdroji a v novej verzii: čísla (presná zhoda),
vlastné mená (zhoda kmeňa, bez modelu len približne), častice a istenie (zoznam nižšie
a zoznamy z metriky.py) a markery sily tvrdenia (príčina, miera, absolútnosť; len info).
Čo leží v kóde, citáciách „>“ a URL, sa nepočíta.
"""
import argparse
import difflib
import json
import os
import re
import sys
from collections import Counter

TADY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TADY)
import metriky  # noqa: E402

SLOVO = re.compile(r"\w+(?:[.,]\d+)*|\S|\s+")
CISLO = re.compile(r"\d")
# Názvy pomocných funkcií v metriky.py (kmeň a zhoda kmeňov); staršie mená ako záloha.
_KMEN = metriky.kmen
_ZHODA_KMENOV = getattr(metriky, "zhoda_kmenov", None) or getattr(metriky, "shoda_kmenu")

# Markery sily tvrdenia (príčina, miera, absolútnosť). Len info: strata tu môže byť zámerná.
SILA = {"spôsobuje", "spôsobil", "spôsobila", "spôsobujú", "pretože", "lebo", "kvôli",
        "dvakrát", "trikrát", "štyrikrát", "vždy", "nikdy", "nesmie", "nesmú", "musí",
        "musia", "každý", "žiadny", "všetci", "výhradne", "iba", "jedine", "výlučne"}
# Častice a istenie, ktoré prepis nemá mazať (SKILL.md, poistky). Zoznam je tu, aby diff
# fungoval rovnako bez ohľadu na zoznamy v metriky.py; tie sa k nemu pridajú.
CASTICE = {"predsa", "veď", "vraj", "totiž", "vlastne", "hádam", "no", "teda", "napokon",
           "aspoň", "hlavne", "akosi", "nuž", "ostatne", "beztak", "celkom", "dosť"}
ISTENIE = {"snáď", "asi", "možno", "zrejme", "pravdepodobne", "údajne", "azda", "zhruba",
           "približne", "takmer", "skoro", "sotva"}
CASTICE_ISTENIE = CASTICE | ISTENIE
for _zoznam in ("CASTICE", "MODALNE", "MODALNI", "OSLABUJUCE", "OSLABUJICI"):
    CASTICE_ISTENIE |= {s for s in getattr(metriky, _zoznam, ()) if " " not in s}


def _maskuj(text, vse=False):
    masked, _ = metriky.maskuj(text, vse)
    return masked


def deleni_na_vety(text):
    """Vety z textu bez kódu a citácií; masku nahradí prázdnym miestom, takže vety sú čisté."""
    masked = _maskuj(text)
    vety = []
    for a, b in metriky.deleni_vet_pravidla(masked, 0, len(masked)):
        v = re.sub(r"[ \t\r\n]+", " ", masked[a:b]).strip()
        if v:
            vety.append(v)
    return vety


def _spoj(tokeny):
    return "".join(tokeny)


def _zmeny(x, y):
    """Opkódy difflib; medzera medzi dvoma zmenami patrí k zmene, susedné zmeny sa zlučujú."""
    ops = difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes()
    for n, (o, k1, k2, l1, l2) in enumerate(ops):
        if 0 < n < len(ops) - 1 and o == "equal" and _spoj(x[k1:k2]).isspace():
            ops[n] = ("replace", k1, k2, l1, l2)
    sloucene = []
    for o, k1, k2, l1, l2 in ops:
        if sloucene and o != "equal" and sloucene[-1][0] != "equal":
            sloucene[-1] = ("replace", sloucene[-1][1], k2, sloucene[-1][3], l2)
        else:
            sloucene.append((o, k1, k2, l1, l2))
    return sloucene


def slovni_diff(pred, po):
    """Vráti zoznam zmien: {veta_pred, veta_po, diff, useky:[{pred, po}]}."""
    a, b = deleni_na_vety(pred), deleni_na_vety(po)
    vysledek = []
    for o, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if o == "equal":
            continue
        if i2 - i1 == j2 - j1:  # rovnaký počet viet: zmenu priraď každej vete osobitne
            dvojice = [(a[i1 + k], b[j1 + k]) for k in range(i2 - i1)]
        else:
            dvojice = [("\n".join(a[i1:i2]), "\n".join(b[j1:j2]))]
        for vp, vn in dvojice:
            vysledek.append(_diff_vety(vp, vn))
    return vysledek


def _diff_vety(vp, vn):
    x, y = SLOVO.findall(vp), SLOVO.findall(vn)
    radek, useky = [], []
    for o2, k1, k2, l1, l2 in _zmeny(x, y):
        if o2 == "equal":
            radek.append(_spoj(x[k1:k2]))
            continue
        smaz, pridej = _spoj(x[k1:k2]), _spoj(y[l1:l2])
        if smaz:
            radek.append("[-" + smaz + "-]")
        if pridej:
            radek.append("{+" + pridej + "+}")
        useky.append({"pred": smaz, "po": pridej})
    return {"veta_pred": vp, "veta_po": vn, "diff": "".join(radek), "useky": useky}


def _tokeny(text):
    """Slová a čísla z textu bez kódu a citácií; vracia (token, je_na_zaciatku_vety)."""
    masked = _maskuj(text)
    out = []
    for a, b in metriky.deleni_vet_pravidla(masked, 0, len(masked)):
        prvni = True
        for m in re.finditer(r"\w+(?:[.,]\d+)*", masked[a:b]):
            out.append((m.group(0), prvni))
            prvni = False
    return out


def _je_meno(tok, zaciatok):
    return (not zaciatok and tok[:1].isupper() and not tok.isupper()
            and not CISLO.search(tok) and len(tok) > 1)


def _zhoda_mena(a, b):
    """Zhoda kmeňa z metriky.py, rozšírená o striedanie koncovky (Nitra/Nitre, Košice/Košíc):
    spoločný začiatok aspoň z troch znakov a rozdiel najviac dva znaky na konci."""
    if _ZHODA_KMENOV(a, b):
        return True
    cp = 0
    for x, y in zip(a, b):
        if x != y:
            break
        cp += 1
    n = min(len(a), len(b))
    return cp >= 3 and cp >= n - 2 and abs(len(a) - len(b)) <= 2


def _chyba_podla_kmena(zdroj, nova):
    """Mená zo zdroja, ku ktorým v novej verzii nezostáva meno so zhodným kmeňom."""
    volna = [_KMEN(t) for t in nova]
    chyba = []
    for t in zdroj:
        k = _KMEN(t)
        for i, n in enumerate(volna):
            if _zhoda_mena(k, n):
                del volna[i]
                break
        else:
            chyba.append(t)
    return chyba


def _ubudlo(zdroj, nova, filtr):
    a = Counter(t for t in zdroj if filtr(t))
    b = Counter(t for t in nova if filtr(t))
    return sorted((a - b).elements())


def straty(pred, po, model=False):
    tp, tn = _tokeny(pred), _tokeny(po)
    slova_p, slova_n = [t.lower() for t, _ in tp], [t.lower() for t, _ in tn]
    mena_p = [t for t, z in tp if _je_meno(t, z)]
    mena_n = [t for t, z in tn if _je_meno(t, z)]
    return {
        "cisla": _ubudlo([t for t, _ in tp], [t for t, _ in tn], CISLO.search),
        "mena": _chyba_podla_kmena(mena_p, mena_n),
        "castice": _ubudlo(slova_p, slova_n, lambda t: t in CASTICE_ISTENIE),
        "markery_sily": _ubudlo(slova_p, slova_n, lambda t: t in SILA),
        "priblizne_mena": not model,
    }


def _prazdne(z):
    return not any(z[k] for k in ("cisla", "mena", "castice"))


# Riadok metrík: popis a kľúč v metriky.py (druhý kľúč je starší názov, ak ho skript má).
POLOZKY_METRIK = [("častice", ("modalne_na_1000_slov", "modalni_na_1000_slov")),
                  ("istenie", ("oslabujuce_na_1000_slov", "oslabujici_na_1000_slov")),
                  ("otázky", ("otazniky_na_100_viet", "otazniky_na_100_vet")),
                  ("čísla", ("cisla_na_1000_slov",)),
                  ("mená", ("vlastne_mena_na_1000_slov", "vlastni_jmena_na_1000_slov"))]


def _hodnota(m, kluce):
    for oddiel in m["metriky"].values():
        if isinstance(oddiel, dict):
            for k in kluce:
                if k in oddiel:
                    return oddiel[k]
    raise KeyError("metriky.py nevracia metriku %s" % kluce[0])


def _riadok_metrik(mp, mn):
    def fmt(x):
        return ("%g" % x).replace(".", ",")
    return "Metriky pred → po: " + " · ".join(
        "%s %s → %s" % (n, fmt(_hodnota(mp, k)), fmt(_hodnota(mn, k)))
        for n, k in POLOZKY_METRIK)


def metriky_pred_po(pred, po, profil, udpipe):
    mp = metriky.analyzuj(pred, profil, udpipe)
    mn = metriky.analyzuj(po, profil, udpipe)

    def hodnoty(m):
        return {n: _hodnota(m, k) for n, k in POLOZKY_METRIK}
    return {"pred": hodnoty(mp), "po": hodnoty(mn),
            "riadok": _riadok_metrik(mp, mn)}


def md(zmeny, z, met):
    out = []
    if zmeny:
        out += ["```text"]
        out += ["[%d] %s" % (i, s["diff"]) for i, s in enumerate(zmeny, 1)]
        out += ["```"]
    else:
        out += ["Bez zmeny."]
    out += ["", "**Tichá strata**", ""]
    if _prazdne(z):
        out += ["Nič nechýba: čísla, mená, častice ani istenie."]
    else:
        for kluc, popis in (("cisla", "čísla"), ("mena", "mená"),
                            ("castice", "častice a istenie")):
            if z[kluc]:
                out += ["- %s: %s" % (popis, ", ".join(z[kluc]))]
        if z["mena"] and z["priblizne_mena"]:
            out += ["- mená sú bez modelu približné, over ich v diffe"]
    if z["markery_sily"]:
        out += ["- info, sila tvrdenia: ubudlo %s (over, že zmena nie je oslabenie)"
                % ", ".join(z["markery_sily"])]
    if met:
        out += ["", met["riadok"]]
    return "\n".join(out) + "\n"


def main(argv=None):
    metriky.utf8_stdio()
    ap = argparse.ArgumentParser(description="Slovný diff po vetách a tichá strata.")
    ap.add_argument("pred", help="zdrojový text")
    ap.add_argument("po", help="nová verzia")
    ap.add_argument("--format", choices=["md", "json", "oboje"], default="md")
    ap.add_argument("--metriky", action="store_true", help="pridá metriky pred → po")
    ap.add_argument("--profil", default="blog")
    ap.add_argument("--udpipe", default=os.environ.get("UNSLOP_UDPIPE"))
    ap.add_argument("--prisne", action="store_true", help="návratový kód 1 pri strate")
    a = ap.parse_args(argv)
    with open(a.pred, encoding="utf-8") as f:
        pred = f.read()
    with open(a.po, encoding="utf-8") as f:
        po = f.read()
    zmeny = slovni_diff(pred, po)
    z = straty(pred, po, bool(a.udpipe))
    met = metriky_pred_po(pred, po, a.profil, a.udpipe) if a.metriky else None
    if a.format in ("md", "oboje"):
        sys.stdout.write(md(zmeny, z, met))
    if a.format in ("json", "oboje"):
        print(json.dumps({"zmeny": zmeny, "straty": z, "metriky": met},
                         ensure_ascii=False, indent=2))
    return 1 if a.prisne and not _prazdne(z) else 0


if __name__ == "__main__":
    sys.exit(main())
