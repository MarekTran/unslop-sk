#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy pre diff.py: python3 tests/test_diff.py"""
import os
import sys
import unittest

TADY = os.path.dirname(os.path.abspath(__file__))
SKRIPTY = os.path.join(TADY, "..", "plugins", "unslop-sk", "skills", "unslop-sk", "scripts")
sys.path.insert(0, SKRIPTY)
import diff  # noqa: E402

NB = " "


def d(pred, po):
    return diff.slovni_diff(pred, po)


class SlovnyDiff(unittest.TestCase):
    def test_bez_zmeny(self):
        self.assertEqual(d("Bratislava je veľká.", "Bratislava je veľká."), [])

    def test_interpunkcia_a_uvodzovky_zostanu_v_kontexte(self):
        z = d("Projekt „Nový most“ je hotový.", "Projekt „Most“ je hotový.")
        self.assertEqual(z[0]["diff"], "Projekt „[-Nový most-]{+Most+}“ je hotový.")

    def test_desatinne_cislo_ako_celok(self):
        z = d("Podiel bol 1,3" + NB + "%.", "Podiel bol 1,5" + NB + "%.")
        self.assertEqual(z[0]["diff"], "Podiel bol [-1,3-]{+1,5+}" + NB + "%.")

    def test_nezlomitelna_medzera_zostane(self):
        z = d("V" + NB + "Nitre žijú 3 milióny.", "V" + NB + "Žiline žijú 3 milióny.")
        self.assertIn("V" + NB + "[-Nitre-]{+Žiline+}", z[0]["diff"])

    def test_pomlcka_sa_nemeni(self):
        z = d("Bol to rok 2019 – a potom 2020.", "Bol to rok 2021 – a potom 2020.")
        self.assertIn(" – a potom", z[0]["diff"])

    def test_kazda_zmenena_veta_ma_vlastny_zaznam(self):
        z = d("Jedna veta. Druhá veta.", "Iná veta. Tretia veta.")
        self.assertEqual(len(z), 2)

    def test_kod_sa_neporovnava(self):
        z = d("Text.\n\n```\na = 1\n```\n", "Text.\n\n```\nb = 2\n```\n")
        self.assertEqual(z, [])

    def test_nezavisi_od_locale(self):
        # Diff je čistý Python, v kóde nie je volanie locale ani gitu.
        with open(os.path.join(SKRIPTY, "diff.py"), encoding="utf-8") as f:
            zdroj = f.read()
        self.assertNotIn("subprocess", zdroj)
        self.assertNotIn("setlocale", zdroj)


class Straty(unittest.TestCase):
    def test_strata_cisla(self):
        z = diff.straty("Ušetrili sme 12 tisíc.", "Ušetrili sme veľa.")
        self.assertEqual(z["cisla"], ["12"])

    def test_cislo_zostalo(self):
        z = diff.straty("Ušetrili sme 12 tisíc.", "Šetrí sa 12 tisíc.")
        self.assertEqual(z["cisla"], [])

    def test_sklonovane_meno_sa_nehlasi(self):
        z = diff.straty("Žijeme v Nitre.", "Pracujem v meste Nitra.")
        self.assertEqual(z["mena"], [])

    def test_sklonovane_meno_s_kvantitou(self):
        z = diff.straty("Vlak ide do Košíc.", "Vlak má cieľ Košice.")
        self.assertEqual(z["mena"], [])

    def test_chybajuce_meno(self):
        z = diff.straty("Šiel do Trnavy.", "Šiel do mesta.")
        self.assertEqual(z["mena"], ["Trnavy"])

    def test_zaciatok_vety_nie_je_meno(self):
        z = diff.straty("Dnes prší.", "Vonku prší.")
        self.assertEqual(z["mena"], [])

    def test_zmazana_castica_a_istenie(self):
        z = diff.straty("Je to asi pravda, predsa.", "Je to pravda.")
        self.assertEqual(sorted(z["castice"]), ["asi", "predsa"])

    def test_slovenske_castice(self):
        z = diff.straty("Vraj to vlastne hádam pôjde, veď možno áno.", "Pôjde to, áno.")
        self.assertEqual(sorted(z["castice"]), ["hádam", "možno", "veď", "vlastne", "vraj"])

    def test_pocet_vyskytov(self):
        z = diff.straty("Asi áno, asi nie.", "Asi áno, nie.")
        self.assertEqual(z["castice"], ["asi"])

    def test_sila_tvrdenia_len_info(self):
        z = diff.straty("To spôsobuje rast.", "To ovplyvňuje rast.")
        self.assertEqual(z["markery_sily"], ["spôsobuje"])
        self.assertTrue(diff._prazdne(z))

    def test_kod_a_citacie_sa_nepocitaju(self):
        zdroj = "Text.\n\n```\n42 Trnava\n```\n\n> Citácia 7 Prešov.\n"
        z = diff.straty(zdroj, "Text.\n")
        self.assertEqual((z["cisla"], z["mena"]), ([], []))


class Rozhranie(unittest.TestCase):
    def _subory(self, a, b):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        pa, pb = os.path.join(self.tmp, "a.txt"), os.path.join(self.tmp, "b.txt")
        for cesta, obsah in ((pa, a), (pb, b)):
            with open(cesta, "w", encoding="utf-8") as f:
                f.write(obsah)
        return pa, pb

    def test_prisne_vracia_1_pri_strate(self):
        pa, pb = self._subory("Je to 12 %.", "Je to málo.")
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(diff.main([pa, pb, "--prisne"]), 1)
            self.assertEqual(diff.main([pa, pb]), 0)

    def test_prisne_vracia_0_bez_straty(self):
        pa, pb = self._subory("Je to 12 %.", "Činí to 12 %.")
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(diff.main([pa, pb, "--prisne"]), 0)

    def test_json_a_metriky(self):
        import io
        import json
        import contextlib
        pa, pb = self._subory("Bratislava je asi veľká. Žijú tu 3 ľudia.", "Bratislava je veľká.")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            diff.main([pa, pb, "--format", "json", "--metriky"])
        v = json.loads(buf.getvalue())
        self.assertEqual(set(v), {"zmeny", "straty", "metriky"})
        self.assertIn("riadok", v["metriky"])
        self.assertTrue(v["metriky"]["riadok"].startswith("Metriky pred → po: častice "))
        self.assertIn(" · mená ", v["metriky"]["riadok"])

    def test_md_strata_a_riadok_metrik(self):
        import io
        import contextlib
        pa, pb = self._subory("Firma Kovo ušetrila asi 12 %.", "Firma ušetrila veľa.")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            diff.main([pa, pb, "--metriky"])
        v = buf.getvalue()
        self.assertIn("**Tichá strata**", v)
        self.assertIn("- čísla: 12", v)
        self.assertIn("- mená: Kovo", v)
        self.assertIn("- častice a istenie: asi", v)
        self.assertIn("Metriky pred → po:", v)

    def test_md_bez_zmeny(self):
        pa, pb = self._subory("Rovnaké.", "Rovnaké.")
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            diff.main([pa, pb])
        self.assertIn("Bez zmeny.", buf.getvalue())
        self.assertIn("Nič nechýba: čísla, mená, častice ani istenie.", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
