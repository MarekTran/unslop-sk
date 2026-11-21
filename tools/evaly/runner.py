#!/usr/bin/env python3
"""Runner regresných prípadov skillu unslop-sk.

Číta evals/pripady.md a každý prípad spúšťa cez `claude -p`
s pluginom načítaným z tohto repozitára (--plugin-dir). Každý prípad beží
niekoľkokrát (predvolene 3×) a o výsledku rozhoduje väčšina behov.

Ako sa rozhoduje o jednom behu:
  - Skill sa musí načítať (vo výstupe je volanie nástroja Skill na unslop-sk).
  - ČISTÝ prípad (režim kontroly): prejde, keď výstup nemá žiadne P0 ani P1.
    Počty číta z riadka `SÚHRN: P0=… P1=… P2=…`, ktorý runner v zadaní
    vyžaduje; keď riadok chýba, rozhodne hodnotiteľ.
  - Ostatné prípady: druhé volanie `claude -p` ako hodnotiteľ odpovie pri každom
    riadku OČAKÁVANÉ (vrátane NESMIE) áno/nie. Riadky „Voliteľne“ sa hodnotia, ale
    do výsledku sa nepočítajú. Hodnotiteľ navyše vypíše nálezy P0/P1 vo
    výstupe, ktoré nezodpovedajú žiadnemu riadku („mimo OČAKÁVANÉ“); beh
    neprejde, keď ich je viac než --max-mimo (predvolene 1, -1 vypne).
  - Chyby infraštruktúry (limit session alebo použitia, preťaženie API, timeout,
    prázdny výstup, rozbitá odpoveď hodnotiteľa) sa opakujú (--opakovania,
    predvolene 3, s rastúcou pauzou). Keď sa nepodarí ani tak, beh je
    „nevyhodnotený“: do väčšiny sa nepočíta a v správe je uvedený osobitne.
  - PREPIS: režim prepisu; opravenú verziu runner žiada medzi riadkami <<<VERZIA
    a VERZIA>>>. Vety z bloku BEZ ZMENY sa v nej hľadajú presne ako reťazec
    (zjednocujú sa len behy bielych znakov), bez hodnotiteľa.

Tokeny: z udalosti `result` v stream-json sa ukladá `usage` behu skillu (vstup,
  zápis a čítanie cache, výstup, počet krokov) do poľa `tokeny` v behy.json; tokeny
  hodnotiteľa sú osobitne v `tokeny_hodnotitele` a do súčtu skillu sa nepočítajú.
  Správa uvádza priemer a medián na beh a so `--porovnat` aj zmenu oproti východiskovému behu.

UDPipe je vypnutý: runner premennú UNSLOP_UDPIPE z prostredia odstráni.
Zapnete ho prepínačom --udpipe CESTA.

Použitie (z koreňa repozitára):
    python3 tools/evaly/runner.py --zoznam            # len načíta prípady, nič nevolá
    python3 tools/evaly/runner.py --stitok vychodisko
    python3 tools/evaly/runner.py --pripady 1,6,20 --behy 1 --stitok skuska
    python3 tools/evaly/runner.py --stitok po-prestavbe \\
        --porovnat tools/evaly/vysledky/<predchadzajuci>/behy.json
    python3 tools/evaly/runner.py --stitok jadro2-1 --behy 1 \\
        --skill-dir <priecinok-so-skillom>

Výstup: tools/evaly/vysledky/<stitok>/vysledky.md (tabuľka) a behy.json
(všetky výstupy a verdikty). Len štandardná knižnica Pythonu 3.8+.
"""

import argparse
import collections
import concurrent.futures
import datetime
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time

KOREN = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLUGIN_DIR = os.path.join(KOREN, "plugins", "unslop-sk")
SKILL_DIR = os.path.join(PLUGIN_DIR, "skills", "unslop-sk")
PRIPADY = os.path.join(KOREN, "evals", "pripady.md")
VYSLEDKY = os.path.join(KOREN, "tools", "evaly", "vysledky")

# Testovaný skill. --skill-dir ho prepíše na variant zabalený do dočasného pluginu
# (zadanie potom volá variant jeho menom); prípady sa berú vždy z PRIPADY.
SKILL = {"meno": "unslop-sk", "plugin_dir": PLUGIN_DIR, "otisk_dir": SKILL_DIR, "zdroj": None}


def nastav_variantu(skill_dir):
    """Holý adresár skillu (SKILL.md v koreni) zabalí do dočasného pluginu a nastaví SKILL.

    Zdroj sa nemení; kópia je v dočasnom adresári. Plugin aj skill sa volajú
    podľa name: v SKILL.md."""
    zdroj = os.path.abspath(skill_dir)
    meno = None
    with open(os.path.join(zdroj, "SKILL.md"), encoding="utf-8") as f:
        for riadok in f:
            if riadok.startswith("name:"):
                meno = riadok.split(":", 1)[1].strip()
                break
    meno = meno or os.path.basename(os.path.normpath(zdroj))
    plugin = os.path.join(tempfile.mkdtemp(prefix="unslop-eval-plugin-"), meno)
    os.makedirs(os.path.join(plugin, ".claude-plugin"))
    with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), "w", encoding="utf-8") as f:
        json.dump({"name": meno, "version": "0.0.0",
                   "description": f"Obal skillu {meno} pre evaly (zdroj {zdroj})"}, f, ensure_ascii=False)
    shutil.copytree(zdroj, os.path.join(plugin, "skills", meno),
                    ignore=shutil.ignore_patterns(".git", "__pycache__", "evals"))
    SKILL.update(meno=meno, plugin_dir=plugin, otisk_dir=zdroj,
                 zdroj=os.path.relpath(zdroj, KOREN).replace(os.sep, "/"))

# Čisté prípady podľa hlavičky pripady.md; parser ich overuje proti nadpisom.
CISTE = {6, 9, 11, 12, 14, 15, 19, 24, 26, 28, 36, 37}

PROFILY = {
    "sociálne siete": "socialne",
    "blog": "blog",
    "e-mail": "email",
    "dokumentácia": "dokumentacia",
    "odborný text": "odborny",
    "prezentácia": "prezentacia",
}

# Model ukladá vstup skriptu často príkazom `mkdir -p X && cd X && cat > v.txt <<EOF`.
# Režim dontAsk ho zamieta aj s pravidlami Bash(cat *), Bash(mkdir *), Bash(cd *): zúžené
# pravidlá nepokrývajú presmerovanie ani cd mimo pracovného adresára (len plné `Bash`
# ich pustí, to runner nepovoľuje), a model potom skript nespustí. Runner preto text sám
# uloží do vstup.txt v pracovnom adresári; model ho len odovzdá skriptu, a to pravidlo
# Bash(python3 *) pustí. Zistenie je prevzaté z českého runnera unslop-cs.
NASTROJE_SKILLU = "Skill Read Write Glob Grep Bash(python3 *) Bash(python *) Bash(py *)"

# Výstupy, ktoré nie sú prácou skillu, ale zlyhaním prostredia. claude -p ich
# vracia aj s podtypom „success“ (limit session).
_INFRA = re.compile(
    r"^\W*(you'?ve hit your|claude (ai )?usage limit|session limit|usage limit|rate.?limit"
    r"|api error|overloaded|internal server error|request timed out|credit balance"
    r"|(error|http)\W*(429|500|502|503|529))", re.I)


_ZAMEK = threading.Lock()
OPAKOVANI_HODNOTITELE = [0]


class InfraChyba(Exception):
    """Zlyhanie prostredia, nie skillu; volanie sa opakuje."""


def infra_chyba(text):
    """Vráti opis chyby infraštruktúry, alebo None. Hlášky claude -p sú
    krátke a začínajú sa textom chyby; dlhší výstup alebo výstup s riadkom SÚHRN
    je práca skillu, aj keď slovo „limit“ obsahuje."""
    t = (text or "").strip()
    if len(t) > 400 or "SÚHRN:" in t or "<<<VERZIA" in t:
        return None
    m = _INFRA.search(t)
    return _bile(t)[:160] if m else None


def tokeny_z_usage(usage, kroku=None):
    """Z objektu `usage` (výsledok claude -p) urobí slovník tokenov. `vstup_celkem`
    je všetko, čo model prečítal: nový vstup + zápis do cache + čítanie z cache."""
    u = usage or {}
    vstup = u.get("input_tokens") or 0
    zapis = u.get("cache_creation_input_tokens") or 0
    cteni = u.get("cache_read_input_tokens") or 0
    return {"vstup": vstup, "cache_zapis": zapis, "cache_cteni": cteni,
            "vstup_celkem": vstup + zapis + cteni,
            "vystup": u.get("output_tokens") or 0, "kroku": kroku}


def souhrn_tokenu(behy, klic="tokeny"):
    """Priemer a medián tokenov cez behy (iterovateľné záznamy behov); None bez dát."""
    t = [z[klic] for z in behy if z.get(klic)]
    if not t:
        return None
    r = {"behu": len(t)}
    for pole in ("vstup_celkem", "vystup", "cache_zapis", "cache_cteni", "kroku"):
        h = [x[pole] for x in t if x.get(pole) is not None]
        if h:
            r[pole] = {"prumer": round(statistics.mean(h)), "median": round(statistics.median(h))}
    return r


# ---------------------------------------------------------------------------
# Načítanie prípadov

Pripad = collections.namedtuple("Pripad", "cislo nazov typ profil vstup riadky bez_zmeny")
Riadok = collections.namedtuple("Riadok", "id text volitelny")

_HLAVICKA = re.compile(r"^## Prípad (\d+) – (.*?)\s*\(profil: ([^)]+)\)\s*$")


def nacti_pripady(cesta=PRIPADY):
    with open(cesta, encoding="utf-8") as f:
        riadky = f.read().splitlines()
    pripady, aktualny = [], None
    for r in riadky:
        m = _HLAVICKA.match(r)
        if r.startswith("## ") and (not m or "Formát výstupu" in m.group(2)):
            aktualny = None  # prípady o formáte výstupu (31 – 34) sa spúšťajú ručne
        elif m:
            aktualny = {"cislo": int(m.group(1)), "nazov": m.group(2),
                        "profil": m.group(3).strip(), "riadky": []}
            pripady.append(aktualny)
        elif aktualny is not None:
            aktualny["riadky"].append(r)
    return [_rozeber(p) for p in pripady]


def _rozeber(p):
    nazov = p["nazov"]
    if nazov.startswith("ČISTÝ:"):
        typ = "cisty"
    elif nazov.startswith("PREPIS:"):
        typ = "prepis"
    else:
        typ = "kontrola"
    vstup, ocakavane, bez, blok = [], [], [], None
    for r in p["riadky"]:
        if re.match(r"^VSTUP\b.*:\s*$", r):
            blok = "vstup"
        elif r.startswith("OČAKÁVANÉ:"):
            blok = "ocakavane"
            zvysok = r[len("OČAKÁVANÉ:"):].strip()
            if zvysok:
                ocakavane.append(zvysok)
        elif r.startswith("BEZ ZMENY:"):
            blok = "bez"
        elif blok == "vstup" and r.startswith(">"):
            vstup.append(r[2:] if r.startswith("> ") else r[1:])
        elif blok == "ocakavane" and r.startswith("- "):
            ocakavane.append(r[2:].strip())
        elif blok == "bez" and r.startswith("- "):
            m = re.match(r"^- „(.*)“\s*$", r)
            if not m:
                raise SystemExit(f"Prípad {p['cislo']}: neznámy riadok BEZ ZMENY: {r}")
            bez.append(m.group(1))
    if not vstup:
        raise SystemExit(f"Prípad {p['cislo']}: chýba VSTUP")
    if p["profil"] not in PROFILY:
        raise SystemExit(f"Prípad {p['cislo']}: neznámy profil {p['profil']}")
    riadky = [Riadok(i + 1, t, t.lower().startswith("voliteľne")) for i, t in enumerate(ocakavane)]
    return Pripad(p["cislo"], nazov, typ, p["profil"], "\n".join(vstup).strip(), riadky, bez)


# ---------------------------------------------------------------------------
# Zadanie

ZADANI_KONTROLA = """Použi skill unslop-sk (unslop-sk:unslop-sk) v režime kontroly: úplný audit (P0, P1 aj P2), profil registra „{profil}“ ({profil_id}).
Skontroluj text medzi značkami <text> a </text>. Text neprepisuj, len ho posúď.
{subor}
Na úplný koniec odpovede pridaj samostatný riadok presne v tomto tvare:
SÚHRN: P0=<počet> P1=<počet> P2=<počet>
Počítaj len nálezy, ktoré po posúdení zostávajú ako chyby; miesta, ktoré sú v kontexte obhájiteľné, a riadky tabuľky Iné chyby nepočítaj.

<text>
{vstup}
</text>"""

ZADANI_PREPIS = """Použi skill unslop-sk (unslop-sk:unslop-sk) v režime prepisu, profil registra „{profil}“ ({profil_id}).
Prepíš text medzi značkami <text> a </text> podľa skillu.
{subor}Celú opravenú verziu textu daj medzi dva samostatné riadky <<<VERZIA a VERZIA>>>. Audit a zoznam zmien napíš mimo nich.

<text>
{vstup}
</text>"""

ZADANI_HODNOTITEL = """Si hodnotiteľ regresných testov skillu, ktorý v slovenskom texte hľadá vzorce typické pre AI (závažnosť P0 > P1 > P2). Dostaneš vstupný text prípadu, výstup skillu a očíslované požiadavky. Pri každej požiadavke rozhodni, či ju výstup spĺňa (true / false), a jednou vetou po slovensky zdôvodni.

Ako požiadavky čítať:
- „P0: X“, „P1: X“, „P2: X“ je splnená, keď výstup X označí ako nález a jeho závažnosť sa od uvedenej líši najviac o jeden stupeň. Nezáleží na formulácii ani na tom, ako výstup nálezy rozdelí alebo zlúči; rozhoduje, či je vzorec na danom mieste označený ako chyba. Výpočet v zátvorke ukazuje, o ktoré miesta ide; stačí, keď výstup označí podstatnú časť z nich.
- „NESMIE označiť: X“ je splnená, keď výstup X ako chybu neoznačí. Zmienka, že X je v poriadku, neprekáža. Riadok v tabuľke „Iné chyby (nie sú znakom AI)“ nie je označenie vzorca AI a požiadavku neporušuje.
- „Upozorniť: X“ je splnená, keď výstup na X upozorní (v náleze, v posúdení alebo značkou [OVERIŤ]).
- Požiadavky na prepis („Prepis musí…“, „Prepis zlyhá, keď…“, „Nová verzia NESMIE…“, „Výstup obsahuje značky…“, „Poistka: …“) posudzuj podľa opravenej verzie medzi riadkami <<<VERZIA a VERZIA>>>. Keď výstup opravenú verziu nemá, posúď, či ju porušujú návrhy opráv vo výstupe; keď žiadne nie sú, je požiadavka splnená.
- Veta „žiadny nález“ je splnená, keď výstup nemá žiadny nález P0 ani P1, ktorý by po posúdení zostal ako chyba.

Potom vypíš do poľa „mimo“ každý nález, ktorý výstup označil ako chybu so závažnosťou P0 alebo P1 a ktorý nepokrýva žiadna požiadavka. Nález je pokrytý, keď sa týka miesta alebo vzorca, o ktorom hovorí ktorákoľvek požiadavka akéhokoľvek typu: riadok „P0/P1/P2: X“, „Upozorniť: X“, „NESMIE označiť: X“ aj požiadavka na prepis (napríklad značky [OVERIŤ] pri uvedených miestach alebo zachovanie uvedenej vety). Požiadavky na prepis nevymenúvajú všetky nálezy, len tie, na ktorých prípad stojí; nález na mieste, ktoré požiadavka spomína alebo ktoré prepis podľa nej musí opraviť, preto nie je „mimo“. Závažnosť ber tak, ako ju uvádza výstup. Nepočítaj nálezy P2, miesta, ktoré výstup sám označil za obhájiteľné, riadky tabuľky „Iné chyby (nie sú znakom AI)“ a návrhy bez označenia chyby. Jeden vzorec na viacerých miestach je jeden nález. Keď taký nález nie je, vráť prázdne pole.

Profil registra: {profil}

<vstup>
{vstup}
</vstup>

<vystup>
{vystup}
</vystup>

Požiadavky:
{poziadavky}"""

SCHEMA_HODNOTITEL = {
    "type": "object",
    "properties": {
        "hodnoceni": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "splneno": {"type": "boolean"},
                    "duvod": {"type": "string"},
                },
                "required": ["id", "splneno", "duvod"],
            },
        },
        "mimo": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "misto": {"type": "string"},
                    "zavaznost": {"type": "string", "enum": ["P0", "P1"]},
                    "duvod": {"type": "string"},
                },
                "required": ["misto", "zavaznost", "duvod"],
            },
        },
    },
    "required": ["hodnoceni", "mimo"],
}


# ---------------------------------------------------------------------------
# Volání claude -p

def _prostredi(udpipe):
    env = dict(os.environ)
    env.pop("UNSLOP_UDPIPE", None)
    if udpipe:
        env["UNSLOP_UDPIPE"] = os.path.abspath(udpipe)
    return env


def _s_opakovanim(fn, a, *args):
    """Zavolá fn; pri InfraChyba počká a skúsi znova. Vráti (výsledok, pokusy,
    zoznam chýb infraštruktúry). Keď sa nepodarí, výsledok je None."""
    chyby = []
    for pokus in range(1, a.opakovani + 2):
        try:
            return fn(*args), pokus, chyby
        except InfraChyba as e:
            chyby.append(str(e))
            if pokus <= a.opakovani:
                time.sleep(a.pauza * pokus)
    return None, a.opakovani + 1, chyby


def _volany_skill(vstup, meno):
    """Volá vstup nástroja Skill skill `meno`? Presné meno s hranicou („unslop-sk“ nesedí
    na „unslop-sk-jadro-2“), hľadá sa v celom vstupe."""
    s = json.dumps(vstup, ensure_ascii=False)
    return re.search(r"(?<![\w-])" + re.escape(meno) + r"(?![\w-])", s) is not None


def spust_skill(zadani, a, vstup=None, nastroje=None):
    """Vrátí dict: text, skill (bool), nastroje, model, cena, tokeny, chyba.
    `nastroje` prebije NASTROJE_SKILLU (prípady o formáte výstupu).
    Zlyhanie prostredia hlási výnimkou InfraChyba."""
    cmd = ["claude", "-p", zadani, "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--strict-mcp-config", "--setting-sources", "project",
           "--plugin-dir", SKILL["plugin_dir"], "--permission-mode", "dontAsk",
           "--allowedTools", nastroje or NASTROJE_SKILLU]
    if a.model:
        cmd += ["--model", a.model]
    cwd = tempfile.mkdtemp(prefix="unslop-eval-")
    if vstup is not None:
        with open(os.path.join(cwd, "vstup.txt"), "w", encoding="utf-8") as f:
            f.write(vstup + "\n")
    try:
        p = subprocess.run(cmd, cwd=cwd, env=_prostredi(a.udpipe), capture_output=True,
                           text=True, timeout=a.timeout)
    except subprocess.TimeoutExpired:
        raise InfraChyba(f"timeout {a.timeout} s")
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    out = {"text": "", "skill": False, "nastroje": [], "model": None, "cena": 0.0, "chyba": None,
           "prikazy": [], "zamitnuto": [], "tokeny": None, "cteni": []}
    volani = {}  # id volania nástroja -> (nástroj, vstup)
    for riadok in p.stdout.splitlines():
        try:
            u = json.loads(riadok)
        except ValueError:
            continue
        if u.get("type") == "system" and u.get("subtype") == "init":
            out["model"] = u.get("model")
        elif u.get("type") == "assistant":
            for c in (u.get("message") or {}).get("content") or []:
                if c.get("type") == "tool_use":
                    nazev = c.get("name")
                    out["nastroje"].append(nazev)
                    volani[c.get("id")] = (nazev, c.get("input") or {})
                    if nazev == "Read":
                        out["cteni"].append(str((c.get("input") or {}).get("file_path", "")))
                    if nazev == "Bash":
                        out["prikazy"].append(str((c.get("input") or {}).get("command", ""))[:400])
                    if nazev == "Skill" and _volany_skill(c.get("input"), SKILL["meno"]):
                        out["skill"] = True
        elif u.get("type") == "user":
            for c in (u.get("message") or {}).get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                    obsah = c.get("content")
                    if isinstance(obsah, list):
                        obsah = " ".join(x.get("text", "") for x in obsah if isinstance(x, dict))
                    if re.search(r"permission|denied|not allowed|zamietn", str(obsah), re.I):
                        nazev, vstup = volani.get(c.get("tool_use_id"), ("?", {}))
                        out["zamitnuto"].append({"nastroj": nazev, "chyba": _bile(str(obsah))[:160],
                                                 "vstup": str(vstup.get("command") or vstup.get("file_path")
                                                              or vstup)[:300]})
        elif u.get("type") == "result":
            out["text"] = u.get("result") or ""
            out["cena"] = u.get("total_cost_usd") or 0.0
            out["tokeny"] = tokeny_z_usage(u.get("usage"), u.get("num_turns"))
            if u.get("is_error"):
                out["chyba"] = u.get("subtype") or "chyba"
    infra = infra_chyba(out["text"]) or (infra_chyba(p.stderr) if not out["text"] else None)
    if infra:
        raise InfraChyba(infra)
    if not out["text"]:
        raise InfraChyba(f"prázdny výstup (kód {p.returncode}): {p.stderr.strip()[:200]}")
    return out


def spust_hodnotitela(pripad, vystup, riadky, a):
    """Vráti (verdikty, mimo, cena, chyba, tokeny). Zlyhanie prostredia opakuje."""
    v, pokusy, infra = _s_opakovanim(_hodnotitel, a, pripad, vystup, riadky, a)
    with _ZAMEK:
        OPAKOVANI_HODNOTITELE[0] += pokusy - 1
    if v is None:
        return None, None, 0.0, "INFRA " + (infra[-1] if infra else "hodnotiteľ: ?"), None
    return v


def _hodnotitel(pripad, vystup, riadky, a):
    poziadavky = "\n".join(f"{r.id}. {r.text}" for r in riadky)
    zadani = ZADANI_HODNOTITEL.format(profil=pripad.profil, vstup=pripad.vstup,
                                      vystup=vystup, poziadavky=poziadavky)
    cmd = ["claude", "-p", zadani, "--output-format", "json", "--no-session-persistence",
           "--strict-mcp-config", "--setting-sources", "project", "--disable-slash-commands",
           "--tools", "", "--json-schema", json.dumps(SCHEMA_HODNOTITEL)]
    if a.hodnotitel_model:
        cmd += ["--model", a.hodnotitel_model]
    cwd = tempfile.mkdtemp(prefix="unslop-hodn-")
    try:
        p = subprocess.run(cmd, cwd=cwd, env=_prostredi(None), capture_output=True,
                           text=True, timeout=a.timeout)
    except subprocess.TimeoutExpired:
        raise InfraChyba(f"hodnotiteľ: timeout {a.timeout} s")
    finally:
        shutil.rmtree(cwd, ignore_errors=True)
    try:
        d = json.loads(p.stdout)
    except ValueError:
        raise InfraChyba("hodnotiteľ: " + (infra_chyba(p.stdout + " " + p.stderr)
                                           or f"nečitateľná odpoveď (kód {p.returncode})"))
    if d.get("is_error") or not d.get("structured_output"):
        raise InfraChyba("hodnotiteľ: " + (infra_chyba(d.get("result") or "")
                                           or f"bez štruktúrovanej odpovede ({d.get('subtype')})"))
    so = d.get("structured_output") or {}
    verdikty = {h["id"]: h for h in so.get("hodnoceni", []) if isinstance(h, dict) and "id" in h}
    mimo = [m for m in so.get("mimo") or [] if isinstance(m, dict)]
    chybaju = [r.id for r in riadky if r.id not in verdikty]
    chyba = f"hodnotiteľ nevrátil riadky {chybaju}" if chybaju else None
    return verdikty, mimo, d.get("total_cost_usd") or 0.0, chyba, tokeny_z_usage(d.get("usage"), d.get("num_turns"))


# ---------------------------------------------------------------------------
# Jeden beh

_SUHRN = re.compile(r"SÚHRN:\s*P0\s*=\s*(\d+)\s*,?\s*P1\s*=\s*(\d+)\s*,?\s*P2\s*=\s*(\d+)")
_VERZIA = re.compile(r"<<<VERZIA\s*\n(.*?)\n\s*VERZIA>>>", re.S)


def _bile(s):
    return re.sub(r"\s+", " ", s).strip()


def jeden_beh(pripad, beh, a):
    vzor = ZADANI_PREPIS if pripad.typ == "prepis" else ZADANI_KONTROLA
    subor = "" if a.bez_vstupu else "Rovnaký text je uložený v súbore vstup.txt (UTF-8) v pracovnom adresári.\n"
    zadani = vzor.format(profil=pripad.profil, profil_id=PROFILY[pripad.profil], vstup=pripad.vstup,
                         subor=subor)
    j = SKILL["meno"]
    zadani = zadani.replace("unslop-sk (unslop-sk:unslop-sk)", f"{j} ({j}:{j})", 1)
    s, pokusy, infra = _s_opakovanim(spust_skill, a, zadani, a, None if a.bez_vstupu else pripad.vstup)
    zaznam = {"pripad": pripad.cislo, "beh": beh, "model": None, "skill": False,
              "nastroje": [], "vystup": "", "cena": 0.0, "souhrn": None, "verdikty": {},
              "mimo": [], "bez_zmeny": [], "chyby": [], "proslo": False,
              "prikazy": [], "zamitnuto": [], "tokeny": None, "tokeny_hodnotitele": None,
              "cteni": [], "pokusy": pokusy, "infra_chyby": infra, "nevyhodnoceno": False}
    if s is None:
        zaznam["nevyhodnoceno"] = True
        zaznam["chyby"].append("INFRA: " + infra[-1])
        return zaznam
    zaznam.update(model=s["model"], skill=s["skill"], nastroje=s["nastroje"],
                  vystup=s["text"], cena=s["cena"], prikazy=s["prikazy"], zamitnuto=s["zamitnuto"],
                  tokeny=s["tokeny"], cteni=s["cteni"])
    if s["chyba"]:
        zaznam["chyby"].append(s["chyba"])
        return zaznam
    if not s["skill"]:
        zaznam["chyby"].append("skill sa nenačítal")

    m = _SUHRN.findall(s["text"])
    if m:
        zaznam["souhrn"] = dict(zip(("P0", "P1", "P2"), map(int, m[-1])))

    ok = s["skill"]
    if pripad.typ == "cisty":
        if zaznam["souhrn"] is not None:
            if zaznam["souhrn"]["P0"] or zaznam["souhrn"]["P1"]:
                ok = False
                zaznam["chyby"].append(f"P0={zaznam['souhrn']['P0']} P1={zaznam['souhrn']['P1']}")
        else:
            riadok = Riadok(1, "žiadny nález (výstup nemá P0 ani P1, ktoré by po posúdení zostali ako chyby)", False)
            v, _, cena, chyba, tok_h = spust_hodnotitela(pripad, s["text"], [riadok], a)
            zaznam["cena"] += cena
            zaznam["tokeny_hodnotitele"] = tok_h
            zaznam["chyby"].append("chýba riadok SÚHRN, rozhodol hodnotiteľ")
            if chyba and chyba.startswith("INFRA"):
                zaznam["nevyhodnoceno"] = True
                zaznam["chyby"].append(chyba)
            elif chyba or not v:
                ok = False
                zaznam["chyby"].append(chyba or "hodnotiteľ nevrátil verdikt")
            else:
                zaznam["verdikty"] = {"1": v[1]}
                if not v[1]["splneno"]:
                    ok = False
    else:
        if pripad.riadky:
            v, mimo, cena, chyba, tok_h = spust_hodnotitela(pripad, s["text"], pripad.riadky, a)
            zaznam["cena"] += cena
            zaznam["tokeny_hodnotitele"] = tok_h
            if chyba and chyba.startswith("INFRA"):
                zaznam["nevyhodnoceno"] = True
                zaznam["chyby"].append(chyba)
                return zaznam
            zaznam["mimo"] = mimo or []
            if a.max_mimo >= 0 and len(zaznam["mimo"]) > a.max_mimo:
                ok = False
                zaznam["chyby"].append(f"mimo OČAKÁVANÉ: nálezy P0/P1 {len(zaznam['mimo'])}")
            if chyba or v is None:
                ok = False
                zaznam["chyby"].append(chyba or "hodnotiteľ nevrátil verdikt")
            v = v or {}
            zaznam["verdikty"] = {str(k): x for k, x in v.items()}
            for r in pripad.riadky:
                if r.volitelny or r.id not in v:
                    continue
                if not v[r.id]["splneno"]:
                    ok = False
        if pripad.typ == "prepis":
            mv = _VERZIA.search(s["text"])
            verzia = _bile(mv.group(1)) if mv else None
            if verzia is None:
                ok = False
                zaznam["chyby"].append("chýba opravená verzia medzi <<<VERZIA a VERZIA>>>")
            for veta in pripad.bez_zmeny:
                najdene = verzia is not None and _bile(veta) in verzia
                zaznam["bez_zmeny"].append({"veta": veta, "najdene": najdene})
                if not najdene:
                    ok = False
    zaznam["proslo"] = ok
    return zaznam


# ---------------------------------------------------------------------------
# Súhrn a správa

def _zkrat(t, n=60):
    t = _bile(t)
    return t if len(t) <= n else t[:n - 1] + "…"


def duvody(pripad, behy):
    """Krátky dôvod z neúspešných behov: čo zlyhalo a v koľkých behoch."""
    pocet = collections.Counter()
    for b in behy:
        if b["proslo"] or b.get("nevyhodnoceno"):
            continue
        for ch in b["chyby"]:
            if ch.startswith("chýba riadok SÚHRN"):
                continue
            pocet[ch] += 1
        for r in pripad.riadky:
            v = b["verdikty"].get(str(r.id))
            if v and not v["splneno"] and not r.volitelny:
                pocet[f"r. {r.id} „{_zkrat(r.text)}“"] += 1
        for z in b["bez_zmeny"]:
            if not z["najdene"]:
                pocet[f"BEZ ZMENY „{_zkrat(z['veta'], 40)}“"] += 1
    nevyh = sum(bool(b.get("nevyhodnoceno")) for b in behy)
    if nevyh:
        pocet[f"nevyhodnotené (infraštruktúra) {nevyh}"] = 0
    return "; ".join(k if n == 0 else f"{k} ({n}/{len(behy)})" for k, n in pocet.most_common())


def _git(*args):
    try:
        return subprocess.run(["git", "-C", KOREN] + list(args), capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def _otisk_skillu():
    h = hashlib.sha256()
    for koren, _, subory in sorted(os.walk(SKILL["otisk_dir"])):
        if "evals" in koren.split(os.sep) or "__pycache__" in koren:
            continue
        for s in sorted(subory):
            with open(os.path.join(koren, s), "rb") as f:
                h.update(s.encode() + f.read())
    return h.hexdigest()[:12]


TYPY = {"cisty": "čistý", "kontrola": "kontrola", "prepis": "prepis"}


def cteni_referenci(behy):
    """Koľko behov prečítalo ktorý súbor z references/ (podľa volaní Read)."""
    pocet = collections.Counter()
    for z in behy:
        for f in {os.path.basename(c) for c in z.get("cteni", []) if "/references/" in c}:
            pocet[f] += 1
    return dict(sorted(pocet.items()))


def _t(souhrn, pole):
    d = (souhrn or {}).get(pole)
    return f"{d['median']:,} / {d['prumer']:,}".replace(",", " ") if d else "?"


def _riadky_tokenov(meta):
    """Riadky správy o tokenoch: medián / priemer na beh skillu, bez hodnotiteľa."""
    t = meta.get("tokeny")
    if not t:
        return ["- Tokeny skillu: runner ich nemeral"]
    r = [f"- Tokeny skillu na beh (medián / priemer, počet behov {t['behu']}, bez hodnotiteľa): "
         f"vstup celkom {_t(t, 'vstup_celkem')} (z toho zápis do cache {_t(t, 'cache_zapis')}, "
         f"čítanie z cache {_t(t, 'cache_cteni')}), výstup {_t(t, 'vystup')}, kroky {_t(t, 'kroku')}"]
    h = meta.get("tokeny_hodnotitele")
    if h:
        r.append(f"- Tokeny hodnotiteľa na beh (osobitne): vstup celkom {_t(h, 'vstup_celkem')}, "
                 f"výstup {_t(h, 'vystup')}")
    s = meta.get("srovnani_tokeny")
    if s:
        def zm(pole):
            a, b = s.get(pole), t.get(pole)
            if not a or not b or not a["median"]:
                return "?"
            return f"{(b['median'] - a['median']) / a['median'] * 100:+.0f} %".replace("-", "−")
        r.append(f"- Východiskový beh (`--porovnat`): vstup celkom {_t(s, 'vstup_celkem')}, výstup "
                 f"{_t(s, 'vystup')}; zmena mediánu: vstup {zm('vstup_celkem')}, výstup {zm('vystup')}")
    elif meta.get("srovnani_kriterium") is not None:
        r.append("- Východiskový beh (`--porovnat`) nemá tokeny, zmena sa nepočíta")
    return r


def zprava(pripady, vysledky, meta, srovnani):
    r = []
    r.append(f"# Výsledky evalov: {meta['stitok']}\n")
    r.append(f"- Dátum: {meta['datum']}")
    r.append(f"- Commit: `{meta['commit']}`, odtlačok skillu (bez evals): `{meta['otisk']}`")
    if meta.get("skill_dir"):
        r.append(f"- Variant skillu: `{meta['skill']}` z `{meta['skill_dir']}` (`--skill-dir`); "
                 "prípady z `evals/pripady.md`")
    r.append(f"- Model skillu: {meta['modely']}; hodnotiteľ: {meta['hodnotitel']}")
    r.append(f"- Behy na prípad: {meta['behy']} (rozhoduje väčšina); UDPipe: {meta['udpipe']}")
    r.append(f"- Kritérium: najviac {meta['max_mimo']} nález P0/P1 mimo OČAKÁVANÉ"
             if meta["max_mimo"] >= 0 else "- Kritérium: nálezy mimo OČAKÁVANÉ sa nepočítajú")
    r.append(f"- Opakovania po chybe infraštruktúry: {meta['opakovani_celkem']} navyše; "
             f"nevyhodnotené behy: {meta['nevyhodnoceno']}")
    r.append(f"- Povolené nástroje skillu: `{meta['nastroje_skillu']}`; "
             + ("vstup.txt s textom prípadu vytvára runner" if meta["vstup_v_souboru"]
                else "vstup.txt runner nevytvára, text ukladá model"))
    r.append(f"- Zamietnuté nástroje: behy {meta['zamitnuto']} z {meta['behu_celkem']} "
             f"(podrobnosti v `behy.json`, pole `zamitnuto`)")
    r.append(f"- Cena celkom: {meta['cena']:.2f} USD")
    r += _riadky_tokenov(meta)
    if meta.get("cteni_referenci"):
        r.append(f"- Čítanie referencií (počet behov z {meta['behu_celkem']}, nástroj Read): "
                 + ", ".join(f"`{k}` {n}" for k, n in meta["cteni_referenci"].items()))
    r.append("")
    cis = [p for p in pripady if p.typ == "cisty"]
    ost = [p for p in pripady if p.typ != "cisty"]
    ok = lambda ps: sum(vysledky[p.cislo]["proslo"] is True for p in ps)  # noqa: E731
    r.append(f"**Prešlo {ok(pripady)} z {len(pripady)}** (čisté {ok(cis)}/{len(cis)}, "
             f"ostatné {ok(ost)}/{len(ost)}).\n")
    hlav = "| Prípad | Typ | Výsledok | Behy | Dôvod |"
    del_ = "|---|---|---|---|---|"
    if srovnani:
        hlav = "| Prípad | Typ | Výsledok | Východiskový stav | Behy | Dôvod |"
        del_ = "|---|---|---|---|---|---|"
    r += [hlav, del_]
    for p in pripady:
        v = vysledky[p.cislo]
        vys = ("nevyhodnotené" if v["proslo"] is None
               else "prešlo" if v["proslo"] else "**neprešlo**")
        behy = f"{v['proslych']}/{v['behu']}"
        nazov = f"{p.cislo} – {_zkrat(p.nazov, 45)}"
        duvod = v["duvod"] or "–"
        if srovnani:
            puv = srovnani.get(p.cislo)
            puv_t = "–" if puv is None else ("prešlo" if puv else "neprešlo")
            if puv is not None and v["proslo"] is not None and puv != v["proslo"]:
                puv_t += " ⇄"
            r.append(f"| {nazov} | {TYPY[p.typ]} | {vys} | {puv_t} | {behy} | {duvod} |")
        else:
            r.append(f"| {nazov} | {TYPY[p.typ]} | {vys} | {behy} | {duvod} |")
    r.append("\nDôvod uvádza, čo zlyhalo a v koľkých behoch. Prípad prejde aj s jedným neúspešným "
             "behom z troch; dôvod vtedy ukazuje nestabilitu. Behy sú vyhodnotené / celkom; "
             "nevyhodnotené behy (chyba infraštruktúry aj po opakovaní) sa do väčšiny nepočítajú. "
             "Úplné výstupy, verdikty a nálezy mimo OČAKÁVANÉ sú v `behy.json`.")
    if srovnani and meta.get("srovnani_kriterium") != meta["max_mimo"]:
        r.append("\n**Pozor:** porovnávaný beh má iné kritérium nálezov mimo OČAKÁVANÉ "
                 f"({meta.get('srovnani_kriterium')}), výsledky nie sú priamo porovnateľné.")
    if srovnani:
        r.append("\n⇄ = výsledok sa oproti východiskovému stavu zmenil.")
    return "\n".join(r) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stitok", help="názov behu, priečinok vo vysledky/ (povinný okrem --zoznam)")
    ap.add_argument("--zoznam", action="store_true",
                    help="len načíta a vypíše prípady z evals/pripady.md; nič nevolá a nič nestojí")
    ap.add_argument("--pripady", help="len vybrané prípady, napr. 1,6,20")
    ap.add_argument("--behy", type=int, default=3, help="behy na prípad (predvolene 3)")
    ap.add_argument("--jobs", type=int, default=4, help="súbežné behy (predvolene 4)")
    ap.add_argument("--model", help="model pre beh skillu (predvolene podľa claude)")
    ap.add_argument("--hodnotitel-model", help="model hodnotiteľa (predvolene podľa claude)")
    ap.add_argument("--udpipe", help="cesta k modelu UDPipe; bez nej beží skript bez modelu")
    ap.add_argument("--timeout", type=int, default=900, help="limit jedného volania v s")
    ap.add_argument("--opakovania", dest="opakovani", type=int, default=3,
                    help="koľkokrát zopakovať volanie po chybe infraštruktúry (predvolene 3)")
    ap.add_argument("--pauza", type=int, default=30,
                    help="pauza pred opakovaním v s, rastie s pokusom (predvolene 30)")
    ap.add_argument("--bez-vstupu", action="store_true",
                    help="runner nevytvorí vstup.txt; model musí text uložiť sám (overenie kroku 3 "
                         "SKILL.md, výsledky nie sú porovnateľné s behom bez prepínača)")
    ap.add_argument("--max-mimo", type=int, default=1,
                    help="najviac nálezov P0/P1 mimo OČAKÁVANÉ na beh (predvolene 1, -1 vypne)")
    ap.add_argument("--porovnat", dest="srovnat",
                    help="behy.json skoršieho behu pre stĺpec Východiskový stav")
    ap.add_argument("--skill-dir", metavar="ADRESAR",
                    help="testovať variant skillu z holého adresára so SKILL.md (napr. "
                         "<priecinok-so-skillom>); zabalí ho do dočasného "
                         "pluginu a zadanie ho volá menom z name: v SKILL.md")
    ap.add_argument("--vystup", help="priečinok na výsledky (predvolene tools/evaly/vysledky/<stitok>)")
    a = ap.parse_args()

    pripady = nacti_pripady()
    najdene_ciste = {p.cislo for p in pripady if p.typ == "cisty"}
    if najdene_ciste != CISTE:
        raise SystemExit(f"Čisté prípady v nadpisoch {sorted(najdene_ciste)} "
                         f"nesedia s hlavičkou {sorted(CISTE)}.")
    if a.pripady:
        vyber = {int(x) for x in a.pripady.split(",")}
        pripady = [p for p in pripady if p.cislo in vyber]
    if not pripady:
        raise SystemExit("Žiadne prípady na beh.")
    if a.zoznam:
        for p in pripady:
            print(f"{p.cislo:>3}  {TYPY[p.typ]:<8}  {PROFILY[p.profil]:<12}  riadky OČAKÁVANÉ: "
                  f"{len(p.riadky)}  BEZ ZMENY: {len(p.bez_zmeny)}  slová vstupu: "
                  f"{len(p.vstup.split())}  {p.nazov}")
        print(f"Spolu {len(pripady)}, z toho čisté {sum(p.typ == 'cisty' for p in pripady)}, "
              f"prepis {sum(p.typ == 'prepis' for p in pripady)}.")
        return
    if not a.stitok:
        ap.error("chýba --stitok")
    if a.skill_dir:
        nastav_variantu(a.skill_dir)
    if not shutil.which("claude"):
        raise SystemExit("Nenašiel som príkaz claude (Claude Code CLI).")

    ulohy = [(p, b) for p in pripady for b in range(1, a.behy + 1)]
    behy = collections.defaultdict(list)
    print(f"prípady: {len(pripady)} × behy: {a.behy} = volania skillu: {len(ulohy)}", file=sys.stderr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        fut = {ex.submit(jeden_beh, p, b, a): (p, b) for p, b in ulohy}
        for i, f in enumerate(concurrent.futures.as_completed(fut), 1):
            p, b = fut[f]
            try:
                z = f.result()
            except Exception as e:  # noqa: BLE001
                z = {"pripad": p.cislo, "beh": b, "proslo": False, "chyby": [f"výnimka: {e!r}"],
                     "verdikty": {}, "mimo": [], "bez_zmeny": [], "cena": 0.0, "model": None,
                     "skill": False, "nastroje": [], "vystup": "", "souhrn": None,
                     "pokusy": 1, "infra_chyby": [], "nevyhodnoceno": False,
                     "prikazy": [], "zamitnuto": [], "tokeny": None, "tokeny_hodnotitele": None,
                     "cteni": []}
            behy[p.cislo].append(z)
            stav = ("nevyhodnotené" if z.get("nevyhodnoceno")
                    else "prešlo" if z["proslo"] else "neprešlo")
            print(f"[{i}/{len(ulohy)}] prípad {p.cislo} beh {b}: {stav} "
                  f"(pokusy: {z.get('pokusy', 1)}) {'; '.join(z['chyby'])}",
                  file=sys.stderr)

    vysledky = {}
    for p in pripady:
        bb = sorted(behy[p.cislo], key=lambda z: z["beh"])
        hodnocene = [z for z in bb if not z.get("nevyhodnoceno")]
        proslych = sum(z["proslo"] for z in hodnocene)
        vysledky[p.cislo] = {"proslo": proslych > len(hodnocene) / 2 if hodnocene else None,
                             "proslych": proslych, "behu": len(hodnocene),
                             "nevyhodnoceno": len(bb) - len(hodnocene),
                             "duvod": duvody(p, bb), "behy": bb}

    srovnani, srovnani_kriterium, srovnani_tokeny = None, None, None
    if a.srovnat:
        with open(a.srovnat, encoding="utf-8") as f:
            puvodni = json.load(f)
        srovnani = {int(k): v["proslo"] for k, v in puvodni["pripady"].items()
                    if v["proslo"] is not None}
        srovnani_kriterium = puvodni.get("meta", {}).get("max_mimo", "bez kritéria")
        srovnani_tokeny = souhrn_tokenu(z for v in puvodni["pripady"].values() for z in v.get("behy", []))

    modely = sorted({z["model"] for v in vysledky.values() for z in v["behy"] if z.get("model")})
    meta = {
        "stitok": a.stitok,
        "datum": datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z"),
        "commit": _git("rev-parse", "--short", "HEAD") + (" (neuložené zmeny)" if _git("status", "--porcelain", "--", ".", ":!tools/evaly/vysledky") else ""),
        "otisk": _otisk_skillu(),
        "skill": SKILL["meno"],
        "skill_dir": SKILL["zdroj"],
        "modely": ", ".join(modely) or "?",
        "hodnotitel": a.hodnotitel_model or "predvolený model claude",
        "behy": a.behy,
        "udpipe": a.udpipe or "vypnutý",
        "cena": sum(z.get("cena") or 0 for v in vysledky.values() for z in v["behy"]),
        "max_mimo": a.max_mimo,
        "nastroje_skillu": NASTROJE_SKILLU,
        "vstup_v_souboru": not a.bez_vstupu,
        "zamitnuto": sum(bool(z.get("zamitnuto")) for v in vysledky.values() for z in v["behy"]),
        "behu_celkem": sum(len(v["behy"]) for v in vysledky.values()),
        "srovnani_kriterium": srovnani_kriterium,
        "tokeny": souhrn_tokenu(z for v in vysledky.values() for z in v["behy"]),
        "tokeny_hodnotitele": souhrn_tokenu((z for v in vysledky.values() for z in v["behy"]),
                                            "tokeny_hodnotitele"),
        "srovnani_tokeny": srovnani_tokeny,
        "cteni_referenci": cteni_referenci(z for v in vysledky.values() for z in v["behy"]),
        "opakovani_celkem": sum(z.get("pokusy", 1) - 1 for v in vysledky.values() for z in v["behy"])
                            + OPAKOVANI_HODNOTITELE[0],
        "nevyhodnoceno": sum(v["nevyhodnoceno"] for v in vysledky.values()),
    }

    cil = a.vystup or os.path.join(VYSLEDKY, a.stitok)
    os.makedirs(cil, exist_ok=True)
    with open(os.path.join(cil, "behy.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "pripady": {str(k): v for k, v in vysledky.items()}},
                  f, ensure_ascii=False, indent=1)
    md = zprava(pripady, vysledky, meta, srovnani)
    with open(os.path.join(cil, "vysledky.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    print(f"Uložené do {cil}", file=sys.stderr)


if __name__ == "__main__":
    main()
