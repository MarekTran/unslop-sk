# Zdroje: o čo sa pravidlá opierajú

Skill rieši slovenčinu, ale žiadne z jeho pravidiel nie je merané na slovenčine. Je to adaptácia českého skillu [PetrHula/unslop-cs](https://github.com/PetrHula/unslop-cs), ktorého pravidlá stoja na českých dátach. Každý zdroj tu má preto štítok: merané na češtine (**CZ**), slovenská norma (**norma SK**), zistenie nezávislé od jazyka (**nezávislé**), alebo prax bez merania (**prax**).

Čo z toho vyplýva:

- Čísla „AI / ľudia“ v skille sú české. Slovenčina je češtine štruktúrne blízka a modely sa obe učia podobne, preto ich berieme ako východiskovú hypotézu. Ak ich slovenské dáta vyvrátia, pravidlo treba zmeniť.
- Slovenské ekvivalenty v `slova.md` sú preklad českého zoznamu, nie výsledok porovnania korpusov. Slovo, ktoré je v češtine typické pre AI, v slovenčine také byť nemusí.
- Oddiel Bohemizmy je slovenský prídavok z praxe. Nikto nezmeral, ako často AI v slovenčine píše české slová v porovnaní s ľuďmi.
- Benchmark českého skillu (podiel ľudských textov s nálezom a podobne) pre túto slovenskú verziu neplatí. Nebola testovaná na ľudských ani AI textoch a regresné prípady z `evals/` zatiaľ nebežali.

Architektúra českého skillu vychádza z jlwin/unslop_ai, české vzorce z nowork-ai/anti-ai-slop-cz a bejek/humanizer-czech. Zoznam bohemizmov a anglicizmov sme porovnali s kuzmany/slovak-humanizer.

## Dimenzie štýlu (merané na češtine)

Pravidlá odkazujú na dimenzie multidimenzionálneho modelu češtiny (Cvrček a kol. 2018, 2020). Benchmark AI-Koditex ukázal, ktorým smerom sa od ľudí odchyľuje česká AI:

| Dimenzia | Posun AI v češtine | Čo to znamená pre skill |
|---|---|---|
| D1 dynamický / statický, D2 spontánny / pripravený | bez konzistentného smeru | rytmus a „uhladenosť“ nemajú oporu v dátach; vnútená hovorovosť je chyba |
| D3 súdržnosť | AI viac | reťaze „ktorý“, korelatíva, „svoj“, začiatky „Tento…“ (Hustá sieť odkazov) |
| D4 jedna téma / viac tém | AI monotematickejšia | odbočky nemazať, slovník plošne neochudobňovať |
| D5 oslovenie adresáta | AI menej | otázky a oslovenia zo zdroja zostávajú |
| D6 všeobecnosť / konkrétnosť | AI všeobecnejšia | univerzálne pravidlo, test prenosnosti, nafúknutý slovník |
| D7 výhľad / obzretie | AI viac výhľadu | Výhľad namiesto výsledku, šablónovité závery |
| D8 postoj / faktuálnosť | AI menej postoja | častice a istenie nemazať, zosilňovače nie sú nález |

## Merané na češtine (CZ)

- **Milička, Marklová, Cvrček: Benchmark of stylistic variation in LLM-generated texts.** arXiv 2509.10179. Korpus AI-Koditex: modely dopisovali písané texty z Koditexu. Zdroj posunov v tabuľke vyššie. Obmedzenie: pokračovanie textu, nie odpovede chatbota; chatbotie frázy, formát odpovedí, e-maily a LinkedIn v ňom nie sú.
- **AI-Koditex v2** (LINDAT, http://hdl.handle.net/11234/1-6189; opis arXiv 2509.22996) a **Koditex** v KonTexte. Z nich je porovnanie slov a gramatických čŕt, z ktorého vychádzajú úrovne v českom `slova.md` a čísla „AI / ľudia“: 25 inštruovaných modelov z rokov 2023 – 2026, rovnakých 150 textov, ľudská referencia 5,08 mil. slov. Porovnanie urobil autor unslop-cs; skripty sú v jeho repozitári v priečinku `tools/koditex/`.
- **Cvrček a kol. (2018, 2020): multidimenzionálna analýza češtiny.** Osem dimenzií štýlu, na ktorých stojí uvedený benchmark. https://korpus.cz/mda
- **Milička, Marklová, Drobil, Pospíšilová: Humans can learn to detect AI-generated texts, or at least learn when they can't.** arXiv 2505.01877. 255 rodených hovoriacich, české texty, GPT-4o. Bez spätnej väzby určili správne 55 % textov, so spätnou väzbou 65 %. Vodidlá „čítavý text je ľudský“ a „AI je statická a pripravená“ klamali. Platné vodidlo bola všeobecnosť namiesto konkrétneho údaja. Opora pre univerzálne pravidlo, pre zásadu „posudzuj vzorce, nie autorstvo“ a pre poistku „oprava nepridáva chyby“.

## Norma (SK)

Typografické a pravopisné pravidlá skillu sa opierajú o slovenskú kodifikáciu:

- **Pravidlá slovenského pravopisu** (JÚĽŠ SAV) a **Krátky slovník slovenského jazyka**, oba dostupné na https://slovniky.juls.savba.sk/.
- **STN 01 6910:2011, Pravidlá písania a úpravy písomností**: písanie dátumu, času, čísel, značiek, percent a pomlčky v rozsahoch.
- **Jazyková poradňa JÚĽŠ SAV**, https://jazykovaporadna.sme.sk/: posudzovanie bohemizmov a kalkov.

Norma hovorí, čo je chyba; či je chyba zároveň signálom AI, je iná otázka (dlhú pomlčku „—“ v slovenčine nikto nezmeral). Niektoré výrazy zo zoznamu bohemizmov slovníky uvádzajú ako hovorové alebo subštandardné, nie ako chybné; preto sú samy osebe slabým signálom.

## Nezávislé od jazyka

- **Shaib, Chakrabarty, Garcia-Olano, Wallace: Measuring AI „Slop“ in Text.** arXiv 2509.19163. Taxonómia slopu: užitočnosť informácie (hustota, relevancia), kvalita informácie (fakty, zaujatosť), štýl. Opora pre oddiel Obsah, pre značku `[OVERIŤ]` a pre rozlíšenie registrov. Merané na angličtine; prenáša sa kategória, nie čísla.
- **Chakrabarty, Laban, Wu: Can AI writing be salvaged?** arXiv 2409.14509. Korpus LAMP: 1 057 anglických odsekov, 8 035 úprav od 18 spisovateľov. Kategórie úprav s podielom: voľba slov 28 %, stavba vety 20 %, zbytočný výklad 18 %, klišé 17 %. Úpravy od spisovateľov text zlepšili viac než úpravy od modelu. Prenáša sa metóda a obsahové kategórie, nie anglické slová.
- **Russell a kol.: StoryScope.** arXiv 2604.03136. 61 608 poviedok, beletria. Opora len pre štruktúru rozprávania (oddiel Rozprávanie), nie pre pracovné texty.

## Kalibrácia skriptu

Prahy `scripts/metriky.py` sú prevzaté z českého skriptu, kde obmedzujú falošné poplachy na ľudských textoch z UD Czech-CAC a UD Czech-FicTree. Slovenský náprotivok je UD Slovak-SNK (licencia CC BY-SA 4.0); kalibračný skript je v repozitári https://github.com/MarekTran/unslop-sk v priečinku `tools/kalibracia/`, dáta do repozitára nepatria. Čo sa na slovenských dátach naozaj zmeralo, je zapísané v `CHANGELOG.md` v repozitári. Citlivosť na AI text prahy nemerajú.
