#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
metriky.py – merateľné kontroly AI slopu v slovenskom texte (skill unslop-sk).

Skript počíta to, čo sa dá spočítať: typografiu, rytmus viet, nálezy zo zoznamov
slov (`references/slova.md`), bohemizmy, kontrastné obraty, trojice, prívesky,
spájacie výrazy, osobu a častice a s modelom UDPipe aj menný štýl, pasívum
a skladbu. O autorstve textu nič nehovorí a nenahrádza úsudok: nález je
dôvod pozrieť sa na dané miesto.

Použitie:
    python3 metriky.py text.txt --profil blog
    python3 metriky.py text.txt --udpipe slovak-snk-ud-2.5-191206.udpipe --format json
    cat text.txt | python3 metriky.py - --profil email
    python3 metriky.py text.txt --vsetko    # aj blokové citácie „>“, tabuľky a „…“ naplno

Bloky kódu (``` ~~~, odsadené, <pre>, <code>), inline kód, URL, e-maily a blokové
citácie „>“ sa nemerajú a nepočítajú do slov, pomlčiek ani rytmu; nálezy v tabuľkách
a vnútri „…“ sú len info. Výstup hlási vynechaný text v suhrn.vylucene.

Bez modelu beží v obmedzenom režime: delenie viet podľa pravidiel, zoznamy slov
cez kmene (výsledok je približný), bez nominalizácie, pasíva a skladby.
Model UDPipe má licenciu CC BY-NC-SA, do repozitára nepatrí; skript ho len
načítava z cesty (prepínač --udpipe alebo premenná UNSLOP_UDPIPE).

Len štandardná knižnica Pythonu 3.8+, bez siete. S modelom navyše balík
`ufal.udpipe` (pip install ufal.udpipe).

Skript vznikol prekladom metriky.py z českého skillu unslop-cs (Petr Hula, MIT).
"""

import argparse
import functools
import json
import math
import os
import re
import statistics
import sys
from dataclasses import dataclass, field

VERZE = "0.1.0"

# ---------------------------------------------------------------------------
# Prahy. "povod": SKILL = prevzaté zo SKILL.md / slova.md bez zmeny,
# NAVRH = prah skriptu, ktorý SKILL.md neurčuje (odhad),
# KALIBRACIA CZ = prah českého skriptu odvodený z českých ľudských textov
# (UD Czech-CAC, FicTree, úseky po ~190 slovách); prevzatý ako východisko,
# KALIBRACIA SNK = overené alebo upravené na slovenských ľudských textoch
# (UD Slovak-SNK 443 úsekov po ~190 slovách, 86 tis. slov, bez modelu a so zlatou
# anotáciou; tools/kalibracia/kalibracia_ud.py --hranice zdroj). Číslo v zátvorke je
# podiel ľudských úsekov s nálezom P1 danej kategórie. SNK je výber viet, nie súvislé
# texty, preto sú čísla o rytme a susedných vetách len orientačné.
# Kalibrácia obmedzuje falošné poplachy; citlivosť na AI text nemeria.
# ---------------------------------------------------------------------------
PRAHY = {
    "pomlcky_na_300_slov": {"hodnota": 1, "povod": "SKILL; KALIBRACIA SNK: samotné prekročenie "
                                                   "je P2, P1 len v zhluku (3 %)"},
    "pomlcky_socialne_v_texte": {"hodnota": 2, "povod": "SKILL"},
    "vykricniky_na_1000_slov": {"hodnota": 1, "povod": "SKILL (slova.md)"},
    "emoji_socialne": {"hodnota": 2, "povod": "SKILL"},
    "hashtagy": {"hodnota": 5, "povod": "SKILL (slova.md: päť a viac)"},
    "uroven2_v_odseku": {"hodnota": 2, "povod": "SKILL (slova.md)"},
    "uroven2_dlhy_odsek_slov": {"hodnota": 120, "povod": "KALIBRACIA CZ + SNK"},
    "uroven2_v_dlhom_odseku": {"hodnota": 3, "povod": "KALIBRACIA CZ + SNK (1,3 – 1,6 %)"},
    "uroven3_v_odseku": {"hodnota": 4, "povod": "NAVRH + KALIBRACIA CZ"},
    "rytmus_podobna_dlzka_slov": {"hodnota": 2, "povod": "NAVRH"},
    "rytmus_podobna_dlzka_podiel": {"hodnota": 0.15, "povod": "NAVRH"},
    "rytmus_beh_p2": {"hodnota": 5, "povod": "NAVRH + KALIBRACIA CZ"},
    "rytmus_cv_min": {"hodnota": 0.25, "povod": "NAVRH + KALIBRACIA CZ"},
    "rytmus_cv_min_viet": {"hodnota": 6, "povod": "NAVRH"},
    "kratka_veta_slov": {"hodnota": 5, "povod": "NAVRH"},
    "retaz_kratkych_viet": {"hodnota": 3, "povod": "SKILL"},
    "heslo_slov": {"hodnota": 3, "povod": "NAVRH"},
    "heslovita_kadencia_miest": {"hodnota": 3, "povod": "SKILL; KALIBRACIA SNK (1,6 – 3,4 %)"},
    "kontrast_na_text": {"hodnota": 1, "povod": "SKILL; KALIBRACIA SNK (0 %)"},
    "trojice_prid_mien_na_text": {"hodnota": 1, "povod": "SKILL; KALIBRACIA SNK (0,4 – 0,7 %)"},
    "privesky_na_100_viet": {"hodnota": 6.0, "povod": "NAVRH + KALIBRACIA CZ"},
    "konektory_na_100_viet": {"hodnota": 12.0, "povod": "NAVRH + KALIBRACIA CZ"},
    "konektory_retaz": {"hodnota": 3, "povod": "SKILL (slova.md)"},
    "avsak_ritual": {"hodnota": 2, "povod": "NAVRH"},
    "menne_vety_podiel_p1": {"hodnota": 0.5, "povod": "SKILL (väčšina viet)"},
    "slovesna_subst_na_1000_slov": {"hodnota": 60.0, "povod": "NAVRH + KALIBRACIA CZ"},
    "opisne_pasivum_p2": {"hodnota": 2, "povod": "SKILL (jedno je slabé samo osebe)"},
    "opisne_pasivum_podiel_p2": {"hodnota": 0.2, "povod": "NAVRH + KALIBRACIA CZ"},
    "zamena_podmet_svoj_okno": {"hodnota": 4, "povod": "NAVRH + KALIBRACIA CZ"},
    "ukazovacie_zaciatky": {"hodnota": 3, "povod": "NAVRH"},
    "ukazovacie_zaciatky_podiel": {"hodnota": 0.25, "povod": "NAVRH"},
    "prechody_p1": {"hodnota": 2, "povod": "KALIBRACIA CZ (jediný prechod v 4 % českých "
                                           "ľudských úsekov); SNK (P1 v 0 %)"},
    "bohemizmy_zhluk": {"hodnota": 3, "povod": "SKILL (slova.md: tri a viac)"},
    "ceska_stopa_max": {"hodnota": 10, "povod": "NAVRH (nad prahom je text zrejme český)"},
}


def prah(jmeno):
    return PRAHY[jmeno]["hodnota"]


# ---------------------------------------------------------------------------
# Referenčné hodnoty SÚ ČESKÉ: písaný Koditex, 5,08 mil. slov, proti AI-Koditexu v2
# (25 modelov, rovnakých 150 textov); zdroje v references/zdroje.md. Na slovenčine
# ich nikto nemeral. Slúžia len ako orientácia pri informatívnych metrikách: česká AI
# má pri postoji a konkrétnosti zhruba polovicu ľudskej hodnoty, pri súdržnosti viac.
# Prepis nemá hodnoty postoja a konkrétnosti znižovať (SKILL.md, poistky).
# ---------------------------------------------------------------------------
REFERENCE = {
    "ktory_na_1000_slov": {"ludia": 7.7, "ai": 11.8, "jazyk": "cs"},
    "co_na_100_viet": {"ludia": 0.59, "ai": 1.16, "jazyk": "cs"},
    "modalne_na_1000_slov": {"ludia": 3.3, "ai": 1.3, "jazyk": "cs"},
    "oslabujuce_na_1000_slov": {"ludia": 1.9, "ai": 1.0, "jazyk": "cs"},
    "osoba2_zamena_na_1000_slov": {"ludia": 3.2, "ai": 1.6, "jazyk": "cs"},
    "otazniky_na_100_viet": {"ludia": 5.38, "ai": 2.65, "jazyk": "cs"},
    "cisla_na_1000_slov": {"ludia": 16.3, "ai": 8.8, "jazyk": "cs"},
    "vlastne_mena_na_1000_slov": {"ludia": 42.4, "ai": 24.1, "jazyk": "cs"},
    "tento_na_zaciatku_podiel_viet": {"ludia": 0.007, "ai": 0.03, "jazyk": "cs"},
}


# ---------------------------------------------------------------------------
# Profily registrov (tabuľka v SKILL.md, oddiel Profily registrov)
# ---------------------------------------------------------------------------
PROFILY = {
    "socialne": dict(seznamy="prisne", pomlcky="socialne", spojovnik_nalez=False,
                     rytmus=False, kratke_vety=False, jmenny_styl=True, pasivum=True,
                     emoji=prah("emoji_socialne"), tech_vyjimky=False, uredni=True,
                     odhaleni=True, vykricniky=False, titulky_upoutavka="P2"),
    "blog": dict(seznamy="prisne", pomlcky="prisne", spojovnik_nalez=True,
                 rytmus=True, kratke_vety=True, jmenny_styl=True, pasivum=True,
                 emoji=0, tech_vyjimky=False, uredni=True, odhaleni=True,
                 vykricniky=True, titulky_upoutavka="P2"),
    "email": dict(seznamy="p0p1", pomlcky="prisne", spojovnik_nalez=False,
                  rytmus=False, kratke_vety=False, jmenny_styl=True, pasivum=True,
                  emoji=0, tech_vyjimky=False, uredni=True, odhaleni=False,
                  vykricniky=True, titulky_upoutavka="P2"),
    "dokumentacia": dict(seznamy="castecne", pomlcky="volne", spojovnik_nalez=False,
                         rytmus=False, kratke_vety=False, jmenny_styl=False, pasivum=False,
                         emoji=0, tech_vyjimky=True, uredni=False, odhaleni=False,
                         vykricniky=True, titulky_upoutavka="P2"),
    "odborny": dict(seznamy="prisne", pomlcky="prisne", spojovnik_nalez=True,
                    rytmus=True, kratke_vety=True, jmenny_styl=False, pasivum=False,
                    emoji=0, tech_vyjimky=True, uredni=True, odhaleni=True,
                    vykricniky=True, titulky_upoutavka="P2"),
    "prezentacia": dict(seznamy="prisne", pomlcky="prisne", spojovnik_nalez=True,
                        rytmus=True, kratke_vety=False, jmenny_styl=False, pasivum=True,
                        emoji=0, tech_vyjimky=False, uredni=True, odhaleni=True,
                        vykricniky=True, titulky_upoutavka="P1"),
}
ALIASY_PROFILU = {
    "soc": "socialne", "socialne-siete": "socialne", "sociálne": "socialne",
    "socialni": "socialne", "linkedin": "socialne", "esej": "blog", "clanok": "blog",
    "článok": "blog", "e-mail": "email", "sprava": "email", "správa": "email",
    "slack": "email", "dok": "dokumentacia", "dokumentácia": "dokumentacia",
    "dokumentace": "dokumentacia", "tech": "dokumentacia", "pravny": "dokumentacia",
    "právny": "dokumentacia", "odb": "odborny", "odborný": "odborny",
    "prez": "prezentacia", "prezentácia": "prezentacia", "prezentace": "prezentacia",
    "slajdy": "prezentacia",
}

PORADI_ZAV = {"P0": 0, "P1": 1, "P2": 2, "info": 3}

# ---------------------------------------------------------------------------
# Pomocné zoznamy (gramatika, nie slovník slopu – ten je v slova.md)
# ---------------------------------------------------------------------------
ZKRATKY_NIKDY_KONEC = {
    "t", "j", "tj", "napr", "tzv", "resp", "cca", "popr", "príp", "č", "čís", "s", "str",
    "obr", "tab", "kap", "ods", "písm", "ing", "mgr", "bc", "mudr", "judr", "phdr",
    "rndr", "paeddr", "mvdr", "mddr", "thdr", "doc", "prof", "dr", "p", "sv", "ul", "nám",
    "tel", "vr", "zvl", "tr", "roč", "zb", "z", "hod", "min", "max", "tis", "mil", "mld",
    "st", "ml", "tzn", "porov", "pozn", "event", "ev", "et", "al", "vs", "jr", "sr",
    "arch", "dipl", "csc", "drsc", "mba", "o", "r", "a", "angl", "nem", "lat", "gr",
    "zák", "vyhl", "čl", "bod",
}
ZKRATKY_MOZNA_KONEC = {"atď", "pod", "apod", "i", "etc", "spol", "a.s", "s.r.o"}

ZVRATNA = {"sa", "si"}
OSOBNI_ZAJMENA = {
    "ja", "ma", "mňa", "mi", "mne", "mnou", "ty", "ťa", "teba", "ti", "tebe", "tebou",
    "my", "nás", "nám", "nami", "vy", "vás", "vám", "vami", "on", "ona", "ono", "oni",
    "ony", "jeho", "ho", "mu", "jemu", "ním", "neho", "nemu", "ňom", "ňu", "ju", "jej",
    "nej", "ňou", "ich", "im", "nimi", "nich", "nim",
}
ZAJMENA_1OS = {"ja", "ma", "mňa", "mi", "mne", "mnou", "my", "nás", "nám", "nami",
               "môj", "moja", "moje", "môjho", "môjmu", "mojím", "mojich", "mojimi",
               "mojej", "moju", "mojou", "moji", "mojom",
               "náš", "naša", "naše", "nášho", "nášmu", "naším", "našich", "našimi",
               "našej", "našu", "našou", "naši", "našom"}
ZAJMENA_2OS = {"ty", "ťa", "teba", "ti", "tebe", "tebou", "vy", "vás", "vám", "vami",
               "tvoj", "tvoja", "tvoje", "tvojho", "tvojmu", "tvojím", "tvojich", "tvojimi",
               "tvojej", "tvoju", "tvojou", "tvoji", "tvojom",
               "váš", "vaša", "vaše", "vášho", "vášmu", "vaším", "vašich", "vašimi",
               "vašej", "vašu", "vašou", "vaši", "vašom"}
TVARY_SVUJ = {"svoj", "svoja", "svoje", "svojho", "svojmu", "svojím", "svojich", "svojimi",
              "svojej", "svoju", "svojou", "svoji", "svojom"}
TVARY_TENTO = {"tento", "táto", "toto", "títo", "tieto", "tohto", "tomuto", "tomto",
               "týmto", "tejto", "túto", "touto", "týchto", "týmito"}
CASTICE = ["predsa", "veď", "hádam", "asi", "vraj", "totiž", "vlastne", "azda", "vari",
           "no", "teda", "ostatne", "napokon", "aspoň"]
# náprotivky českej definície (unslop-cs, tools/koditex/features.py); s českou
# referenciou sú porovnateľné len orientačne
MODALNI = {"predsa", "veď", "vraj", "totiž", "vlastne", "no", "vari", "ostatne", "napokon",
           "aspoň", "hlavne", "teda"}
OSLABUJICI = {"snáď", "asi", "možno", "zrejme", "pravdepodobne", "údajne", "azda",
              "hádam", "akiste"}
KONEKTORY = ["v neposlednom rade", "okrem toho", "vďaka tomu", "navyše", "zároveň",
             "avšak", "ďalej", "rovnako", "súčasne", "celkovo", "taktiež"]
# v českých dátach nie sú na začiatku vety pri AI častejšie než pri ľuďoch, prekážajú
# len v reťazi
KONEKTORY_JEN_RETEZ = {"navyše", "ďalej"}
POMOCNE_PRIKLONKY = {"som", "si", "sme", "ste", "by"}
STOP = {"byť", "o", "v", "vo", "na", "a", "sa", "si", "ten", "to", "že", "do", "s", "so",
        "z", "zo", "k", "ku", "u", "je", "i", "aj", "ako", "pre", "po", "za", "sú", "tak",
        "toho", "tom", "pri", "som", "sme", "ste"}
ZASTUPCE = {"x", "y", "z", "niekým", "niekoho", "niečo", "niečoho", "niekto", "niečom",
            "…", "..."}
VNOUN_NEJSOU = {"námestie", "šťastie", "nešťastie", "zbožie", "ústie", "lístie",
                "kamenie", "uhlie", "imanie", "zdravie", "napätie", "hnutie", "storočie",
                "dianie", "znamenie", "pokolenie", "umenie", "svedomie", "vedomie",
                "stavenie", "pobrežie", "zátišie", "územie", "prostredie", "obdobie",
                "údolie", "poschodie", "podujatie", "oddelenie", "zariadenie",
                "vzdelanie", "povolanie", "zamestnanie", "tisícročie", "desaťročie",
                "výročie", "predmestie", "ovzdušie", "podnebie", "pohorie", "úsilie",
                "popoludnie", "dopoludnie", "väzenie", "podsvetie", "opatrenie",
                "stretnutie", "utrpenie", "pokušenie", "presvedčenie", "podozrenie",
                "prekvapenie", "predstavenie", "postavenie", "správanie"}
NEJSOU_CLENY = {"a", "i", "aj", "ale", "alebo", "či", "ani", "však", "teda", "že", "ako",
                "čo", "ktorý", "ktorá", "ktoré", "keď", "aby", "pretože", "lebo", "nie",
                "len", "potom"}
CISLOVKY_SLOVY = (r"(?:jeden|jedna|jedno|dva|dve|dvaja|tri|traja|štyri|päť|šesť|sedem|osem|"
                  r"deväť|desať|\d+)")

# Bohemizmy, ktoré sa neskloňujú: len presný tvar (kmeň by chytil „beh“, „hodný“).
BOHEMIZMY_PRESNE = {"behom", "naviac", "zrovna", "hodne", "pokiaľ", "kľudne", "predať",
                    "previesť"}
# Tvary, ktoré kmeňovač nespojí (krátky kmeň sa páruje len presne, pohyblivá samohláska).
BOHEMIZMY_TVARY = {
    "zbytok": {"zbytku", "zbytky", "zbytkom", "zbytkov", "zbytkami"},
    "vadiť": {"vadí", "vadia", "vadil", "vadila", "vadilo", "vadili", "nevadí", "nevadia",
              "nevadilo"},
    "kľud": {"kľudu", "kľude", "kľudom"},
    "dotaz": {"dotazy", "dotazu", "dotazov", "dotazom", "dotazoch"},
    "dopis": {"dopisy", "dopisu", "dopisov", "dopise", "dopisom"},
    "sleva": {"slevy", "slevu", "slevou", "slev", "sleve"},
    "jednať": {"jedná", "jednalo", "jednala", "jednal", "jednali"},
    "celá": {"celú", "celej", "celou"},
    "rada": {"radu", "rady", "radou"},
}
# Hrubý odhad slovesa bez modelu (minulý čas, 1. a 2. osoba, neurčitok, byť, zvratné).
RE_ASI_SLOVESO = re.compile(r"^(?:je|sú|som|si|sme|ste|sa|bol[aoi]?|bude|budú|má|máš|máte|"
                            r"vieš|viete|chceš|chcete|ide|idú)$|[^\W\d_]{2,}(?:l[aoi]?|te|"
                            r"me|š|ť|jem|jú|ím|ám)$")
RE_ADJ_Z_MENA = re.compile(r"(?:sk|ck)(?:ý|á|é|ého|ému|ej|ú|om|ým|ou|í|ých|ými|e)$")
RE_CESKE_PISMENO = re.compile(r"(?<![^\W_])[^\W\d_]*[ěřů][^\W\d_]*")

# Prívesky: „, čo“ len so slovesom dôsledku (približné), „, čím“ bez stupňovania,
# „, a tým“. „Pričom“ sa nepočíta: v ľudskej slovenčine je bežné.
_SLOVESA_DOSLEDKU = (r"znamen|umožň|vedie|viedl|zvyš|zniž|zvýš|zníž|robí|dáva|prináš|"
                     r"prispiev|zabezpeč|posil|demonštr|dokazuj|svedč|podčiark|zdôrazň|"
                     r"odráž|vytvár|uľahč|zlepš|zrých|šetr|pomáh|ukazuj|potvrdz|predstavuj")
RE_PRIVESOK_CO = re.compile(r"(?i),\s*čo\s+(?:\w+\s+){0,2}?(?:%s)\w*" % _SLOVESA_DOSLEDKU)
RE_PRIVESOK = re.compile(
    r"(?i),\s*(čo(?=\s+(?:\w+\s+){0,2}?(?:%s))"
    r"|čím\b(?!\s+(?:viac|menej|skôr|neskôr|ďalej|\w+(?:šie|ší|šia|šiu|ť)\b))"
    r"|a\s+tým\b)" % _SLOVESA_DOSLEDKU)

RE_SLOVO = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*")
RE_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")


# ---------------------------------------------------------------------------
# Dátové štruktúry
# ---------------------------------------------------------------------------
@dataclass
class Tok:
    form: str
    lemma: str
    upos: str
    feats: dict
    head: int
    deprel: str
    start: int
    end: int
    idx: int  # poradie vo vete od 0

    @property
    def low(self):
        return self.form.lower()

    def je_slovo(self):
        if self.upos:
            return self.upos not in ("PUNCT", "SYM")
        return any(c.isalnum() for c in self.form)


@dataclass
class Veta:
    start: int
    end: int
    tokens: list
    blok: int
    druh: str  # veta | titulek | riadok
    text: str = ""

    def slova(self):
        return [t for t in self.tokens if t.je_slovo()]

    def pocet_slov(self):
        return len(self.slova())


@dataclass
class Nalez:
    metrika: str
    kategorie: str
    zavaznost: str
    start: int
    end: int
    text: str
    poznamka: str = ""
    priblizne: bool = False
    zdroj: str = ""

    def jako_dict(self, radky):
        r, s = radky(self.start)
        d = dict(metrika=self.metrika, kategoria=self.kategorie, zavaznost=self.zavaznost,
                 text=self.text, pozicia=[self.start, self.end], riadok=r, stlpec=s)
        if self.poznamka:
            d["poznamka"] = self.poznamka
        if self.zdroj:
            d["zdroj"] = self.zdroj
        if self.priblizne:
            d["priblizne"] = True
        return d


# ---------------------------------------------------------------------------
# Kmeňovanie bez modelu (ľahký kmeňovač pre slovenčinu; výsledok je približný)
# ---------------------------------------------------------------------------
_PRIPONY = sorted(set("""
ovať ujúci ujúca ujúce ujúcich ujete ujeme ovali ovala ovalo ujem uješ ujú uje
ých ými ého ému ieho iemu ími ích iach iami iam ách ami ovia ovi och
ajú ám áš áme áte am ame ate ím íš íme íte ia ie iu ií iou
em eš eme ete om ov ou ej
ať iť ieť áť úť al ala alo ali il ila ilo ili ul ula ulo uli
a e i o u y á é í ú ý ä
""".split()), key=len, reverse=True)


@functools.lru_cache(maxsize=None)
def kmen(slovo):
    w = slovo.lower()
    for p in _PRIPONY:
        if w.endswith(p) and len(w) - len(p) >= 3:
            return w[: -len(p)]
    return w


_SAMOHLASKY = set("aeiouyáäéíóôúýĺŕ")
_ALTERNACE = {frozenset(p) for p in ("kč", "kc", "hž", "gž", "dď", "tť", "nň", "lľ",
                                     "sš", "zž", "cč", "šc", "kš", "hš")}


def shoda_kmenu(a, b):
    if a == b:
        return True
    n = min(len(a), len(b))
    if n < 5 or max(len(a), len(b)) - n > 1:
        return False
    cp = 0
    for x, y in zip(a, b):
        if x != y:
            break
        cp += 1
    if cp >= n:
        return True
    if cp < n - 1:
        return False
    # líši sa posledný znak kratšieho kmeňa: samohláska je obmena kmeňa (úroveň/úrovn),
    # dve spoluhlásky len vtedy, keď ide o slovenskú alternáciu (t/ť, n/ň, k/č), nie
    # o iné slovo (model/modern)
    x, y = a[cp], b[cp]
    if x in _SAMOHLASKY or y in _SAMOHLASKY:
        return True
    return frozenset((x, y)) in _ALTERNACE


# ---------------------------------------------------------------------------
# UDPipe
# ---------------------------------------------------------------------------
class UDPipe:
    def __init__(self, cesta):
        try:
            from ufal.udpipe import Model, Pipeline, ProcessingError  # noqa
        except ImportError:
            raise SystemExit("Chýba balík ufal.udpipe (pip install ufal.udpipe).")
        self._PE = ProcessingError
        self.model = Model.load(cesta)
        if not self.model:
            raise SystemExit(f"Model UDPipe sa nepodarilo načítať: {cesta}")
        self.pipe = Pipeline(self.model, "tokenizer=ranges", Pipeline.DEFAULT,
                             Pipeline.DEFAULT, "conllu")
        self.pipe_preseg = Pipeline(self.model, "tokenizer=ranges;presegmented",
                                    Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")

    def zpracuj(self, text, presegmented=False):
        """Vráti zoznam viet; každá veta je zoznam Tok s offsetmi voči `text`."""
        err = self._PE()
        out = (self.pipe_preseg if presegmented else self.pipe).process(text, err)
        if err.occurred():
            raise RuntimeError(err.message)
        vety, akt, mwt = [], [], {}
        for line in out.split("\n"):
            if not line:
                if akt:
                    vety.append(akt)
                akt, mwt = [], {}
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 10:
                continue
            rng = re.search(r"TokenRange=(\d+):(\d+)", c[9])
            if "-" in c[0]:
                a, b = map(int, c[0].split("-"))
                for i in range(a, b + 1):
                    mwt[i] = (int(rng.group(1)), int(rng.group(2))) if rng else None
                continue
            if "." in c[0]:
                continue
            i = int(c[0])
            if rng:
                s, e = int(rng.group(1)), int(rng.group(2))
            elif mwt.get(i):
                s, e = mwt[i]
            else:
                s = e = akt[-1].end if akt else 0
            feats = {}
            if c[5] != "_":
                for f in c[5].split("|"):
                    if "=" in f:
                        k, v = f.split("=", 1)
                        feats[k] = v
            akt.append(Tok(c[1], c[2], c[3], feats, int(c[6]) if c[6].isdigit() else 0,
                           c[7], s, e, len(akt)))
        if akt:
            vety.append(akt)
        return vety


# ---------------------------------------------------------------------------
# Príprava textu: maskovanie chránených miest a bloky
# ---------------------------------------------------------------------------
RE_OHRAZENI = re.compile(r"^ {0,3}(`{3,}|~{3,})")
RE_CITACE_RADEK = re.compile(r"^ {0,3}>")
RE_UPOZORNENI = re.compile(r"\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", re.I)
RE_TAB_ODDELOVAC = re.compile(r"^ {0,3}\|?[ \t]*:?-+:?[ \t]*(\|[ \t]*:?-+:?[ \t]*)*\|?[ \t]*$")
RE_ODSAZENY_KOD = re.compile(r"^( {4}|\t)[ \t]*\S")
RE_POLOZKA_RADEK = re.compile(r"^ {0,3}([-*+•]|\d{1,2}[.)])[ \t]+\S")
RE_HTML_KOD = re.compile(r"<(pre|code)\b[^>]*>.*?</\1\s*>", re.S | re.I)
RE_INLINE_KOD = re.compile(r"(`+)(?!`)[^\n]*?[^`\n](?<!`)\1(?!`)")
RE_URL_MAIL = re.compile(r"\bhttps?://\S+|\bwww\.\S+|\b[\w.+-]+@[\w-]+\.[\w.]+")


def maskuj(text, vse=False):
    """Pripraví text na meranie. Vráti (masked, pasma).

    masked: kópia textu, v ktorej sú kód, URL, e-mailové adresy a blokové citácie „>“
    nahradené medzerami (dĺžka a konce riadkov zostávajú, pozície nálezov sedia na
    pôvodný text). Vylúčený text sa nepočíta do ničoho: do slov, pomlčiek, viet ani rytmu.

    pasma: [(start, end, druh)] blokov mimo merania pre hlásenie vo výstupe a hranice
    rytmu. Druh kod a citacia je vymazaný; druh tabulka zostáva, len bez zvislých čiar
    a oddeľovacieho riadka: miestne nálezy v bunkách idú do info a bunky sa nepočítajú
    do slov, pomlčiek ani rytmu (Dokument.slova).

    Kód (ohradenie ``` a ~~~, odsadený blok, <pre>, <code>, inline `kód`), URL
    a e-maily sa maskujú vždy. S vse=True sa citácie a tabuľky merajú ako bežný text.
    Upozornenia GitHubu („> [!NOTE]“) sú text autora a merajú sa aj bez vse."""
    chars = list(text)

    def vymaz(a, b):
        for i in range(a, b):
            if chars[i] != "\n":
                chars[i] = " "

    radky = []
    pos = 0
    for line in text.split("\n"):
        radky.append((pos, pos + len(line), line))
        pos += len(line) + 1
    n = len(radky)
    obsazeno = [False] * n
    pasma = []

    def pridej_pasmo(i, j, druh):
        """Riadky i..j (vrátane) ako jedno pásmo."""
        for k in range(i, j + 1):
            obsazeno[k] = True
        pasma.append((radky[i][0], radky[j][1], druh))

    # 1. ohradené bloky ``` a ~~~ (neuzavretý blok siaha do konca textu)
    i = 0
    while i < n:
        m = RE_OHRAZENI.match(radky[i][2])
        if m and not (m.group(1)[0] == "`" and "`" in radky[i][2][m.end():]):
            zn = m.group(1)
            zav = re.compile(r"^ {0,3}" + re.escape(zn[0]) + "{" + str(len(zn)) + r",}[ \t]*$")
            j = i + 1
            while j < n and not zav.match(radky[j][2]):
                j += 1
            j = min(j, n - 1)
            pridej_pasmo(i, j, "kod")
            vymaz(radky[i][0], radky[j][1])
            i = j + 1
        else:
            i += 1

    def radek_na(p):
        lo, hi = 0, n - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if radky[mid][0] <= p:
                lo = mid
            else:
                hi = mid - 1
        return lo

    # 2. HTML <pre> a <code>; viacriadkový sa hlási ako blok kódu, jednoriadkový ako inline
    for m in RE_HTML_KOD.finditer(text):
        i, j = radek_na(m.start()), radek_na(m.end())
        if any(obsazeno[k] for k in range(i, j + 1)):
            continue
        vymaz(m.start(), m.end())
        if m.group(1).lower() == "pre" or i != j:
            for k in range(i, j + 1):
                obsazeno[k] = True
            pasma.append((m.start(), m.end(), "kod"))

    # 3. blokové citácie „>“; upozornenia GitHubu zostávajú, maže sa len značka [!NOTE]
    i = 0
    while i < n:
        if obsazeno[i] or not RE_CITACE_RADEK.match(radky[i][2]):
            i += 1
            continue
        j = i
        while j + 1 < n and not obsazeno[j + 1] and RE_CITACE_RADEK.match(radky[j + 1][2]):
            j += 1
        prvni = radky[i][2].lstrip(" >\t")
        upoz = RE_UPOZORNENI.match(prvni)
        if upoz:
            s = radky[i][0] + radky[i][2].index(upoz.group(0))
            vymaz(s, s + len(upoz.group(0)))
        elif not vse:
            pridej_pasmo(i, j, "citacia")
            vymaz(radky[i][0], radky[j][1])
        i = j + 1

    # 4. tabuľky Markdownu: riadok so zvislou čiarou a pod ním oddeľovací riadok
    if not vse:
        i = 0
        while i + 1 < n:
            if obsazeno[i] or obsazeno[i + 1] or "|" not in radky[i][2] or \
                    "|" not in radky[i + 1][2] or not RE_TAB_ODDELOVAC.match(radky[i + 1][2]):
                i += 1
                continue
            j = i + 1
            while j + 1 < n and not obsazeno[j + 1] and "|" in radky[j + 1][2] and \
                    radky[j + 1][2].strip():
                j += 1
            pridej_pasmo(i, j, "tabulka")
            vymaz(radky[i + 1][0], radky[i + 1][1])
            for k in range(i, j + 1):
                a, b, _ = radky[k]
                for p in range(a, b):
                    if chars[p] == "|":
                        chars[p] = " "
            i = j + 1

    # 5. odsadený kód (CommonMark): pred blokom prázdny riadok a nejde o pokračovanie
    # položky zoznamu. Keď je odsadená viac než polovica odsekov, ide o odsadenie
    # prvého riadka (text z Wordu), nie o kód.
    kandidati = []
    odstavcu = 0
    i = 0
    predchozi_neprazdny = None  # index posledného neprázdneho riadka
    while i < n:
        line = radky[i][2]
        if not line.strip() or obsazeno[i]:
            if line.strip():
                predchozi_neprazdny = i
            i += 1
            continue
        odstavcu += 1
        zacatek_odstavce = i
        if RE_ODSAZENY_KOD.match(line) and (i == 0 or not radky[i - 1][2].strip()) and (
                predchozi_neprazdny is None or
                not (RE_POLOZKA_RADEK.match(radky[predchozi_neprazdny][2]) or
                     re.match(r"^[ \t]{2,}\S", radky[predchozi_neprazdny][2]))):
            j = i
            while True:
                k = j + 1
                while k < n and not radky[k][2].strip() and not obsazeno[k]:
                    k += 1
                if k < n and not obsazeno[k] and RE_ODSAZENY_KOD.match(radky[k][2]):
                    j = k
                else:
                    break
            kandidati.append((i, j))
            predchozi_neprazdny = j
            i = j + 1
            continue
        while i < n and radky[i][2].strip() and not obsazeno[i]:
            i += 1
        predchozi_neprazdny = i - 1 if i > zacatek_odstavce else predchozi_neprazdny
    if kandidati and len(kandidati) * 2 <= odstavcu:
        for i, j in kandidati:
            pridej_pasmo(i, j, "kod")
            vymaz(radky[i][0], radky[j][1])

    # 6. inline kód, URL a e-maily (vždy, mimo už vymazaných blokov)
    for k, (a, b, line) in enumerate(radky):
        if obsazeno[k]:
            continue
        for m in RE_INLINE_KOD.finditer(line):
            vymaz(a + m.start(), a + m.end())
    for m in RE_URL_MAIL.finditer(text):
        vymaz(m.start(), m.end())
    pasma.sort()
    return "".join(chars), pasma


RE_ZNACKA = re.compile(r"^([ \t]*)(#{1,6}[ \t]+|>[ \t]?|[-*•][ \t]+|\d{1,2}[.)][ \t]+)")
RE_KONCOVA = re.compile(r"[.!?:;…]\s*[\"“”»)]*\s*$")


def bloky(masked, tabulky=()):
    """Rozdelí text na bloky: (start, end, druh) s druhom odstavec | nadpis | polozka |
    tabulka (každý riadok tabuľky je samostatný blok). Značky zoznamov, nadpisov
    a citácií v `masked` nahradí medzerami (vracia nový masked). `tabulky` sú rozsahy
    (start, end) tabuliek z maskuj()."""
    chars = list(masked)
    out = []
    pos = 0
    odst = None  # [start, end]
    for line in masked.split("\n"):
        ls, le = pos, pos + len(line)
        pos = le + 1
        if any(a <= ls and le <= b for a, b in tabulky):
            if odst:
                out.append((odst[0], odst[1], "odstavec"))
                odst = None
            if line.strip():
                out.append((ls, le, "tabulka"))
            continue
        m = RE_ZNACKA.match(line)
        druh = "text"
        if m:
            zn = m.group(2)
            for i in range(ls + len(m.group(1)), ls + m.end()):
                chars[i] = " "
            if zn.startswith("#"):
                druh = "nadpis"
            elif zn.startswith(">"):
                druh = "text"
            else:
                druh = "polozka"
        obsah = "".join(chars[ls:le]).strip()
        if not obsah:
            if odst:
                out.append((odst[0], odst[1], "odstavec"))
                odst = None
            continue
        if druh in ("nadpis", "polozka"):
            if odst:
                out.append((odst[0], odst[1], "odstavec"))
                odst = None
            out.append((ls, le, druh))
            continue
        if odst:
            odst[1] = le
        else:
            odst = [ls, le]
    if odst:
        out.append((odst[0], odst[1], "odstavec"))
    return "".join(chars), out


def segmenty(masked, start, end):
    """Odsek rozdelí na riadkové úseky: zalomenie riadka je hranica, keď riadok
    nekončí interpunkciou a ďalší sa začína veľkým písmenom (podpis, oslovenie, titulok)."""
    text = masked[start:end]
    radky = []
    p = start
    for line in text.split("\n"):
        radky.append((p, p + len(line)))
        p += len(line) + 1
    seg = []
    akt = None
    for i, (a, b) in enumerate(radky):
        obsah = masked[a:b].strip()
        if not obsah:
            continue
        if akt is None:
            akt = [a, b]
        else:
            predchozi = masked[akt[0]:akt[1]].rstrip()
            zacatek = obsah[:1]
            if not RE_KONCOVA.search(predchozi) and zacatek.isupper():
                seg.append(tuple(akt))
                akt = [a, b]
            else:
                akt[1] = b
    if akt:
        seg.append(tuple(akt))
    return seg


# ---------------------------------------------------------------------------
# Delenie na vety bez modelu
# ---------------------------------------------------------------------------
RE_KANDIDAT = re.compile(r"[.!?…]+[\"“”»’)\]]*(?=\s|$)")


def deleni_vet_pravidla(text, a, b):
    """Vráti zoznam (start, end) viet v text[a:b]."""
    vety = []
    s = a
    while s < b and text[s].isspace():
        s += 1
    for m in RE_KANDIDAT.finditer(text, s, b):
        if m.start() < s:
            continue
        interp = m.group(0)
        konec = m.end()
        # ďalší znak po medzerách
        j = konec
        while j < b and text[j].isspace():
            j += 1
        dalsi = text[j] if j < b else ""
        dalsi_n = dalsi
        k = j
        while dalsi_n and dalsi_n in "„\"“‚'(«»[" and k + 1 < b:
            k += 1
            dalsi_n = text[k]
        pred = re.search(r"([^\W_]+)[\W_]*$", text[s:m.start() + 1]) if m.start() >= s else None
        slovo = pred.group(1) if pred else ""
        tecka_jen = set(interp.rstrip("\"“”»’)]")) <= {"."}
        if not dalsi:
            je_konec = True
        elif not tecka_jen:
            # ! ? … ukončujú vetu, ak nepokračuje malé písmeno po výpustke
            # slovenská veta sa nezačína malým písmenom („Čo?“ spýtala sa.)
            je_konec = not dalsi_n.islower()
        elif dalsi_n.islower():
            je_konec = False
        elif dalsi_n.isdigit():
            je_konec = not (slovo.isdigit() or slovo.lower() in ZKRATKY_NIKDY_KONEC)
        else:
            lo = slovo.lower()
            if lo in ZKRATKY_NIKDY_KONEC:
                je_konec = False
            elif len(slovo) == 1 and slovo.isupper():
                je_konec = False  # iniciálka
            elif re.search(r"\b(?:Ph|Th|Dr|Mgr|Ing|Bc)\.\s*[A-Z]?$", text[s:m.start()]):
                je_konec = False
            else:
                je_konec = True
        if je_konec:
            vety.append((s, konec))
            s = j
    if s < b and text[s:b].strip():
        e = b
        while e > s and text[e - 1].isspace():
            e -= 1
        vety.append((s, e))
    return vety


def tokeny_pravidla(text, a, b):
    toks = []
    for m in re.finditer(r"[^\W_]+(?:[-'’][^\W_]+)*|[^\w\s]", text[a:b]):
        f = m.group(0)
        toks.append(Tok(f, kmen(f) if f[0].isalnum() else f, "", {}, 0, "",
                        a + m.start(), a + m.end(), len(toks)))
    return toks


# ---------------------------------------------------------------------------
# Analýza textu: vety a tokeny
# ---------------------------------------------------------------------------
class Dokument:
    def __init__(self, text, udpipe=None, vse=False):
        self.text = text
        self.udpipe = udpipe
        self.masked0, self.pasma = maskuj(text, vse)
        self.masked, self.bloky = bloky(self.masked0, [(a, b) for a, b, d in self.pasma
                                                       if d == "tabulka"])
        self.vety = []
        self._radky = [0]
        for i, ch in enumerate(text):
            if ch == "\n":
                self._radky.append(i + 1)
        self._analyzuj()

    def radek(self, pos):
        import bisect
        r = bisect.bisect_right(self._radky, pos) - 1
        return r + 1, pos - self._radky[r] + 1

    def _vety_z_useku(self, a, b, blok, titulek):
        useky = []
        if self.udpipe:
            usek = self.masked[a:b]
            for toks in self.udpipe.zpracuj(usek.replace("\n", " "), presegmented=titulek):
                for t in toks:
                    t.start += a
                    t.end += a
                if toks:
                    useky.append(toks)
        else:
            rozsahy = [(a, b)] if titulek else deleni_vet_pravidla(self.masked, a, b)
            for s, e in rozsahy:
                toks = tokeny_pravidla(self.masked, s, e)
                if toks:
                    useky.append(toks)
        for toks in useky:
            s, e = toks[0].start, toks[-1].end
            text = self.masked[s:e]
            n = sum(1 for t in toks if t.je_slovo())
            if titulek:
                druh = "titulek"
            else:
                druh = "veta"
            self.vety.append(Veta(s, e, toks, blok, druh, text))

    def _analyzuj(self):
        for bi, (a, b, druh) in enumerate(self.bloky):
            obsah = self.masked[a:b].strip()
            if not obsah:
                continue
            n_slov = len(RE_SLOVO.findall(obsah))
            if druh == "tabulka":
                n0 = len(self.vety)
                self._vety_z_useku(a, b, bi, True)
                for v in self.vety[n0:]:
                    v.druh = "tabulka"
                continue
            if druh == "nadpis" or (druh == "polozka" and not RE_KONCOVA.search(obsah)
                                     and n_slov <= 12):
                self._vety_z_useku(a, b, bi, True)
                continue
            for sa, sb in segmenty(self.masked, a, b):
                seg = self.masked[sa:sb].strip()
                ns = len(RE_SLOVO.findall(seg))
                samostatny = (len(self.bloky) > 1 and (sa, sb) == (a, b) and
                              not RE_KONCOVA.search(seg) and ns <= 10)
                if samostatny:
                    self._vety_z_useku(sa, sb, bi, True)
                elif not RE_KONCOVA.search(seg) and ns <= 4 and (sa, sb) != (a, b):
                    # krátky riadok bez interpunkcie vnútri odseku (podpis, oslovenie)
                    n0 = len(self.vety)
                    self._vety_z_useku(sa, sb, bi, False)
                    for v in self.vety[n0:]:
                        v.druh = "riadok"
                else:
                    self._vety_z_useku(sa, sb, bi, False)

    def slova(self):
        """Slová textu bez buniek tabuliek (tie sú mimo počtu slov, pomlčiek aj rytmu)."""
        return [t for v in self.vety if v.druh != "tabulka" for t in v.tokens if t.je_slovo()]

    def pocet_slov(self):
        return len(self.slova())

    def prozni_vety(self):
        return [v for v in self.vety if v.druh == "veta"]

    def vylouceno(self):
        """Súhrn textu mimo merania: koľko slov a koľko blokov podľa druhu."""
        slov, useku = 0, {}
        for a, b, druh in self.pasma:
            useku[druh] = useku.get(druh, 0) + 1
            if druh == "tabulka":
                slov += sum(v.pocet_slov() for v in self.vety
                            if v.druh == "tabulka" and a <= v.start < b)
            else:
                slov += len(RE_SLOVO.findall(self.text[a:b]))
        return {"slov": slov, "usekov": useku}

    def preruseno(self, a, b):
        """True, keď medzi pozíciami a < b leží blok mimo merania (kód, citácia, tabuľka)."""
        return any(a <= s and e <= b for s, e, _ in self.pasma)


# ---------------------------------------------------------------------------
# Parsovanie references/slova.md
# ---------------------------------------------------------------------------
@dataclass
class Polozka:
    sekce: str          # uroven1 | uroven2 | uroven3 | kalk | bohemizmus | fraze | vagni | chatbot | anglicizmus | opis | menny | uredni
    kategorie: str      # podrobnejšia kategória (napr. Úvody)
    zavaznost: str      # predvolená závažnosť
    raw: str
    varianty: list
    poznamka: str = ""
    podminka: bool = False   # poznámka obmedzuje platnosť (skript ju nevie overiť)
    tech: bool = False       # neplatí v technickom/odbornom profile
    privesek: bool = False   # platí len ako prívesok (, čo / čím / a tým)
    vzory: list = field(default_factory=list)
    presne: list = field(default_factory=list)   # bohemizmy: tvary na presnú zhodu


PREPISY_POLOZEK = {
    # Položky, kde čiarka neoddeľuje alternatívy, ale predmety jedného slovesa.
    "kontrolovať proces, tím, rozpočet": ["kontrolovať proces", "kontrolovať tím",
                                          "kontrolovať rozpočet"],
    "zdieľať s niekým novinku, aktualizáciu": ["zdieľať novinku", "zdieľať aktualizáciu"],
}

KATEGORIE_FRAZI = {
    "úvody": ("uvod", "P1"), "prechody": ("prechod", "P1"), "závery": ("zaver", "P2"),
    "falošné precitnutie": ("precitnutie", "P1"), "mravoučné pointy": ("pointa", "P1"),
    "okrídlené metafory": ("metafora-ai", "P1"),
    "plastová ľudskosť": ("hrana-uprimnost", "P1"),
    "ošúchané trojice": ("osuchana-trojica", "P1"), "sociálne siete": ("socialne-siete", "P1"),
}

# Frázy, ktoré sú celou vetou: párujú sa prísne, so všetkými slovami („Otvorilo mi to
# oči.“ nie je „otvoril oči“). KALIBRACIA SNK: voľné párovanie dávalo P1 v 4 % ľudských
# úsekov beletrie.
FRAZY_PRISNE = {"precitnutie", "pointa", "metafora-ai", "hrana-uprimnost"}

RE_PODMINKA = re.compile(r"\b(ako|mimo|pri|bez|keď|v prenesenom|prenesene|inflačne|v zmysle|"
                         r"namiesto)\b")
RE_TECH = re.compile(r"mimo (techni|odbor|štatisti|opisu technického)")


def _split_mimo_zavorky(s, sep=","):
    parts, d, akt = [], 0, ""
    for ch in s:
        if ch in "([":
            d += 1
        elif ch in ")]":
            d -= 1
        if ch == sep and d == 0:
            parts.append(akt)
            akt = ""
        else:
            akt += ch
    parts.append(akt)
    return [p.strip() for p in parts if p.strip()]


def _rozepis_lomitka(s):
    """Rozpíše alternatívy s lomkou podľa konvencie zápisu slova.md: „posunúť na
    ďalšiu / novú úroveň“ strieda jedno slovo, „odomknúť / uvoľniť / naplno využiť
    potenciál“ strieda hlavu pred spoločným posledným slovom."""
    if "/" not in s:
        return [s]
    segs = [x.strip() for x in s.split("/")]
    vys = set()

    def slova(x):
        w = x.split()
        # zvratné sa/si drž s nasledujúcim slovom
        out, i = [], 0
        while i < len(w):
            if w[i].lower() in ZVRATNA and i + 1 < len(w):
                out.append(w[i] + " " + w[i + 1])
                i += 2
            else:
                out.append(w[i])
                i += 1
        return out

    sw = [slova(x) for x in segs]
    if len(sw[0]) == 1:
        # „odomknúť / uvoľniť / naplno využiť potenciál“: hlavy zdieľajú posledné slovo
        posl = sw[-1][-1]
        for x in sw[:-1]:
            vys.add(" ".join(x + [posl]))
        vys.add(" ".join(sw[-1]))
    else:
        # „posunúť na ďalšiu / novú úroveň“: strieda sa jedno slovo
        prefix = sw[0][:-1]
        suffix = sw[-1][1:]
        alt = [sw[0][-1]] + [" ".join(x) for x in sw[1:-1]] + [sw[-1][0]]
        for a in alt:
            vys.add(" ".join(prefix + [a] + suffix))
    for x in segs:  # celé úseky, ktoré sú samy vetou
        if len(x.split()) >= 4:
            vys.add(x)
    return sorted(vys)


def _rozepis_volitelne(s):
    """„V dnešnej (rýchlo sa meniacej / digitálnej) dobe“ → bez zátvorky a s každou alternatívou."""
    m = re.search(r"\(([^)]*)\)", s)
    if not m:
        return [s]
    pred, za = s[: m.start()], s[m.end():]
    out = [re.sub(r"\s+", " ", pred + " " + za).strip()]
    for alt in m.group(1).split("/"):
        out.append(re.sub(r"\s+", " ", pred + " " + alt.strip() + " " + za).strip())
    vys = []
    for o in out:
        vys.extend(_rozepis_volitelne(o))
    return vys


def _cisti(s):
    s = s.replace("*", "").replace("„", "").replace("“", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip(" .;:")


def _polozky_z_bunky(cell, sekce, kategorie, zav, bunka=False):
    """Bunka alebo položka výpočtu → Polozka so zoznamom variantov. V bunke tabuľky platí
    zátvorka na konci pre všetky položky („revolučný, prelomový (pri bežnej veci)“)."""
    vys = []
    kusy = []
    for k in _split_mimo_zavorky(cell):  # „je dôkazom toho, že“: „že“ patrí k predchádzajúcemu
        if kusy and re.match(r"(že|aby|ako|kde|kedy)\b", k):
            kusy[-1] += ", " + k
        else:
            kusy.append(k)
    if bunka and len(kusy) > 1:
        m = re.search(r"\(([^()]*)\)\s*$", kusy[-1])
        if m and not any("(" in k for k in kusy[:-1]):
            kusy = [k if k is kusy[-1] else f"{k} ({m.group(1)})" for k in kusy]
    for kus in kusy:
        pozn = " ".join(re.findall(r"\(([^)]*)\)", kus))
        zaklad = re.sub(r"\([^)]*\)", " ", kus)
        if re.search(r"\bako \*[^*]+\*", zaklad):
            # „prostredie ako *landscape*“ opisuje význam, nie tvar; skript ho neoverí
            vys.append(Polozka(sekce, kategorie, zav, kus.strip(), [], "význam: " +
                               re.search(r"\*([^*]+)\*", zaklad).group(1)))
            continue
        zaklad = _cisti(zaklad)
        if not zaklad:
            continue
        # zátvorka bez „=“ a bez podmienky obsahuje predmety („krajina (trhu, technológií)“)
        predmety = []
        if pozn and "=" not in pozn and not RE_PODMINKA.search(pozn) and "„" not in kus:
            predmety = [p.strip() for p in pozn.split(",") if p.strip()]
        p = Polozka(sekce, kategorie, zav, kus.strip(), [], pozn.strip())
        p.tech = bool(RE_TECH.search(pozn))
        p.privesek = "prívesok" in pozn
        p.podminka = bool(pozn) and not predmety and not p.tech and not p.privesek
        if "=" in pozn:
            p.podminka = True
        klic = zaklad.lower()
        varianty = PREPISY_POLOZEK.get(klic) or _rozepis_lomitka(zaklad)
        if predmety:
            varianty = [v + " " + o for v in varianty for o in predmety]
        p.varianty = varianty
        vys.append(p)
    # „kontrolovať proces, tím, rozpočet“ – prepis platí pre celú bunku
    celek = _cisti(re.sub(r"\([^)]*\)", " ", cell)).lower()
    if celek in PREPISY_POLOZEK:
        p = Polozka(sekce, kategorie, zav, cell.strip(), PREPISY_POLOZEK[celek],
                    " ".join(re.findall(r"\(([^)]*)\)", cell)))
        p.podminka = "=" in p.poznamka
        return [p]
    return vys


def _fraze_z_textu(text, sekce, kategorie, zav):
    """Vytiahne frázy v „…“ s prípadnou poznámkou v zátvorke hneď za nimi."""
    vys = []
    for m in re.finditer(r"„([^“]+)“(\s*\(([^)]*)\))?", text):
        fr = m.group(1).strip()
        if fr.lower().strip(" .…") in KONEKTORY:
            continue  # spájacie výrazy na začiatku viet meria metrika súdržnosti
        pozn = (m.group(3) or "").strip()
        varianty = []
        for v in _rozepis_volitelne(fr):
            varianty.extend(_rozepis_lomitka(v))
        p = Polozka(sekce, kategorie, zav, fr, varianty, pozn)
        p.podminka = bool(pozn) and "rozpätie" not in pozn
        vys.append(p)
    return vys


def _bohemizmy_z_tela(telo):
    """Oddiel Bohemizmy: tabuľka „Česká stopa“ (presné tvary, P1) a tabuľka
    „Bohemizmus“ (rozšírené bohemizmy: jednotlivo info, v zhluku P2)."""
    vys, druh = [], None
    for row in re.findall(r"^\|(.+)\|\s*$", telo, flags=re.M):
        cells = [c.strip() for c in row.split("|")]
        if not cells or set(cells[0]) <= set("-: "):
            continue
        hlava = cells[0].lower()
        if hlava == "česká stopa":
            druh = "stopa"
            continue
        if hlava == "bohemizmus":
            druh = "bohemizmus"
            continue
        po_sk = re.sub(r"\s+", " ", cells[1])[:80] if len(cells) > 1 else ""
        if druh == "stopa":
            tvary = [_cisti(x).lower() for x in cells[0].split(",") if _cisti(x)]
            p = Polozka("bohemizmus", "česká stopa", "P1", cells[0], [],
                        "po slovensky: " + po_sk)
            p.presne = tvary
            vys.append(p)
        elif druh == "bohemizmus":
            pozn = " ".join(re.findall(r"\(([^)]*)\)", cells[0]))
            zaklad = re.sub(r"\([^)]*\)", " ", cells[0])
            tvary = [_cisti(x).lower() for x in zaklad.split(",") if _cisti(x)]
            p = Polozka("bohemizmus", "bohemizmus", "info", cells[0], [],
                        (pozn + "; " if pozn else "") + "po slovensky: " + po_sk)
            p.podminka = bool(pozn)
            p.presne = tvary
            vys.append(p)
    return vys


def nacti_slova(cesta):
    """Robustný parser references/slova.md. Vracia (položky, varovania)."""
    with open(cesta, encoding="utf-8") as f:
        md = f.read()
    polozky, varovani = [], []
    sekce = re.split(r"^## +", md, flags=re.M)
    for s in sekce[1:]:
        nadpis, _, telo = s.partition("\n")
        n = nadpis.lower()
        if "úroveň 1" in n:
            for row in re.findall(r"^\|(.+)\|\s*$", telo, flags=re.M):
                cells = [c.strip() for c in row.split("|")]
                if not cells or set(cells[0]) <= set("-: ") or cells[0].lower() == "namiesto":
                    continue
                polozky += _polozky_z_bunky(cells[0], "uroven1", "úroveň 1", "P1", bunka=True)
        elif "úroveň 2" in n or "úroveň 3" in n:
            u = "uroven2" if "úroveň 2" in n else "uroven3"
            odst = [o for o in telo.strip().split("\n\n") if o.strip()]
            if odst:
                polozky += _polozky_z_bunky(odst[0].replace("\n", " "), u,
                                            "úroveň 2" if u == "uroven2" else "úroveň 3",
                                            "P1" if u == "uroven2" else "P2")
        elif "kalk" in n:
            for row in re.findall(r"^\|(.+)\|\s*$", telo, flags=re.M):
                cells = [c.strip() for c in row.split("|")]
                if not cells or set(cells[0]) <= set("-: ") or cells[0].lower() == "kalk":
                    continue
                for p in _polozky_z_bunky(cells[0], "kalk", "kalk", "P2", bunka=True):
                    if len(cells) > 2 and re.search(r"slabé samo\s?osebe", cells[2], re.I):
                        p.zavaznost = "info"
                    if len(cells) > 2 and cells[2]:
                        p.poznamka = (p.poznamka + "; " if p.poznamka else "") + \
                            "po slovensky: " + re.sub(r"\s+", " ", cells[2])[:80]
                    polozky.append(p)
            for m in re.finditer(r"^\*\*([^*]+)\*\*\s*(.+?)(?=\n\n|\Z)", telo, flags=re.M | re.S):
                stitek, obsah = m.group(1).lower(), m.group(2).replace("\n", " ")
                if "anglicizm" in stitek:
                    it = re.search(r"\*([^*]+)\*", obsah)
                    if it:
                        polozky += _polozky_z_bunky(it.group(1), "anglicizmus", "anglicizmus",
                                                    "info")
                    continue
                if "stupňovanie" in stitek:
                    continue  # rieši regulárny výraz
                vycet = re.split(r"\.\s+(?=[A-ZÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽ])", obsah)[0]
                if "opisy" in stitek:
                    polozky += _polozky_z_bunky(vycet, "opis", "opis pre je/má", "P2")
                elif "menný" in stitek:
                    polozky += _polozky_z_bunky(vycet, "menny", "menný štýl", "P2")
                elif "úradné" in stitek:
                    polozky += _polozky_z_bunky(vycet, "uredni", "úradný výraz", "P2")
                else:
                    varovani.append(f"slova.md: neznámy odsek „{m.group(1)}“ v sekcii {nadpis}")
        elif "ustálené frázy" in n:
            for m in re.finditer(r"^\*\*([^*]+?):?\*\*:?\s*(.+?)(?=\n\n|\Z)", telo,
                                 flags=re.M | re.S):
                stitek = m.group(1).strip().rstrip(":").lower()
                klic = next((k for k in KATEGORIE_FRAZI if stitek.startswith(k)), None)
                kat, zav = KATEGORIE_FRAZI.get(klic, (stitek, "P2"))
                if klic is None:
                    varovani.append(f"slova.md: neznáma kategória fráz „{m.group(1)}“ → P2")
                polozky += _fraze_z_textu(m.group(2), "fraze", kat, zav)
        elif "vágne autorit" in n:
            odst = [o for o in telo.strip().split("\n\n") if o.strip()]
            if odst:
                polozky += _fraze_z_textu(odst[0], "vagni", "vágna autorita", "P0")
        elif "chatbot" in n:
            for o in telo.strip().split("\n\n"):
                if re.search(r"\bnie sú\b", o):
                    continue  # chránené frázy (oslovenie, rozlúčka)
                zav = "info" if "(P1)" in o else "P0"
                polozky += _fraze_z_textu(o, "chatbot", "chatbot", zav)
        elif "bohemizm" in n:
            polozky += _bohemizmy_z_tela(telo)
        elif "typografia" in n:
            continue  # typografiu rieši metrika 1
        else:
            varovani.append(f"slova.md: neznáma sekcia „{nadpis.strip()}“ preskočená")
    return polozky, varovani


# ---------------------------------------------------------------------------
# Párovanie vzorov
# ---------------------------------------------------------------------------
@dataclass
class VzorTok:
    klic: str
    zvratne: str = ""     # vyžadované sa/si
    mezera: int = 2       # povolená medzera pred týmto tokenom


def _klic(t, model):
    """S modelom: lema (so záporom) + stupeň a |tvar pre záložnú zhodu; bez modelu kmeň."""
    if model:
        k = t.lemma.lower()
        if t.feats.get("Polarity") == "Neg" and not k.startswith("ne"):
            k = "ne" + k  # zápor: „nejde“ (ísť) → „neísť“; „neoddeliteľný“ zostáva
        if t.feats.get("Degree") in ("Cmp", "Sup"):
            k += "^" + t.feats["Degree"].lower()
        return k + "|" + t.form.lower()
    return kmen(t.form)


def _shoda(klic_t, klic_v, model):
    if model:
        lt, ft = klic_t.split("|", 1)
        lv, fv = klic_v.split("|", 1)
        if lt == lv or ft == fv:
            return True
        # vidové dvojice a cudzie slová, ktoré model lematizuje rôzne (odomknúť/odomykať)
        if "^" in lt or "^" in lv:
            return False
        return shoda_kmenu(kmen(lt), kmen(lv))
    return shoda_kmenu(klic_t, klic_v)


def priprav_vzory(polozky, udpipe):
    """Prevedie varianty na postupnosti kľúčov (lemy s modelom, kmene bez neho)."""
    vsechny = []
    for p in polozky:
        for v in p.varianty:
            vsechny.append((p, v))
    tokenizace = []
    if udpipe:
        text = "\n".join(_cisti(v) for _, v in vsechny)
        vety = udpipe.zpracuj(text, presegmented=True)
        if len(vety) != len(vsechny):  # poistka: spracuj jednotlivo
            vety = [sum(udpipe.zpracuj(_cisti(v), presegmented=True), []) for _, v in vsechny]
        tokenizace = vety
    else:
        tokenizace = [tokeny_pravidla(_cisti(v), 0, len(_cisti(v))) for _, v in vsechny]
    nepar = [f"{p.raw} → len význam ({p.poznamka})" for p in polozky
             if not p.varianty and not p.presne]
    for (p, v), toks in zip(vsechny, tokenizace):
        vz, zvr, mez = [], "", 2
        for t in toks:
            lo = t.form.lower()
            if not t.je_slovo():
                continue
            if lo in ZASTUPCE:
                mez = 6
                continue
            if lo in ZVRATNA:
                zvr = lo
                continue
            je_prs = (t.upos == "PRON" and t.feats.get("PronType") == "Prs") if udpipe \
                else lo in OSOBNI_ZAJMENA
            if je_prs:
                mez += 1
                continue
            vz.append(VzorTok(_klic(t, bool(udpipe)), "", mez))
            mez = 2
        if not udpipe and len([x for x in vz if not _je_stop(x.klic, False)]) < 2 and \
                any(t.form.lower() in OSOBNI_ZAJMENA for t in toks):
            # jediné obsahové slovo: osobné zámeno je súčasť vzoru („sme tu pre vás“ nie
            # je „sme tu“); KALIBRACIA SNK
            vz, mez = [], 2
            for t in toks:
                lo = t.form.lower()
                if not t.je_slovo() or lo in ZVRATNA:
                    continue
                if lo in ZASTUPCE:
                    mez = 6
                    continue
                vz.append(VzorTok(lo if lo in OSOBNI_ZAJMENA else _klic(t, False), "", mez))
                mez = 2
        if vz and zvr:
            vz[0].zvratne = zvr
        obsah = [x for x in vz if not _je_stop(x.klic, True)]
        if not udpipe:
            obsah = [x for x in vz if not any(shoda_kmenu(x.klic, kmen(s)) for s in STOP)
                     and x.klic not in STOP]
        if not obsah:
            nepar.append(f"{p.raw} → „{v}“")
            continue
        p.vzory.append((v, vz))
    return nepar


_SLOVA_CACHE = {}


def pripravene_slova(cesta, udpipe):
    """Položky slova.md s pripravenými vzormi; výsledok sa pamätá pre súbor a model."""
    kluc = (os.path.abspath(cesta), os.path.getmtime(cesta), id(udpipe))
    if kluc not in _SLOVA_CACHE:
        polozky, var = nacti_slova(cesta)
        nepar = priprav_vzory(polozky, udpipe)
        _SLOVA_CACHE[kluc] = (polozky, var, nepar)
    polozky, var, nepar = _SLOVA_CACHE[kluc]
    return polozky, list(var), list(nepar)


@functools.lru_cache(maxsize=None)
def _stop_kmene():
    return frozenset(kmen(x) for x in STOP)


def _je_stop(klic, model):
    k = klic.split("|")[0]
    if model:
        return k in STOP
    return k in STOP or k in _stop_kmene()


def najdi_vzor(veta, vz, model, prisne=False):
    """Vráti zoznam (i_start, i_end) indexov tokenov vety, kde vzor sedí."""
    toks = [t for t in veta.tokens if t.je_slovo() and t.low not in ZVRATNA]
    klice = [_klic(t, model) for t in toks]
    vysl = []
    obsahove = [v for v in vz if not _je_stop(v.klic, model)]
    volitelne = len(obsahove) >= 2 and not prisne  # spojky smú chýbať, keď vzor má obsah
    for i in range(len(toks)):
        if not _shoda(klice[i], vz[0].klic, model):
            continue
        pos, ok, posl = i, True, i
        for v in vz[1:]:
            nasel = None
            for j in range(pos + 1, min(len(toks), pos + 2 + v.mezera)):
                if _shoda(klice[j], v.klic, model):
                    nasel = j
                    break
            if nasel is None:
                if volitelne and _je_stop(v.klic, model):
                    continue
                ok = False
                break
            pos = posl = nasel
        if not ok:
            continue
        if vz[0].zvratne:
            a, b = toks[i].idx - 3, toks[posl].idx + 3
            if not any(t.low == vz[0].zvratne and a <= t.idx <= b for t in veta.tokens):
                continue
        vysl.append((toks[i], toks[posl]))
    return vysl


# ---------------------------------------------------------------------------
# Analyzátor
# ---------------------------------------------------------------------------
class Analyza:
    def __init__(self, text, profil="blog", udpipe=None, slova_cesta=None, vse=False):
        self.profil_jm = profil
        self.p = PROFILY[profil]
        self.model = udpipe is not None
        self.vse = vse
        self.doc = Dokument(text, udpipe, vse)
        self.text = text
        self.m = self.doc.masked
        self.nalezy = []
        self.metriky = {}
        self.varovani = []
        self.udpipe = udpipe
        self.slova_cesta = slova_cesta
        self.uvozovky = [] if vse else self._uvozovky()
        self.tabulky = [(a, b) for a, b, d in self.doc.pasma if d == "tabulka"]

    # -- pomocné ----------------------------------------------------------
    # Nálezy, ktoré platia aj vnútri citácie „…“ a tabuľky: uniknutý citačný token je chyba
    # vždy, nikdy citácia.
    VZDY_PLATI = {"citacny-token"}

    def pridej(self, metrika, kategorie, zav, a, b, poznamka="", priblizne=False, zdroj=""):
        if zav is None:
            return
        if zav != "info" and kategorie not in self.VZDY_PLATI:
            pasmo = self.info_pasmo(a, b)
            if pasmo:
                zav = "info"
                poznamka += ("; " if poznamka else "") + pasmo
        self.nalezy.append(Nalez(metrika, kategorie, zav, a, b, self.text[a:b].strip(),
                                 poznamka, priblizne or (not self.model and metrika in
                                                          ("zoznamy_slov", "trojice")), zdroj))

    POZN_CITACE = {"uvozovky": "v úvodzovkách – citácia?", "kurziva": "v kurzíve – zmienka?"}

    def _uvozovky(self):
        """Rozsahy citácií „…“ a kurzívy *…* / _…_ ako (start, end, druh). Kurzívou sa
        píšu spomenuté slová („slová ako *kľúčový*“), preto sa s ňou zaobchádza
        ako s citáciou: nález v nej ide do info. Tučné **…** kurzíva nie je."""
        rozsahy = []
        for m in re.finditer(r"„[^“\n]*“|‚[^‘\n]*‘|»[^«\n]*«|\"[^\"\n]*\"", self.m):
            rozsahy.append((m.start(), m.end(), "uvozovky"))
        for m in re.finditer(r"(?<![*\w])\*(?![*\s])[^*\n]*?[^*\s]\*(?![*\w])"
                             r"|(?<![_\w])_(?![_\s])[^_\n]*?[^_\s]_(?![_\w])", self.m):
            rozsahy.append((m.start(), m.end(), "kurziva"))
        return rozsahy

    def pozn_citace(self, a, b):
        """„v úvodzovkách – citácia?“ alebo „v kurzíve – zmienka?“, keď je úsek a–b celý
        vnútri citácie alebo kurzívy, inak None."""
        for s, e, druh in self.uvozovky:
            if s <= a and b <= e:
                return self.POZN_CITACE[druh]
        return None

    def v_uvozovkach(self, a, b):
        return self.pozn_citace(a, b) is not None

    def info_pasmo(self, a, b):
        """Poznámka pre nález celý vnútri citácie „…“, kurzívy alebo tabuľky (taký nález
        ide do info: priama reč v AI texte je legitímny cieľ, ale nemá dávať P0–P2), inak
        None. S --vsetko sa úvodzovky, kurzíva ani tabuľky nehľadajú."""
        if any(s <= a and b <= e for s, e in self.tabulky):
            return "v tabuľke"
        return self.pozn_citace(a, b)

    @staticmethod
    def _cislo_verze(t, pos):
        """Číslo na `pos` je označenie verzie, nie desatinné číslo: stojí hneď za názvom
        („Sonnet 5.5“, „CC BY-NC-SA 4.0“, „GPT-4.5“). Názov je slovo s veľkým písmenom
        vnútri (GPT, BY-NC-SA), alebo s veľkým začiatočným, ktoré nezačína vetu."""
        m = re.search(r"(\S+)[  -]$", t[max(0, pos - 40):pos])
        if not m:
            return False
        slovo = m.group(1).strip("()[]„“\"'")
        if not slovo or not slovo[0].isalpha() or re.match(r"[\d.]+\s*%", t[pos:]):
            return False
        if any(c.isupper() for c in slovo[1:]):
            return True
        if not slovo[0].isupper():
            return False
        pred_slovem = t[max(0, pos - 40):pos][:m.start(1)].rstrip("  („\"")
        return bool(pred_slovem) and pred_slovem[-1] not in ".!?:\n"

    def veta_na(self, pos):
        for v in self.doc.vety:
            if v.start <= pos < v.end + 1:
                return v
        return None

    # -- spustenie ---------------------------------------------------------
    def spust(self):
        self.m_typografie()
        self.m_seznamy()
        self.m_bohemizmy()
        self.m_vestavene()
        self.m_kontrast()
        self.m_rytmus()
        self.m_trojice()
        self.m_privesky()
        self.m_soudrznost()
        self.m_postoj()
        self.m_titulky()
        if self.model:
            self.m_skladba()
        self._dedup()
        self._rozpocet_v_zhluku()
        return self

    def _rozpocet_v_zhluku(self):
        """Prekročený rozpočet pomlčiek je P1 len spolu s iným nálezom P0/P1."""
        ine = any(n.zavaznost in ("P0", "P1") and n.kategorie != "rozpocet-pomlciek"
                  for n in self.nalezy)
        for n in self.nalezy:
            if n.kategorie == "rozpocet-pomlciek" and n.zavaznost == "P2" and ine:
                n.zavaznost = "P1"
                n.poznamka += "; v zhluku s inými nálezmi"
        self.nalezy.sort(key=lambda n: (n.start, PORADI_ZAV[n.zavaznost]))

    def _dedup(self):
        """Prekrývajúce sa nálezy zo zoznamov slov: ponechaj najzávažnejší a najdlhší."""
        vys = []
        serazene = sorted(self.nalezy, key=lambda n: (PORADI_ZAV[n.zavaznost],
                                                      -(n.end - n.start)))
        for n in serazene:
            if n.metrika == "zoznamy_slov" and any(
                    x.metrika == "zoznamy_slov" and x.start < n.end and n.start < x.end
                    for x in vys):
                continue
            vys.append(n)
        self.nalezy = sorted(vys, key=lambda n: (n.start, PORADI_ZAV[n.zavaznost]))

    # -- 1 typografia -----------------------------------------------------
    def m_typografie(self):
        t, p = self.m, self.p
        slov = self.doc.pocet_slov()
        met = {}
        dlouhe = list(re.finditer("—", t))
        met["dlha_pomlcka"] = len(dlouhe)
        for m in dlouhe:
            bez = not (m.start() > 0 and t[m.start() - 1] == " ")
            self.pridej("typografia", "dlha-pomlcka", "P1", m.start(), m.end(),
                        "anglická dlhá pomlčka „—“" + (" bez medzier" if bez else "") +
                        "; po slovensky „–“ s medzerami")
        # pomlčky medzi vetnými členmi (nie rozsahy)
        pomlcky = []
        for m in re.finditer(r"(?<=\S) ([–-]) (?=\S)", t):
            pred = t[max(0, m.start() - 4):m.start()]
            za = t[m.end():m.end() + 2]
            if re.search(r"\d\.?$", pred) and re.match(r"\d", za):
                if m.group(1) == "-":
                    self.pridej("typografia", "rozsah", "P2", m.start() - 1, m.end() + 1,
                                "rozsah so spojovníkom; po slovensky pomlčka „2 – 3“"
                                " (v sadzbe aj „2–3“)")
                continue
            if not self.info_pasmo(m.start(), m.end()):
                pomlcky.append(m)  # pomlčky v citáciách a tabuľkách mimo rozpočtu
            if m.group(1) == "-" and p["spojovnik_nalez"]:
                self.pridej("typografia", "spojovnik-namiesto-pomlcky", "P2", m.start(),
                            m.end(), "v texte na publikovanie pomlčka „–“")
        for m in re.finditer(r"\b(\d{4}) ?- ?(\d{4})\b", t):
            if " - " not in m.group(0) and "-" in m.group(0):
                self.pridej("typografia", "rozsah", "info", m.start(), m.end(),
                            "rozsah rokov sa píše s pomlčkou „–“ (slabé samo osebe)")
        dlouhe = [m for m in dlouhe if not self.info_pasmo(m.start(), m.end())]
        met["pomlcky"] = len(pomlcky) + len(dlouhe)
        if p["pomlcky"] == "socialne":
            limit = prah("pomlcky_socialne_v_texte")
        elif p["pomlcky"] == "volne":
            limit = max(2, math.ceil(slov / 300) * 2)
        else:
            limit = max(1, math.ceil(slov / 300) * prah("pomlcky_na_300_slov"))
        met["pomlcky_limit"] = limit
        if met["pomlcky"] > limit:
            vse = sorted([m.start(1) for m in pomlcky] + [m.start() for m in dlouhe])
            # slova.md: P1 len v zhluku s inými tikmi; samotný prekročený rozpočet je P2
            # (KALIBRACIA SNK: samotný rozpočet prekročí asi 9 % ľudských úsekov).
            # Na P1 ho povýši _rozpocet_v_zhluku(), keď text má iný nález P0/P1.
            self.pridej("typografia", "rozpocet-pomlciek", "P2", vse[limit], vse[limit] + 1,
                        f"{met['pomlcky']} pomlčiek na {slov} slov (limit {limit})")
        # úvodzovky
        rovne = re.findall(r"\"[^\"\n]+\"", t)
        met["rovne_uvodzovky"] = len(rovne)
        for m in re.finditer(r"\"[^\"\n]+\"", t):
            self.pridej("typografia", "rovne-uvodzovky", "info", m.start(), m.end(),
                        "rovné úvodzovky (slabé samo osebe); po slovensky „…“")
        # čísla
        for m in re.finditer(r"(?<![\d.,])(\d{1,3})((?:,\d{3})+)(?![\d,])(\s?(€|\$|EUR|USD|Kč|CZK|"
                             r"eur|korún|dolárov))?", t):
            vic = m.group(2).count(",") > 1
            if m.group(3) or vic:
                self.pridej("typografia", "oddelovac-radov", "P1", m.start(), m.end(),
                            "anglický oddeľovač rádov mení význam; po slovensky „1 500“")
            else:
                self.pridej("typografia", "oddelovac-radov", "info", m.start(), m.end(),
                            "desatinná čiarka s tromi miestami, alebo anglický oddeľovač rádov?")
        cesky_des = re.search(r"(?<![\d,])\d+,\d{1,2}(?!\d)", t)
        anglicke = []
        for m in re.finditer(r"(?<![\d.,])(\d+)\.(\d+)(?![\d.])", t):
            a, b = m.group(1), m.group(2)
            pred = t[max(0, m.start() - 8):m.start()].lower()
            if len(b) == 2 and int(a) <= 24 and int(b) < 60:
                continue  # čas 9.00, 14.30
            if re.search(r"(verzia|verzie|verzii|verziu|v|ver\.|python|ios|android)\s*$", pred):
                continue
            if self._cislo_verze(t, m.start()):
                continue
            if len(b) == 1 or len(b) == 2 or len(b) == 3:
                anglicke.append(m)
                self.pridej("typografia", "desatinna-bodka", "P2", m.start(), m.end(),
                            "desatinná bodka; po slovensky „2,5“")
        if anglicke and cesky_des:
            self.pridej("typografia", "zmiesane-formaty", "P1", anglicke[0].start(),
                        anglicke[0].end(), "v texte sú slovenské aj anglické formáty čísel")
        for m in re.finditer(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", t):
            self.pridej("typografia", "datum", "P1", m.start(), m.end(),
                        "anglický formát dátumu je dvojznačný; po slovensky „4. 5. 2026“")
        for m in re.finditer(r"(?<![\d.])(\d{1,2})\.(\d{1,2})\.(\d{4})\b", t):
            if len(m.group(1)) == 1 or len(m.group(2)) == 1:
                self.pridej("typografia", "datum", "P2", m.start(), m.end(),
                            "dátum bez medzier; po slovensky „4. 5. 2026“")
        for m in re.finditer(r"\b(January|February|March|April|May|June|July|August|September|"
                             r"October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|"
                             r"Nov|Dec)\.? \d{1,2}\b", t):
            self.pridej("typografia", "datum", "P1", m.start(), m.end(), "anglický zápis dátumu")
        for m in re.finditer(r"\b\d{1,2}(:\d{2})?\s?(AM|PM|am|pm|a\.m\.|p\.m\.)", t):
            self.pridej("typografia", "cas", "P1", m.start(), m.end(),
                        "čas AM/PM; po slovensky „14.30 h“ alebo „14:30“")
        for m in re.finditer(r"\b\d{1,2}(st|nd|rd|th)\b", t):
            self.pridej("typografia", "radova-cislovka", "P1", m.start(), m.end(),
                        "anglická radová číslovka; po slovensky „1.“")
        for m in re.finditer(r"(\d+)%(?=(\s+([^\W\d_]+))|[^\w]|$)", t):
            # v slovenčine vždy s medzerou; prídavné meno je „25-percentný“
            self.pridej("typografia", "percenta", "P2", m.start(), m.end(),
                        "percentá sa píšu s medzerou: „25 %“; prídavné meno "
                        "„25-percentný“")
        if not p["tech_vyjimky"]:
            for m in re.finditer(r"\bEUR[  ]?\d[\d  ]*(?:,\d+)?", t):
                self.pridej("typografia", "mena", "P2", m.start(), m.end(),
                            "kód meny pred sumou; v bežnom texte „1 500 €“ alebo „1 500 eur“")
        # výkričníky, emoji, hashtagy
        vykr_poz = [i for i, ch in enumerate(t) if ch == "!" and not self.info_pasmo(i, i + 1)]
        vykr = len(vykr_poz)
        met["vykricniky"] = vykr
        if p["vykricniky"] and slov and vykr >= 2 and vykr * 1000 / slov > prah(
                "vykricniky_na_1000_slov"):
            i = vykr_poz[0]
            self.pridej("typografia", "vykricniky", "P2", i, i + 1,
                        f"{vykr} výkričníkov na {slov} slov")
        emoji = list(RE_EMOJI.finditer(t))
        met["emoji"] = len(emoji)
        if len(emoji) > p["emoji"]:
            m = emoji[p["emoji"]]
            self.pridej("typografia", "emoji", "P2", m.start(), m.end(),
                        f"{len(emoji)} emoji (profil {self.profil_jm} znesie {p['emoji']})")
        hasht = list(re.finditer(r"(?<!\w)#[^\W\d_]\w+", t))
        met["hashtagy"] = len(hasht)
        if len(hasht) >= prah("hashtagy"):
            self.pridej("typografia", "hashtagy", "P1", hasht[0].start(), hasht[-1].end(),
                        f"{len(hasht)} hashtagov")
        for m in re.finditer(r"↓|👇", t):
            self.pridej("typografia", "hacik-sipka", "P1", m.start(), m.end(),
                        "háčik so šípkou")
        self.metriky["typografia"] = met

    # -- 3 zoznamy slov ---------------------------------------------------
    def m_seznamy(self):
        cesta = self.slova_cesta
        if not cesta or not os.path.exists(cesta):
            self.varovani.append(f"slova.md sa nenašiel ({cesta}); zoznamy slov preskočené")
            self.metriky["zoznamy_slov"] = {"nacitane": 0}
            return
        polozky, var, nepar = pripravene_slova(cesta, self.udpipe)
        self.varovani += var
        p = self.p
        nalezy_l2 = {}   # blok -> {raw: (a,b,polozka)}
        nalezy_l3 = {}
        pocty = {}
        prechody = []    # (a, b, pozn, polozka): jeden v texte P2, dva a viac P1
        prvni_ve_bloku = {}
        for v in self.doc.vety:
            prvni_ve_bloku.setdefault(v.blok, v.start)
        self._bohemizmy = [x for x in polozky if x.sekce == "bohemizmus"]
        for pol in polozky:
            if pol.sekce == "bohemizmus":
                continue  # presné tvary, rieši m_bohemizmy
            if pol.tech and p["tech_vyjimky"]:
                continue
            if pol.sekce == "uredni" and not p["uredni"]:
                continue
            if pol.sekce == "menny" and not p["jmenny_styl"]:
                continue
            for v in self.doc.vety:
                for var, vz in pol.vzory:
                    prisne = pol.sekce == "chatbot" or (
                        pol.sekce == "fraze" and pol.kategorie in FRAZY_PRISNE)
                    for t0, t1 in najdi_vzor(v, vz, self.model, prisne):
                        a, b = t0.start, t1.end
                        if pol.privesek:
                            pred = self.m[max(v.start, a - 40):a].lower()
                            if not re.search(r"(,\s*čo|\bčím|\btým|\bpričom)\b[^.]*$", pred):
                                continue
                        pocty[pol.sekce] = pocty.get(pol.sekce, 0) + 1
                        zav = pol.zavaznost
                        if pol.sekce in ("uroven2", "uroven3"):
                            # jedno slovo, ktoré zodpovedá dvom položkám (efektívny,
                            # efektívne), sa počíta raz
                            cil = nalezy_l2 if pol.sekce == "uroven2" else nalezy_l3
                            bl = cil.setdefault(v.blok, {})
                            if not any(x[0] < b and a < x[1] for x in bl.values()):
                                bl.setdefault(pol.raw, (a, b, pol))
                            continue
                        if pol.podminka and zav in ("P1", "P2") and pol.sekce != "chatbot":
                            zav = "P2" if zav == "P1" else "info"
                        if pol.sekce == "kalk" and zav == "P2" and len(var.split()) >= 3 \
                                and not pol.podminka:
                            zav = "P1"
                        pozn = pol.kategorie
                        if pol.poznamka:
                            pozn += f" ({pol.poznamka})"
                        if pol.sekce == "fraze" and pol.kategorie == "uvod" and zav == "P1" \
                                and prvni_ve_bloku.get(v.blok) != v.start:
                            zav, pozn = "P2", pozn + "; uprostred odseku"
                        if self.v_uvozovkach(a, b):
                            zav, pozn = "info", pozn + "; " + self.pozn_citace(a, b)
                        zav = self._filtr_profilu(zav, pol)
                        if pol.sekce == "fraze" and pol.kategorie == "prechod" and zav == "P1":
                            prechody.append((a, b, pozn, pol))
                            continue
                        self.pridej("vstavane" if pol.sekce == "vagni" else "zoznamy_slov",
                                    self._kat_seznamu(pol), zav, a, b, pozn,
                                    zdroj=f"slova.md: {pol.raw}")
        ruzne = {pol.raw for *_, pol in prechody}
        for a, b, pozn, pol in prechody:
            zav = "P1" if len(ruzne) >= prah("prechody_p1") else "P2"
            self.pridej("zoznamy_slov", self._kat_seznamu(pol), zav, a, b,
                        pozn + f"; prechodov v texte: {len(ruzne)}", zdroj=f"slova.md: {pol.raw}")
        slov_v_bloku = {}
        for v in self.doc.vety:
            slov_v_bloku[v.blok] = slov_v_bloku.get(v.blok, 0) + v.pocet_slov()
        for blok, nal in nalezy_l2.items():
            hranice = prah("uroven2_v_dlhom_odseku") if slov_v_bloku.get(blok, 0) > \
                prah("uroven2_dlhy_odsek_slov") else prah("uroven2_v_odseku")
            zav = "P1" if len(nal) >= hranice else "info"
            for raw, (a, b, pol) in nal.items():
                z = self._filtr_profilu(zav, pol)
                if self.v_uvozovkach(a, b):
                    z = "info"
                self.pridej("zoznamy_slov", "uroven-2", z, a, b,
                            f"úroveň 2: {len(nal)} rôznych v odseku (prah {hranice})" +
                            (f"; {pol.poznamka}" if pol.poznamka else ""),
                            zdroj=f"slova.md: {raw}")
        for blok, nal in nalezy_l3.items():
            zav = "P2" if len(nal) >= prah("uroven3_v_odseku") else "info"
            for raw, (a, b, pol) in nal.items():
                z = self._filtr_profilu(zav, pol)
                self.pridej("zoznamy_slov", "uroven-3", z, a, b,
                            f"úroveň 3: {len(nal)} rôznych v odseku (prah "
                            f"{prah('uroven3_v_odseku')})", zdroj=f"slova.md: {raw}")
        self.metriky["zoznamy_slov"] = {"poloziek": len(polozky),
                                        "vzorov": sum(len(x.vzory) for x in polozky),
                                        "neparovatelne": nepar, "vyskyty": pocty}

    # -- bohemizmy (slovenský oddiel slova.md) -------------------------------
    def m_bohemizmy(self):
        """Česká stopa (presný tvar alebo písmeno ě/ř/ů v slove s malým začiatočným
        písmenom) je P1 aj raz. Rozšírené bohemizmy sú jednotlivo info; tri a viac
        rôznych v texte dávajú P2. Položky s podmienkou „(= …)“ sú vždy len info."""
        polozky = getattr(self, "_bohemizmy", [])
        stopy, rozsirene = [], []   # (a, b, polozka)

        def sedi(tok, slovo):
            lo = tok.low
            if lo == slovo or (slovo == "k" and lo == "ku"):
                return True
            if lo in BOHEMIZMY_TVARY.get(slovo, ()):
                return True
            k = kmen(slovo)
            if slovo in BOHEMIZMY_PRESNE or len(k) < 5:
                return False  # krátky kmeň by chytil iné slovo (pred, beh, vada)
            return kmen(lo) == k

        for v in self.doc.vety:
            if v.druh == "tabulka":
                continue
            toks = v.slova()
            for pol in polozky:
                stopa = pol.kategorie == "česká stopa"
                for tvar in pol.presne:
                    ws = tvar.split()
                    for i in range(len(toks) - len(ws) + 1):
                        okno = toks[i:i + len(ws)]
                        if stopa:
                            ok = all(t.low == w for t, w in zip(okno, ws))
                        else:
                            ok = all(sedi(t, w) for t, w in zip(okno, ws))
                        if not ok:
                            continue
                        if tvar == "pokiaľ" and i + 1 < len(toks) and \
                                toks[i + 1].low in ("ide", "išlo", "pôjde"):
                            continue  # „pokiaľ ide o“ je v poriadku
                        (stopy if stopa else rozsirene).append((okno[0].start, okno[-1].end, pol))
        for m in RE_CESKE_PISMENO.finditer(self.m):
            w = m.group(0)
            if w[0].isupper() or any(a <= m.start() < b for a, b, _ in stopy):
                continue  # mená a názvy (Dvořák, Jiří) sa nehlásia
            if len(w) == 1:
                continue  # samotné písmeno je zmienka o písmene („písmená ě, ř, ů“)
            pred = re.search(r"([^\W\d_]+)[ \u00a0]$", self.m[max(0, m.start() - 40):m.start()])
            if (pred and pred.group(1)[0].isupper()) or RE_ADJ_Z_MENA.search(w):
                continue  # český názov („Mladé tvorbě“) alebo prídavné meno z mena
                          # („břevnovský“); KALIBRACIA SNK: Wikipédia
            stopy.append((m.start(), m.end(), None))
        stopy.sort(key=lambda x: x[0])
        strop = prah("ceska_stopa_max")
        if len(stopy) > strop:
            self.varovani.append(f"{len(stopy)} českých tvarov: text je zrejme český, nie "
                                 f"slovenský; hlásené sú len prvé tri")
            stopy = stopy[:3]
        for a, b, pol in stopy:
            if pol is None:
                self.pridej("bohemizmy", "ceska-stopa", "P1", a, b,
                            "česká stopa (písmeno): ě, ř a ů slovenčina nemá")
            else:
                self.pridej("bohemizmy", "ceska-stopa", "P1", a, b,
                            f"česká stopa; {pol.poznamka}", zdroj=f"slova.md: {pol.raw}")
        ruzne = {pol.raw for _, _, pol in rozsirene if not pol.podminka}
        zhluk = len(ruzne) >= prah("bohemizmy_zhluk")
        for a, b, pol in rozsirene:
            zav = "P2" if zhluk and not pol.podminka else "info"
            pozn = (f"bohemizmus; rôznych v texte: {len(ruzne)} (prah "
                    f"{prah('bohemizmy_zhluk')}); {pol.poznamka}") if zav == "P2" else \
                f"bohemizmus (slabé samo osebe, patrí do tabuľky Iné chyby); {pol.poznamka}"
            self.pridej("bohemizmy", "bohemizmus", zav, a, b, pozn,
                        zdroj=f"slova.md: {pol.raw}")
        self.metriky["bohemizmy"] = {"ceska_stopa": len(stopy), "rozsirene": len(rozsirene),
                                     "rozsirene_rozne": len(ruzne)}

    def _kat_seznamu(self, pol):
        if pol.sekce == "uroven1":
            return "uroven-1"
        if pol.sekce == "fraze":
            return "fraza-" + pol.kategorie
        if pol.sekce == "vagni":
            return "vagna-autorita"
        if pol.sekce == "uredni":
            return "uradny"
        return pol.sekce

    def _filtr_profilu(self, zav, pol):
        p = self.p
        if p["seznamy"] == "p0p1":
            if pol.sekce in ("uroven2", "uroven3") or (pol.sekce == "kalk" and zav != "P1"):
                return "info"
        return zav

    # -- vstavané P0 --------------------------------------------------------
    def m_vestavene(self):
        t = self.m
        # uniknuté citačné tokeny hľadá v pôvodnom texte: sú chybou aj v kóde a v URL
        for m in re.finditer(r"oaicite|contentReference|turn\d+search\d+|utm_source=chatgpt\.com"
                             r"|:contentReference\[", self.text):
            self.pridej("vstavane", "citacny-token", "P0", m.start(), m.end(),
                        "uniknutý citačný token")
        for m in re.finditer(r"\[(?!OVERIŤ)(Meno|Názov|Firma|Dátum|Doplniť|Vaše meno|meno|"
                             r"názov|firma|dátum|doplniť|Your Name|Name)[^\]]*\]", t):
            self.pridej("vstavane", "zastupny-text", "P0", m.start(), m.end(),
                        "nevyplnený zástupný text")
        for m in re.finditer(r"(?i)\b(ignoruj|ignorujte|zabudni|zabudnite|nedbaj|nedbajte)\b[^.\n]{0,40}?"
                             r"\b(pravidl|pokyn|inštrukc|vyššie|predchádzajúc)\w*|\bignore (all )?"
                             r"(previous|prior|above)\b", t):
            self.pridej("vstavane", "vlozeny-pokyn", "P0", m.start(), m.end(),
                        "pokyn vložený do kontrolovaného textu – označiť, neplniť")
        for m in re.finditer(r"(?i)\b(štúdie|výskumy|prieskumy|odborníci|experti|vedci)\s+"
                             r"(ukazujú|ukazuje|dokazujú|potvrdzujú|tvrdia|sa zhodujú|"
                             r"naznačujú|zistili|dokázali|preukázali)\b|\b(podľa)\s+(odborníkov|"
                             r"expertov|vedcov|štúdií|výskumov)\b|\bje\s+(vedecky\s+)?"
                             r"(preukázané|dokázané)\b", t):
            if any(n.kategorie == "vagna-autorita" and n.start < m.end() and m.start() < n.end
                   for n in self.nalezy):
                continue
            citace = self.pozn_citace(m.start(), m.end())
            self.pridej("vstavane", "vagna-autorita", "info" if citace else "P0", m.start(),
                        m.end(), "vágna autorita bez zdroja (neplatí, keď hneď nasleduje "
                                 "pomenovaný zdroj)" + (f"; {citace}" if citace else ""))
        for m in re.finditer(r"\[OVERIŤ[^\]]*\]", t):
            self.pridej("vstavane", "znacka-overit", "info", m.start(), m.end(),
                        "značka skillu pre chýbajúci fakt")
        if self.p["odhaleni"]:
            vety = self.doc.prozni_vety()
            for i, v in enumerate(vety):
                n = v.pocet_slov()
                txt = v.text.strip()
                puvodni = self.text[v.start:v.end]
                if "`" in puvodni or "**" in puvodni:
                    continue  # kód alebo formátovaný štítok, nie inscenovaná pauza
                dalsi = vety[i + 1] if i + 1 < len(vety) else None
                # bez modelu: najviac tri slová a žiadne nevyzerá ako sloveso
                # (KALIBRACIA SNK: bez toho 9 % ľudských úsekov, hlavne dialógy)
                bez_slovesa = not any(t.upos in ("VERB", "AUX") for t in v.tokens) \
                    if self.model else n <= 3 and not any(
                        RE_ASI_SLOVESO.search(t.low) for t in v.slova())
                if txt.endswith("?") and n <= 4 and bez_slovesa and dalsi and \
                        not dalsi.text.rstrip().endswith("?") and \
                        dalsi.blok == v.blok and dalsi.pocet_slov() <= 8 and \
                        not re.search(r"[\"„“”»«]", txt + dalsi.text):
                    self.pridej("vstavane", "otazka-s-odpovedou", "P1", v.start, v.end,
                                "otázka s okamžitou odpoveďou inscenuje pauzu")
                m = re.match(r"^([^\W\d_]+(?:\s+[^\W\d_]+){0,2}):\s+(.+)$", txt)
                if m and n <= 8 and not re.search(r"\d", m.group(2)) and \
                        not re.match(r"[„\"“»‚']", m.group(2)):  # dvojbodka pred citáciou
                    self.pridej("vstavane", "dvojbodkove-odhalenie", "P1", v.start, v.end,
                                "dvojbodkové odhalenie; dvojbodka pred výpočtom alebo citáciou "
                                "je v poriadku")

    # -- 2 rytmus ---------------------------------------------------------
    def m_rytmus(self):
        vety = self.doc.prozni_vety()
        delky = [v.pocet_slov() for v in vety]
        met = {"viet": len(delky)}
        if delky:
            met["priemer"] = round(statistics.mean(delky), 1)
            met["median"] = statistics.median(delky)
            met["min"], met["max"] = min(delky), max(delky)
        if len(delky) >= 2:
            sd = statistics.pstdev(delky)
            met["smerodajna_odchylka"] = round(sd, 1)
            met["variacny_koeficient"] = round(sd / met["priemer"], 2) if met["priemer"] else 0
        met["dlzky"] = delky
        # vety oddelené blokom mimo merania (kód, citácia, tabuľka) nie sú susedné
        predel = [False] + [self.doc.preruseno(vety[k - 1].end, vety[k].start)
                            for k in range(1, len(vety))]
        # behy podobnej dĺžky
        behy = []
        if len(delky) >= 3:
            tol = max(prah("rytmus_podobna_dlzka_slov"),
                      round(prah("rytmus_podobna_dlzka_podiel") * statistics.mean(delky)))
            i = 0
            while i < len(delky):
                j = i + 1
                while j < len(delky) and max(delky[i:j + 1]) - min(delky[i:j + 1]) <= tol \
                        and delky[j] > 3 and not predel[j]:
                    j += 1
                if j - i >= 3 and delky[i] > 3:
                    behy.append((i, j))
                    i = j
                else:
                    i += 1
        met["behy_podobnej_dlzky"] = [[a, b - a] for a, b in behy]
        # reťaze krátkych viet
        kr = prah("kratka_veta_slov")
        retezy = []
        i = 0
        while i < len(delky):
            j = i
            while j < len(delky) and delky[j] <= kr and (j == i or not predel[j]):
                j += 1
            if j - i >= prah("retaz_kratkych_viet"):
                retezy.append((i, j))
            i = max(j, i + 1)
        met["retaze_kratkych_viet"] = [[a, b - a] for a, b in retezy]
        # heslovitá kadencia
        hesla = []
        for i, v in enumerate(vety):
            txt = v.text.strip()
            n = delky[i]
            cis = re.match(rf"(?i)^{CISLOVKY_SLOVY}\s+[^\W\d_]+,\s+{CISLOVKY_SLOVY}\s+[^\W\d_]+[.!]?$",
                           txt)
            je = False
            if cis:
                je = "par"
            elif n <= prah("heslo_slov") and not txt.endswith("?") and \
                    not re.search(r"[\"„“”»«]", txt) and \
                    not any(a <= v.start and v.end <= b for a, b in self._kontrast_rozsahy):
                if self.model:
                    je = not any(t.upos in ("VERB", "AUX") for t in v.tokens)
                else:
                    je = True
            hesla.append(je)
        mista, i = 0, 0
        while i < len(hesla):
            if hesla[i] == "par":
                mista += 1
                i += 1
                continue
            if hesla[i]:
                j = i
                while j < len(hesla) and hesla[j] is True:
                    j += 1
                mista += math.ceil((j - i) / 2) if j - i >= 2 else 0
                i = j
            else:
                i += 1
        met["heslovite_miesta"] = mista
        self.metriky["rytmus"] = met
        if mista >= prah("heslovita_kadencia_miest") and self.p["odhaleni"]:
            prvni = next(k for k, h in enumerate(hesla) if h)
            self.pridej("rytmus", "heslovita-kadencia", "P1", vety[prvni].start, vety[-1].end,
                        f"{mista} heslovitých miest v texte (prah "
                        f"{prah('heslovita_kadencia_miest')})")
        if not self.p["rytmus"]:
            return
        for a, b in behy:
            zav = "P2" if b - a >= prah("rytmus_beh_p2") else "info"
            self.pridej("rytmus", "podobna-dlzka", zav, vety[a].start, vety[b - 1].end,
                        f"{b - a} viet za sebou s dĺžkou {delky[a:b]} slov")
        if len(delky) >= prah("rytmus_cv_min_viet") and \
                met.get("variacny_koeficient", 1) < prah("rytmus_cv_min"):
            self.pridej("rytmus", "jednotvarny-rytmus", "P2", vety[0].start, vety[-1].end,
                        f"variačný koeficient dĺžky viet {met['variacny_koeficient']} "
                        f"(prah {prah('rytmus_cv_min')})")
        if self.p["kratke_vety"]:
            for a, b in retezy:
                self.pridej("rytmus", "retaz-kratkych-viet", "P2", vety[a].start,
                            vety[b - 1].end, f"{b - a} viet za sebou do {kr} slov")

    # -- 4 kontrastné obraty ---------------------------------------------
    def m_kontrast(self):
        vety = [v for v in self.doc.vety if v.druh in ("veta", "titulek")]
        texty = [v.text.lower() for v in vety]
        nalezy = []
        neg_a = re.compile(r"\b(?:nejde|nešlo|neišlo|nepôjde|nejedná sa|nejednalo sa|nešlo by)"
                           r"(?:\s+(?:tu|už|len|iba|predsa|vôbec|natoľko))?\s+o\b")
        poz_a = re.compile(r"^(?:ale\s+|a\s+)?(?:ide|išlo|šlo|pôjde|jedná sa|jednalo sa)"
                           r"(?:\s+(?:tu|hlavne|predovšetkým|skôr|o to))?\s+o\b")
        neg_b = re.compile(r"\b(?:nie je|nebolo|nebude)\s+to\b")
        poz_b = re.compile(r"^(?:ale\s+)?(?:je|bolo|bude)\s+to\b|^to\s+je\b")
        i = 0
        while i < len(vety):
            t = texty[i]
            m = neg_a.search(t)
            if m:
                if re.search(r",\s*(?:ale|lež|no)\s+(?:(?:ide|išlo|šlo)\s+)?o\b", t[m.end():]):
                    nalezy.append((vety[i].start, vety[i].end, "nejde o X, ale o Y", "A"))
                    i += 1
                    continue
                negs, j = 1, i + 1
                while j < len(vety) and j <= i + 3 and neg_a.search(texty[j]) and \
                        not poz_a.search(texty[j]):
                    negs += 1
                    j += 1
                if j < len(vety) and poz_a.search(texty[j]):
                    pozn = "nejde o X. Ide o Y." + (" s nahromadenými zápormi" if negs > 1
                                                    else "")
                    nalezy.append((vety[i].start, vety[j].end, pozn, "A"))
                    i = j + 1
                    continue
            m = neg_b.search(t)
            if m:
                if re.search(r",\s*(?:ale\s+|lež\s+)?(?:je|bolo|bude)\s+to\b", t[m.end():]):
                    nalezy.append((vety[i].start, vety[i].end, "nie je to X, je to Y", "B"))
                    i += 1
                    continue
                if i + 1 < len(vety) and poz_b.search(texty[i + 1]):
                    nalezy.append((vety[i].start, vety[i + 1].end, "nie je to X. Je to Y.", "B"))
                    i += 2
                    continue
            m = re.search(r"\bnielen\b.{1,120}?\b(?:ale|lež)\b(?:\s+(?:aj|i|tiež|"
                          r"zároveň|hlavne))?", t)
            if m:
                nalezy.append((vety[i].start + m.start(), vety[i].start + m.end(),
                               "nielen X, ale aj Y", "C"))
            if (vety[i].druh == "titulek" or vety[i].pocet_slov() <= 5) and \
                    re.match(r"^[^\W\d_]+(?:\s+[^\W\d_]+)?\s+namiesto\s+[^\W\d_]+(?:\s+[^\W\d_]+)?"
                             r"[.!]?$", t.strip()):
                nalezy.append((vety[i].start, vety[i].end, "skrátené „A namiesto B“", "D"))
            i += 1
        celkem = len(nalezy)
        self._kontrast_rozsahy = [(a, b) for a, b, _, _ in nalezy]
        self.metriky["kontrast"] = {"pocet": celkem}
        for a, b, pozn, typ in nalezy:
            if typ in ("A", "B", "D"):
                zav = "P1"
            else:
                zav = "P1" if celkem > prah("kontrast_na_text") else "P2"
            if celkem > prah("kontrast_na_text"):
                pozn += f"; kontrastných obratov v texte: {celkem} (limit "\
                        f"{prah('kontrast_na_text')})"
            elif typ == "C":
                pozn += "; posúď, či ide o rečnícku figúru"
            self.pridej("kontrast", "kontrastny-obrat", zav, a, b, pozn)

    # -- 5 trojice --------------------------------------------------------
    def m_trojice(self):
        slovnik = self._slovnik_klicu()
        pocet, prid = 0, []
        vys = []
        for v in self.doc.vety:
            for m in re.finditer(r"(?<!, )(?<!,)\b([^\W\d_]+), ([^\W\d_]+) (a|i|aj|či|alebo|"
                                 r"ani) ([^\W\d_]+)\b(?!,? [^\W\d_]+,)", v.text):
                a, b = v.start + m.start(), v.start + m.end()
                pred = self.m[max(0, a - 3):a]
                if re.search(r",\s?$", pred):
                    continue  # dlhší výpočet
                clenove = [m.group(1), m.group(2), m.group(4)]
                if any(c.lower() in NEJSOU_CLENY for c in clenove):
                    continue
                upos = None
                if self.model:
                    toks = []
                    for c, g in ((clenove[0], 1), (clenove[1], 2), (clenove[2], 4)):
                        s = v.start + m.start(g)
                        tk = next((t for t in v.tokens if t.start == s), None)
                        toks.append(tk)
                    if None in toks:
                        continue
                    uposy = {t.upos for t in toks}
                    if len(uposy) != 1:
                        continue
                    upos = uposy.pop()
                    if upos in ("PROPN", "NUM", "PRON", "DET"):
                        continue
                    klice = [_klic(t, True) for t in toks]
                else:
                    klice = [kmen(c) for c in clenove]
                ze_slovniku = [c for c, k in zip(clenove, klice) if self._ve_slovniku(k, slovnik)]
                pocet += 1
                vys.append((a, b, upos, ze_slovniku))
                if upos in ("ADJ", "ADV"):
                    prid.append(a)
        for a, b, upos, zs in vys:
            if zs:
                zav = "P1"
                pozn = "ozdobná trojica: " + ", ".join(zs) + " zo zoznamu slov"
            elif upos in ("ADJ", "ADV"):
                zav = "P1" if len(prid) > prah("trojice_prid_mien_na_text") else "P2"
                pozn = f"trojica prídavných mien/prísloviek ({len(prid)} v texte, limit " \
                       f"{prah('trojice_prid_mien_na_text')})"
            elif pocet >= 3:
                zav = "P2"
                pozn = f"{pocet} trojíc v texte"
            else:
                zav = "info"
                pozn = "trojica; zostáva, keď má obsah tri časti"
            if upos:
                pozn += f" [{upos}]"
            self.pridej("trojice", "trojice", zav, a, b, pozn)
        self.metriky["trojice"] = {"pocet": pocet, "pridavne_mena": len(prid)}

    def _slovnik_klicu(self):
        if not hasattr(self, "_slovnik"):
            self._slovnik = []
            if self.slova_cesta and os.path.exists(self.slova_cesta):
                polozky, _, _ = pripravene_slova(self.slova_cesta, self.udpipe)
                polozky = [p for p in polozky if p.sekce in ("uroven1", "uroven2")]
                for p in polozky:
                    if p.tech and self.p["tech_vyjimky"]:
                        continue
                    for _, vz in p.vzory:
                        if len(vz) == 1:
                            self._slovnik.append(vz[0].klic)
        return self._slovnik

    def _ve_slovniku(self, k, slovnik):
        return any(_shoda(k, s, self.model) for s in slovnik)

    # -- 6 prívesky -------------------------------------------------------
    def m_privesky(self):
        vety = len(self.doc.prozni_vety()) or 1
        # „čo“ je v slovenčine mnohoznačné (vzťažné aj opytovacie): počíta sa len
        # „, čo“ + sloveso dôsledku; „, čím“ bez stupňovania („čím skôr, tým lepšie“)
        pr = list(re.finditer(RE_PRIVESOK, self.m))
        na100 = len(pr) * 100 / vety
        self.metriky["privesky"] = {"pocet": len(pr), "na_100_viet": round(na100, 1)}
        for m in pr:
            za = self.m[m.end():m.end() + 40].lower()
            obecne = re.match(r"\s+(?:\w+\s+){0,2}?(prispiev|zabezpeč|umožň|posil|demonštr|"
                              r"dokazuj|svedč|podčiark|zdôrazň|odráž|prináš|vytvár)\w*", za)
            if obecne:
                self.pridej("privesky", "privesok", "P2", m.start(), m.end() + len(obecne.group(0)),
                            "prívesok so všeobecným slovesom; škrtni, alebo z neho urob vetu "
                            "s doloženým faktom", priblizne=True)
        if len(pr) >= 2 and na100 > prah("privesky_na_100_viet"):
            self.pridej("privesky", "privesky-pocetnost", "P2", pr[0].start(), pr[0].end(),
                        f"{len(pr)} príveskov s „, čo“/„čím“/„a tým“, {na100:.1f} na 100 viet "
                        f"(prah {prah('privesky_na_100_viet')})", priblizne=True)

    # -- 7 súdržnosť ------------------------------------------------------
    def m_soudrznost(self):
        vety = self.doc.prozni_vety()
        zac = []
        for v in vety:
            t = v.text.strip().lower()
            t = re.sub(r"^(a|ale)\s+", "", t)
            k = next((x for x in KONEKTORY if re.match(rf"{x}\b", t)), None)
            zac.append(k)
        pocet = sum(1 for k in zac if k and k not in KONEKTORY_JEN_RETEZ)
        na100 = pocet * 100 / (len(vety) or 1)
        slov = self.doc.pocet_slov() or 1
        if self.model:
            ktery = sum(1 for t in self.doc.slova() if t.lemma == "ktorý")
        else:
            ktery = len(re.findall(r"(?i)\b(ktor[ýáéíúoey]\w*)\b", self.m))
        coz = len(re.findall(RE_PRIVESOK_CO, self.m))
        self.metriky["sudrznost"] = {
            "konektory_na_zaciatku": pocet, "na_100_viet": round(na100, 1),
            "vyskyty": {k: zac.count(k) for k in set(zac) if k},
            "ktory_na_1000_slov": round(ktery * 1000 / slov, 1),
            "co_na_100_viet": round(coz * 100 / (len(vety) or 1), 2),
            "reference": {k: REFERENCE[k] for k in ("ktory_na_1000_slov", "co_na_100_viet")},
            "poznamka": "ktorý a „, čo“ len informatívne (referencia je česká: který, což); "
                        "navyše a ďalej sa do početnosti nepočítajú",
        }
        # ukazovacie „tento“ na začiatku vety len ako hodnota; nález dáva metrika skladby
        uk = [v for v in vety if v.slova() and v.slova()[0].low in TVARY_TENTO]
        self.metriky["sudrznost"]["tento_na_zaciatku_podiel_viet"] = round(
            len(uk) / (len(vety) or 1), 3)

        # v neposlednom rade kdekoľvek
        for m in re.finditer(r"(?i)\bv neposlednom rade\b", self.m):
            self.pridej("sudrznost", "prechod", "P1", m.start(), m.end(),
                        "šablónovitý prechod")
        # reťaz troch viet s konektorom
        i = 0
        while i < len(zac):
            j = i
            while j < len(zac) and zac[j]:
                j += 1
            if j - i >= prah("konektory_retaz"):
                self.pridej("sudrznost", "konektory-retaz", "P1", vety[i].start,
                            vety[j - 1].end, f"{j - i} vety za sebou sa začínajú spájacím "
                                             f"výrazom")
            i = max(j, i + 1)
        nic = [i for i, k in enumerate(zac) if k == "avšak"]
        if len(nic) >= prah("avsak_ritual"):
            v = vety[nic[1]]
            self.pridej("sudrznost", "avsak", "P2", v.start, v.start + 5,
                        f"„Avšak“ na začiatku {len(nic)} viet")
        if pocet >= 3 and na100 > prah("konektory_na_100_viet"):
            v = vety[next(i for i, k in enumerate(zac) if k)]
            self.pridej("sudrznost", "konektory-pocetnost", "P2", v.start, v.end,
                        f"{pocet} viet sa začína spájacím výrazom, {na100:.1f} na 100 viet "
                        f"(prah {prah('konektory_na_100_viet')})")

    # -- 8 postoj a oslovenie (len informatívne) ---------------------------
    def m_postoj(self):
        slova = self.doc.slova()
        n = len(slova) or 1
        if self.model:
            os1 = sum(1 for t in slova if t.feats.get("Person") == "1")
            os2 = sum(1 for t in slova if t.feats.get("Person") == "2")
        else:
            os1 = sum(1 for t in slova if t.low in ZAJMENA_1OS)
            os2 = sum(1 for t in slova if t.low in ZAJMENA_2OS)
        cast = {}
        for c in CASTICE:
            k = sum(1 for t in slova if t.low == c)
            if k:
                cast[c] = k
        modalni = sum(1 for t in slova if t.low in MODALNI)
        # „možno“ pred neurčitkom je modálne („možno konštatovať“), nie oslabujúce
        oslab = sum(1 for i, t in enumerate(slova) if t.low in OSLABUJICI and not (
            t.low == "možno" and i + 1 < len(slova) and slova[i + 1].low.endswith("ť")))
        zaj2 = sum(1 for t in slova if t.low in ZAJMENA_2OS)
        vety = self.doc.prozni_vety()
        otazky = sum(1 for v in vety if v.text.rstrip().endswith("?"))
        self.metriky["postoj"] = {
            "osoba1": os1, "osoba2": os2, "osoba1_na_100_slov": round(os1 * 100 / n, 2),
            "osoba2_na_100_slov": round(os2 * 100 / n, 2), "castice": cast,
            "castice_na_100_slov": round(sum(cast.values()) * 100 / n, 2),
            "modalne_na_1000_slov": round(modalni * 1000 / n, 1),
            "oslabujuce_na_1000_slov": round(oslab * 1000 / n, 1),
            "osoba2_zamena_na_1000_slov": round(zaj2 * 1000 / n, 1),
            "otazniky_na_100_viet": round(otazky * 100 / (len(vety) or 1), 1),
            "reference": {k: REFERENCE[k] for k in (
                "modalne_na_1000_slov", "oslabujuce_na_1000_slov",
                "osoba2_zamena_na_1000_slov", "otazniky_na_100_viet")},
            "poznamka": "len informatívne; referencia je česká (Koditex), na slovenčine "
                        "nemeraná: AI v češtine má zhruba polovicu ľudskej hodnoty; "
                        "prepis ju nemá znižovať ani umelo zvyšovať",
        }
        # konkrétnosť (D6): čísla a vlastné mená
        cisla = sum(1 for t in slova if re.search(r"\d", t.form))
        if self.model:
            jmena = sum(1 for t in slova if t.upos == "PROPN")
        else:
            jmena = sum(1 for v in self.doc.vety for t in v.slova()[1:]
                        if t.form[:1].isupper() and not t.form.isupper())
        self.metriky["konkretnost"] = {
            "cisla_na_1000_slov": round(cisla * 1000 / n, 1),
            "vlastne_mena_na_1000_slov": round(jmena * 1000 / n, 1),
            "reference": {k: REFERENCE[k] for k in ("cisla_na_1000_slov",
                                                     "vlastne_mena_na_1000_slov")},
            "priblizne": not self.model,
            "poznamka": "len informatívne (referencia je česká); prepis nesmie čísla ani mená ubrať",
        }

    # -- titulky ------------------------------------------------------------
    def m_titulky(self):
        for v in self.doc.vety:
            if v.druh != "titulek":
                continue
            txt = v.text.strip().rstrip(".")
            slova = [m for m in RE_SLOVO.finditer(txt)]
            if len(slova) >= 3 and not txt.isupper():
                dalsi = slova[1:]
                if self.model:
                    propn = {t.start - v.start for t in v.tokens if t.upos == "PROPN"}
                else:
                    propn = set()
                velka = [s for s in dalsi if s.group(0)[0].isupper() and s.start() not in propn]
                mala_obsah = [s for s in dalsi if s.group(0)[0].islower() and len(s.group(0)) > 2]
                if len(velka) >= 2 and len(velka) >= len(dalsi) * 2 / 3 and not mala_obsah:
                    self.pridej("typografia", "title-case", "P1", v.start, v.end,
                                "anglický title case; po slovensky veľké len prvé písmeno "
                                "a vlastné mená")
            lo = txt.lower()
            if re.fullmatch(r"(úvod|prehľad|záver|na záver|zhrnutie|kľúčové poznatky.*|"
                            r"čo si odniesť|ďalšie kroky)", lo):
                self.pridej("titulky", "sablonovity-titulok", "P2", v.start, v.end,
                            "šablónovitý titulok; pomenuj obsah")
            elif re.match(r"(čo|ako|prečo|kto|kde|kedy|takto|toto|pohľad na|"
                          r"predstavenie|poďme|pozrime)\b", lo):
                # Mimo prezentácie je vetný titulok eseje legitímny, keď kladie
                # skutočnú otázku („Kde sú ich stroje?“) alebo sľubuje
                # odpoveď („Prečo deti prestali čítať návody“); vzorce.md, Nadpisy.
                otazka = self.p["titulky_upoutavka"] != "P1" and (
                    v.text.strip().endswith("?") or lo.startswith("prečo "))
                if otazka:
                    self.pridej("titulky", "uputavkovy-titulok", "info", v.start, v.end,
                                "vetný titulok s otázkou; v eseji a článku legitímny, "
                                "keď na ňu text odpovie")
                else:
                    self.pridej("titulky", "uputavkovy-titulok",
                                self.p["titulky_upoutavka"], v.start, v.end,
                                "upútavkový alebo hovorový titulok; menné spojenie "
                                "pomenuje obsah")

    # -- 9 skladba (len s modelom) -----------------------------------------
    def m_skladba(self):
        vety = self.doc.prozni_vety()
        slova = sum(v.pocet_slov() for v in vety) or 1
        vnoun, opisne, zvratne = [], [], []
        jmenne_vety = 0
        for v in vety:
            vn = [t for t in v.tokens if self._je_vnoun(t)]
            op = [t for t in v.tokens if t.deprel == "aux:pass"]
            zv = [t for t in v.tokens if t.deprel == "expl:pass"]
            dojit = any(t.lemma in ("dôjsť", "dochádzať") for t in v.tokens) and vn
            vnoun += vn
            opisne += op
            zvratne += zv
            if len(vn) >= 2 or op or dojit:
                jmenne_vety += 1
        n = len(vety) or 1
        na1000 = len(vnoun) * 1000 / slova
        podil = jmenne_vety / n
        met = {"slovesne_substantiva": len(vnoun),
               "slovesne_substantiva_na_1000_slov": round(na1000, 1),
               "opisne_pasivum": len(opisne), "zvratne_pasivum": len(zvratne),
               "menne_vety": jmenne_vety, "menne_vety_podiel": round(podil, 2),
               "poznamka_vnoun": "ak model neznačí VerbForm=Vnoun, odhad: neutrum "
                                 "s lemou na -nie/-tie"}
        if self.p["jmenny_styl"] or self.p["pasivum"]:
            if len(vety) >= 2 and podil > prah("menne_vety_podiel_p1") and \
                    self.p["jmenny_styl"] and self.p["pasivum"]:
                self.pridej("skladba", "menny-styl", "P1", vety[0].start, vety[-1].end,
                            f"menný štýl alebo opisné pasívum v {jmenne_vety} z {len(vety)} viet")
            elif self.p["jmenny_styl"] and len(vnoun) >= 3 and \
                    na1000 > prah("slovesna_subst_na_1000_slov"):
                self.pridej("skladba", "menny-styl", "P2", vnoun[0].start, vnoun[-1].end,
                            f"{len(vnoun)} slovesných podstatných mien, {na1000:.0f} na 1 000 slov "
                            f"(prah {prah('slovesna_subst_na_1000_slov')})")
        if self.p["pasivum"]:
            podil_op = sum(1 for v in vety if any(t.deprel == "aux:pass" for t in v.tokens)) / n
            met["opisne_pasivum_podiel_viet"] = round(podil_op, 2)
            if len(opisne) >= prah("opisne_pasivum_p2") and \
                    podil_op > prah("opisne_pasivum_podiel_p2"):
                for t in opisne:
                    self.pridej("skladba", "opisne-pasivum", "P2", t.start, t.end + 12,
                                "opisné pasívum: pomenuj aktéra, keď ho zdroj pozná")
            else:
                for t in opisne:
                    self.pridej("skladba", "opisne-pasivum", "info", t.start, t.end,
                                "opisné pasívum ojedinele je slabé samo osebe")
        # podmetové zámená a svoj
        po_vetach = []
        for v in vety:
            po_vetach.append([t for t in v.tokens if (
                t.deprel.startswith("nsubj") and t.upos == "PRON" and
                t.feats.get("PronType") == "Prs" and t.feats.get("Reflex") != "Yes")
                or t.lemma == "svoj"])
        self._zajmena_v_rade(po_vetach, met, False)
        # ukazovacie zámená na začiatku viet
        uk = [v for v in vety if v.tokens and v.tokens[0].lemma == "tento"]
        met["ukazovacie_na_zaciatku"] = len(uk)
        if len(uk) >= prah("ukazovacie_zaciatky") and len(uk) / n >= prah("ukazovacie_zaciatky_podiel"):
            for v in uk:
                self.pridej("skladba", "ukazovaci-ritual", "P2", v.tokens[0].start,
                            v.tokens[0].end, f"{len(uk)} viet sa začína tvarom „tento“")
        # príklonky za slovesom
        for v in vety:
            for t in v.tokens:
                if t.low in POMOCNE_PRIKLONKY and t.deprel.startswith("aux") and t.head:
                    h = v.tokens[t.head - 1] if t.head - 1 < len(v.tokens) else None
                    if not h or h.upos != "VERB" or h.idx >= t.idx or h.idx == 0:
                        continue
                    pred = v.tokens[h.idx - 1]
                    # spojka alebo častica na začiatku („A očervenel som.“) sa do prvej
                    # pozície nepočíta (KALIBRACIA SNK: bez toho 2 % ľudských úsekov)
                    if pred.upos in ("PUNCT", "CCONJ", "SCONJ", "PART") or \
                            pred.low in ("a", "i", "aj", "ale", "no", "však", "lebo") or \
                            pred.feats.get("PronType") in ("Rel", "Int"):
                        continue
                    self.pridej("skladba", "priklonka", "P1", h.start, t.end,
                                "príklonka patrí za prvý vetný člen („Tento problém sme "
                                "riešili“)")
        self.metriky["skladba"] = met

    def _je_vnoun(self, t):
        if t.feats.get("VerbForm") == "Vnoun":
            return True
        lem = t.lemma.lower()
        return (t.upos == "NOUN" and t.feats.get("Gender") == "Neut" and
                (lem.endswith("nie") or lem.endswith("tie")) and len(lem) >= 6 and
                lem not in VNOUN_NEJSOU)

    def _zajmena_v_rade(self, po_vetach, met, priblizne):
        """Podmetové zámená a „svoj“ v rade: súčet v dvoch po sebe idúcich vetách."""
        met["podmetove_zamena_a_svoj"] = sum(len(x) for x in po_vetach)
        okno = 0
        hit = set()
        for i in range(len(po_vetach)):
            o = po_vetach[i] + (po_vetach[i + 1] if i + 1 < len(po_vetach) else [])
            okno = max(okno, len(o))
            if len(o) >= prah("zamena_podmet_svoj_okno"):
                hit.update(id(t) for t in o)
                for t in o:
                    if not any(n.start == t.start and n.kategorie == "nadbytocne-zamena"
                               for n in self.nalezy):
                        self.pridej("skladba", "nadbytocne-zamena", "P1", t.start, t.end,
                                    f"{len(o)} podmetových zámen alebo „svoj“ v dvoch "
                                    f"vetách za sebou (prah "
                                    f"{prah('zamena_podmet_svoj_okno')})", priblizne=priblizne)
        met["zamena_max_v_dvoch_vetach"] = okno

    # -- výstup -----------------------------------------------------------
    def vysledek(self):
        if not self.model:
            vety = self.doc.prozni_vety()
            po_vetach = [[t for t in v.tokens if t.low in ("ja", "my") or t.low in TVARY_SVUJ]
                         for v in vety]
            uk = [v for v in vety if v.tokens and v.tokens[0].low in TVARY_TENTO]
            n = len(vety) or 1
            self.metriky["skladba"] = {"ukazovacie_na_zaciatku": len(uk),
                                       "poznamka": "bez modelu: len „ja“, „my“, tvary „svoj“ a "
                                                   "„tento“; nominalizácia a pasívum vynechané"}
            self._zajmena_v_rade(po_vetach, self.metriky["skladba"], True)
            if len(uk) >= prah("ukazovacie_zaciatky") and \
                    len(uk) / n >= prah("ukazovacie_zaciatky_podiel"):
                for v in uk:
                    self.pridej("skladba", "ukazovaci-ritual", "P2", v.tokens[0].start,
                                v.tokens[0].end, f"{len(uk)} viet sa začína tvarom „tento“")
            self.nalezy.sort(key=lambda n: (n.start, PORADI_ZAV[n.zavaznost]))
        pocty = {k: 0 for k in PORADI_ZAV}
        for n in self.nalezy:
            pocty[n.zavaznost] += 1
        return {
            "verzia": VERZE,
            "rezim": "udpipe" if self.model else "pravidla",
            "vsetko": self.vse,
            "priblizne": not self.model,
            "profil": self.profil_jm,
            "slova_md": self.slova_cesta,
            "suhrn": {"slov": self.doc.pocet_slov(), "viet": len(self.doc.prozni_vety()),
                       "titulkov": sum(1 for v in self.doc.vety if v.druh == "titulek"),
                       "nalezy": pocty, "vylucene": self.doc.vylouceno()},
            "metriky": self.metriky,
            "nalezy": [n.jako_dict(self.doc.radek) for n in self.nalezy],
            "prahy": PRAHY,
            "varovania": self.varovani,
        }


# ---------------------------------------------------------------------------
# Čitateľný prehľad
# ---------------------------------------------------------------------------
def prehled(v):
    r = []
    s = v["suhrn"]
    rezim = "s modelom UDPipe" if v["rezim"] == "udpipe" else "bez modelu (približne)"
    r.append(f"unslop-sk metriky {v['verzia']} · profil {v['profil']} · {rezim}")
    r.append(f"{s['slov']} slov, {s['viet']} viet, {s['titulkov']} titulkov · nálezy: " +
             ", ".join(f"{k} {n}" for k, n in s["nalezy"].items()))
    vyl = s.get("vylucene", {})
    if vyl.get("usekov"):
        nazvy = {"kod": "kód", "citacia": "citácia", "tabulka": "tabuľka"}
        r.append(f"vylúčené z merania: {vyl['slov']} slov (" +
                 ", ".join(f"{nazvy[k]} {vyl['usekov'][k]}" for k in nazvy if k in vyl["usekov"]) +
                 ")" + ("" if v.get("vsetko") or not ({"citacia", "tabulka"} & set(vyl["usekov"]))
                        else "; --vsetko zmeria citácie a tabuľky"))
    ry = v["metriky"].get("rytmus", {})
    if ry.get("viet"):
        r.append(f"rytmus: priemer {ry.get('priemer')} slov, sd {ry.get('smerodajna_odchylka', 0)}, "
                 f"cv {ry.get('variacny_koeficient', 0)}")
    sk = v["metriky"].get("skladba", {})
    if "slovesne_substantiva_na_1000_slov" in sk:
        r.append(f"skladba: slovesné podstatné mená {sk['slovesne_substantiva_na_1000_slov']}/1000 "
                 f"slov, opisné pasívum {sk['opisne_pasivum']}, zvratné {sk['zvratne_pasivum']}")
    po, ko = v["metriky"].get("postoj", {}), v["metriky"].get("konkretnost", {})
    if po and ko:
        ref = {**po.get("reference", {}), **ko.get("reference", {})}

        def h(m, k):
            return f"{m.get(k)} (ľudia CZ {ref[k]['ludia']})"
        r.append("postoj a konkrétnosť (info, prepis ich nemá znižovať; referencia „ľudia CZ“ "
                 "je česká, na slovenčine nemeraná): modálne častice "
                 f"{h(po, 'modalne_na_1000_slov')}, oslabujúce {h(po, 'oslabujuce_na_1000_slov')}"
                 f"/1000 slov, otázniky {h(po, 'otazniky_na_100_viet')}/100 viet, čísla "
                 f"{h(ko, 'cisla_na_1000_slov')}, vlastné mená "
                 f"{h(ko, 'vlastne_mena_na_1000_slov')}/1000 slov")
    for zav in ("P0", "P1", "P2"):
        nal = [n for n in v["nalezy"] if n["zavaznost"] == zav]
        if not nal:
            continue
        r.append("")
        r.append(f"{zav}:")
        for n in nal:
            txt = n["text"].replace("\n", " ")
            if len(txt) > 70:
                txt = txt[:67] + "…"
            pozn = f" – {n['poznamka']}" if n.get("poznamka") else ""
            r.append(f"  r. {n['riadok']}: [{n['metrika']}/{n['kategoria']}] „{txt}“{pozn}")
    info = [n for n in v["nalezy"] if n["zavaznost"] == "info"]
    if info:
        r.append("")
        r.append(f"info ({len(info)} slabých signálov, samy osebe nie sú nález):")
        for n in info:
            txt = n["text"].replace("\n", " ")
            if len(txt) > 50:
                txt = txt[:47] + "…"
            pozn = f" – {n['poznamka']}" if n.get("poznamka") else ""
            r.append(f"  r. {n['riadok']}: [{n['metrika']}/{n['kategoria']}] „{txt}“{pozn}")
    for w in v["varovania"]:
        r.append(f"varovanie: {w}")
    return "\n".join(r)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def vychozi_slova():
    tady = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(tady, "..", "references", "slova.md"))


_UDPIPE_CACHE = {}


def nacti_udpipe(cesta):
    if not cesta:
        return None
    if cesta not in _UDPIPE_CACHE:
        _UDPIPE_CACHE[cesta] = UDPipe(cesta)
    return _UDPIPE_CACHE[cesta]


def analyzuj(text, profil="blog", udpipe=None, slova=None, vse=False, vsetko=False):
    """API pre testy a iné skripty. `udpipe` je cesta k modelu, objekt UDPipe, alebo None.
    `vsetko` (alias `vse`): citácie „>“, tabuľky a „…“ merať ako bežný text (kód zostáva
    vylúčený vždy)."""
    vse = vse or vsetko
    if isinstance(udpipe, str):
        udpipe = nacti_udpipe(udpipe)
    profil = ALIASY_PROFILU.get(profil, profil)
    return Analyza(text, profil, udpipe, slova or vychozi_slova(), vse).spust().vysledek()


def utf8_stdio():
    """Štandardný vstup a výstup v UTF-8 aj tam, kde má konzola iné kódovanie (Windows cp1252).

    Bez toho výpis s diakritikou na Windows spadne na UnicodeEncodeError a text odovzdaný
    na stdin sa načíta zle. Prúdy bez reconfigure (zachytené v testoch) zostávajú.
    """
    for proud, chyby in ((sys.stdin, "strict"), (sys.stdout, "replace"), (sys.stderr, "replace")):
        if hasattr(proud, "reconfigure") and (proud.encoding or "").lower().replace("-", "") != "utf8":
            proud.reconfigure(encoding="utf-8", errors=chyby)


def main(argv=None):
    utf8_stdio()
    ap = argparse.ArgumentParser(description="Merateľné kontroly AI slopu v slovenskom texte.")
    ap.add_argument("vstup", nargs="?", default="-", help="súbor s textom, alebo - pre stdin")
    ap.add_argument("--profil", default="blog",
                    help="socialne | blog | email | dokumentacia | odborny | prezentacia")
    ap.add_argument("--udpipe", default=os.environ.get("UNSLOP_UDPIPE"),
                    help="cesta k modelu slovak-snk-ud-2.5-191206.udpipe")
    ap.add_argument("--bez-modelu", action="store_true",
                    help="obmedzený režim aj pri nastavenej premennej UNSLOP_UDPIPE")
    ap.add_argument("--slova", default=vychozi_slova(), help="cesta k references/slova.md")
    ap.add_argument("--format", choices=["text", "json", "oboje"], default="text",
                    help="text (predvolený) je stručný prehľad vrátane slabých signálov; "
                         "json je úplný výstup bez prahov")
    ap.add_argument("--prahy", action="store_true",
                    help="pridať do JSON pole prahy (konštantné dáta, predvolený výstup ich nemá)")
    ap.add_argument("--vsetko", action="store_true",
                    help="merať aj blokové citácie „>“, tabuľky a citácie v „…“ s plnou "
                         "závažnosťou (kód, URL a e-maily zostávajú vylúčené)")
    ap.add_argument("--prah", choices=["P0", "P1", "P2"],
                    help="návratový kód 1, keď existuje nález tejto alebo vyššej závažnosti")
    a = ap.parse_args(argv)
    profil = ALIASY_PROFILU.get(a.profil, a.profil)
    if profil not in PROFILY:
        ap.error(f"neznámy profil {a.profil}")
    if a.vstup == "-":
        text = sys.stdin.read()
    else:
        with open(a.vstup, encoding="utf-8") as f:
            text = f.read()
    v = analyzuj(text, profil, None if a.bez_modelu else a.udpipe, a.slova, a.vsetko)
    if not a.prahy:
        v.pop("prahy", None)
    if a.format in ("json", "oboje"):
        print(json.dumps(v, ensure_ascii=False, indent=2))
    if a.format in ("text", "oboje"):
        print(prehled(v), file=sys.stderr if a.format == "oboje" else sys.stdout)
    if a.prah:
        mez = PORADI_ZAV[a.prah]
        if any(PORADI_ZAV[n["zavaznost"]] <= mez for n in v["nalezy"]):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
