# Tabuľka nálezov a kontrola prepisu

Podrobnosti k oddielu Formáty výstupu v `SKILL.md`. Tvar výstupu je pre používateľa vždy rovnaký: verdikt, tabuľka nálezov s pozíciou, pôvodným úsekom a návrhom, potom čistá verzia. Nástroje (Python, git, úprava súborov) menia len to, ako prepis overíš a kam ho zapíšeš.

## Pozícia

Pozícia sa musí dať nájsť bez hľadania.

- **Súbor:** číslo riadka ako odkaz `clanok.md:62`; v rozhraní, ktoré odkazy pozná, sa naň dá kliknúť. Pri kontrole ide o riadok originálu. Po úprave súboru uveď riadok v upravenom súbore, lebo tam používateľ zmenu otvorí. Úsek, ktorý zaberá viac riadkov, má rozpätie `clanok.md:62–64`.
- **Text v chate:** `¶odsek.veta`. Odseky počítaj od 1 podľa prázdnych riadkov; nadpis, položka zoznamu a riadok citácie sú samostatný odsek. Vety počítaj v rámci odseku. Výklad patrí do riadka legendy pod verdiktom: „¶3.2 = 3. odsek, 2. veta“. Zmena cez celý odsek má len `¶3`, cez dva odseky `¶3–4`.
- **Dlhý text s nadpismi** (nad zhruba 1000 slov): pred `¶` napíš názov oddielu a odseky počítaj od jeho nadpisu, nadpis sám sa nepočíta. „Meranie ¶2.1“ je prvá veta druhého odseku pod nadpisom Meranie. Nadpis ako miesto nálezu má len názov („Meranie, nadpis“). Text pred prvým nadpisom (perex) má „Úvod ¶1.1“. Legenda pod verdiktom potom znie „Meranie ¶2.1 = oddiel Meranie, 2. odsek, 1. veta“.
- **Vlastné číslovanie textu** má prednosť: paragrafy a odseky zákona či zmluvy („§ 4 ods. 2“), číslované body („bod 7“), čísla riadkov v básni alebo scenári.
- **Prezentácia:** „slajd 5, titulok“, „slajd 5, odrážka 3“, „slajd 5, poznámky“.

## Tabuľka

```markdown
| # | kde | P | pôvodne | návrh | prečo |
|---|---|---|---|---|---|
| 1 | ¶1.1 | P1 | Poďme sa ponoriť do sveta dátovej analytiky. | (zmazať) | šablónovitý úvod: veta nič nehovorí, „ponoriť sa do“ je kalk |
| 2 | ¶1.2 | P1 | …umožňujú tímom adresovať problémy na dennej báze. | …pomáhajú tímom riešiť problémy každý deň. | kalky: „adresovať problém“ a „na dennej báze“ |
```

- Riadky idú v poradí textu. Používateľ číta tabuľku súbežne s textom; závažnosť je v stĺpci P a v počtoch vo verdikte.
- **Pôvodne** kopíruj zo zdroja znak po znaku, aj s preklepmi a typografiou. Vezmi zmenený úsek a toľko slov okolia, aby bol v texte jednoznačný. Dlhší úsek skráť „…“ na začiatku alebo na konci, nikdy uprostred zmeny.
- **Návrh** je ten istý úsek po úprave a začína sa aj končí na rovnakom mieste ako „pôvodne“, aby sa dali porovnať očami. Zmazanie je „(zmazať)“. Chýbajúci fakt je `[OVERIŤ: čo chýba]` na mieste, kam patrí.
- **Prečo:** názov vzorca, dvojbodka a čím prekáža čitateľovi. Interné skratky (D6, úroveň 1) sem nepatria.
- Viac úprav v jednej vete je jeden riadok, inak sa poradie tabuľky rozpadne; v „prečo“ ich vymenuj. Jeden vzorec na viacerých miestach má riadok pre každé miesto; v „prečo“ môžeš napísať „ako [2]“.
- V bunkách nepíš `~~`, `**` ani `[-…-]`. Zvislú čiaru z textu zapíš ako `\|`, inak rozbije tabuľku.
- V kontrole je stĺpec „návrh“ ponuka: text sa nemení. Keď sa miesto nedá opraviť bez faktu, ktorý nemáš, napíš do návrhu len značku `[OVERIŤ: …]`.

**Veľké zmeny.** Zlúčenie viet, presun alebo prestavba odseku sa do bunky nezmestí. V tabuľke má riadok s pozíciou, závažnosťou a „pozri pod tabuľkou“ v stĺpcoch „pôvodne“ a „návrh“. Pod tabuľkou dostane blok:

```text
[3] ¶2 · P1 · rovnako stavané odseky · tri vety sa začínajú „Tento…“ a končia príveskom s „čo“
pred: (celé pôvodné vety zo zdroja, bez zmeny)
po: (nové znenie)
```

Zmazaná veta mimo tabuľky má „po: (zmazané)“, nová veta „pred: (nová)“. Nová veta smie vzniknúť len z obsahu zdroja (poistky).

## Iné chyby

Chyby, ktoré nie sú vzorcom AI (filter presnosti v `SKILL.md`), idú do vlastnej tabuľky pod tabuľkou nálezov. Používateľ tak hneď vidí, že nejde o AI nálezy:

```markdown
Iné chyby (nie sú znakom AI):

| kde | pôvodne | návrh | čo |
|---|---|---|---|
| ¶2.2 | …sa potom vrátil naspäť späť do kancelárie. | …sa potom vrátil do kancelárie. | zdvojený výraz: „naspäť“ a „späť“ hovoria to isté |
| ¶3.1 | V kľude sme to stihli do obeda. | Pokojne sme to stihli do obeda. | bohemizmus: „v kľude“ |
| ¶4.1 | Na porade sme sa stretli s kolegami s Košíc. | Na porade sme sa stretli s kolegami z Košíc. | predložka: „z Košíc“, nie „s Košíc“ |
```

- Bez čísla a bez P; do počtov vo verdikte, do riadka `SÚHRN` ani do Ponechaných nepatria.
- Pravidlá pre „kde“, „pôvodne“ a „návrh“ sú rovnaké ako v tabuľke nálezov. „Čo“ pomenuje chybu dvoma až šiestimi slovami.
- Najviac päť riadkov, najdôležitejšie chyby. Osobitne ich nehľadáš; zapíš, čo ti padlo do oka pri čítaní.
- Rozšírený bohemizmus, ktorý píšu aj ľudia („v kľude“, „doporučiť“, „vadí mi“), patrí sem. Česká stopa (slovo alebo tvar, ktorý slovenčina nemá) je nález v hlavnej tabuľke (`slova.md`, oddiel Bohemizmy).
- Pri prepise ich čistá verzia neopravuje: ľudský text zostáva drsný a opravu si autor vyberie sám.

## Zistenie nástrojov

Na nástroje sa používateľa nepýtaj. Zisti ich sám, bez komentára:

```sh
python3 --version   # keď python3 neexistuje (typicky Windows), použi python alebo py -3
git --version
[ "$(LC_ALL=C.UTF-8 locale charmap 2>/dev/null)" = UTF-8 ] && echo utf8
```

Neúspech ktoréhokoľvek kroku ticho znamená, že sa bez nástroja zaobídeš. Používateľovi to neoznamuj, okrem jednej vety o chýbajúcom riadku metrík.

## Kontrola prepisu skriptom

Tabuľka je pre používateľa, diff je pre teba: overí, že prepis nezmenil nič, čo v tabuľke nie je, a že nič ticho nezmizlo. Oba texty ulož do súborov v pracovnom adresári.

**Python (predvolené).** `scripts/diff.py` rozdelí oba texty na vety, vynechá kód a citácie, vypíše slovný diff zmenených viet a stráži tichú stratu (čísla, mená, častice a istenie, markery sily tvrdenia). Od locale nezávisí:

```sh
python3 <adresár skillu>/scripts/diff.py pred.txt po.txt --metriky --profil blog
```

Výstup má tri časti: blok diffu s očíslovanými zmenenými vetami (`[-zmazané-]` a `{+pridané+}`), oddiel `**Tichá strata**` a riadok `Metriky pred → po: …`:

```text
[1] Firma[- Kovo-] ušetrila [-asi 12 %-]{+veľa+}.

**Tichá strata**

- čísla: 12
- mená: Kovo
- častice a istenie: asi
- mená sú bez modelu približné, over ich v diffe
- info, sila tvrdenia: ubudlo spôsobuje (over, že zmena nie je oslabenie)

Metriky pred → po: častice 3,1 → 3,1 · istenie 4 → 2 · otázky 0 → 0 · čísla 18 → 12 · mená 30 → 28
```

- Každá zmenená veta z diffu musí mať riadok v tabuľke. Zmenu bez riadka vráť, alebo ju do tabuľky doplň s dôvodom.
- Čo skript hlási ako tichú stratu (riadky „čísla“, „mená“, „častice a istenie“), vráť do novej verzie, alebo to zapíš do tabuľky ako vedomý škrt s dôvodom. Hlásenie mien je bez modelu približné, over ho v diffe. Riadok „info, sila tvrdenia“ je len upozornenie: over, že zmena tvrdenie neoslabila. Keď nič nechýba, oddiel hovorí „Nič nechýba: čísla, mená, častice ani istenie.“
- Do odpovede prenes bez zmeny oddiel Tichá strata (len keď niečo hlási) a riadok metrík. Blok diffu do odpovede nedávaj, iba ak oň používateľ požiada; tabuľka hovorí to isté čitateľnejšie.
- `--format json` dá rovnaké dáta strojovo (kľúče `zmeny`, `straty`, `metriky`), `--prisne` vráti kód 1 pri strate. Prepínač `--metriky` spustí `metriky.py` na oba texty; samostatný beh `metriky.py` na novú verziu preto nespúšťaj.

**Git** (len bez Pythonu). Rozdeľ oba texty na jednu vetu na riadok, odsek je inak pre diff jeden dlhý riadok. Regex drží pohromade slová s diakritikou a čísla s desatinnou čiarkou:

```sh
LC_ALL=C.UTF-8 git diff --no-index --word-diff=plain \
  --word-diff-regex='[[:alnum:]]+([.,][[:digit:]]+)*|[^[:space:]]' \
  pred.txt po.txt | tail -n +6
```

`LC_ALL=C.UTF-8` je povinné. V locale `C` regex delí UTF-8 po bajtoch a výstup poškodí (`Ob�[-� pos-]`). Stratu čísel a mien git nestráži, prejdi ju v diffe ručne. Riadok metrík bez Pythonu chýba; povedz to jednou vetou.

**Bez shellu** porovnaj tabuľku s čistou verziou sám: každý rozdiel medzi zdrojom a čistou verziou má riadok v tabuľke, čísla a mená zo zdroja sú v čistej verzii.

## Úprava súboru

Prepis urob ako úpravu kópie súboru (napríklad `text.unslop.md` vedľa originálu), v režime Úprava súboru priamo v súbore. Diff ukáže rozhranie agenta, preto ho do odpovede neprepisuj. Tabuľka zmien má pozície `súbor:riadok` v upravenom súbore; čistá verzia je súbor sám, v odpovedi stačí cesta.

## Ponuka opráv

Kontrola aj prepis sa končia jednou otázkou, ako opravy dostať do zdroja. Ponuka chýba pri čistom texte bez iných chýb, pri volaní z iného skillu, v režime Písanie a pri prepise textu vloženého do chatu, kde je výstupom čistá verzia sama.

**Cieľ podľa zdroja.** Zisti ho z toho, odkiaľ text prišiel, nie otázkou:

| zdroj | ponuka | ako zapíšeš |
|---|---|---|
| lokálny súbor | „opraviť v súbore“, alebo „do kópie `text.unslop.md`“ | úprava súboru po úsekoch (oddiel Úprava súboru) |
| artefakt claude.ai alebo Claude Doc, kam má používateľ zápis | „opraviť v artefakte“ | nástroj toho úložiska, nová verzia na rovnakom odkaze |
| dokument cez konektor (Google Docs, Confluence, Notion) | „opraviť v dokumente“ | nástroj konektora; keď vie návrhy alebo komentáre, zapíš zmeny ako návrhy |
| .docx | „sledované zmeny v kópii“ | sledované zmeny, dôvod ako komentár |
| webová stránka, PDF, text v chate | „čistá verzia na skopírovanie“ | čistá verzia a zoznam „pred → po“ v poradí textu na ručný prenos do redakčného systému |

Keď nástroj na zápis chýba alebo používateľ do zdroja zapisovať nesmie (cudzí artefakt len na čítanie, publikovaný článok), ponúkni posledný riadok tabuľky a jednou vetou povedz prečo.

**Rozsah.** Ponúkni voľbu: všetky nálezy, len P0 a P1, alebo vybrané čísla riadkov. Iné chyby ponúkni osobitne („aj iné chyby“), lebo nie sú znakom AI a autor si ich vyberá sám. V používateľskom rozhraní s tlačidlami daj odporúčanú voľbu ako prvú, inak jednu vetu:

```text
Mám opravy zapísať do súboru clanok.md? Môžem všetky (3), len P0 a P1 (1), alebo len vybrané čísla; iné chyby (2) len na želanie.
```

**Po súhlase.**
1. Zapíš len vybrané riadky, každý presne podľa stĺpca „návrh“. Nič ďalšie nemeň, ani susedné slovo; nová úprava by potrebovala nový riadok tabuľky a nový súhlas.
2. Riadok so značkou `[OVERIŤ: …]` do zdroja nezapisuj. Opýtaj sa na chýbajúci fakt, alebo riadok vynechaj a povedz to. Riadok „(zmazať)“ zmaž celý, aj s medzerou navyše.
3. Pri úložisku s verziami (artefakt, dokument) najprv načítaj aktuálnu verziu. Keď sa od kontrolovanej líši, zapíš len riadky, ktorých „pôvodne“ v nej nájdeš bez zmeny, a ostatné vymenuj.
4. Zdroj znova prečítaj. Keď máš shell, ulož starú a novú verziu a spusti `diff.py --metriky`: každá zmena z diffu musí mať vybraný riadok a tichá strata musí byť prázdna.
5. Ohlás tabuľku vykonaných zmien s pozíciami v novej verzii (`súbor:riadok`, pri artefakte `¶`), riadok metrík a čo si vynechal a prečo.

Zápis do zdieľaného alebo publikovaného miesta vidia ostatní, preto bez súhlasu nezapisuj nikdy, ani keď používateľ na začiatku povedal len „skontroluj“. Súhlas platí pre tento zápis, nie pre ďalšie.

## Revízna stránka a sledované zmeny

Len keď o ne zadávateľ požiada. Revízna stránka (artefakt) ukáže tabuľku s dvoma stĺpcami vedľa seba, zmenené slová zvýrazní a pozíciu odkáže na miesto v plnom texte. Súbor .docx dostane zmeny ako sledované zmeny a dôvod ako komentár. Obsah sa nemení: čísla zmien, pozície, metriky aj zoznam `[OVERIŤ: …]` zostávajú.

## Riadok metrík

```text
Metriky pred → po: častice 6,1 → 6,1 · istenie 4,0 → 2,0 · otázky 0 → 0 · čísla 18 → 12 · mená 30 → 30
```

Častice, istenie, čísla a mená sú počty na 1000 slov, otázky na 100 viet. Pokles čísel, mien, častíc alebo istenia je varovanie: vráť sa do diffu a nájdi, kde zmizli. Keď pokles zodpovedá vedomej zmene (zmazaná vágna autorita), napíš to za riadok jednou vetou. Pri úprave súboru spusti `diff.py --metriky` na zdroj a kópiu a prevezmi len riadok.

## Ukážka prepisu (text v chate, bez shellu)

VSTUP (profil blog):

> Poďme sa ponoriť do sveta dátovej analytiky. Moderné nástroje umožňujú tímom adresovať problémy na dennej báze. Odborníci sa zhodujú, že firmy, ktoré investujú do dát, sú úspešnejšie.

VÝSTUP:

Krátky odsek s chatbotím úvodom, kalkami a vágnou autoritou: P0 1, P1 2, P2 0.

P = priorita úpravy: P0 ničí dôveru, P1 zreteľný AI tik, P2 drobnosť; ¶1.2 = 1. odsek, 2. veta.

| # | kde | P | pôvodne | návrh | prečo |
|---|---|---|---|---|---|
| 1 | ¶1.1 | P1 | Poďme sa ponoriť do sveta dátovej analytiky. | (zmazať) | šablónovitý úvod: veta nič nehovorí, „ponoriť sa do“ je kalk |
| 2 | ¶1.2 | P1 | …umožňujú tímom adresovať problémy na dennej báze. | …pomáhajú tímom riešiť problémy každý deň. | kalky: „adresovať problém“ a „na dennej báze“ |
| 3 | ¶1.3 | P0 | Odborníci sa zhodujú, že firmy… | `[OVERIŤ: kto to tvrdí a o aké dáta sa opiera]` Firmy… | vágna autorita: „odborníci“ bez mena a zdroja |

- `[OVERIŤ: kto to tvrdí a o aké dáta sa opiera]`

Ponechané: „Moderné nástroje“ je všeobecné, ale bez zvyšku článku sa nedá spresniť.

Riadok metrík chýba, skript nebežal (text má tri vety a agent nemá shell).

Čistá verzia:

> Moderné nástroje pomáhajú tímom riešiť problémy každý deň. [OVERIŤ: kto to tvrdí a o aké dáta sa opiera] Firmy, ktoré investujú do dát, sú úspešnejšie.

Druhý prechod nič nenašiel, preto sa nepíše. Oddiel bez obsahu sa nepíše vôbec.

## Volanie z iného skillu

Nepýtaj sa nikdy, ani na cieľ. Volajúci dostane opravený text a pod ním zoznam zmien bez tabuľky, lebo ho volajúci skill ďalej spracúva a tabuľku by musel rozoberať:

```text
[1] ¶1.2 · P1 · kalky · „adresovať problém“ a „na dennej báze“
pred: Moderné nástroje umožňujú tímom adresovať problémy na dennej báze.
po: Moderné nástroje pomáhajú tímom riešiť problémy každý deň.
```

Značky `[OVERIŤ: …]` idú len do zoznamu pod textom, text zostáva bez nich. V režime Písanie, kde nijaký zdroj nie je, dostane volajúci len text a zoznam Neoverené údaje.
