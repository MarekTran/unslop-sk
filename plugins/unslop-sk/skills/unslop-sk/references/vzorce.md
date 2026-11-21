# Pravidlá a vzorce: pred a po

Podrobné pravidlá úrovní 1 – 3 a registrov. Pri každom vzorci je pravidlo, príklad PRED a PO a podobný prípad, ktorý zostáva (PONECHAŤ). Jadro skillu, režimy, závažnosť, poistky a sebakontrola sú v `../SKILL.md`, zoznamy slov s prahmi a typografia v `slova.md`, opora pravidiel v `zdroje.md`.

Obsah príkladov je vymyslený. Skutočné miesta a inštitúcie slúžia len ako kulisa a tvrdenia o nich nie sú skutočné. Každá verzia PO obsahuje len informácie z verzie PRED; čo chýba, označuje značka `[OVERIŤ: …]`. Pri vzorcoch, ktoré stoja na meraní, je opora v `zdroje.md`. Čísla „AI / ľudia“ sú z porovnania AI-Koditexu s ľudskými textami a sú merané na češtine (D3 až D8 sú dimenzie štýlu češtiny podľa Cvrčka a kol.); pre slovenčinu ich preberáme ako hypotézu, nikto ich na nej nemeral.

## Obsah

- **Úroveň 1: slová a typografia** – nafúknutý slovník a význam, reklamný jazyk, kalky a falošní priatelia, bohemizmy, chatbotie artefakty, typografia a mikroformáty
- **Úroveň 2: veta a rytmus** – rytmus a reťaz krátkych viet, kontrastný obrat, trojica, prívesky s „čo“ a „čím“, opisy pre „je“ a „má“, vrstvené istenie, synonymický kolotoč, falošný agens, dvojbodkové odhalenie a otázka s odpoveďou, inscenovaný dôraz, heslovitá kadencia, opakovaný obrat, tautologické zdvojenia
- **Slovenská skladba** – nová informácia na koniec, príklonky, nadbytočné zámená, ukazovacie zámená ako rituál, slovesá a aktér, slovo, ktoré by si povedal nahlas, jedna myšlienka na vetu, hustá sieť odkazov
- **Úroveň 3: obsah** – relevancia, čitateľova ďalšia otázka, pomenované namiesto vágnych odkazov, test prenosnosti, výhľad namiesto výsledku
- **Úroveň 3: stavba** – pointa raz, rovnako stavané odseky, nadpisy, šablónovité úvody a závery, falošné precitnutie a mravoučná pointa, okrídlené metafory o AI, metakomentár a text o sebe, ohlásenie, rekapitulácia a šablónovitá vyváženosť, fantómové námietky, počítané zoznamy, odpoveď, ktorá stavia kontext nanovo, formát podľa obsahu
- **Úroveň 3: rozprávanie** – príbehy, historky, prípadové štúdie, emócie
- **Registre** – register prezentácií, odborný text
- **Poistky v príkladoch** – význam v rovnakej sile, postoj a konkrétnosť, oprava bez nových chýb
- **Výpočty tvarov podľa závažnosti** – úplné výpočty P1 a P2

## Úroveň 1: slová a typografia

Najslabší, ale najviditeľnejší signál. Zoznamy slov, kalkov, bohemizmov, ustálených fráz a typografických konvencií s prahmi sú v `slova.md`.

### Nafúknutý slovník a nafúknutý význam

*kľúčový, fascinujúci, udržateľný, inovatívny, komplexný, aspekt, výzva, posunúť na ďalšiu úroveň, zohrávať kľúčovú úlohu, neoddeliteľná súčasť.* Podľa úrovne v `slova.md` ich nahraď, alebo ich označ až v zhluku. Úrovne vychádzajú z porovnania českých AI a ľudských textov (AI-Koditex); zosilňovače ako „veľmi“, „úplne“, „naozaj“ AI v českých dátach nepreháňa a samy nálezom nie sú.

- PRED: „Otvorenie novej pobočky knižnice v Rači predstavuje významný míľnik, ktorý otvára nové obzory pre celú komunitu.“
- PO: „V Rači otvorili novú pobočku knižnice.“ `[OVERIŤ: čo pobočka obyvateľom prináša]`
- PONECHAŤ: „Zákon po prvý raz zaviedol povinné poistenie zodpovednosti.“ Veta tvrdí overiteľnú zmenu.

Test: keď po zmazaní vety o význame zostane veta, ktorá stále funguje, bola to vata.

### Reklamný jazyk

- PRED: „Naša revolučná platforma prináša komplexné riešenie s unikátnou pridanou hodnotou.“
- PO: Bez podloženého prepisu. `[OVERIŤ: čo platforma robí, pre koho a čím sa líši od konkurencie]`
- PONECHAŤ (sociálne siete, trocha predaja je v poriadku): „Nová kolekcia je vonku. Mrknite do e-shopu.“

### Kalky a falošní priatelia

*adresovať problém, na dennej báze, na konci dňa, realizovať si (= uvedomiť si), eventuálne (= napokon).* Falošný priateľ, ktorý mení význam, a celá kalkovaná fráza, ktorá po slovensky znie cudzo („dúfam, že vás e-mail zastihne v poriadku“), sú P1, ostatné kalky P2. V pokračovaniach českých textov z AI-Koditexu sa kalky ako signál AI nepotvrdili; sleduj ich hlavne v odpovediach chatbota a v marketingu, kde model prekladá z angličtiny.

- PRED: „Musíme adresovať tento problém na týždennej báze.“ → PO: „Musíme tento problém riešiť každý týždeň.“
- PRED: „Až neskôr som si zrealizoval, že server beží na starom disku.“ → PO: „Až neskôr som si uvedomil, že server beží na starom disku.“
- PRED: „Dlho sme váhali, ale eventuálne sme systém vymenili.“ → PO: „Dlho sme váhali, ale napokon sme systém vymenili.“
- PONECHAŤ: „Projekt sa podarilo realizovať do konca roka.“ (realizovať = uskutočniť), „Pošlite fotku, eventuálne sken.“ (eventuálne = prípadne), „Tá veta nedáva zmysel.“, „Zdieľam váš názor.“

### Bohemizmy

Slovenský oddiel, zoznamy sú v `slova.md`, oddiel Bohemizmy. Modely majú českých textov viac než slovenských a do slovenčiny im presakuje čeština. Opora je prax a kodifikačné príručky, meranie neexistuje.

**Česká stopa** je slovo alebo tvar, ktorý slovenčina nemá (*pokud, protože, který, když, není, jsou*), a písmená ě, ř, ů v slove, ktoré nie je meno, názov ani citát. Slovák ich v slovenskom texte nenapíše ani hovorovo, preto sú P1 aj raz.

**Rozšírené bohemizmy** (*kľud, doporučiť, jedná sa o, behom, naviac, vzhľadom k*) píšu aj ľudia, hovorovo veľmi často. Samy osebe sú slabé a patria do tabuľky Iné chyby (nie sú znakom AI), nie medzi nálezy. Nálezom P2 sú až v zhluku troch a viac v texte, ktorý má byť spisovný.

- PRED: „Pokud sa rozhodnete pre ročné predplatné, ušetríte dva mesiace.“ → PO: „Ak sa rozhodnete pre ročné predplatné, ušetríte dva mesiace.“ („pokud“ je česká stopa, P1 aj raz)
- PRED (tlačová správa): „Jedná sa o dielčí výsledok. Doporučujeme zachovať kľud a behom týždňa vydáme ďalšie informácie.“ → PO: „Ide o čiastkový výsledok. Odporúčame zachovať pokoj a počas týždňa vydáme ďalšie informácie.“ (zhluk štyroch bohemizmov v spisovnom texte, P2)
- PONECHAŤ: „Zmluvu podpísal Jiří Dvořák z brnianskej pobočky.“ (české meno), „Na dverách viselo: ‚Zavřeno z technických důvodů.‘“ (citovaný český text), „V kľude, stihneme to.“ (zámerne hovorová správa kolegovi; jeden rozšírený bohemizmus nálezom nie je).

### Chatbotie artefakty

Zoznam je v `slova.md` (P0).

- PRED: „Skvelá otázka! Rád vám pripravím prehľad. Tu je zoznam postupov. Dúfam, že vám to pomôže!“
- PO: len samotný prehľad.
- PONECHAŤ: „Dobrý deň, posielam zmluvu na podpis. S pozdravom Jana Malá“ Bežné e-mailové oslovenie a rozlúčka nie sú chatbotie artefakty.

### Typografia a mikroformáty

Pravidlá (pomlčka a rozpočet pomlčiek, úvodzovky, desatinná čiarka, rády, percentá, mena, dátum, čas, nadpisy, tykanie a vykanie) sú v tabuľke v `slova.md`. Typografia je norma: chyba bez ohľadu na to, kto text písal. Dlhá pomlčka ako signál AI v slovenčine zmeraná nie je, v praxi však patrí k najviditeľnejším.

- PRED: „Nová funkcia—dlho očakávaná—je konečne tu.“ → PO: „Nová funkcia je konečne tu. Čakalo sa na ňu dlho.“ V texte na publikovanie, kde inak pomlčky nie sú, prejde aj „Nová funkcia – dlho očakávaná – je konečne tu.“
- PRED: „Zľava 25% platí do 5/4/2026.“ → PO: „Zľava 25 % platí do `[OVERIŤ: 4. 5. 2026, alebo 5. 4. 2026?]`.“
- PRED (e-shop): „Všetky ceny sú uvedené v EUR.“ → PO: „Všetky ceny sú uvedené v eurách.“ EUR je bankový kód meny; v bežnom texte o sumách sa píše „€“ alebo „eur“ (P2).
- PRED: „Strategické Priority Na Rok 2027“ → PO: „Strategické priority na rok 2027“ (anglický title case, P1)
- PRED: „Vyplňte formulár a odošlite ho. Potom ti príde potvrdenie.“ → PO: „Vyplňte formulár a odošlite ho. Potom vám príde potvrdenie.“ (zjednotené podľa prevažujúcej formy; keď žiadna neprevažuje, opýtaj sa)
- PONECHAŤ: „25-percentná zľava na všetko“ (prídavné meno), „Ahoj, posielam to - keby niečo, napíš“ (spojovník v chate), „Suma 12 500 EUR bude odpísaná z účtu SK31 1200 …“ (bankový kontext, kód meny je tu na mieste).

## Úroveň 2: veta a rytmus

### Rytmus a reťaz krátkych viet

**Rytmus.** Hľadaj tri po sebe idúce vety podobnej dĺžky a rovnakej stavby. Dĺžka sama je len indícia. Česká AI píše skôr dlhšie súvetia než ľudia, nie útržky (orientačné meranie na češtine); v súvislom texte preto sleduj hlavne dlhé súvetia s reťazou „ktorý“ (Hustá sieť odkazov). Striedaj krátke vety (3 – 8 slov) s dlhými (25 a viac), kde to obsah dovolí. Nikdy nenaťahuj ani nesekaj čistú pasáž pre kvótu.

**Pasca reťaze krátkych viet.** Rad krátkych hlavných viet („Krátka veta. Ďalšia. A ešte jedna.“) je sám AI tik. Spájaj myšlienky spojkami, vedľajšími vetami, bodkočiarkou alebo dvojbodkou, aby príčina a protiklad žili v skladbe. Jeden zámerný útržok je v poriadku, tri rovnaké za sebou už tvoria vzorec (P2). Jednoslovné vety pre drámu („Brutálne.“ „Bodka.“) patria sem.

- PRED: „Tím chcel rýchlejšie výsledky. Nasadil nový nástroj. Práca sa zrýchlila. Všetci boli spokojní.“
- PO: „Tím chcel rýchlejšie výsledky, a tak nasadil nový nástroj. Práca sa zrýchlila a všetci boli spokojní.“ `[OVERIŤ: o koľko sa práca zrýchlila]`
- PRED: štyri vety po osemnástich slovách, každá v tvare podmet – prísudok – predmet.
- PO: dve súvisiace vety spoj do súvetia, jednu nechaj krátku. Obsah bez zmeny.
- PONECHAŤ: „Hotovo. Teraz môžeš súbor zavrieť.“ Jeden zámerný útržok.

### Kontrastný obrat

„Nejde o X, ide o Y“, „Nie je to X, je to Y“, „nielen X, ale aj Y“ ako rečnícka figúra, aj rozdelené do dvoch viet, s nahromadenými zápormi pred odhalením („Nejde o nástroje. Nejde o procesy. Ide o ľudí.“) a v skrátenej podobe „A namiesto B“ („Dialóg namiesto prednášky“). Ako rečnícka figúra je nálezom P1 aj raz za text. Obvykle stačí kladná veta, pretože alternatívu vylučuje sama. Zostávajú tri podobné prípady: pokyn, ktorý opravuje, opravené číslo a tvrdenie o pravosti.

- PRED: „Nejde o softvér. Nejde o procesy. Ide o ľudí.“
- PO: Bez podloženého prepisu. `[OVERIŤ: čo konkrétne sa má pri ľuďoch zmeniť]`
- PRED: „Kurz nie je len o varení, ale aj o spoločnej večeri, pri ktorej účastníci zjedia, čo uvarili.“
- PO: „Na konci kurzu účastníci spoločne zjedia, čo uvarili.“
- PRED (slajd, kde nikto prednášku nenavrhoval): „Workshop namiesto prednášky“
- PO: „Formát: workshop“
- PONECHAŤ: „Pošli faktúru za marec, nie za apríl.“ (pokyn, ktorý opravuje), „Tržby klesli o 12 %, nie o 21 %.“ (opravené číslo), „Fotka je skutočná, nie montáž.“ (tvrdenie o pravosti)

### Trojica

„Rýchlo, lacno a spoľahlivo“: AI tlačí všetko do skupín po troch. Vezmi dve, štyri, alebo napíš celú vetu. Najviac jedna trojica prídavných mien na text. Trojica so slovom z úrovne 1 alebo 2 („praktický, flexibilný a udržateľný“) je P1 hneď, druhá trojica prídavných mien v texte tiež; ostatné P2. Vzorec rastie aj do väčších celkov: odsek z troch rovnakých príkladov alebo z troch krátkych tvrdení s mravným ponaučením na konci. Trojica zostáva len tam, kde má obsah tri časti.

- PRED: „Naša pekáreň je tradičná, poctivá a lokálna: múku berieme z mlyna v Sládkovičove.“
- PO: „Múku berieme z mlyna v Sládkovičove.“
- PRED: odsek z troch rovnako stavaných príkladov zakončený vetou „Všetky tri ukazujú, aká dôležitá je komunikácia.“
- PO: príklady ponechaj, zovšeobecnenie na konci škrtni.
- PONECHAŤ: „Formulár chce meno, e-mail a číslo zmluvy.“ Obsah má tri časti.

### Prívesky s „čo“ a „čím“

„…, čo podčiarkuje význam…“, „…, čím prispieva k…“, „…, a tým zabezpečuje…“, „…, pričom zdôrazňuje…“ sú slovenskou obdobou anglických -ing príveskov. Predstierajú hĺbku. Česká AI píše ich české náprotivky („což“, „čímž“) zhruba dvakrát častejšie než ľudia (AI-Koditex, merané na češtine). Škrtni ich, alebo z nich urob samostatnú vetu s doloženým faktom. Prívesok, ktorý nesie skutočný dôsledok, zostáva.

- PRED: „Obec opravila chodník pri škole, čo podčiarkuje jej záujem o bezpečnosť detí.“
- PO: „Obec opravila chodník pri škole.“
- PRED: „Aplikácia ukladá dáta len v telefóne, čím zabezpečuje maximálne súkromie používateľov.“
- PO: „Aplikácia ukladá dáta len v telefóne.“
- PONECHAŤ: „Uzávierka sa posunula na piatok, čo znamená, že výplaty odídu v pondelok.“ Prívesok nesie skutočný dôsledok.

### Opisy pre „je“ a „má“

„predstavuje“, „slúži ako“, „funguje ako“, „disponuje“, „pýši sa“, „ponúka“ v zmysle „má“. Opis škrtni, alebo povedz, čo vec robí. „Je“ napíš len tam, kde ide o totožnosť alebo zaradenie; česká AI píše menných prísudkov s „je“ viac než ľudia, takže prostá výmena opisu za „je“ tik nezruší (D3, D7; české dáta). Samo osebe P2; nafúknutá ustálená fráza v tej istej vete môže osobitne zaslúžiť P1.

- PRED: „Hrad Ľubovňa predstavuje obľúbený cieľ výletov a disponuje vyhliadkovou vežou.“
- PO: „Na hrad Ľubovňa chodia výletníci radi, má vyhliadkovú vežu.“
- PRED: „Nová aplikácia predstavuje nástroj na správu výdavkov.“
- PO: „Nová aplikácia stráži výdavky.“ `[OVERIŤ: aké výdavky a ako]`
- PONECHAŤ: „Zastupiteľstvo predstavilo návrh rozpočtu.“ (predstaviť = ukázať verejnosti), „Tabuľka slúži na evidenciu výpožičiek.“ (skutočný účel)

### Vrstvené istenie

Istenie sú opatrné formulácie typu „asi“, „dáta naznačujú“. „Mohlo by potenciálne“, „dalo by sa povedať, že možno“: dve a viac istení v jednom tvrdení. Nechaj jedno. Istenie samo nálezom nie je: česká AI istí menej než ľudia („asi“, „snad“, „zřejmě“ píše trikrát až päťkrát menej; merané na češtine), takže škrtanie jednotlivých istení posúva text k AI (D8). Kalibrované istenie pri skutočnej neistote zostáva, v odbornom a technickom registri je nevyhnutné.

- PRED: „Tento prístup by mohol potenciálne v niektorých prípadoch viesť k určitému zlepšeniu.“
- PO: „Tento prístup môže v niektorých prípadoch viesť k zlepšeniu.“ `[OVERIŤ: v akých prípadoch a o koľko]`
- PONECHAŤ (zdravotnícky text): „Liek môže u niektorých pacientov spôsobiť závraty.“ Istenie je obsah.
- PONECHAŤ: „Asi to do piatka nestihneme, chýbajú nám podklady od dodávateľa.“ Jedno istenie v tvrdení je ľudský postoj.

### Synonymický kolotoč

„Spoločnosť… firma… podnik… korporácia“ pre tú istú vec v jednom odseku. Platí pre termíny a pomenovania tej istej entity v odbornom a technickom texte: tam vyber jeden výraz a drž sa ho; zámeno alebo vynechanie podmetu je v poriadku. Inde len v zhluku s ďalšími tikmi. Česká AI má slovník skôr chudobnejší než ľudia (D4; české dáta), pestrosť slov preto plošne neznižuj.

### Falošný agens

„Čísla hovoria samy za seba“, „dáta rozprávajú príbeh“, „nástroj rozhoduje“. Povedz, čo číslo ukazuje, alebo pomenuj mechanizmus. Bežné technické slovesá zostávajú.

- PRED: „Návštevnosť vzrástla z 1 200 na 1 900 mesačne. Čísla hovoria samy za seba.“ → PO: „Návštevnosť vzrástla z 1 200 na 1 900 mesačne.“
- PONECHAŤ: „Parser prečíta súbor a test zlyhá, keď chýba hlavička.“

### Dvojbodkové odhalenie a otázka s odpoveďou

„Najlepšie na tom: učí sa.“, „Výsledok? Rýchlejšia práca.“, „Najväčší problém? Ľudia.“ Dvojbodka alebo otáznik tu inscenujú pauzu namiesto spojenia dvoch myšlienok. Prepíš na obyčajnú vetu len z toho, čo zdroj tvrdí. Dvojbodka pred výpočtom, citáciou alebo vecne uvedeným dôsledkom zostáva. Skutočná otázka na čitateľa zostáva vždy: česká AI sa pýta zhruba o polovicu menej než ľudia (D5; merané na češtine), mazať sa má len inscenovaná pauza.

- PRED: „Najlepšie na tom: funguje aj offline.“ → PO: „Funguje aj offline.“
- PRED: „Výsledok? Rýchlejšia práca.“ → PO: „Práca sa zrýchlila.“ `[OVERIŤ: o koľko]`
- PONECHAŤ: „Potrebujete: občiansky preukaz, výpis z účtu, plnú moc.“ (dvojbodka pred výpočtom), „Kedy presne termín vyprší? V zmluve je 30. jún.“ (skutočná otázka, ktorú si čitateľ kladie)

### Inscenovaný dôraz

Slová veľkými písmenami alebo rozsekané bodkami („KAŽDÝ. JEDEN. DEŇ.“) a pokyn na pauzu („Prečítajte si to znova.“, „Nechajte to chvíľu doznieť.“). Škrtni, alebo tam daj fakt, ktorý by váhu uniesol.

### Heslovitá kadencia

Dvojtaktové heslo („Menej papierovania. Viac času.“), číselná dvojica („Jeden účet, tri pobočky.“) a nadpis z dvoch útržkov („Jeden klik. Hotovo.“). Jedno také miesto je hlas autora, od troch v jednom texte ide o šablónu. Spoj ich do normálnej vety, alebo obmeň tvar. Na slajdoch a v odrážkach platí register prezentácií.

- PRED: „Menej klikania. Viac predaja. Jeden účet, tri systémy.“ → PO: „S jedným účtom sa prihlásite do všetkých troch systémov, takže menej klikáte a viac predáte.“ `[OVERIŤ: o koľko menej klikania a viac predaja]`
- PONECHAŤ: jedno heslo v texte („Menej papierovania.“ ako podnadpis) je hlas autora.

### Opakovaný obrat

Tá istá viacslovná figúra s rovnakou rétorickou funkciou sa v texte vracia znova a znova: trikrát „akoby“, opakované „A práve tu…“, „Nejde len o…“, „To nie je náhoda.“. Je to vzorec: P2 od troch výskytov, P1 v zhluku s ďalšími tikmi. Obmeň tvar, alebo nechaj len jeden výskyt.

Opakované jedno slovo vzorec nie je, ani keď ide o spojku alebo časticu („pritom“, „tiež“, „ale“, „totiž“). Patrí do tabuľky Iné chyby ako štylistická poznámka, nie medzi nálezy. Poistka o časticiach platí ďalej: navrhni obmenu alebo škrt len tam, kde slovo nič nenesie, a zvyšok nechaj.

- PRED: „Mesto vyzeralo, akoby spalo. Tržnica stála, akoby ju niekto opustil. Rieka tiekla, akoby sa ponáhľala preč.“ → PO: „Mesto spalo. Tržnica stála prázdna a rieka tiekla rýchlo.“
- PONECHAŤ (Iné chyby): „Knižnica pritom otvára o siedmej… Výpožička je pritom zadarmo… Pritom má len dvoch zamestnancov.“ Opakované „pritom“ je slovo, nie figúra; v tabuľke Iné chyby stačí „pritom 3×, obmeniť“.

### Tautologické zdvojenia

„rôzne a rozmanité“, „efektívny a účinný“, „jasný a zrozumiteľný“, „dôležitý a zásadný“. Nechaj jedno slovo.

## Slovenská skladba

Odstrániť tiky je len polovica druhej úrovne. Druhá polovica je, ako sa veta stavia. Dobre postavená veta sa začína aktérom a slovesom a slovenská AI navyše často presvitá anglickou kostrou.

Poistky platia aj tu: meníš stavbu, nikdy obsah. Žiadne nové fakty, žiadna vnútená osobnosť. Pravidlá platia pre súvislý text; prezentácie časť z nich obracajú, tam je striedmy menný štýl profesionálny hlas (Register prezentácií).

### Nová informácia na koniec (aktuálne členenie)

V slovenčine nesie dôraz koniec vety. Anglický slovosled s podmetom vždy na začiatku znie ako preklad.

- PRED: „Nová verzia aplikácie vyriešila tento problém.“ (novinkou je, čo problém vyriešilo)
- PO: „Tento problém vyriešila nová verzia aplikácie.“

### Príklonky za prvým vetným členom

*sa, si, som, sme, ste, by, mi, ti, mu, ho* stoja hneď za prvým vetným členom, vo vedľajšej vete za spojkou alebo vzťažným slovom.

- PRED: „Túto zmluvu podpísal som včera.“ → PO: „Túto zmluvu som podpísal včera.“
- PRED: „Problém riešili sme celý týždeň.“ → PO: „Problém sme riešili celý týždeň.“

### Nadbytočné zámená

Vynechávaj zámená, ktoré slovenčina nepotrebuje: podmetové zámená bez dôrazu („Ja som išiel…“, „On povedal…“) a privlastňovacie tam, kde je vlastník jasný („Otvoril svoje oči“ → „Otvoril oči“). Oboje je anglický odtlačok a nadbytočné „svoj“ k nemu patrí najčastejšie. Slovenské štylistické príručky hodnotia také privlastňovacie zámeno ako nadbytočné; české „svůj“ píše česká AI o pätinu častejšie než ľudia (merané na češtine). Nadbytočné podmetové zámená české dáta nepreukázali, zostávajú ako slabý signál.

- PRED: „Peter vzal svoj telefón zo svojho stola a on skontroloval svoje správy.“
- PO: „Peter vzal telefón zo stola a skontroloval správy.“
- PONECHAŤ: „Vezmi si svoj, tento je môj.“ Zámeno rozlišuje vlastníka. „Ja to podpíšem, ty nie.“ Podmetové zámeno nesie dôraz.

### Ukazovacie zámená ako rituál

Rad viet, ktoré sa začínajú „Tento problém… Táto situácia… Tieto faktory…“, je úradnícky zvyk, ktorý AI preháňa. Je to najpevnejší vetný signál z českých dát: AI začína vetu ukazovacím zámenom štyrikrát častejšie než ľudia, a to pri všetkých 25 meraných modeloch; podobne „Každý…“ a „Niektoré…“ na začiatku vety. Ukazovacie zámeno patrí tam, kde na niečo skutočne ukazuje. Neurčité „jeden“ („jeden kolega mi hovoril“) je tiež bežné; signálom je až šablónovitý začiatok historky bez mena a detailu (Rozprávanie).

- PRED: „Tento problém sa týka mnohých firiem. Táto situácia si vyžaduje rýchle riešenie. Tieto faktory treba zvážiť.“
- PO: „Problém sa týka mnohých firiem a vyžaduje si rýchle riešenie.“ `[OVERIŤ: ktoré faktory]`
- PONECHAŤ: „Ten server, čo sme minulý týždeň reštartovali, zase spadol.“ Zámeno ukazuje na známu vec. „Jeden kolega mi hovoril, že…“ je bežná slovenčina.

### Slovesá a aktér

**Slovesá namiesto podstatných mien.** „Došlo k realizácii implementácie“ → „Nasadili sme“. Každé „vykonanie“, „zabezpečenie“, „realizácia“, „dochádza k“, „v rámci vykonávania“ skrýva sloveso, ktoré veta chcela.

**Pomenuj aktéra.** Opisné pasívum („bolo rozhodnuté“, „je vykonávaný“) skrýva, kto čo robí. Pomenuj ho, keď ho zdroj pozná. Zvratné pasívum („kontroluje sa“, „platí sa vopred“) je v slovenčine prirodzené a samo osebe nálezom nie je. Jedno opisné pasívum je tiež slabé samo osebe.

**Sloveso musí pomenovať skutočnú operáciu.** Keď je aktér pomenovaný, sloveso má povedať, čo sa s predmetom deje: číta, triedi, posiela, kontroluje, maže. Metafora na mieste slovesa („nesie“, „ťahá“, „stojí na“) zruší prácu, ktorú urobil pomenovaný aktér.

- PRED: „V rámci realizácie projektu došlo k vykonaniu migrácie dát zo strany externého dodávateľa.“
- PO: „Externý dodávateľ v projekte preniesol dáta.“
- PRED: „Bolo rozhodnuté, že bude pripravený nový postup.“
- PO: `[OVERIŤ: kto rozhodol a kto postup pripraví]`
- PONECHAŤ: „Prihlášky sa podávajú do 30. júna.“ (zvratné pasívum, aktér je jasný), „Pacient bol prevezený na JIS.“ (aktér nehrá úlohu)

### Slovo, ktoré by si povedal nahlas

„riešiť“ namiesto „adresovať“, „zistiť“ namiesto „eruovať“, „mať“ namiesto „disponovať“, „použiť“ namiesto „využiť“ (keď nejde o využitie výhody, príležitosti alebo kapacity). Výnimkou sú registre, kde je odborný výraz ten presný (právo, medicína, bezpečnosť).

### Jedna myšlienka na vetu

Jedna vedľajšia veta je východiskový stav. Reťaze „ktorý“ a „pričom“ pôsobia ako generovaná vata. Rozdeľ vetu a spojenie nechaj niesť logické slovo (pretože, ale, preto), nie nahromadené „okrem toho“ a „zároveň“.

### Hustá sieť odkazov

Česká AI drží text pokope viac než ľudia (D3; merané na češtine): píše o polovicu viac „který“, takmer dvakrát viac „, což“, korelatív („to, co“; „tak, aby“; „ten, kdo“) a „svůj“ a začína vety „Tento…“. Pre slovenské „ktorý“, „, čo“, „to, čo“, „ten, kto“ a „svoj“ to preberáme ako hypotézu. Jeden taký prostriedok je obyčajná slovenčina. Signálom je pasáž, kde sa hromadia a každá veta odkazuje na predchádzajúcu namiesto toho, aby povedala niečo nové. Pomenuj vec, na ktorú zámeno ukazuje, alebo vetu rozdeľ. „Navyše“ a „Ďalej“ na začiatku vety AI v českých dátach nepreháňa; prekáža až reťaz troch a viac.

- PRED: „Firma zaviedla nový systém evidencie, ktorý zrýchlil schvaľovanie faktúr, čo ocenili hlavne účtovníci, ktorí predtým trávili hodiny tým, čo teraz zvládnu za minúty. Tento systém zároveň umožnil, aby každý videl, v akom stave jeho faktúra je.“
- PO: „Firma zaviedla nový systém evidencie a schvaľovanie faktúr sa zrýchlilo. Účtovníci, ktorí na ňom predtým trávili hodiny, ho teraz zvládnu za minúty. Každý navyše vidí, v akom stave je jeho faktúra.“ `[OVERIŤ: o koľko sa schvaľovanie zrýchlilo]`
- PONECHAŤ: „Faktúru, ktorú ste poslali v piatok, sme zaplatili.“ Jedna vzťažná veta s „ktorý“ je obyčajná slovenčina.

## Úroveň 3: obsah

Relevancia k zadaniu a hustota informácie najsilnejšie predpovedajú, či čitateľ text označí za slop; zoznamy slov ich nezachytia (Shaib a kol. 2025). Prejdi ich preto ako prvé.

### Relevancia

Každý odsek odpovedá na to, prečo čitateľ text číta. Odsek, ktorý vysvetľuje všeobecné pozadie, opakuje zadanie alebo rozoberá vec, na ktorú sa nikto nepýtal, skráť na vetu, alebo škrtni.

### Odpovedz na čitateľovu ďalšiu otázku

Človek po tvrdení napíše dôsledok („Stojí o 15 € viac. Odpadne však druhá návšteva.“), model zopakuje tvrdenie inými slovami. Keď ďalšia veta nepridáva informáciu, škrtni ju.

### Pomenované namiesto vágnych odkazov

„Jedna známa kniha o produktivite“ → skutočný názov. Odborníci dostanú meno, „nedávno“ dostane dátum. Vágna autorita („štúdie ukazujú“, „odborníci sa zhodujú“) buď dostane skutočný zdroj, alebo zmizne (P0, zoznam v `slova.md`). To isté platí pre prestížny výpočet („Písali o nás tri celoštátne denníky a dva odborné weby“): ponechaj médium, ktoré povedalo niečo konkrétne, a čo povedalo. Chýbajúca citácia sama osebe tik nie je, väčšina textov žiadne nemá.

- PRED: „Odborníci sa zhodujú, že pravidelné zálohovanie je kľúčové.“
- PO: „Zálohujte pravidelne.“ `[OVERIŤ: kto to odporúča]`
- PRED: „Štúdie ukazujú, že ľudia čítajú na mobile menej pozorne.“
- PO: `[OVERIŤ: ktorá štúdia, kedy, na akej vzorke]` Číslo ani zdroj nevymýšľaj.
- PRED: „Jedna známa kniha o návykoch tvrdí…“
- PO: `[OVERIŤ: názov a autor knihy]`
- PRED: „Písali o nás Ranné listy, Týždeň v biznise aj Techportál. Ranné listy v marci porovnávali naše ceny s konkurenciou.“
- PO: „Ranné listy v marci porovnávali naše ceny s konkurenciou.“
- PONECHAŤ: „Podľa Štatistického úradu SR…“ s konkrétnym údajom. Bežný text bez citácií, ktorý žiadnu autoritu nepredstiera.

### Test prenosnosti

Presuň vetu bez zmeny do textu o inej firme, produkte alebo človeku. Keď tam stále sedí, bola to vata. Nahraď ju faktom, mechanizmom, dôsledkom alebo úsudkom, ktorý platí len tu, alebo ju škrtni. Je to najrýchlejší jednotlivý prechod hotovým textom a zachytí, čo zoznamy slov minú.

### Výhľad namiesto výsledku

Text, ktorý má povedať, čo sa stalo alebo čo platí, skĺzne k tomu, čo bude a čo by mohlo byť: „otvára cestu k ďalšiemu rozvoju“, „má potenciál zmeniť“, „prináša nové príležitosti“, „v budúcnosti bude zohrávať úlohu“. Česká AI píše slová výhľadu (budúcnosť, potenciál, rozvoj, perspektíva, príležitosť, otvárať, umožňovať) dvaapolkrát častejšie než ľudia a väzbu „je dôležité, aby“ o dve tretiny častejšie (D7; merané na češtine). Nahraď ich tým, čo sa stalo, čo platí teraz, alebo konkrétnym plánom s dátumom. Budúci čas sám signálom nie je, AI ho v českých dátach píše menej než ľudia. Výhľad zostáva tam, kde ho text sľubuje: plán, odhad, prognóza so zdrojom. P2, v zhluku so slovami z úrovne 2 P1.

- PRED: „Nová cyklotrasa medzi Dúbravkou a Devínskou Novou Vsou otvára cestu k ďalšiemu rozvoju mestskej dopravy a má potenciál zmeniť, ako sa ľudia v štvrti pohybujú.“
- PO: „Medzi Dúbravkou a Devínskou Novou Vsou vedie nová cyklotrasa.“ `[OVERIŤ: odkedy a koľko ľudí ju používa]`
- PRED: „Je dôležité, aby obec v budúcnosti hľadala nové príležitosti na rozvoj cestovného ruchu.“
- PO: Bez podloženého prepisu. `[OVERIŤ: čo konkrétne má obec urobiť a dokedy]`
- PONECHAŤ: „Trasa sa má do konca roka 2027 predĺžiť do Lamača, rozhodlo o tom miestne zastupiteľstvo.“ Plán s dátumom a zdrojom je informácia.

## Úroveň 3: stavba

### Pointa raz

Hlavnú myšlienku povedz raz, na mieste s najväčším účinkom. Výnimkou sú povinné zhrnutia (perex, manažérske zhrnutie). Neopakuj ju v každom oddiele a nepridávaj rituálny odsek „Čo to znamená pre vás?“. Aspoň jeden príklad nechaj bez výkladu; čitateľ vie myslieť.

- PRED: úvod hovorí „Pravidelný servis šetrí peniaze“, každý oddiel sa končí vetou o úsporách a záver to isté opakuje.
- PO: pointa raz, na mieste s najväčším účinkom; oddiely sa končia svojím posledným faktom.
- PONECHAŤ: perex alebo manažérske zhrnutie, ktoré pointu opakuje z povahy formátu.

### Rovnako stavané odseky

Keď má každý odsek tri až päť viet rovnakej dĺžky, rozbi vzorec zámerne: jeden odsek o jednej vete, jeden dlhší. To isté platí pre oddiely, ktoré všetky idú podľa schémy tvrdenie, tri opory, minizhrnutie.

### Nadpisy pomenúvajú obsah

Nahraď šablónu („Úvod / Prehľad / Záver / Kľúčové poznatky“) a dramatizujúce titulky menným spojením, ktoré obsah pomenuje: „Vývoj tržieb 2024 – 2026“, „Riziká projektu“. Označ nadpis-upútavku, ktorá len naznačuje („Čo to pre nás znamená“, „Pohľad na naše čísla“), hovorový vetný nadpis („Čo na školení bolo“ → „Obsah školenia“), číselný nadpis z útržkov („Jedna hodina. Tri úlohy.“) a nadpis, ktorý pomenúva akt prezentácie namiesto obsahu („Predstavenie výsledkov“). Nadpisy v slovenčine majú veľké len prvé písmeno a vlastné mená; anglický title case je nález. V eseji a publicistike je vetný titulok legitímny, keď nesie konkrétne tvrdenie.

- PRED (slajd): „Čo nám prezradila spätná väzba zákazníkov“ → PO: „Spätná väzba zákazníkov“
- PRED (slajd): „Pohľad na naše čísla“ → PO: „Čísla“ `[OVERIŤ: ktoré ukazovatele a za aké obdobie]`
- PRED: „Jedna hodina. Tri úlohy.“ → PO: „Úlohy na jednu hodinu“
- PRED: „Prispôsobil lektor obsah?“ → PO: „Prispôsobenie obsahu“
- PRED: „Predstavenie výsledkov prieskumu“ → PO: „Výsledky prieskumu“
- PRED: „Čo na školení bolo“ → PO: „Obsah školenia“
- PRED: „Koho sme sa pýtali“ → PO: „Respondenti“
- PONECHAŤ (akčný titulok s overiteľným tvrdením): „Odchod zákazníkov klesá od mája o 2 body mesačne“
- PONECHAŤ (titulok eseje): „Prečo deti prestali čítať návody“. V publicistike je vetný titulok legitímny, keď sľubuje konkrétnu odpoveď.

### Šablónovité úvody a závery

Nezačínaj širokouhlým kontextom („V dnešnej rýchlo sa meniacej dobe…“, „V ére umelej inteligencie…“). Začni správou alebo tvrdením, kontext príde potom. Žiadny všeobecný koniec („Budúcnosť ukáže“, „Čakajú nás zaujímavé časy“). AI takmer vždy končí rituálom „Na záver možno konštatovať…“ alebo nadpisom „Záver“ so zhrnutím toho, čo už zaznelo. Keď text záverečný oddiel potrebuje, musí priniesť novú myšlienku: dôsledok, rozhodnutie, ďalší krok. Inak ho škrtni a skonči o odsek skôr.

- PRED: „V dnešnej rýchlo sa meniacej dobe je čoraz dôležitejšie venovať pozornosť kybernetickej bezpečnosti. Minulý týždeň útočníci zašifrovali dáta dvoch obecných úradov na Orave.“
- PO: „Minulý týždeň útočníci zašifrovali dáta dvoch obecných úradov na Orave.“
- PRED (koniec článku): „Na záver možno konštatovať, že digitalizácia prináša výzvy aj príležitosti. Budúcnosť ukáže.“
- PO: zmazať a skončiť posledným konkrétnym odsekom.
- PONECHAŤ: oddiel „Záver“ v odbornej práci, keď prináša výsledok.

### Falošné precitnutie a mravoučná pointa

„Potvrdilo mi to jednu vec.“, „Otvorilo mi to oči.“, „Pravda je takáto:“, „A práve vtedy mi došlo…“ predstierajú aha moment, ktorý sa nestal. Záverečná veta, ktorá pointu povýši na metaforu alebo múdrosť („Technológia sama osebe nestačí.“, „Všetko sa začína pri ľuďoch.“, „Nástroje sa menia, remeslo zostáva.“), je to isté. Zmaž ju a nevylepšuj: lepšia metafora by v texte nechala rovnaký vzorec. Skonči najkonkrétnejšou vetou, ktorú text už má.

- PRED (posledná veta): „Technológie sa menia, ale ľudia zostávajú.“ → PO: zmazať a skončiť najkonkrétnejšou vetou, ktorú text už má.
- PRED: „Potvrdilo mi to jednu vec: AI nie je o technológii.“ → PO: `[OVERIŤ: čo konkrétne autor videl]`, alebo celé zmazať.
- PONECHAŤ: priama citácia, ktorá múdrosť obsahuje a je pripísaná autorovi.

### Okrídlené metafory o AI

„AI je kopilot, nie autopilot“, „dáta sú nová ropa“, „prompt je nový brief“. Také ošúchané, že samy prezradia strojový text. Opíš, čo nástroj konkrétne robí.

- PRED: „AI je kopilot, nie autopilot: napíše prvú verziu, ale čo v nej zostane, rozhoduje človek.“ → PO: „AI napíše prvú verziu, ale čo v nej zostane, rozhoduje človek.“

### Metakomentár a text o sebe

Vety, ktoré vystúpia z témy a hovoria čitateľovi, ako čítať: „To je dôležitejšie, než sa zdá“, „Rozhodujúce je toto:“, „Ako vidíte“, „Inými slovami“ po vete, ktorá už bola jasná. Sem patrí aj predstieraný vhľad („Čo väčšina ľudí prehliada“, „Čo vám nikto nepovie“) a text o sebe samom („V tomto článku sa pozrieme na…“, „Teraz sa zameriame na…“, „Ako sme si ukázali vyššie…“, „Tabuľka nižšie porovnáva…“). Zmaž, alebo na to miesto daj chýbajúci fakt. Oslovenie, ktoré čitateľovi šetrí čas („Keď sa ponáhľate, stačí posledný odsek.“), zostáva; česká AI oslovuje čitateľa menej než ľudia (D5; merané na češtine).

- PRED: „To je dôležitejšie, než sa na prvý pohľad zdá. Čo väčšina ľudí prehliada: zálohy sa musia aj testovať.“
- PO: „Zálohy sa musia aj testovať.“
- PRED: „Pre tento prehľad sme prešli weby všetkých dodávateľov a údaje previedli do tabuľky. Tabuľka nižšie je zoradená podľa ceny.“
- PO: tabuľku ponechaj; zdroj uveď raz pod ňou, keď na ňom záleží.
- PONECHAŤ: „Kto potrebuje len cenu, nájde ju v treťom odseku.“ Jedno skutočné oslovenie čitateľa, ktoré mu šetrí čas. Poznámky k vydaniu a changelog, kde opis zmeny je obsah.

### Ohlásenie, rekapitulácia a šablónovitá vyváženosť

**Ohlásenie a rekapitulácia.** Úvod ohlási osnovu, nadpisy ju zopakujú a záver zrekapituluje úvod. Čitateľ dostane štruktúru trikrát a obsah raz. Škrtni ohlásenie, nechaj nadpisy pomenovať obsah, skonči posledným novým bodom.

**Šablónovitá vyváženosť.** Ústupok, ktorý nič neváži („Hoci je X sľubné, Y zostáva výzvou“), a rámec „na jednej strane… na druhej strane… napokon záleží na konkrétnej situácii“ v texte, ktorý čitateľovi dlhuje záver. Pomenuj skutočný kompromis, alebo zaujmi stanovisko a obháj ho. Recenzie, posudky a prehľady literatúry, ktoré protinázory potrebujú, sú výnimka.

- PRED: „Na jednej strane prináša home office flexibilitu, na druhej strane so sebou nesie riziká. Napokon záleží na konkrétnej situácii.“
- PO: Bez podloženého prepisu. `[OVERIŤ: aké riziká a k akému odporúčaniu text smeruje]`
- PRED: „V tomto článku sa pozrieme na tri oblasti…“ + nadpisy, ktoré ich opakujú + záver „Ako sme si ukázali…“
- PO: ohlásenie aj rekapituláciu škrtni, nadpisy ponechaj.
- PONECHAŤ: recenzia alebo posudok, kde je porovnanie pre a proti účelom textu.

### Fantómové námietky

Text sa bráni tvrdeniu, ktoré nikto nevyslovil: „Tým nechcem povedať, že…“, „Nechápte ma zle“, „Aby bolo jasné“. Zmaž obrannú polovicu a povedz, čo sa tvrdí. Námietka zostáva, keď text uvedie, kto ju vzniesol, alebo sa s ňou skutočne vyrovná.

- PRED: „Tým nechcem povedať, že by tabuľky boli zlé. Nechápte ma zle, Excel má svoje miesto. Ale na zdieľanú evidenciu je tabuľka v e-maile nevhodná, pretože každý má potom inú verziu.“
- PO: „Na zdieľanú evidenciu je tabuľka v e-maile nevhodná, pretože každý má potom inú verziu.“
- PONECHAŤ: „Vedenie namietlo, že prechod bude drahý. Licencia stojí 1 600 € ročne, ale odpadne ručné prepisovanie.“ Námietku niekto vzniesol a text s ňou pracuje.

### Počítané zoznamy pre efekt

„Tri kľúčové poznatky“, „5 vecí, ktoré musíte vedieť“. Číslo tu o obsahu nič nehovorí. Počítaj, len keď je počet informácia.

### Odpoveď, ktorá stavia kontext nanovo

V odpovedi na e-mail alebo správu čitateľ kontext pozná. Keď odpoveď rekapituluje problém, prechádza analýzu a rozhodnutie povie až na konci, pointa sa stratí. Rozhodnutie patrí na začiatok. Ponechaj fakt, ktorý čitateľovi chýba, úvahu, ktorá by zmenila jeho súhlas, a odkaz, ktorý potrebuje na akciu.

- PRED (odpoveď v Teams): „Ako vieš, minulý týždeň sme riešili meškanie dodávok. Prešiel som 14 objednávok a 9 z nich prišlo neskoro, hoci zmluva garantuje dva dni. Prebral som to s logistikou a po zvážení všetkých možností som dospel k záveru, že by sme mali zmeniť dopravcu.“
- PO: „Navrhujem zmeniť dopravcu. Zo 14 objednávok prišlo 9 neskoro, hoci zmluva garantuje dva dni. S logistikou je to prebraté.“
- PONECHAŤ: prvý e-mail adresátovi, ktorý kontext nepozná.

### Formát podľa obsahu

Nadpis nad oddielom o dvoch vetách, odrážky, ktoré rozsekajú argument, emoji v nadpisoch, zoznamy s tučným štítkom a dvojbodkou, ktoré len opakujú riadok („**Výkon:** Výkon sa zlepšil…“), tučné písmo pri každom pojme. Odrážky si miesto zaslúžia, keď sú položky naozaj súbežné a čitateľ ich preletí. Markdown nepatrí do textu pre pole bez formátovania (e-mail, príspevok, SMS).

- PRED:
  - **Rýchlosť:** Aplikácia je rýchlejšia.
  - **Bezpečnosť:** Pridali sme šifrovanie.
- PO: „Aplikácia je rýchlejšia a pridali sme šifrovanie.“
- PONECHAŤ: „**Krok 1. Stiahnite si formulár.** Nájdete ho na úradnej tabuli obce.“ Štítok pomenuje krok a za ním nasleduje nová informácia.

## Úroveň 3: rozprávanie (príbehy, historky, prípadové štúdie)

- **Škrtni dovetok s ponaučením.** „…a vtedy mi došlo, že nikdy nešlo o nástroj.“ Skonči udalosťou, číslom alebo otvorenou otázkou; ponaučenie si čitateľ vyvodí sám.
- **Žiadny epilóg po konci.** Keď príbeh dopadne, prestaň. Jeden nevyriešený koniec znie ľudsky, úplne uprataný strojovo.
- **Nechaj ambivalenciu stáť.** „Prechod sa oplatil a starý systém mi aj tak chýba“ nepotrebuje zmierlivú vetu.
- **Neservíruj celé pozadie vopred.** Jeden časový ťah na text (začiatok uprostred scény, odložené číslo, návrat k detailu) dá viac než akákoľvek výmena slov.
- **Uveď ľudí tým, čo robia alebo hovoria.** Odsek s titulom a životopisom skráť, alebo škrtni. Kde existuje skutočný výrok, cituj ho. Nikdy ho nevymýšľaj.
- **Generická historka bez mena a detailu** („Nedávno mi jeden klient povedal…“) pôsobí vymyslene, pretože väčšinou vymyslená je. Keď zdroj detail nemá, označ medzeru.
- **Emócie: obraz najviac raz.** Keď text emóciu hrá sériou obrazov (zovreté hrdlo, zatajený dych, ticho, ktoré by sa dalo krájať), nechaj jeden, alebo ju pomenuj. Pomenovaný pocit z ľudského textu zostáva („Bál som sa.“ je v poriadku). V prepise emóciu nemaž; keď obraz nemá v zdroji oporu, uveď medzeru v zozname značiek, vetu nechaj. Opora je len v anglickej beletrii, pravidlo preto platí úzko: stráži sériu obrazov, nie emóciu samotnú.
- **Jedna odbočka je dovolená.** Ľudia v príbehu aj v eseji odbočia, AI drží jednu tému (D4; české dáta). Odbočku zo zdroja v prepise nemaž.
- **Oslov čitateľa len tam, kde je to skutočné.** Otázku alebo oslovenie zo zdroja nechaj; nové nepridávaj, to by bola vnútená osobnosť.

Nikdy z toho nerob kontrolný zoznam. Vyber jeden alebo dva ťahy na text a striedaj ich medzi textami. Keby každý text dostal všetky ťahy naraz, vznikla by nová šablóna.

- PRED: „V pondelok poslala tabuľku sama, bez urgencie. A vtedy mi došlo, že nikdy nešlo o tabuľky, ale o dôveru.“
- PO: „V pondelok poslala tabuľku sama, bez urgencie.“
- PRED: „Jana Kováčová, vedúca prevádzky s pätnásťročnou praxou v logistike, je známa svojím systematickým prístupom. Po dvoch minútach prerušila prezentáciu: ‚Toto nám trvá pridlho.‘“
- PO: „Vedúca prevádzky Jana Kováčová prerušila prezentáciu po dvoch minútach: ‚Toto nám trvá pridlho.‘“ (pätnásťročná prax sa dá spomenúť neskôr, keď na nej v príbehu záleží)
- PRED: „Nedávno mi jeden klient povedal niečo, čo mi zmenilo pohľad.“
- PO: `[OVERIŤ: kto, kedy a čo presne povedal]`
- PRED: „Keď som otvoril e-mail, zovrelo mi žalúdok, svet sa na chvíľu zastavil a v ušiach mi hučalo.“
- PO: „Keď som otvoril e-mail, zovrelo mi žalúdok.“ Jeden obraz zostáva, pocit sa neháda a nemaže.
- PRED: „Ten e-mail ma vydesil. Zovrelo mi žalúdok a svet sa na chvíľu zastavil.“
- PO: „Ten e-mail ma vydesil, zovrelo mi žalúdok.“
- PONECHAŤ: príbeh, ktorý sa končí otvorene a ambivalentne, bez zmierlivej vety. „Bál som sa.“ Jeden obraz vo chvíli, ktorá si ho zaslúži.

## Registre

### Register prezentácií

Prezentácie sú vlastný register a jedno pravidlo pre súvislý text obracajú: na slajde je vecný menný štýl ľudský profesionálny hlas. „Úvod do základov“ je menný ekvivalent „začneme od nuly“; hovorová veta, ktorá v blogu znie živo, na slajde pôsobí nedbalo.

- **Rad titulkov je zhrnutie prezentácie.** Prečítaj len titulky po sebe; musia niesť príbeh samy. Jedno hlavné posolstvo na slajd. Agenda je zoznam titulkov.
- **Podstatné mená namiesto hovorových slovies.** „Funkcie systému“ namiesto „Čo systém vie“, „Postup“ namiesto „Ako na to“. Striedme pasívum je tu v poriadku: „Neoverené údaje sa nepreberajú“ hovorí jasné pravidlo.
- **Žiadne senzačné jednovetné pointy a žiadna nosná metafora ako verdikt** („Koncept drží“, „Toto je chrbtica stratégie“). Daj na slajd číslo alebo kritérium.
- **Tón odporúčania.** „Odporúčanie: čísla pred odoslaním skontrolovať“ namiesto „Čísla vždy čeknite!“.
- **Poznámky patria do poznámok.** Pokyny pre rečníka a interné komentáre nikdy na slajd. Žiadne pečiatky („Návrh“, „Finálne“, „Dôverné“), ak o ne nikto nežiada.
- **Žiadna dlhá pomlčka.** Konštrukciu s pomlčkou nahraď spojkou, dvojbodkou alebo vedľajšou vetou. Pomlčka „–“ v rozsahu (2024 – 2026) je v poriadku.

Vnútri odrážok neplatí pravidlo o útržkoch; odrážky na slajde sú útržky zámerne. Posudzuj ich podľa obsahu informácie. Odrážky rovnakého gramatického tvaru, ktoré netvrdia nič overiteľné, zostávajú nálezom.

- PRED (slajd): „Čísla pred odoslaním vždy čeknite!“ → PO: „Odporúčanie: čísla pred každým odoslaním skontrolovať“
- PRED (slajd): „Neoverené = bezcenné“ → PO: označ medzeru: čo sa s neovereným údajom stane a prečo. Pravidlo prijatia nedomýšľaj.
- PRED (slajd): „Rýchle nasadenie—ideálne pre nových kolegov“ → PO: „Rýchle nasadenie, ideálne pre nových kolegov“
- PRED (slajd): „Tu zdôrazniť, že rozpočet ešte nie je schválený“ → PO: presunúť do poznámok rečníka.
- PONECHAŤ (slajd): „Rozpočet 2027: 4,2 mil. € (+8 %)“. Menný štýl je tu správny.

### Odborný text

Odborný text má k zoznamom slov navyše vlastný zoznam: prehnané slovesá („dokazuje“ → „ukazuje“, len keď zdroj tú silu nepodporuje), klišé vo výpočte prínosov, hromadné citácie bez zaradenia, „nový“ a „unikátny“ ako nafúknutie. Žiadne sloveso silnejšie než jeho dôkaz. Keď dôkaz chýba, označ medzeru, tvrdenie potichu neoslabuj. Opisné pasívum a „my“ sú tu prirodzené. Ľudský odborný text je vecný a neosobný: neutralita a presnosť sú tu ľudský hlas, osobnosť doň nevnášaj. Ponechaj kalibrované istenie („dáta naznačujú“), pasívum tam, kde aktér nehrá úlohu, „my“, terminológiu a všetky čísla a citácie bez zmeny.

- PRED: „Rozsiahle experimenty na množstve dátových súborov jednoznačne dokazujú, že náš nový prístup výrazne prekonáva súčasné metódy.“
- PO: Bez podloženého prepisu. Označ medzery: ktoré dátové súbory, ktoré metódy, aké skóre a aký test podporuje „výrazne“. Dôkaz nevymýšľaj a porovnanie potichu neoslabuj.
- PONECHAŤ: „Výsledky naznačujú, že vzťah medzi premennými nie je lineárny (r = 0,31; p = 0,02).“

## Poistky v príkladoch

Pravidlá poistiek sú celé v `../SKILL.md`. Tu sú kontrolné príklady.

### Význam v rovnakej sile

- „spôsobuje“ sa nesmie zmeniť na „ovplyvňuje“
- „trikrát rýchlejší“ sa nesmie zmeniť na „rýchlejší“
- „73 % opýtaných“ sa nesmie zmeniť na „opýtaní“
- „zhruba 50 %“ sa nesmie zmeniť na „50 %“
- „nesmie“ sa nesmie zmeniť na „nemal by“
- „musí“ sa nesmie zmeniť na „treba“
- „od 2 do 5 dní“ si ponechá oba konce
- „súčasne“ nesmie vypadnúť, keď tvrdí, že sa dve veci dejú naraz

### Postoj a konkrétnosť pri prepise

Česká AI píše menej častíc, istení, otázok a čísel než ľudia (merané na češtine; pre slovenčinu hypotéza). Prepis ich preto nesmie ubrať, aj keď vetu inak čistí.

- PRED (ľudský text s jedným tikom): „Úprimne, ten nový paušál je vlastne celkom výhodný. Platíme zhruba o 12 € mesačne menej a zmenu sme stihli za dva dni. Prečo sme to neurobili skôr?“
- ZLÉ PO: „Nový paušál je výhodný. Platíme menej a zmena prebehla rýchlo.“ Zmizla častica, istenie „celkom“ a „zhruba“, číslo, čas aj otázka.
- PO: „Ten nový paušál je vlastne celkom výhodný. Platíme zhruba o 12 € mesačne menej a zmenu sme stihli za dva dni. Prečo sme to neurobili skôr?“ Škrtnuté je len dodatočné „Úprimne“.
- ŠKRTNI AJ TAK: vrstvené istenie („mohlo by možno potenciálne“) skráť na jedno; české „možná“ AI v českých dátach naopak preháňa.

### Oprava bez nových chýb

AI píše gramaticky a čítavo. Prepis, ktorý vnesie chybu, text nepoľudští, len pokazí.

- PRED: „Dáta spracovala firma z Košíc. Výsledky poslala v piatok.“
- ZLÉ PO: „Dáta spracovala firma z Košíc a výsledky poslali v piatok.“ Zlúčenie rozbilo zhodu.
- PO: „Dáta spracovala firma z Košíc a výsledky poslala v piatok.“
- PRED: „Nový paušál—platí od mája—je lacnejší.“
- ZLÉ PO: „Nový paušál ktorý platí od mája je lacnejší.“ Chýbajú čiarky okolo vedľajšej vety.
- PO: „Nový paušál, ktorý platí od mája, je lacnejší.“
- PRED: „Problém sme vyriešili. Potom sme ho nahlásili.“
- ZLÉ PO: „Problém vyriešili sme a potom nahlásili.“ Príklonka „sme“ patrí za prvý vetný člen.
- PO: „Problém sme vyriešili a potom nahlásili.“
- PRED: „Zľavu si uplatníte pri pokladni, čo podčiarkuje náš záujem o zákazníka.“
- ZLÉ PO: „Slevu si uplatníte pri pokladni.“ Oprava vniesla českú stopu.
- PO: „Zľavu si uplatníte pri pokladni.“

## Výpočty tvarov podľa závažnosti

Definície P0 – P2, P0 celé a filter presnosti sú v `../SKILL.md`. Závažnosť radí nález až po uplatnení registra, prahov, zámerného použitia a filtra presnosti; neznamená, že každý vymenovaný tvar je nález. Vzorce obsahu, stavby a rozprávania sú P1 aj jednotlivo; slabé samy osebe sú len drobné signály.

**P1 – jasné AI tiky** (oprav pred zverejnením, s ohľadom na profil, prahy a výnimky): nálezy zo zoznamu slov nad prahom, kalky a falošní priatelia, ktorí menia význam alebo znejú cudzo, česká stopa (slovo alebo tvar, ktorý slovenčina nemá, a písmená ě, ř, ů mimo mien, názvov a citátov), kontrastné obraty a trojice mimo povoleného použitia, šablónovité úvody a prechody, dlhá pomlčka „—“ v slovenskom texte, prekročený rozpočet pomlčiek, nadužívané tučné písmo, vrstvené istenie v jednom tvrdení, nafúknutý význam, dvojbodkové odhalenie a otázka s odpoveďou, predstieraný vhľad, falošné precitnutie a mravoučná pointa, plastová ľudskosť („Úprimne povedané“, „A viete, čo je na tom najlepšie?“), vágne tvrdenie o výsledku alebo účinku bez údaja („výrazne zrýchľuje“, „používatelia ju milujú“), okrídlené metafory o AI, fantómové námietky, inscenovaný dôraz, heslovitá kadencia od troch výskytov v texte, prestížne výpočty, falošný agens, šablónovitá vyváženosť, upútavkové a hovorové titulky, anglický title case v nadpisoch, nadbytočné privlastňovacie a podmetové zámená v rade, anglický slovosled, ktorý mení dôraz, príklonky mimo svojho miesta, menný štýl a opisné pasívum, keď tvoria väčšinu viet textu, zmiešané slovenské a anglické formáty čísel v jednom texte (oddeľovač rádov, desatinná čiarka, dátum, čas), generická historka bez mena a detailu (P0 len vtedy, keď zdroj ukazuje, že údaj je vymyslený), dovetok s ponaučením a epilóg v príbehu, vysvetlený podtext, emócia hraná telom a atmosférou, aforistická pointa na konci aj uprostred textu, rovnako stavané odseky, metakomentár a výklad pre čitateľa („Ako vidno“, „Čo väčšina ľudí prehliada“), text o sebe, počítané zoznamy pre efekt, ohlásenie a rekapitulácia, všeobecné a šablónovité závery, výhľad namiesto výsledku, rovnomerná emočná gradácia v príbehu, uvedenie postavy životopisným odsekom, rad titulkov prezentácie, ktorý sám nenesie príbeh, odkaz na obsah, ktorý v texte chýba (ohlásená príloha alebo aktualizácia).

**P2 – vyleštenie** (keď je čas): jednotvárny rytmus a reťaze krátkych viet mimo ich domáceho registra, odpoveď, ktorá stavia kontext nanovo, vety, ktoré neprejdú testom prenosnosti, opakované začiatky viet, opakovaný obrat od troch výskytov, nepodložené absolútne výrazy v presviedčacom texte („vždy“, „všetci“, „nikto“), opisy pre „je“ a „má“, šablónovité nadpisy a titulky slajdov („Úvod“, „Záver“, „Kľúčové poznatky“), menný štýl a opisné pasívum v súvislom texte, ukazovacie zámená ako rituál, hustá sieť odkazov, jediný šablónovitý prechod v texte, slabé kalky, zhluk troch a viac rozšírených bohemizmov v texte, ktorý má byť spisovný (jednotlivo patria do Iných chýb), nejednotné veľké a malé V vo vykaní, tautologické zdvojenia, drobnosti v mikroformátoch (medzera v „50 %“, dátum, desatinná čiarka, kód „EUR“ namiesto „€“ alebo „eur“ v bežnom texte o sumách).
