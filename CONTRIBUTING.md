# Ako skill upravovať

Súbor opisuje údržbu skillu `plugins/unslop-sk/skills/unslop-sk`. Skill je v plugine `plugins/unslop-sk`; koreň repozitára drží testy, evaly a nástroje.

## Kde čo je

Cesty v skille sú relatívne k `plugins/unslop-sk/skills/unslop-sk`.

- `SKILL.md` – jadro, ktoré model číta vždy: description, princíp, režimy, postup, profily registrov, závažnosť, poistky, sebakontrola a formáty výstupu. Referencie sa nečítajú povinne, takže jadro samo musí stačiť na bežný text.
- `references/vzorce.md` – pravidlá úrovní 1 až 3, slovenská skladba, rozprávanie a registre; ku každému vzorcu príklad pred a po a chránený podobný prípad.
- `references/slova.md` – zoznamy slov s prahmi, kalky, bohemizmy, ustálené frázy, vágne autority, chatbotie artefakty, typografia. Skript `metriky.py` tento súbor parsuje: nadpisy oddielov, hlavičky tabuliek a tučné štítky musia zostať v tvare, ktorý parser pozná (`nacti_slova` v skripte), inak skript vypíše varovanie.
- `references/vystup.md` – úrovne výstupu a diff; `references/pisanie.md` – krátka verzia pravidiel pre režim písania.
- `references/zdroje.md` – opora pravidiel a čo z nej na slovenčine nikto nemeral.
- `scripts/metriky.py` – merateľné kontroly; testy `python3 tests/test_metriky.py`.
- `scripts/diff.py` – diff a tichá strata pri prepise; testy `python3 tests/test_diff.py`.

## Pravidlá úprav

- **Uč sa z opráv.** Keď používateľ opraví výstup, zovšeobecni opravu na pravidlo alebo dvojicu pred a po a zapracuj ju do `vzorce.md` alebo `slova.md`.
- **Len vymyslené príklady.** Nikdy necituj zdrojový materiál doslova; každý vzorec postav znova s vymysleným obsahom. Dôverné vstupy do skillu nepatria, ani do histórie gitu.
- **Opora.** Nové pravidlo potrebuje oporu v slovenských dátach, v slovenskej kodifikácii alebo vo výskume nezávislom od jazyka (`references/zdroje.md`). České a anglické jazykové zistenia sú hypotéza: označ ich tak. Slovenské meranie, ktoré české číslo potvrdí alebo vyvráti, má prednosť.
- **Dva príklady na vzorec.** Každý nový vzorec prichádza s príkladom, ktorý má chytiť, a s podobným prípadom, ktorý má nechať tak.
- **Verzia a záznam.** Zvýš verziu (v `.claude-plugin/marketplace.json` na oboch miestach a v `plugins/unslop-sk/.claude-plugin/plugin.json`) a zapíš zmenu do `CHANGELOG.md`.
- **Len súbory potrebné za behu.** Do `plugins/unslop-sk/skills/unslop-sk` patria len súbory, ktoré skill potrebuje za behu; plugin sa používateľom kopíruje celý.

## Testy skriptov

```
python3 tests/test_metriky.py
python3 tests/test_diff.py
```

Testy potrebujú len štandardnú knižnicu Pythonu. Testy, ktoré vyžadujú model UDPipe, sa bez neho preskočia; cestu k modelu udáva premenná `UNSLOP_UDPIPE`. Modely ÚFAL majú licenciu CC BY-NC-SA 4.0, preto v repozitári nie sú.

## Regresné prípady

Prípady sú v `evals/pripady.md`. Runner ich spúšťa cez `claude -p`, takže beh stojí peniaze; `--zoznam` prípady len načíta a nič nevolá.

```
python3 tools/evaly/runner.py --zoznam
python3 tools/evaly/runner.py --pripady 1,6,13 --behy 1 --stitok skuska
python3 tools/evaly/runner.py --stitok <nazov> --porovnat tools/evaly/vysledky/<predchadzajuci>/behy.json
```

Čisté prípady musia zostať čisté; prehnané označovanie je tiež regresia. Prípady 31 až 34 (formát výstupu) hlavný runner preskakuje; púšťa ich `tools/evaly/format_vystupu.py` a hodnotia sa ručne. Výsledky sa ukladajú do `tools/evaly/vysledky/` a do gitu nepatria.

## Kalibrácia

Po zmene `references/slova.md` alebo prahov v skripte spusti kalibráciu na ľudských textoch (`tools/kalibracia/kalibracia_ud.py`; dáta UD Slovak-SNK v repozitári nie sú, postup je v hlavičke skriptu). Položka, ktorá dáva P1 vo viac než 5 % ľudských úsekov, ide o úroveň nižšie.
