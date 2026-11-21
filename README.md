# unslop-sk

Redaktor pre slovenské texty písané s pomocou AI. Nájde miesta, ktoré znejú ako AI, opraví ich a nič si pritom nevymyslí. Ľudský text nechá tak.

Skill pre Claude a ďalších agentov, ktorí čítajú formát `SKILL.md` (Claude Code, Claude Desktop, Claude.ai, Cursor, Codex).

Inšpirované repozitárom [PetrHula/unslop-cs](https://github.com/PetrHula/unslop-cs), z ktorého je táto slovenská verzia adaptovaná.

*English: an editor for Slovak prose written with AI. Flags and fixes AI tells at the word, rhythm and structure levels, leaves human text alone, never invents facts. Slovak-language instructions.*

## Inštalácia

**Claude Code (plugin):**

```
/plugin marketplace add MarekTran/unslop-sk
/plugin install unslop-sk@unslop-sk
```

**Ručne (Claude Code, Cursor, Codex):** skopírujte priečinok [`plugins/unslop-sk/skills/unslop-sk`](plugins/unslop-sk/skills/unslop-sk) do adresára so skillmi, v Claude Code `~/.claude/skills/unslop-sk`.

**Claude.ai a Claude Desktop:** zabaľte ten istý priečinok do súboru .zip a nahrajte ho v nastaveniach v časti Skills.

## Použitie

Skill sa spúšťa na požiadanie, nie pri každom písaní. Stačí napísať napríklad „skontroluj, či to neznie ako AI“ alebo „prepíš to ľudsky“ a vložiť text.

- **Kontrola** – tabuľka nálezov: kde v texte sú (riadok súboru, alebo odsek a veta), pôvodné znenie, návrh úpravy, priorita P0 – P2 a dôvod. Text nemení.
- **Prepis** – rovnaká tabuľka zmien a pod ňou opravená verzia.
- **Zápis opráv** – kontrola aj prepis sa končia ponukou, kam opravy zapísať. Bez súhlasu skill nič nezapíše.
- **Úprava súboru** – opraví text priamo v súbore, s čo najmenšími zásahmi.
- **Písanie** – iný skill (napríklad na e-maily alebo články) ho môže požiadať, aby jeho pravidlá uplatňoval potichu pri písaní.

Prísnosť sa riadi registrom: čo prekáža v odbornom texte, môže byť v poriadku na LinkedIne. Podporované profily sú sociálne siete, blog a článok, e-mail, dokumentácia, odborný text a prezentácia.

## Čo hľadá

Od najsilnejších vzorcov. Body 1 – 8 sú nálezom aj raz, slabé signály až v zhluku.

1. **Zvyšky chatu a vymyslené autority:** „Dúfam, že vám to pomôže!“, nevyplnené „[meno]“, „odborníci sa zhodujú“ bez zdroja.
2. **Tvrdenie bez faktu:** „výrazne zrýchľuje“, „používatelia ju milujú“ bez čísla, mena alebo mechanizmu.
3. **Pointa ako maxima:** „Nástroje sa menia. Remeslo zostáva.“
4. **Šablónovitý úvod a záver:** „V dnešnej dobe…“, zhrnutie na konci, výhľad namiesto výsledku.
5. **Text, ktorý vykladá sám seba:** „Ako vidno…“, „Čo väčšina ľudí prehliada:“.
6. **Vysvetlené rozprávanie:** „…a vtedy mi došlo, že nikdy nešlo o…“, epilóg po prirodzenom konci.
7. **Kontrastné obraty a trojice zo zvyku:** „nejde o X, ide o Y“, tri prídavné mená za sebou.
8. **Česká stopa:** „pokud“, „protože“, „který“ a písmená ě, ř, ů v slovenskom texte.
9. **Slovenská skladba a slová:** anglický slovosled, kalky (*adresovať problém, na dennej báze*), nafúknutý slovník (*kľúčový, robustný*), „—“ namiesto „–“.
10. **Slabé signály:** jedna pomlčka, jedno istenie, rovné úvodzovky, jeden hovorový bohemizmus („v kľude“).

Citácie, kód, tabuľky a text tretích strán neprepisuje. Chýbajúce číslo, meno alebo zdroj nedoplní, ale označí značkou `[OVERIŤ: …]`. Úplné výpočty s príkladmi sú v [`references/vzorce.md`](plugins/unslop-sk/skills/unslop-sk/references/vzorce.md) a [`references/slova.md`](plugins/unslop-sk/skills/unslop-sk/references/slova.md).

## Stav overenia

Pravidlá a čísla českého originálu stoja na českých dátach. Na slovenčine ich nikto nemeral: slovenské zoznamy slov sú preklad a oddiel o bohemizmoch vychádza z praxe. Benchmark českého skillu pre túto verziu neplatí. Čo je na slovenských textoch naozaj overené a čo nie, je v [`references/zdroje.md`](plugins/unslop-sk/skills/unslop-sk/references/zdroje.md) a v [CHANGELOG.md](CHANGELOG.md).

## Pre vývojárov

```
.claude-plugin/marketplace.json   katalóg pluginu
plugins/unslop-sk/                plugin; používateľ dostane len tento priečinok
└── skills/unslop-sk/             SKILL.md, references/, scripts/ (metriky.py, diff.py)
evals/pripady.md                  regresné prípady
tests/                            testy skriptov
tools/evaly/                      runner regresných prípadov (claude -p)
tools/kalibracia/                 kalibrácia prahov na UD Slovak-SNK (bez dát)
```

Postup úprav a testovania opisuje [CONTRIBUTING.md](CONTRIBUTING.md).

## Licencia

MIT, pozri [LICENSE](LICENSE).
