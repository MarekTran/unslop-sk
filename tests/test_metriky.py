#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testy pre metriky.py.

    python3 tests/test_metriky.py                       # bez modelu
    UNSLOP_UDPIPE=/cesta/model.udpipe python3 tests/test_metriky.py   # aj s modelom
    python3 tests/test_metriky.py --udpipe /cesta/model.udpipe -v

Testy z evals/pripady.md: čisté prípady (6, 9, 11, 12, 14, 15, 19, 24, 26, 28, 36, 37)
nemajú nález P0 ani P1, zašpinené majú aspoň jeden nález v očakávanej kategórii.
Prípady, ktoré skript meraním zachytiť nevie, sú v OCAKAVANE_ZLYHANIA s dôvodom.

Trieda SModelom sa spúšťa len s modelom UDPipe pre slovenčinu; pri preklade
z českého skillu nebola overená (model má nekomerčnú licenciu a v repozitári nie je).
"""
import os
import re
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
SKRIPTY = os.path.join(TU, "..", "plugins", "unslop-sk", "skills", "unslop-sk", "scripts")
sys.path.insert(0, SKRIPTY)
import metriky  # noqa: E402

PRIPADY_MD = os.path.join(TU, "..", "evals", "pripady.md")
CISTE = {6, 9, 11, 12, 14, 15, 19, 24, 26, 28, 36, 37}

# Pre každý zašpinený prípad: zoznam (metrika, kategória-prefix) – aspoň jeden musí
# padnúť so závažnosťou P0–P2. Kategórie zodpovedajú očakávaniu v pripady.md.
OCAKAVANE = {
    1: [("zoznamy_slov", "fraza-uvod"), ("kontrast", "kontrastny-obrat"),
        ("trojice", "trojice"), ("zoznamy_slov", "uroven-1")],
    2: [("zoznamy_slov", "uroven-1"), ("zoznamy_slov", "kalk"),
        ("typografia", "dlha-pomlcka"), ("vstavane", "vagna-autorita")],
    3: [("typografia", "title-case"), ("titulky", "uputavkovy-titulok")],
    4: [("zoznamy_slov", "kalk"), ("zoznamy_slov", "chatbot")],
    5: [("zoznamy_slov", "menny"), ("skladba", "menny-styl")],
    7: [("skladba", "nadbytocne-zamena"), ("skladba", "ukazovaci-ritual"),
        ("skladba", "priklonka")],
    8: [("vstavane", "vagna-autorita")],
    10: [("zoznamy_slov", "fraza-precitnutie"), ("kontrast", "kontrastny-obrat"),
         ("zoznamy_slov", "fraza-pointa")],
    13: [("typografia", "percenta"), ("typografia", "datum"),
         ("typografia", "oddelovac-radov"), ("typografia", "rozsah"), ("typografia", "cas")],
    16: [("zoznamy_slov", "fraza-uvod"), ("zoznamy_slov", "fraza-prechod")],
    17: [("vstavane", "otazka-s-odpovedou"), ("vstavane", "dvojbodkove-odhalenie"),
         ("rytmus", "heslovita-kadencia"), ("rytmus", "retaz-kratkych-viet")],
    18: [("skladba", "menny-styl"), ("zoznamy_slov", "menny")],
    20: [("vstavane", "vlozeny-pokyn"), ("zoznamy_slov", "fraza-uvod"),
         ("zoznamy_slov", "uroven-1")],
    21: [("skladba", "ukazovaci-ritual")],
    22: [("zoznamy_slov", "uroven-2")],
    23: [("zoznamy_slov", "fraza-hrana")],
    25: [("typografia", "dlha-pomlcka")],
    27: [("zoznamy_slov", "uroven-1"), ("zoznamy_slov", "uroven-2")],
    35: [("bohemizmy", "ceska-stopa")],
}

# Kategórie, ktoré musia padnúť všetky (nie len jedna) – kontrolujú konkrétne metriky.
POVINNE = {
    1: [("kontrast", "kontrastny-obrat")],
    2: [("typografia", "dlha-pomlcka")],
    3: [("typografia", "title-case")],
    10: [("kontrast", "kontrastny-obrat")],
    13: [("typografia", "datum"), ("typografia", "oddelovac-radov"), ("typografia", "cas")],
    20: [("vstavane", "vlozeny-pokyn")],
    21: [("skladba", "ukazovaci-ritual")],
    22: [("zoznamy_slov", "uroven-2")],
    25: [("typografia", "dlha-pomlcka")],
    27: [("zoznamy_slov", "uroven-2")],
    29: [("zoznamy_slov", "kalk"), ("zoznamy_slov", "uroven-1"), ("typografia", "dlha-pomlcka")],
    30: [("vstavane", "vagna-autorita")],
    35: [("bohemizmy", "ceska-stopa")],
}

# Prípady, ktoré meranie nezachytí (štruktúra, význam, alebo treba model), s dôvodom.
OCAKAVANE_ZLYHANIA = {
    18: "rekapitulácia kontextu a rozhodnutie až na konci nie sú v slova.md; ide o štruktúru "
        "odpovede, nie o merateľný vzorec",
}

PROFIL_Z_NADPISU = {
    "sociálne siete": "socialne", "blog": "blog", "prezentácia": "prezentacia",
    "e-mail": "email", "dokumentácia": "dokumentacia", "odborný text": "odborny",
}


def nacitaj_pripady(cesta=PRIPADY_MD):
    with open(cesta, encoding="utf-8") as f:
        md = f.read()
    pripady = {}
    for blok in re.split(r"^## ", md, flags=re.M)[1:]:
        hlava, _, telo = blok.partition("\n")
        m = re.match(r"Prípad (\d+)", hlava)
        if not m or "Formát výstupu" in hlava or "\nZDROJ:" in telo:
            continue  # formát výstupu skript nemeria
        cislo = int(m.group(1))
        pm = re.search(r"profil: ([^)]+)\)", hlava)
        profil = PROFIL_Z_NADPISU.get(pm.group(1).strip(), "blog") if pm else "blog"
        vstup = telo.split("OČAKÁVANÉ")[0]
        riadky = [re.sub(r"^> ?", "", r) for r in vstup.split("\n") if r.startswith(">")]
        pripady[cislo] = (profil, "\n".join(riadky).strip())
    return pripady


def nalezy(v, minimalna="P2"):
    medza = metriky.PORADI_ZAV[minimalna]
    return [n for n in v["nalezy"] if metriky.PORADI_ZAV[n["zavaznost"]] <= medza]


def ma(v, metrika, kat, minimalna="P2"):
    return any(n["metrika"] == metrika and n["kategoria"].startswith(kat)
               for n in nalezy(v, minimalna))


class _Zaklad:
    UDPIPE = None

    @classmethod
    def setUpClass(cls):
        cls.pripady = nacitaj_pripady()

    def analyzuj(self, text, profil="blog"):
        return metriky.analyzuj(text, profil, self.UDPIPE)

    # -- evals ---------------------------------------------------------------
    def test_pocet_pripadov(self):
        self.assertEqual(len(self.pripady), 33)

    def test_ciste_pripady_bez_p0_p1(self):
        for c in sorted(CISTE):
            profil, text = self.pripady[c]
            v = self.analyzuj(text, profil)
            chybne = nalezy(v, "P1")
            with self.subTest(pripad=c):
                self.assertEqual(chybne, [], f"prípad {c}: {chybne}")

    def test_zaspinene_pripady(self):
        for c, ocak in OCAKAVANE.items():
            profil, text = self.pripady[c]
            v = self.analyzuj(text, profil)
            with self.subTest(pripad=c):
                if c in OCAKAVANE_ZLYHANIA:
                    continue
                self.assertTrue(any(ma(v, m, k) for m, k in ocak),
                                f"prípad {c}: žiadny nález z {ocak}; nájdené "
                                f"{[(n['metrika'], n['kategoria']) for n in nalezy(v)]}")
                for m, k in POVINNE.get(c, []):
                    self.assertTrue(ma(v, m, k), f"prípad {c}: chýba {m}/{k}")

    def test_pripady_s_blokom_nic_vnutri(self):
        # prípad 29 má blok kódu, 30 citáciu „>“: nálezy len mimo nich, text nad 100 slov
        for c, vnutri in ((29, "game changer"), (30, "game changer")):
            profil, text = self.pripady[c]
            v = self.analyzuj(text, profil)
            with self.subTest(pripad=c):
                self.assertGreater(v["suhrn"]["slov"], 100)
                zaciatok = text.index(vnutri)
                koniec = text.index("\n", zaciatok)
                self.assertFalse([n for n in nalezy(v) if zaciatok <= n["pozicia"][0] < koniec])
                self.assertEqual(v["suhrn"]["vylucene"]["usekov"],
                                 {"kod": 1} if c == 29 else {"citacia": 1})

    def test_vsetky_bezia(self):
        for c, (profil, text) in self.pripady.items():
            v = self.analyzuj(text, profil)
            self.assertIn("nalezy", v)
            self.assertGreater(v["suhrn"]["slov"], 0)

    # -- delenie viet --------------------------------------------------------
    def vety(self, text):
        d = metriky.Dokument(text, metriky.nacti_udpipe(self.UDPIPE) if self.UDPIPE else None)
        return [v.text.strip() for v in d.vety]

    def test_vety_skratky(self):
        t = ("Firma Alfa, s. r. o., dodá tovar, t. j. stoly, stoličky atď. do konca mesiaca. "
             "Ing. Jana Nová, PhD., to potvrdila. Platí to napr. pre tzv. veľké zákazky, "
             "resp. pre zákazky nad cca 1 mil. eur. Ďalšia veta.")
        self.assertEqual(len(self.vety(t)), 4, self.vety(t))

    def test_vety_datumy_a_cislovky(self):
        t = ("Stretnutie bude 4. 5. 2026 o 10.30. Druhé kolo sa začne 5. mája a 2. kolo sa "
             "skončí v júni. V roku 2026. Potom nič.")
        self.assertEqual(len(self.vety(t)), 4, self.vety(t))

    def test_vety_zakoncenie(self):
        t = "Naozaj? Áno! Uvidíme… Možno zajtra. Posledná veta bez bodky"
        self.assertEqual(len(self.vety(t)), 5, self.vety(t))

    def test_vety_riadky(self):
        t = "Dobrý deň,\n\nposielam podklady.\n\nS pozdravom\nMartin Kos"
        v = self.vety(t)
        self.assertIn("posielam podklady.", v)

    # -- jednotlivé metriky --------------------------------------------------
    def test_dlha_pomlcka(self):
        v = self.analyzuj("Projekt sa skončil načas—a v rozpočte.")
        self.assertTrue(ma(v, "typografia", "dlha-pomlcka", "P1"))

    def test_jedna_pomlcka_nie_je_nalez(self):
        v = self.analyzuj("Projekt sa skončil načas – a v rozpočte. Tím bol spokojný.")
        self.assertFalse(ma(v, "typografia", "rozpocet-pomlciek"))

    def test_rozpocet_pomlciek(self):
        # samotný prekročený rozpočet je P2, v zhluku s iným nálezom P0/P1 je P1
        v = self.analyzuj("Projekt – ako vieme – sa skončil načas – a v rozpočte.")
        self.assertTrue(ma(v, "typografia", "rozpocet-pomlciek"))
        self.assertFalse(ma(v, "typografia", "rozpocet-pomlciek", "P1"))
        v = self.analyzuj("Projekt – ako vieme – sa skončil načas – a je to game changer.")
        self.assertTrue(ma(v, "typografia", "rozpocet-pomlciek", "P1"))

    def test_rozsah_s_pomlckou_nie_je_nalez(self):
        # slovenský rozsah je „2024 – 2026“ (STN 01 6910), v sadzbe aj „2024–2026“
        for t in ("Zmluva platí na roky 2024 – 2026 a týka sa 5 – 10 ľudí.",
                  "Zmluva platí na roky 2024–2026 a týka sa 5–10 ľudí."):
            v = self.analyzuj(t)
            self.assertFalse(ma(v, "typografia", "rozsah"), t)
            self.assertFalse(ma(v, "typografia", "rozpocet-pomlciek"), t)
        v = self.analyzuj("Zmluva platí na roky 2024 - 2026.")
        self.assertTrue(ma(v, "typografia", "rozsah"))

    def test_cas_nie_je_desatinne_cislo(self):
        v = self.analyzuj("Otvorené je 9.00 – 18.00 a v sobotu do 12.30.")
        self.assertFalse(ma(v, "typografia", "desatinna-bodka"))

    def test_desatinna_bodka(self):
        v = self.analyzuj("Rast bol 2.5 percenta.")
        self.assertTrue(ma(v, "typografia", "desatinna-bodka"))

    def test_percenta_bez_medzery(self):
        # v slovenčine je „25%“ bez medzery P2 vždy; prídavné meno je „25-percentný“
        v = self.analyzuj("Dostanete 25% zľavu na všetko.")
        self.assertTrue(ma(v, "typografia", "percenta"))
        v = self.analyzuj("Dostanete 25-percentnú zľavu, teda 25 % z ceny.")
        self.assertFalse(ma(v, "typografia", "percenta"))

    def test_mena_kod_pred_sumou(self):
        self.assertTrue(ma(self.analyzuj("Oprava stála EUR 1500 a trvala týždeň."),
                           "typografia", "mena"))
        self.assertFalse(ma(self.analyzuj("Oprava stála 1 500 € a trvala týždeň."),
                            "typografia", "mena"))

    def test_title_case(self):
        v = self.analyzuj("# Strategické Partnerstvo A Globálne Riešenia\n\nText odseku je tu.")
        self.assertTrue(ma(v, "typografia", "title-case", "P1"))

    def test_nadpis_bez_title_case(self):
        v = self.analyzuj("# Vývoj tržieb 2024 – 2026\n\nText odseku je tu.")
        self.assertFalse(ma(v, "typografia", "title-case"))

    def test_otazka_v_titulku_eseje_nie_je_nalez(self):
        t = ("# Kde sú ich stroje?\n\nText odseku je tu.\n\n# Prečo deti prestali čítať návody"
             "\n\nĎalší odsek.")
        self.assertFalse(ma(self.analyzuj(t, "blog"), "titulky", "uputavkovy-titulok"))

    def test_otazka_v_titulku_slajdu_je_nalez(self):
        t = "# Kde sú naše čísla?\n\nText odseku je tu."
        self.assertTrue(ma(self.analyzuj(t, "prezentacia"), "titulky", "uputavkovy-titulok", "P1"))

    def test_hovorovy_titulok_eseje_je_nalez(self):
        t = "# Čo na školení bolo\n\nText odseku je tu."
        self.assertTrue(ma(self.analyzuj(t, "blog"), "titulky", "uputavkovy-titulok"))

    def test_zoznam_slov_tvary(self):
        v = self.analyzuj("Školenie je neoddeliteľnou súčasťou nástupu do firmy.")
        self.assertTrue(ma(v, "zoznamy_slov", "uroven-1"))
        v = self.analyzuj("Dáta zohrávajú kľúčovú úlohu v celom projekte.")
        self.assertTrue(ma(v, "zoznamy_slov", "uroven-1"))

    def test_zoznam_slov_slovesne_tvary(self):
        if not self.UDPIPE:
            self.skipTest("slovesné tvary („hrala“ ← „hrať“) páruje len model")
        v = self.analyzuj("Táto zmena hrala kľúčovú úlohu v celom projekte.")
        self.assertTrue(ma(v, "zoznamy_slov", "uroven-1"))

    def test_zoznam_slov_v_kode_nie(self):
        v = self.analyzuj("Premenná `game_changer` sa nastaví v konfigurácii.")
        self.assertFalse(ma(v, "zoznamy_slov", "uroven-1"))

    def test_kontrast_tvary(self):
        v = self.analyzuj("Nešlo o peniaze. Išlo o čas.")
        self.assertTrue(ma(v, "kontrast", "kontrastny-obrat", "P1"))
        v = self.analyzuj("Nebude to ľahké, bude to však stáť za to.")
        self.assertTrue(ma(v, "kontrast", "kontrastny-obrat"))
        v = self.analyzuj("Nie je to nástroj, je to zrkadlo.")
        self.assertTrue(ma(v, "kontrast", "kontrastny-obrat", "P1"))
        v = self.analyzuj("Kurz učí nielen písať, ale aj čítať cudzie texty.")
        self.assertTrue(ma(v, "kontrast", "kontrastny-obrat"))

    def test_kontrast_oprava_nie_je_nalez(self):
        v = self.analyzuj("Vezmite verziu 3, nie 2. Podiel klesol o 40 %, nie o 4 %.")
        self.assertFalse(ma(v, "kontrast", "kontrastny-obrat"))

    def test_namiesto_v_nadpise(self):
        v = self.analyzuj("# Dialóg namiesto prednášky\n\nNa kurze sa hlavne hovorí.")
        self.assertTrue(ma(v, "kontrast", "kontrastny-obrat", "P1"))

    def test_trojica_bez_ciarky_pred_a(self):
        v = self.analyzuj("Nový program je praktický, flexibilný a udržateľný.")
        self.assertTrue(ma(v, "trojice", "trojice", "P1"))

    def test_privesky(self):
        v = self.analyzuj("Firma zaviedla nový systém, čo podčiarkuje jej ambície. Tím rástol, "
                          "čím prispel k rastu.")
        self.assertTrue(ma(v, "privesky", "privesok"))

    def test_privesok_nie_je_kazde_co(self):
        # vzťažné „čo“ a „čím … tým“ nie sú prívesok
        v = self.analyzuj("Urobil všetko, čo sľúbil. Čím skôr prídete, tým lepšie. "
                          "Pýtal sa, čo znamená tá skratka. Nevedel, čím začať.")
        self.assertFalse(ma(v, "privesky", "privesok"))
        self.assertLessEqual(v["metriky"]["privesky"]["pocet"], 1)

    def test_fraza_veta_sa_paruje_prisne(self):
        v = self.analyzuj("Ten rok v dielni mi dal veľa. Otvorilo mi to oči.")
        self.assertTrue(ma(v, "zoznamy_slov", "fraza-precitnutie", "P1"))
        v = self.analyzuj("Chlapec otvoril oči a pozrel sa na strop.")
        self.assertFalse(ma(v, "zoznamy_slov", "fraza-precitnutie"))

    def test_kalk_s_jednym_obsahovym_slovom_potrebuje_zameno(self):
        v = self.analyzuj("Napíšte nám kedykoľvek, sme tu pre vás každý deň.")
        self.assertTrue(ma(v, "zoznamy_slov", "kalk", "P1"))
        v = self.analyzuj("A sme tu, povedala. Sme tu pre deti z okolia.")
        self.assertFalse(ma(v, "zoznamy_slov", "kalk"))

    def test_otazka_s_odpovedou(self):
        v = self.analyzuj("Výsledok? Rýchlejšia práca. Tím to zvládol za dva dni.")
        self.assertTrue(ma(v, "vstavane", "otazka-s-odpovedou", "P1"))
        # skutočná otázka so slovesom a rad otázok nie sú inscenovaná pauza
        v = self.analyzuj("Všimli ste si? Taká krutá irónia. Genialitu? Odvahu? Vášeň? "
                          "Občas sa niekto chabo a dosť bezvýsledne pokúsil sfúknuť tie plamene.")
        self.assertFalse(ma(v, "vstavane", "otazka-s-odpovedou"))

    def test_konektory_retaz(self):
        v = self.analyzuj("Systém je rýchly. Navyše je lacný. Okrem toho je spoľahlivý. "
                          "Ďalej ponúka podporu.")
        self.assertTrue(ma(v, "sudrznost", "konektory-retaz", "P1"))

    def test_postoj_informativne(self):
        v = self.analyzuj("Veď to predsa viete. My sme to vraj skúšali.")
        self.assertGreater(v["metriky"]["postoj"]["castice_na_100_slov"], 0)
        self.assertFalse(any(n["metrika"] == "postoj" for n in v["nalezy"]))

    # -- prahy prevzaté z českej kalibrácie ------------------------------------
    def test_prechod_jeden_p2_dva_p1(self):
        v = self.analyzuj("Pokiaľ ide o rozpočet, nič sa nemení. Tím zostáva rovnaký.")
        self.assertTrue(ma(v, "zoznamy_slov", "fraza-prechod"))
        self.assertFalse(ma(v, "zoznamy_slov", "fraza-prechod", "P1"))
        v = self.analyzuj("Pokiaľ ide o rozpočet, nič sa nemení. Čo sa týka tímu, zostáva.")
        self.assertTrue(ma(v, "zoznamy_slov", "fraza-prechod", "P1"))

    def test_uvod_uprostred_odseku_p2(self):
        v = self.analyzuj("Firma vznikla v Nitre. V súčasnej dobe má tridsať ľudí.")
        self.assertFalse(ma(v, "zoznamy_slov", "fraza-uvod", "P1"))
        v = self.analyzuj("V súčasnej dobe má firma tridsať ľudí. Vznikla v Nitre.")
        self.assertTrue(ma(v, "zoznamy_slov", "fraza-uvod", "P1"))

    def test_prenesene_znizuje_na_p2(self):
        v = self.analyzuj("Potápač sa pomaly ponoril do jazera.")
        self.assertFalse(ma(v, "zoznamy_slov", "uroven-1", "P1"))

    def test_vagna_autorita_zo_slova_md(self):
        v = self.analyzuj("Odborníci sa zhodujú, že to funguje.")
        self.assertTrue(ma(v, "vstavane", "vagna-autorita", "P0"))
        self.assertEqual(sum(1 for n in v["nalezy"] if n["kategoria"] == "vagna-autorita"), 1)

    def test_datum_bez_medzier(self):
        v = self.analyzuj("Zmluvu sme podpísali 4.5.2026 v Žiline.")
        self.assertTrue(ma(v, "typografia", "datum"))
        self.assertFalse(ma(v, "typografia", "desatinna-bodka"))
        v = self.analyzuj("Zmluvu sme podpísali 04.05.2026 v Žiline.")
        self.assertFalse(ma(v, "typografia", "datum"))

    def test_zosilnovac_nie_je_nalez(self):
        v = self.analyzuj("Bolo to naozaj veľmi ťažké a úplne nečakané. Výsledok nás absolútne "
                          "prekvapil a výrazne zmenil plán.")
        self.assertFalse(any(n["zdroj"].endswith(w) for n in v["nalezy"] if n.get("zdroj")
                             for w in ("úplne", "absolútne", "naozaj", "veľmi", "výrazne")))

    def test_uroven2_dlhy_odsek(self):
        kratky = "Tento inovatívny prístup je flexibilný. Tím ho zaviedol v marci."
        self.assertTrue(ma(self.analyzuj(kratky), "zoznamy_slov", "uroven-2", "P1"))
        vypln = " ".join(["Tím robil na zákazke celý mesiac a výsledok odovzdal zákazníkovi "
                          "v pondelok ráno."] * 9)
        dlhy = kratky + " " + vypln
        self.assertFalse(ma(self.analyzuj(dlhy), "zoznamy_slov", "uroven-2", "P1"))

    def test_postoj_a_konkretnost_s_referenciou(self):
        v = self.analyzuj("Asi to vyjde. Prídete o 9.30? Jana Nová poslala 3 návrhy.")
        po, ko = v["metriky"]["postoj"], v["metriky"]["konkretnost"]
        self.assertGreater(po["oslabujuce_na_1000_slov"], 0)
        self.assertGreater(po["otazniky_na_100_viet"], 0)
        self.assertGreater(ko["cisla_na_1000_slov"], 0)
        ref = po["reference"]["modalne_na_1000_slov"]
        self.assertIn("ludia", ref)
        self.assertEqual(ref["jazyk"], "cs")  # referencia je česká, nie slovenská
        self.assertFalse(any(n["metrika"] in ("postoj", "konkretnost") for n in v["nalezy"]))

    def test_mozno_pred_neurcitkom_nie_je_istenie(self):
        v = self.analyzuj("Na záver možno povedať, že plán vyšiel.")
        self.assertEqual(v["metriky"]["postoj"]["oslabujuce_na_1000_slov"], 0)
        v = self.analyzuj("Možno to vyjde až v piatok.")
        self.assertGreater(v["metriky"]["postoj"]["oslabujuce_na_1000_slov"], 0)

    def test_navyse_dalej_sa_nepocitaju_do_pocetnosti(self):
        v = self.analyzuj("Systém je rýchly. Navyše je lacný. Tím je malý. Ďalej ponúka podporu.")
        self.assertEqual(v["metriky"]["sudrznost"]["konektory_na_zaciatku"], 0)

    # -- bohemizmy -------------------------------------------------------------
    def test_ceska_stopa_p1(self):
        v = self.analyzuj("Okná treba utesniť, protože tadiaľ uniká teplo.")
        self.assertTrue(ma(v, "bohemizmy", "ceska-stopa", "P1"))
        v = self.analyzuj("Je to dobře urobené a drží to už rok.")
        self.assertTrue(ma(v, "bohemizmy", "ceska-stopa", "P1"))

    def test_ceska_stopa_len_presny_tvar(self):
        # „proto“ nie je „protokol“, „jak“ nie je „jakot“, „tady“ nie je „tadiaľ“
        v = self.analyzuj("Protokol podpísali včas. Jakot stíchol a voda tadiaľ odtiekla.")
        self.assertFalse(ma(v, "bohemizmy", "ceska-stopa"))

    def test_jeden_bohemizmus_nie_je_nalez(self):
        v = self.analyzuj("V kľude to stihneme do stredy, faktúru pošlem zajtra.")
        self.assertFalse(ma(v, "bohemizmy", "bohemizmus"))
        self.assertTrue(ma(v, "bohemizmy", "bohemizmus", "info"))

    def test_zhluk_bohemizmov_p2(self):
        v = self.analyzuj("Doporučujeme zľavu využiť behom týždňa. Naviac dostanete darček. "
                          "Tovar sa predáva v pôvodnom balení.")
        self.assertTrue(ma(v, "bohemizmy", "bohemizmus", "P2"))
        self.assertFalse(ma(v, "bohemizmy", "bohemizmus", "P1"))

    def test_bohemizmus_nie_je_podobne_slovo(self):
        # beh, hodný, zbytočný, pred, vopred sú slovenské slová
        v = self.analyzuj("Ranný beh pred prácou nie je zbytočný. Je hodný pochvaly, že vopred "
                          "predal lístky a previedol peniaze.")
        self.assertEqual([n for n in v["nalezy"] if n["metrika"] == "bohemizmy"
                          and n["zavaznost"] != "info"], [])
        self.assertFalse(any(n["text"].lower() in ("beh", "hodný", "zbytočný", "pred", "vopred")
                             for n in v["nalezy"] if n["metrika"] == "bohemizmy"))

    def test_ceske_meno_sa_nehlasi(self):
        v = self.analyzuj("Prednášal architekt Jiří Dvořák z Brna a pán Růžička z Přerova.")
        self.assertFalse(ma(v, "bohemizmy", "ceska-stopa", "info"))
        # český názov s malým písmenom vnútri a prídavné meno z českého mena
        v = self.analyzuj("Básne publikoval v Mladé tvorbě a kódex kúpil břevnovský kláštor.")
        self.assertFalse(ma(v, "bohemizmy", "ceska-stopa", "info"))

    def test_samotne_ceske_pismeno_sa_nehlasi(self):
        v = self.analyzuj("Slovenčina nemá písmená ě, ř a ů, čeština ich má.")
        self.assertFalse(ma(v, "bohemizmy", "ceska-stopa", "info"))

    def test_ceska_citacia_len_info(self):
        v = self.analyzuj("Začal vetou „Protože dům není stroj, musí se v něm dát bydlet.“ a "
                          "potom ukazoval pôdorysy.")
        self.assertFalse(ma(v, "bohemizmy", "ceska-stopa"))
        self.assertTrue(ma(v, "bohemizmy", "ceska-stopa", "info"))

    def test_cesky_text_varovanie(self):
        v = self.analyzuj("Protože dům není stroj, musí se v něm dát bydlet. Když přijde zima, "
                          "který z nás řekne, že se tady špatně žije? Pokud někdo, tak ať "
                          "přijde teď. Stroj není dům a dům není stroj, jak říkával.")
        self.assertTrue(any("český" in w for w in v["varovania"]))
        self.assertEqual(sum(1 for n in v["nalezy"] if n["kategoria"] == "ceska-stopa"), 3)

    # -- výstup ----------------------------------------------------------------
    def test_json_vystup(self):
        import io
        import contextlib
        import json
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                         encoding="utf-8") as f:
            f.write("V dnešnej dobe je to game changer.")
        buf = io.StringIO()
        args = [f.name, "--format", "json"] + (["--udpipe", self.UDPIPE] if self.UDPIPE
                                               else ["--bez-modelu"])
        with contextlib.redirect_stdout(buf):
            metriky.main(args)
        os.unlink(f.name)
        d = json.loads(buf.getvalue())
        self.assertEqual(d["rezim"], "udpipe" if self.UDPIPE else "pravidla")
        self.assertEqual(set(d), {"verzia", "rezim", "vsetko", "priblizne", "profil", "slova_md",
                                  "suhrn", "metriky", "nalezy", "varovania"})
        self.assertEqual(set(d["nalezy"][0]) - {"poznamka", "zdroj", "priblizne"},
                         {"metrika", "kategoria", "zavaznost", "text", "pozicia", "riadok",
                          "stlpec"})

    def spust_cli(self, text, *args):
        import io
        import contextlib
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                         encoding="utf-8") as f:
            f.write(text)
        buf = io.StringIO()
        zaklad = [f.name] + (["--udpipe", self.UDPIPE] if self.UDPIPE else ["--bez-modelu"])
        with contextlib.redirect_stdout(buf):
            metriky.main(zaklad + list(args))
        os.unlink(f.name)
        return buf.getvalue()

    def test_json_bez_prahov_ale_s_prepinacom(self):
        import json
        text = "V dnešnej dobe je to game changer."
        self.assertNotIn("prahy", json.loads(self.spust_cli(text, "--format", "json")))
        d = json.loads(self.spust_cli(text, "--format", "json", "--prahy"))
        self.assertIn("prahy", d)

    def test_aliasy_profilov(self):
        for alias, profil in (("linkedin", "socialne"), ("prezentácia", "prezentacia"),
                              ("dokumentácia", "dokumentacia"), ("e-mail", "email")):
            self.assertEqual(metriky.analyzuj("Krátky text.", alias)["profil"], profil)

    def test_text_vypisuje_slabe_signaly(self):
        # slová úrovne 3 sú len info; textový výstup ich musí vypísať po riadkoch,
        # pretože SKILL.md číta text namiesto JSON
        v = self.analyzuj("Tento prístup je dôležitý a zásadný. Je to praktický nástroj.")
        info = [n for n in v["nalezy"] if n["zavaznost"] == "info"]
        self.assertTrue(info)
        r = metriky.prehled(v)
        self.assertIn(f"info ({len(info)} slabých signálov", r)
        for n in info:
            self.assertIn(f"[{n['metrika']}/{n['kategoria']}]", r)
        self.assertNotIn("--format json", r)

    def test_text_je_kratsi_nez_json(self):
        text = "V dnešnej dobe je to game changer a robustné riešenie. " * 3
        self.assertLess(len(self.spust_cli(text)), len(self.spust_cli(text, "--format", "json")) / 3)

    # -- kód a citácie mimo merania ---------------------------------------------
    # Každý vylúčený typ: slop vnútri (úroveň 1 a „—“) nesmie dať P0–P2, rovnaká veta
    # mimo bloku je chránený náprotivok a merať sa musí.
    SLOP = "Toto je game changer — naozaj"
    UVOD = "Úvodná veta je obyčajná a nič zvláštne v nej nie je."
    ZAVER = "Záverečná veta je tiež obyčajná."

    def assertMerane(self, v, ocak=True):
        nal = ma(v, "zoznamy_slov", "uroven-1", "P2") and ma(v, "typografia",
                                                              "dlha-pomlcka", "P2")
        self.assertEqual(nal, ocak, [(n["zavaznost"], n["kategoria"], n["text"])
                                     for n in v["nalezy"]])

    def vyluceny_typ(self, blok, druh):
        text = f"{self.UVOD}\n\n{blok}\n\n{self.ZAVER}"
        v = self.analyzuj(text)
        self.assertEqual(nalezy(v), [], f"{druh}: {nalezy(v)}")
        self.assertEqual(v["suhrn"]["vylucene"]["usekov"].get(druh), 1)
        chraneny = f"{self.UVOD}\n\n{self.SLOP}.\n\n{self.ZAVER}"
        self.assertMerane(self.analyzuj(chraneny))

    def test_vylucene_ohradenie_backticky(self):
        self.vyluceny_typ(f"```\n{self.SLOP}\n```", "kod")

    def test_vylucene_ohradenie_vlnovky(self):
        self.vyluceny_typ(f"~~~python\n{self.SLOP}\n~~~", "kod")

    def test_vylucene_neuzavrete_ohradenie(self):
        v = self.analyzuj(f"{self.UVOD}\n\n```\n{self.SLOP}")
        self.assertEqual(nalezy(v), [])

    def test_vyluceny_odsadeny_kod(self):
        self.vyluceny_typ(f"    {self.SLOP}\n\t{self.SLOP}", "kod")

    def test_vylucene_html_pre(self):
        self.vyluceny_typ(f"<pre>\n{self.SLOP}\n</pre>", "kod")

    def test_vylucene_html_code(self):
        v = self.analyzuj(f"Nastavte <code>{self.SLOP}</code> v konfigurácii.")
        self.assertEqual(nalezy(v), [])

    def test_vyluceny_inline_kod(self):
        v = self.analyzuj(f"Nastavte `{self.SLOP}` v konfigurácii.")
        self.assertEqual(nalezy(v), [])

    def test_vylucena_citacia(self):
        self.vyluceny_typ(f"> {self.SLOP}.\n>Druhý riadok citácie.", "citacia")

    def test_tabulka_len_info(self):
        tab = f"| Stĺpec | Opis |\n|---|---|\n| A | {self.SLOP} |\n| B | – |"
        v = self.analyzuj(f"{self.UVOD}\n\n{tab}\n\n{self.ZAVER}")
        self.assertEqual(nalezy(v), [])
        info = [n for n in v["nalezy"] if n["zavaznost"] == "info"]
        self.assertTrue(any("v tabuľke" in n["poznamka"] and n["kategoria"] == "uroven-1"
                            for n in info), info)
        self.assertEqual(v["suhrn"]["vylucene"]["usekov"], {"tabulka": 1})
        # bez krajných zvislých čiar je to tiež tabuľka
        tab2 = f"Stĺpec | Opis\n--- | ---\nA | {self.SLOP}"
        self.assertEqual(nalezy(self.analyzuj(f"{self.UVOD}\n\n{tab2}")), [])

    def test_citacia_v_uvodzovkach_info(self):
        v = self.analyzuj(f"Kolega povedal „{self.SLOP}“ a odišiel domov.")
        self.assertEqual(nalezy(v), [])
        self.assertTrue(all("citácia?" in n["poznamka"] for n in v["nalezy"]))
        self.assertTrue(ma(v, "zoznamy_slov", "uroven-1", "info"))
        # krátka citácia sa nevylučuje: slová v nej sa počítajú
        self.assertEqual(v["suhrn"]["slov"], 10)
        self.assertEqual(v["suhrn"]["vylucene"]["slov"], 0)

    def test_pomlcky_v_citacii_mimo_rozpoctu(self):
        text = "Projekt sa skončil načas – a v rozpočte. Tím povedal „rýchlo – lacno – dobre“."
        self.assertFalse(ma(self.analyzuj(text), "typografia", "rozpocet-pomlciek"))
        text = "Projekt sa skončil načas – a v rozpočte. Tím bol rýchly – lacný – dobrý."
        self.assertTrue(ma(self.analyzuj(text), "typografia", "rozpocet-pomlciek"))

    def test_upozornenie_githubu_sa_meria(self):
        v = self.analyzuj(f"{self.UVOD}\n\n> [!NOTE]\n> {self.SLOP}.\n\n{self.ZAVER}")
        self.assertMerane(v)
        self.assertEqual(v["suhrn"]["vylucene"]["slov"], 0)

    def test_odsadenie_odsekov_nie_je_kod(self):
        # odsadenie prvého riadka (text z Wordu) sa meria
        text = f"\t{self.UVOD}\n\n\t{self.SLOP}.\n\n\t{self.ZAVER}"
        self.assertMerane(self.analyzuj(text))
        # pokračovanie položky zoznamu sa meria
        text = f"- Položka zoznamu.\n\n    {self.SLOP}.\n\n{self.ZAVER}"
        self.assertMerane(self.analyzuj(text))

    def test_prepinac_vsetko(self):
        citacia = f"{self.UVOD}\n\n> {self.SLOP}.\n\n{self.ZAVER}"
        tab = f"{self.UVOD}\n\n| A | B |\n|---|---|\n| x | {self.SLOP} |"
        uvodz = f"Kolega povedal „{self.SLOP}“ a odišiel domov."
        kod = f"{self.UVOD}\n\n```\n{self.SLOP}\n```"
        for text in (citacia, tab, uvodz):
            with self.subTest(text=text[-30:]):
                self.assertMerane(metriky.analyzuj(text, "blog", self.UDPIPE, vsetko=True))
        v = metriky.analyzuj(kod, "blog", self.UDPIPE, vsetko=True)
        self.assertEqual(nalezy(v), [])  # kód zostáva vylúčený aj s --vsetko
        self.assertTrue(v["vsetko"])

    def test_pocet_slov_bez_vyluceneho(self):
        proza = "Jeden dva tri štyri päť."
        blok = "```\nsest sedem osem devat desat\n```"
        cit = "> jedenásť dvanásť trinásť"
        tab = "| štrnásť | pätnásť |\n|---|---|\n| šestnásť | sedemnásť |"
        v = self.analyzuj(f"{proza}\n\n{blok}\n\n{cit}\n\n{tab}")
        self.assertEqual(v["suhrn"]["slov"], 5)
        self.assertEqual(v["suhrn"]["vylucene"],
                         {"slov": 12, "usekov": {"kod": 1, "citacia": 1, "tabulka": 1}})
        self.assertEqual(self.analyzuj(proza)["suhrn"]["vylucene"], {"slov": 0, "usekov": {}})

    def test_rytmus_nepreskoci_blok(self):
        kratke = "Bolo to rýchle. Bolo to lacné."
        cez_blok = f"{kratke}\n\n```\nkód\n```\n\n{kratke}"
        self.assertFalse(ma(self.analyzuj(cez_blok), "rytmus", "retaz-kratkych-viet"))
        self.assertTrue(ma(self.analyzuj(f"{kratke}\n\n{kratke}"), "rytmus",
                           "retaz-kratkych-viet"))

    def test_citacny_token_aj_v_kode(self):
        v = self.analyzuj("Text odseku.\n\n```\nzdroj :contentReference[oaicite:0]\n```")
        self.assertTrue(ma(v, "vstavane", "citacny-token", "P0"))

    def test_zastupny_text_a_znacka_overit(self):
        v = self.analyzuj("Dobrý deň, [Meno], posielam ponuku pre [Názov firmy].")
        self.assertTrue(ma(v, "vstavane", "zastupny-text", "P0"))
        v = self.analyzuj("Predaj vzrástol o [OVERIŤ: presné číslo] percent.")
        self.assertFalse(ma(v, "vstavane", "zastupny-text"))
        self.assertTrue(ma(v, "vstavane", "znacka-overit", "info"))

    def test_dvojbodka_pred_citaciou(self):
        v = self.analyzuj("Riaditeľ povedal: „Začneme v pondelok.“ Potom odišiel.")
        self.assertFalse(ma(v, "vstavane", "dvojbodkove-odhalenie"))
        v = self.analyzuj("Výsledok: úspech. Potom sme oslavovali celý večer.")
        self.assertTrue(ma(v, "vstavane", "dvojbodkove-odhalenie", "P1"))

    def test_kurziva_je_zmienka(self):
        zmienka = "Skilly zakážu slová ako *kľúčový* alebo _game changer_ a tým končia."
        v = self.analyzuj(zmienka)
        self.assertFalse(ma(v, "zoznamy_slov", "uroven-1"))
        self.assertTrue(any("v kurzíve" in n.get("poznamka", "") for n in v["nalezy"]))
        # tučné písmo kurzíva nie je, odrážka „* “ tiež nie
        self.assertTrue(ma(self.analyzuj("Zohráva **kľúčovú** úlohu v rozpočte obce."),
                           "zoznamy_slov", "uroven-1"))
        self.assertTrue(ma(self.analyzuj("* Zohráva kľúčovú úlohu v rozpočte obce."),
                           "zoznamy_slov", "uroven-1"))

    def test_cislo_verzie_nie_je_desatinne(self):
        for text in ("Merané na modeli Claude Sonnet 5.5 so strednou úrovňou úsilia.",
                     "Modely majú licenciu CC BY-NC-SA 4.0 len na nekomerčné použitie.",
                     "Porovnali sme to s GPT-4.5 na rovnakej sade."):
            with self.subTest(text=text):
                self.assertFalse(ma(self.analyzuj(text), "typografia", "desatinna-bodka"))
        for text in ("Podiel vzrástol na 2.5 percenta.", "Inflácia dosiahla 3.4 % v marci.",
                     "Priemer 2.5 bodu je nad plánom."):
            with self.subTest(text=text):
                self.assertTrue(ma(self.analyzuj(text), "typografia", "desatinna-bodka"))

    def test_zhoda_kmenov_len_slovenske_alternacie(self):
        self.assertFalse(metriky.shoda_kmenu(metriky.kmen("modelov"), metriky.kmen("moderný")))
        self.assertTrue(metriky.shoda_kmenu(metriky.kmen("príležitosti"),
                                            metriky.kmen("príležitosť")))
        self.assertTrue(metriky.shoda_kmenu(metriky.kmen("úrovne"), metriky.kmen("úroveň")))
        self.assertTrue(metriky.shoda_kmenu(metriky.kmen("umožnil"), metriky.kmen("umožňovať")))
        self.assertEqual(metriky.kmen("kľúčových"), metriky.kmen("kľúčovú"))
        self.assertEqual(metriky.kmen("inováciami"), metriky.kmen("inovácia"))

    def test_slova_md_sa_parsuje_bez_varovani(self):
        polozky, varovania = metriky.nacti_slova(metriky.vychozi_slova())
        self.assertEqual(varovania, [])
        sekcie = {p.sekce for p in polozky}
        self.assertEqual(sekcie, {"uroven1", "uroven2", "uroven3", "kalk", "anglicizmus",
                                  "opis", "menny", "uredni", "bohemizmus", "fraze", "vagni",
                                  "chatbot"})
        stopy = [p for p in polozky if p.kategorie == "česká stopa"]
        self.assertEqual(len(stopy), 15)
        self.assertTrue(all(p.zavaznost == "P1" for p in stopy))
        # chránené frázy e-mailu (oslovenie, rozlúčka) sa nenačítajú, P1 odsek áno
        chatbot = [p.raw for p in polozky if p.sekce == "chatbot"]
        self.assertNotIn("S pozdravom", chatbot)
        self.assertIn("Samozrejme!", chatbot)

    def test_vylucenie_v_textovom_vystupe(self):
        v = self.analyzuj(f"{self.UVOD}\n\n```\nkód\n```\n\n> citácia")
        r = metriky.prehled(v)
        self.assertIn("vylúčené z merania: 2 slov (kód 1, citácia 1); --vsetko zmeria", r)
        self.assertNotIn("vylúčené", metriky.prehled(self.analyzuj(self.UVOD)))


class BezModelu(_Zaklad, unittest.TestCase):
    UDPIPE = None


_MODEL = os.environ.get("UNSLOP_UDPIPE")


@unittest.skipUnless(_MODEL and os.path.exists(_MODEL), "model UDPipe nie je k dispozícii "
                     "(nastav UNSLOP_UDPIPE alebo --udpipe)")
class SModelom(_Zaklad, unittest.TestCase):
    UDPIPE = _MODEL

    def test_pasivum_opisne_a_zvratne(self):
        v = self.analyzuj("Bolo rozhodnuté o zmene. Systém bude spustený v pondelok. "
                          "Poplatky sa platia vopred.")
        sk = v["metriky"]["skladba"]
        self.assertEqual(sk["opisne_pasivum"], 2)
        self.assertGreaterEqual(sk["zvratne_pasivum"], 1)

    def test_nominalizacia_nie_pridavne_mena(self):
        v = self.analyzuj("Denný a národný vnútorný most a hosť. Informácie o situácii.")
        self.assertEqual(v["metriky"]["skladba"]["slovesne_substantiva"], 0)

    def test_priklonka(self):
        v = self.analyzuj("Tento problém riešili sme už minulý týždeň.")
        self.assertTrue(ma(v, "skladba", "priklonka", "P1"))
        v = self.analyzuj("Tento problém sme riešili už minulý týždeň.")
        self.assertFalse(ma(v, "skladba", "priklonka"))


if __name__ == "__main__":
    argv = sys.argv[:]
    if "--udpipe" in argv:
        i = argv.index("--udpipe")
        os.environ["UNSLOP_UDPIPE"] = argv[i + 1]
        SModelom.UDPIPE = argv[i + 1]
        del argv[i:i + 2]
        SModelom.__unittest_skip__ = False
    unittest.main(argv=argv)
