# Exa Search

## Čo je Exa

Exa je vyhľadávacie API určené pre aplikácie, agentov a pracovné postupy,  
ktoré potrebujú nájsť relevantné webové stránky a pracovať s ich obsahom.  
Vyhľadávací dotaz môže byť napísaný prirodzeným jazykom.  

Exa vráti zoradené výsledky s metadátami, napríklad s názvom, URL,  
a dátumom publikovania. Pomocou parametra `contents` môžeme k výsledkom  
pridať relevantné úryvky, celý text alebo zhrnutie stránky. Ak `contents`  
nepošleme, výsledky obsahujú iba metadáta (názov, URL, dátum) bez textu.  

Exa neposiela odpoveď ako všeobecný chat. Najskôr vyhľadá zdroje a potom  
môže vrátiť obsah týchto zdrojov. Výsledky preto môžeme použiť na vyhľadávanie,  
RAG, rešerš alebo ako podklady pre ďalší model. Okrem vyhľadávania ponúka Exa  
aj samostatné API na priame odpovede s citáciami (`answer`) a na hľadanie  
podobných stránok (`find_similar`) — obe si ukážeme nižšie.  

## Inštalácia a API kľúč

Oficiálny Python SDK sa volá `exa-py`:

```bash
uv add exa-py
```

API kľúč nastavíme v prostredí:

```bash
export EXA_API_KEY="váš-api-kľúč"
```

V PowerShelli vo Windows použijeme:

```powershell
$env:EXA_API_KEY = "váš-api-kľúč"
```

Klient `Exa()` túto premennú automaticky použije. Kľúč nevkladáme priamo do  
zdrojového kódu ani do git repozitára.  

## Prvé vyhľadávanie

Najmenšia užitočná požiadavka obsahuje prirodzený dotaz a `highlights`.  
Exa vyberie relevantné úryvky a prispôsobí ich dĺžku výsledku.  

```python
from exa_py import Exa

exa = Exa()
result = exa.search(
    "Recent techniques for improving retrieval in RAG systems",
    type="auto",
    contents={"highlights": True},
)

for item in result.results:
    print(item.title)
    print(item.url)
    print(item.highlights)
```

Vyhľadávanie a načítanie obsahu môžeme spojiť aj do jedného volania pomocou  
`search_and_contents()`, čo je bežnejší spôsob v praxi:  

```python
from exa_py import Exa

exa = Exa()
result = exa.search_and_contents(
    "Recent techniques for improving retrieval in RAG systems",
    type="auto",
    highlights=True,
)

for item in result.results:
    print(item.title)
    print(item.url)
    print(item.highlights)
```

Vyhľadávanie štandardne vráti najviac desať výsledkov. Počet môžeme zmeniť  
parametrom `num_results`, najviac však na sto výsledkov. Search API nepodporuje  
stránkovanie výsledkov.  

## Režimy vyhľadávania

Parameter `type` volí spôsob vyhľadávania. Jednotlivé režimy sa líšia  
kvalitou aj latenciou, preto voľbu prispôsobíme konkrétnej úlohe:  

| Režim (`type`) | Popis | Kedy použiť |
|---|---|---|
| `auto` (predvolený) | Exa inteligentne kombinuje neurónové a kľúčové vyhľadávanie | Väčšina prípadov, dobrý štart |
| `neural` | Sémantické vyhľadávanie podľa významu dotazu | Koncepčné, opisné dotazy |
| `keyword` | Klasické vyhľadávanie podľa presných slov | Presné zhody — názvy funkcií, chybové hlášky, konkrétne URL |
| `fast` | Odľahčená verzia neurónového vyhľadávania | Nižšia latencia bez veľkej straty kvality |
| `instant` | Najrýchlejší režim (rádovo pod 200 ms) | Autocomplete, live návrhy v reálnom čase |
| `deep` | Rozsiahlejšia rešerš a syntéza výsledkov | Komplexné otázky, viacero krokov vyhľadávania |
| `deep-lite` | Odľahčená verzia `deep` | Syntéza s nižšou latenciou ako plný `deep` |
| `deep-reasoning` | Hĺbková rešerš s uvažovaním nad výsledkami | Náročné výskumné otázky |

Pre technickú dokumentáciu (napríklad hľadanie konkrétnej chybovej hlášky  
alebo API funkcie) je často vhodnejší `keyword` než `auto`, pretože  
sémantické vyhľadávanie môže presné reťazce interpretovať príliš voľne.  

## Ako písať dotazy

Dotaz má opisovať stránky, ktoré chceme nájsť, nie iba zoznam kľúčových slov.  
Pomáha uviesť tému, typ zdroja, obdobie alebo vlastnosť relevantného obsahu.  

```python
from exa_py import Exa

exa = Exa()
result = exa.search(
    "Technical articles comparing hybrid and semantic retrieval "
    "for RAG systems",
    contents={"highlights": True},
)

for item in result.results:
    print(item.title, item.url)
    print(item.highlights)
```

Pri ladení kvality meníme naraz iba jednu časť požiadavky. Najskôr skontrolujeme  
názvy, URL a úryvky. Až potom pridávame filtre, meníme počet výsledkov alebo  
volíme iný režim vyhľadávania.  

## Filtrovanie domén, obsahu a dátumu

`include_domains` obmedzí výsledky na dôveryhodné domény. `exclude_domains`  
naopak odstráni domény, ktoré nechceme použiť. Filter je vhodný vtedy, keď  
by výsledok mimo danej podmienky nebol použiteľný.  
  
Parameter `category` obmedzí výsledky na konkrétny typ zdroja, napríklad  
`company`, `research paper`, `news`, `pdf`, `github`, `personal site`,  
`linkedin profile` alebo `tweet`. Je to často presnejší nástroj než  
doménové filtre, ak nám ide o typ obsahu, nie o konkrétny web.  

```python
from exa_py import Exa

exa = Exa()
result = exa.search(
    "New Python features for data engineering",
    num_results=5,
    category="github",
    include_domains=["python.org", "docs.python.org"],
    start_published_date="2025-01-01",
    contents={"highlights": True},
)

for item in result.results:
    print(item.title, item.url)
```

Ak potrebujeme filtrovať priamo podľa slov v texte stránky (nie iba v dotaze),  
poslúžia `include_text` a `exclude_text`.  

Preferenciu zdroja je často lepšie vyjadriť priamo v dotaze. Tvrdý filter  
používame iba vtedy, keď iné zdroje nemôžeme použiť.  
 
## Úryvky a celý text

Úryvky (`highlights`) sú vhodné pre RAG, odpovede a náhľady, pretože vracajú  
iba časti stránky relevantné pre dotaz. Celý text (`text`) použijeme vtedy,  
keď potrebujeme širší kontext alebo štruktúru dokumentu.  

```python
from exa_py import Exa

exa = Exa()
result = exa.search(
    "Technical postmortems of large-scale inference outages",
    num_results=3,
    contents={"text": {"max_characters": 10000}},
)

for item in result.results:
    print(item.title)
    print(item.text[:1000])
```

V jednej požiadavke je vhodné vybrať iba potrebný typ obsahu. Úryvky a celý  
text zväčšujú odpoveď a každý požadovaný pohľad môže mať vlastnú cenu.  

Ak už URL poznáme, nepoužívame vyhľadávanie. Vtedy je vhodnejšie zavolať  
`exa.get_contents()` a požiadať priamo o obsah týchto stránok:  

```python
from exa_py import Exa

exa = Exa()
result = exa.get_contents(
    ["https://docs.python.org/3/whatsnew/3.14.html"],
    text={"max_characters": 5000},
    subpages=2,
    subpage_target=["docs", "tutorial"],
)

for item in result.results:
    print(item.url)
    print(item.text[:500])
```

Parameter `subpages` umožňuje spolu s hlavnou stránkou načítať aj vybraný  
počet podstránok; `subpage_target` obmedzí, ktoré podstránky sa majú  
uprednostniť podľa kľúčových slov v ich URL alebo obsahu.  

## Živé sťahovanie obsahu (livecrawl)

Exa štandardne vracia obsah z vlastného indexu, ktorý nemusí byť úplne  
aktuálny. Parameter `livecrawl` vnútri `contents` určuje, kedy sa má stránka  
sťahovať naživo:

- `never` (predvolené) — použije sa iba uložený obsah z indexu.  
- `fallback` — použije index, a ak chýba, stiahne stránku naživo.  
- `always` — vždy sťahuje naživo (vyššia latencia, najčerstvejší obsah).  
- `preferred` — skúsi najprv naživo, pri zlyhaní použije index.  

Súvisiaci parameter `max_age_hours` (mimo `contents`, priamo v požiadavke  
na vyhľadávanie) určuje maximálny vek indexovaného obsahu v hodinách — ak je  
obsah starší, Exa ho podľa potreby dohľadá naživo. Hodnota `0` vynúti vždy  
čerstvé sťahovanie, `-1` naopak použije výhradne uložený index.  

```python
from exa_py import Exa

exa = Exa()
result = exa.get_contents(
    ["https://blog.python.org/"],
    text=True,
    livecrawl="preferred",
)

for item in result.results:
    print(item.url)
    print(item.text[:1000])
```

## Hľadanie podobných stránok

Okrem vyhľadávania podľa textového dotazu vie Exa nájsť stránky podobné  
zadanej URL — užitočné napríklad na hľadanie konkurenčného obsahu,  
podobných článkov alebo alternatívnych zdrojov k dokumentácii.  

```python
from exa_py import Exa

exa = Exa()
result = exa.find_similar_and_contents(
    "https://docs.python.org/3/whatsnew/3.14.html",
    exclude_source_domain=True,
    text={"max_characters": 2000},
)

for item in result.results:
    print(item.title, item.url)
```

Parameter `exclude_source_domain` odstráni z výsledkov stránky z rovnakej  
domény ako zdrojová URL, čo sa hodí, ak chceme naozaj externé porovnanie.  

## Priama odpoveď s citáciami (Answer API)

Ak nepotrebujeme zoznam výsledkov, ale rovno odpoveď na otázku podloženú  
zdrojmi, poslúži `exa.answer()`. Na rozdiel od `search` s `output_schema`  
ide o samostatný endpoint určený priamo na tento účel:  

```python
from exa_py import Exa

exa = Exa()
response = exa.answer(
    "What are the main differences between HTTP/2 and HTTP/3?",
    text=True,
)

print(response.answer)
for citation in response.citations:
    print(citation.url)
```

Pre postupné vypisovanie odpovede (napríklad v chatovacom rozhraní) existuje  
aj `exa.stream_answer()`, ktorý vracia odpoveď po častiach:  

```python
from exa_py import Exa

exa = Exa()
for chunk in exa.stream_answer("Explain the CAP theorem"):
    print(chunk, end="", flush=True)
```

## Štruktúrovaný výstup

Pomocou `output_schema` môže Exa vytvoriť odpoveď podľa schémy. Výsledky  
vyhľadávania zostanú v `result.results` a vytvorená hodnota bude v  
`result.output.content`.  

```python
from exa_py import Exa

exa = Exa()
result = exa.search(
    "Who is the CEO of OpenAI?",
    type="deep",
    system_prompt="Prefer official sources and avoid duplicate results",
    contents={"highlights": True},
    output_schema={
        "type": "object",
        "properties": {
            "leader": {"type": "string"},
            "title": {"type": "string"},
        },
        "required": ["leader", "title"],
    },
)

if result.output:
    print(result.output.content)
    print(result.output.grounding)
```

Schému udržiavame malú. `system_prompt` slúži na pokyny o zdrojoch alebo  
spôsobe syntézy. Citácie a dôkazy sa vracajú v `output.grounding`, preto ich  
netreba duplikovať vo vlastnej schéme.

## Vyhľadávanie k historickému dátumu

Snapshot umožňuje pracovať s uloženou verziou stránky, ktorá existovala  
najneskôr v určenom čase. Na Search API patrí `snapshot_as_of` dovnútra  
objektu `contents`.

```python
from exa_py import Exa

exa = Exa()
result = exa.search(
    "Latest stable Python release notes",
    num_results=3,
    contents={
        "snapshot_as_of": "2026-07-01T00:00:00Z",
        "highlights": True,
    },
)

for item in result.results:
    print(item.title, item.url)
```

Snapshot je užitočný pri spätnom testovaní agentov, opakovateľných evaluáciách  
alebo porovnávaní starších verzií dokumentácie. Exa hľadá kandidátne URL podľa  
aktuálnych signálov, ale obsah výsledkov obmedzí zadaným časom.  

Pri snapshote nekombinujeme `snapshot_as_of` s čerstvým načítaním stránky,  
`subpages` ani s `max_age_hours`. Historické výsledky musia pochádzať z  
uloženej verzie.  

## Spracovanie chýb

Volania API môžu zlyhať — napríklad pri neplatnom kľúči, prekročení limitu  
požiadaviek alebo nevalidných parametroch (napríklad `num_results` nad 100).  
Volania preto obaľujeme do `try`/`except`:  

```python
from exa_py import Exa

exa = Exa()

try:
    result = exa.search("query", num_results=150)
except Exception as e:
    print(f"Chyba pri volaní Exa API: {e}")
```

Pri produkčnom nasadení sa oplatí rozlíšiť chyby spôsobené prekročením limitu  
(retry s odstupom) od chýb v samotnej požiadavke (opraviť parametre).  

## Asynchrónne volania

Pre servery a agentov, ktorí spracúvajú viac požiadaviek naraz, SDK ponúka  
aj asynchrónny klient:  
 
```python
import asyncio
from exa_py import AsyncExa

async def main():
    exa = AsyncExa()
    result = await exa.search("async web search example")
    print(result.results)

asyncio.run(main())
```

## Latencia, kontext a cena

Každý parameter spotrebúva iný zdroj:

- Viac výsledkov zväčší odpoveď a následný kontext.
- Celý text je väčší než relevantné úryvky.
- `summary` pridáva syntézu pre každý výsledok.
- `output_schema` pridáva syntézu výsledkov.
- Režimy `deep` a `deep-reasoning` vykonávajú viac krokov vyhľadávania a uvažovania.
- `max_age_hours=0` alebo `livecrawl="always"` môže vyvolať čerstvé načítanie stránky.

Najprv používame najmenšiu požiadavku s `highlights=True`. Ďalšie možnosti  
pridávame až vtedy, keď ich vyžaduje konkrétna úloha.  

## Dôležité názvy v Python SDK

Python SDK používa názvy v tvare `snake_case`. Napríklad API parameter  
`includeDomains` je v Pythone `include_domains` a `maxAgeHours` je  
`max_age_hours`. Pri `search` sú voľby obsahu vnorené pod `contents`.  

Pri už známych URL je rozdiel v umiestnení obsahu dôležitý:  

```python
from exa_py import Exa

exa = Exa()

exa.search(
    "python release notes",
    contents={"highlights": True},
)

exa.get_contents(
    ["https://docs.python.org/3/whatsnew/3.14.html"],
    highlights=True,
)
```

## Jednoduchý RAG pipeline

Na záver príklad, ktorý spája vyhľadávanie, získanie textu a spracovanie  
ďalším modelom — typický základ RAG pracovného postupu:  

```python
from exa_py import Exa

exa = Exa()

result = exa.search_and_contents(
    "Best practices for chunking documents in RAG systems",
    type="auto",
    num_results=5,
    highlights=True,
)

context = "\n\n".join(
    f"{item.title} ({item.url})\n{' '.join(item.highlights)}"
    for item in result.results
)

# `context` teraz môžeme poslať ako podklad ďalšiemu LLM,
# napríklad ako súčasť promptu pre generovanie odpovede.
print(context)
```

## Zdroje

Dokument vychádza z oficiálnej dokumentácie Exa:

- [SDK Quickstart](https://exa.ai/docs/sdks/quickstart)
- [Search Quickstart](https://exa.ai/docs/search/quickstart)
- [Search Reference](https://exa.ai/docs/reference/search)
- [Search Best Practices](https://exa.ai/docs/search/best-practices)
- [Exa Snapshot](https://exa.ai/docs/search/snapshot)
- [Contents Retrieval](https://exa.ai/docs/reference/contents-retrieval)
- [exa-py na PyPI](https://pypi.org/project/exa-py/)
