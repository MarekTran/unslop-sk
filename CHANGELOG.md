# Zmeny

## 0.1.0 – 2026-11-21

Prvá verzia skillu `unslop-sk`: slovenská adaptácia českého skillu [PetrHula/unslop-cs](https://github.com/PetrHula/unslop-cs) vo verzii 1.0.3.

- **Preklad a adaptácia** jadra skillu, vzorcov, zoznamov slov, výstupného formátu, skriptov `metriky.py` a `diff.py`, testov, regresných prípadov a runnera. Príklady, gramatické pravidlá (príklonky, prívesky s „čo“ a „čím“, menný štýl) a typografia sú slovenské (Pravidlá slovenského pravopisu, STN 01 6910).
- **Bohemizmy** ako nový oddiel: česká stopa („pokud“, „protože“, písmená ě, ř, ů mimo mien a citátov) je P1 aj raz; rozšírené hovorové bohemizmy („v kľude“, „doporučiť“) sú slabé samy osebe a nálezom P2 až v zhluku troch a viac.
- **Vynechané z originálu:** nástroje na analýzu českého korpusu (`tools/koditex`), dva regresné prípady s českými ľudskými textmi z webu a benchmark.
- **Zmeny v skripte oproti českému:** samotný prekročený rozpočet pomlčiek je P2 (P1 až pri inom náleze P0 alebo P1); „25%“ bez medzery je vždy P2; „EUR 1500“ v súvislom texte je P2; celovetné frázy sa párujú presne.

### Zmerané

- **Testy skriptov:** `tests/test_metriky.py` 169 testov, z toho 87 preskočených (vyžadujú model UDPipe alebo neplatia pre daný prípad), ostatné prešli; `tests/test_diff.py` 24 testov prešlo.
- **Kalibrácia na UD Slovak-SNK** (ľudské texty, 443 úsekov, 86 tisíc slov, režim bez modelu): aspoň jeden nález P0 alebo P1 má 16,9 % úsekov. Dlhá pomlčka „—“ je nálezom v 5,8 % úsekov, zhruba štyri pätiny z jedného zdroja; ostatné metriky sú do 3,6 % (otázka s odpoveďou 3,1 – 3,6 %, heslovitá kadencia 1,6 – 3,4 %, slová úrovne 2 1,3 – 1,6 %, česká stopa 0,5 %). SNK je výber viet, nie súvislé texty, takže čísla o rytme sú orientačné.

### Nezmerané

- Regresné prípady z `evals/pripady.md` cez model ešte nebežali; runner je overený len po načítanie prípadov.
- Skill nebol testovaný na skutočných ľudských ani AI textoch. Čísla „AI / ľudia“ v pravidlách sú z českých dát.
- Cesta skriptu s modelom UDPipe nebola skúšaná so slovenským modelom.

### Známe obmedzenia skriptu

- České slovo s veľkým začiatočným písmenom skript nehlási (chráni mená ako Dvořák), takže české slovo na začiatku vety mu unikne.
- Kalk „je tu pre vás“ hlási aj v doslovnom význame („Kniha je tu pre vás“).
