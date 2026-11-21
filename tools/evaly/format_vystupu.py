#!/usr/bin/env python3
"""Spúšťa prípady 31 a 32 (formát výstupu prepisu) a meria tokeny.

Hlavný runner ich preskakuje, lebo nekontrolujú nálezy, ale tvar výstupu, a
ten sa hodnotí ručne podľa riadkov OČAKÁVANÉ v evals/pripady.md.
Tento skript len spustí skill s rovnakým zadaním a obmedzením nástrojov, uloží úplné
výstupy na ručnú kontrolu a spočíta tokeny rovnako ako runner.py, aby sa
východiskový stav a zmenený skill dali porovnať aj na týchto prípadoch.

  31: agent bez shellu a bez súborov (povolené nástroje: Skill, Read)
  32: agent s Pythonom a gitom, text v súbore vstup.txt

Použitie (z koreňa repozitára):
    python3 tools/evaly/format_vystupu.py --stitok format --model claude-sonnet-5-5

Výstup: tools/evaly/vysledky/<stitok>/format-vystupu.json a format-vystupu.md.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runner  # noqa: E402

NASTROJE = {
    31: "Skill Read",
    32: runner.NASTROJE_SKILLU + " Bash(git *)",
}

ZADANI_31 = """Použi skill unslop-sk (unslop-sk:unslop-sk). Prepíš to ľudsky, profil registra „blog“ (blog).

<text>
{vstup}
</text>"""

ZADANI_32 = """Použi skill unslop-sk (unslop-sk:unslop-sk). Prepíš to ľudsky, profil registra „blog“ (blog).
Rovnaký text je uložený v súbore vstup.txt (UTF-8) v pracovnom adresári.

<text>
{vstup}
</text>"""


def vstup_pripadu_31():
    """Text prípadu 31 z pripady.md (riadky „> “ pred prvým OČAKÁVANÉ)."""
    with open(runner.PRIPADY, encoding="utf-8") as f:
        riadky = f.read().splitlines()
    i = next(k for k, r in enumerate(riadky) if r.startswith("## Prípad 31"))
    vstup = []
    for r in riadky[i + 1:]:
        if r.startswith("OČAKÁVANÉ"):
            break
        if r.startswith(">"):
            vstup.append(r[2:] if r.startswith("> ") else r[1:])
    if not vstup:
        raise SystemExit("V prípade 31 chýba VSTUP.")
    return "\n".join(vstup).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stitok", required=True, help="názov behu, priečinok vo vysledky/")
    ap.add_argument("--pripady", default="31,32")
    ap.add_argument("--behy", type=int, default=1)
    ap.add_argument("--model")
    ap.add_argument("--udpipe")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--opakovania", dest="opakovani", type=int, default=3)
    ap.add_argument("--pauza", type=int, default=30)
    a = ap.parse_args()

    vstup = vstup_pripadu_31()
    zaznamy = []
    for cislo in (int(x) for x in a.pripady.split(",")):
        for beh in range(1, a.behy + 1):
            zadani = (ZADANI_31 if cislo == 31 else ZADANI_32).format(vstup=vstup)
            s, pokusy, infra = runner._s_opakovanim(
                runner.spust_skill, a, zadani, a, vstup if cislo == 32 else None, NASTROJE[cislo])
            z = {"pripad": cislo, "beh": beh, "pokusy": pokusy, "infra_chyby": infra}
            if s is None:
                z["chyba"] = "INFRA: " + (infra[-1] if infra else "?")
            else:
                z.update(model=s["model"], skill=s["skill"], nastroje=s["nastroje"], prikazy=s["prikazy"],
                         zamitnuto=s["zamitnuto"], cteni=s["cteni"], cena=s["cena"], tokeny=s["tokeny"], vystup=s["text"])
            zaznamy.append(z)
            print(f"prípad {cislo} beh {beh}: tokeny {z.get('tokeny')}", file=sys.stderr)

    cil = os.path.join(runner.VYSLEDKY, a.stitok)
    os.makedirs(cil, exist_ok=True)
    with open(os.path.join(cil, "format-vystupu.json"), "w", encoding="utf-8") as f:
        json.dump({"commit": runner._git("rev-parse", "--short", "HEAD"), "otisk": runner._otisk_skillu(),
                   "behy": zaznamy}, f, ensure_ascii=False, indent=1)
    md = [f"# Prípady o formáte výstupu: {a.stitok}\n",
          f"Commit `{runner._git('rev-parse', '--short', 'HEAD')}`, odtlačok skillu `{runner._otisk_skillu()}`. "
          "Tvar výstupu sa kontroluje ručne podľa OČAKÁVANÉ v `pripady.md`.\n"]
    for z in zaznamy:
        t = z.get("tokeny") or {}
        md.append(f"## Prípad {z['pripad']}, beh {z['beh']}\n")
        md.append(f"Tokeny: vstup celkom {t.get('vstup_celkem')}, výstup {t.get('vystup')}, kroky {t.get('kroku')}; "
                  f"nástroje: {', '.join(z.get('nastroje', [])) or '–'}\n")
        md.append(re.sub(r"^", "> ", z.get("vystup") or z.get("chyba") or "", flags=re.M) + "\n")
    with open(os.path.join(cil, "format-vystupu.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Uložené do {cil}", file=sys.stderr)


if __name__ == "__main__":
    main()
