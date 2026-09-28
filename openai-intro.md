# Úvod do OpenAI

**OpenAI** je výskumné laboratórium a spoločnosť zaoberajúca sa umelou  
inteligenciou, známa vývojom pokročilých AI modelov, najmä série GPT  
(Generative Pre-trained Transformer). Jej modely poháňajú aplikácie na  
spracovanie prirodzeného jazyka, generovanie kódu či konverzačných agentov.  
OpenAI ponúka API, vďaka ktorému môžu vývojári integrovať možnosti umelej  
inteligencie do vlastných aplikácií a jednoduchšie tak budovať inteligentné,  
interaktívne a automatizované systémy.  

**Knižnica OpenAI** je oficiálny balík pre Python, ktorý vyvíja spoločnosť  
OpenAI, aby zjednodušila prácu s jej modelmi. Umožňuje jednoducho začleniť  
výkonné jazykové modely, ako je rodina GPT-6, do vašich aplikácií pomocou  
prehľadného kódu v Pythone. Môžete odosielať výzvy (prompty), prijímať  
odpovede generované AI a spravovať požiadavky na API bez zložitého  
nastavovania. Knižnica sa postará o autentifikáciu, formátovanie aj  
spracovanie odpovedí, takže sa môžete sústrediť na tvorbu chatbotov, nástrojov  
na tvorbu obsahu alebo automatizáciu. Vďaka svojej jednoduchosti robí  
pokročilú umelú inteligenciu dostupnou aj pre vývojárov, ktorí so strojovým  
učením len začínajú.  

## Vytvorenie účtu na platforme OpenAI

1. Otvorte prehliadač a prejdite na <https://platform.openai.com>.
2. Prihláste sa existujúcim účtom alebo si vytvorte nový (e-mail, Google
   alebo Microsoft).
3. Ak sa zobrazí výzva, overte svoju e-mailovú adresu.

## Pridanie platobných údajov a kreditu

1. Po prihlásení otvorte v ovládacom paneli sekciu **Billing**.
2. Pridajte platobný prostriedok (kreditná alebo debetná karta).
3. Zakúpte kredit alebo zapnite platbu podľa spotreby (pay-as-you-go).

> Používanie API vyžaduje aktívne nastavenú fakturáciu.  

## Vytvorenie API kľúča

1. V ovládacom paneli prejdite do sekcie **API Keys**.
2. Kliknite na **Create new secret key**.
3. Skopírujte kľúč a bezpečne ho uložte.

> Kľúč sa zobrazí iba raz. Nikdy ho nezverejňujte a nevkladajte ho do  
> zdrojového kódu ani do verejných repozitárov.  

## Inštalácia klientskej knižnice OpenAI

Otvorte príkazový riadok alebo PowerShell:  

```bash
pip install openai
```

## Nastavenie API kľúča v prostredí

Vo *Windows PowerShelli* uložte kľúč do premennej prostredia:  

```powershell
setx OPENAI_API_KEY "your_api_key_here"
```

Príkaz `setx` premennú uloží trvalo, no prejaví sa až v **nových**  
termináloch. Po jeho spustení preto terminál zatvorte a otvorte znova. Ak kľúč  
potrebujete iba v aktuálnej relácii PowerShellu, použite:  

```powershell
$env:OPENAI_API_KEY = "your_api_key_here"
```

V systéme macOS alebo Linux použite:  

```bash
export OPENAI_API_KEY="your_api_key_here"
```

## Výber modelu

OpenAI ponúka rodinu modelov GPT-6, ktoré sa líšia výkonom aj cenou. V tomto  
návode používame dva z nich:  

- `gpt-6-luna` – rýchly a lacný model pre jednoduché úlohy, ako sú krátke
  otázky a odpovede, klasifikácia alebo analýza menších dát,
- `gpt-6-sol` – výkonnejší model pre zložité programátorské a agentické
  úlohy, pri ktorých záleží na dôkladnejšom uvažovaní.

Nad nimi stojí vlajkový model GPT-6 Astra. Ako pravidlo platí: začnite s Lunou  
a na Sol prejdite, až keď kvalita odpovedí nestačí. Aktuálny zoznam modelov  
nájdete v dokumentácii OpenAI.  

## Základný príklad v Pythone

Tento program ukazuje, ako pomocou OpenAI Python SDK komunikovať s **Responses  
API**, teda s jednotným rozhraním OpenAI na generovanie výstupov modelu,  
napríklad textu.  

**Responses API** má nahradiť staršie, samostatné rozhrania tým, že v jedinom  
objekte odpovede podporuje viac typov výstupu (napríklad text alebo volanie  
nástrojov). V tomto príklade žiadame iba textový výstup, takže je vhodný na  
jednoduché otázky a odpovede. API vracia bohatú štruktúru odpovede, no  
vlastnosť `output_text` zjednodušuje prístup tým, že spojí všetky vygenerované  
textové časti do jedného reťazca.  

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-6-luna",
    input="Write a haiku about Python on Windows."
)

print(response.output_text)
```

Príklad ukazuje najjednoduchší spôsob, ako odoslať výzvu modelu OpenAI a  
získať jeho textový výstup. Používa metódu `responses.create()` a pohodlnú  
vlastnosť `output_text`, ktorá automaticky vyberie a spojí všetok text  
vygenerovaný modelom do jedného reťazca. Tento prístup je ideálny pre rýchle  
skripty, prototypy a nástroje príkazového riadka, kde stačí iba výsledná  
textová odpoveď.  

## Nastavenie API kľúča v kóde

Ak parameter `api_key` vynecháte, SDK si kľúč automaticky hľadá v premennej  
prostredia `OPENAI_API_KEY`. Toto predvolené správanie udržiava citlivé údaje  
mimo zdrojového kódu a umožňuje bezpečnejšiu správu kľúčov na rôznych  
strojoch, v rôznych nasadeniach aj v systémoch na správu verzií. Kľúč však  
môžete klientovi odovzdať aj explicitne:  

```python
import os

from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

response = client.responses.create(
    model="gpt-6-luna",
    input="Write a haiku about Python on Windows."
)

print(response.output_text)
```

V tomto skripte sa kľúč načíta z premennej prostredia a pri vytváraní klienta  
`OpenAI` sa odovzdá explicitne, vďaka čomu SDK môže overovať požiadavky voči  
službe OpenAI. Autentifikácia je tak v kóde viditeľná, čo sa hodí pri rýchlych  
testoch alebo keď kľúč pochádza z iného zdroja, napríklad zo správcu  
tajomstiev. Kľúč nikdy nezapisujte priamo do zdrojového kódu ako textový  
reťazec.  

## Staršie API (Chat Completions)

Tento skript používa staršie rozhranie Chat Completions API, ktoré vzniklo  
pred novším Responses API. Konverzácia sa vytvára cez  
`client.chat.completions.create()` a výstup modelu sa získava z poľa  
`choices`. Toto API je z dôvodu spätnej kompatibility stále podporované, no  
predstavuje skorší návrh zameraný iba na textové výstupy v štýle četu.  

```python
import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

completion = client.chat.completions.create(
    model="gpt-6-luna",
    messages=[
        {
            "role": "user",
            "content": "Is Pluto a planet?"
        }
    ]
)

print(completion.choices[0].message.content)
```

Jedným z dôvodov, prečo je toto API stále relevantné, je, že mnoho ďalších  
poskytovateľov LLM a open-source frameworkov ponúka rozhrania v štýle chat  
completions, ktoré sú koncepčne podobné. Kód napísaný podľa tohto vzoru sa  
preto dá ľahšie prispôsobiť rôznym modelom a poskytovateľom.  

Moderné Responses API naopak zjednocuje generovanie textu, volanie nástrojov a  
multimodálne výstupy do jednej flexibilnejšej štruktúry odpovede. Pre túto  
širšiu pôsobnosť ho mimo OpenAI podporuje menej modelov a platforiem, a preto  
je vzor chat completions v niektorých multimodelových alebo  
viacposkytovateľských nasadeniach prenosnejší.  

## Režim uvažovania (reasoning)

Režim uvažovania je nastavenie, ktoré modelu ukladá, aby pred vytvorením  
konečnej odpovede venoval viac výpočtového času „premýšľaniu“.  

Namiesto okamžitého výpisu textu model interne rozloží zložitý problém na  
kroky, naplánuje postup a opraví vlastné chyby. Tieto interné *reasoning  
tokeny* sa vám nevracajú v surovej podobe, no započítavajú sa do spotreby  
výstupných tokenov. Takýto oneskorený prístup pripomína ľudské rozmýšľanie a  
prináša výrazne vyššiu presnosť pri náročných úlohách, ako je pokročilé  
programovanie, matematika či hlbšia logika. Úroveň úsilia určuje parameter  
`effort` s hodnotami `none`, `low`, `medium` (predvolená), `high`, `xhigh` a  
`max`. Vyššia úroveň znamená kvalitnejšie, ale pomalšie a drahšie odpovede.  

```python
from openai import OpenAI

client = OpenAI()

prompt = """
Write a bash script that takes a matrix represented as a string with
format '[1,2],[3,4],[5,6]' and prints the transpose in the same format.
"""

response = client.responses.create(
    model="gpt-6-sol",
    reasoning={"effort": "medium"},
    input=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print(response.output_text)
```

Vo fragmente vyššie `reasoning={"effort": "medium"}` API oznamuje, že má pred  
konečným výsledkom vyhradiť viac výpočtového výkonu na interné uvažovanie krok  
za krokom. Model namiesto okamžitého vrátenia prvého riešenia, ktoré ho  
napadne, posúdi obmedzenia požadovaného formátu matice, na pozadí prejde  
logikou transpozície a potom cez `response.output_text` vráti hotový a presný  
skript. Keďže ide o náročnejšiu úlohu, použili sme model `gpt-6-sol`.  

## Nastavenie rolí

**Nastavenie rolí** určuje, ako má model interpretovať jednotlivé správy. Rola  
`system` slúži na zadanie všeobecných pokynov alebo správania – tu model  
usmerňuje, aby sa správal ako expert na astronómiu a programovanie. Rola  
`user` predstavuje samotnú otázku. Vďaka oddeleniu pokynov (`system`) od  
dotazov (`user`) model spoľahlivejšie dodržiava obmedzenia a poskytuje  
relevantné odpovede s ohľadom na kontext. V novších modeloch OpenAI sa  
namiesto roly `system` často používa rola `developer`, ktorá plní rovnakú  
funkciu.  

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-6-luna",
    input=[
        {
            "role": "system",
            "content": "You are an expert in Astronomy and Programming.",
        },
        {
            "role": "user",
            "content": "Is Pluto a planet?",
        },
    ],
)

# Pohodlná vlastnosť: spojený textový výstup
print("--- Text Output ---")
print(response.output_text)
```

Skript inicializuje klienta `OpenAI` a metóde `responses.create()` odošle  
štruktúrovaný konverzačný vstup. Vstup je zadaný ako zoznam objektov správ,  
vďaka čomu model spracúva kontext v podobe dialógu. Po spracovaní požiadavky  
program vypíše spojený textový výstup modelu pomocou pohodlnej vlastnosti  
`response.output_text`.  

## Viackolové konverzácie

Model si medzi jednotlivými požiadavkami sám nič nepamätá – každé volanie API  
je samostatné. Ak chcete viesť konverzáciu, musíte mu pri každom kole  
poskytnúť predchádzajúci kontext. Responses API na to ponúka dva spôsoby:  

- `previous_response_id` – odkážete na predchádzajúcu odpoveď a históriu
  uchováva OpenAI,
- ručná správa histórie – celú konverzáciu držíte v zozname správ vy a
  posielate ju v parametri `input`.

Prvý spôsob je jednoduchší a kód je kratší. Nižšie je jednoduchý chatbot v  
termináli, ktorý na nadviazanie konverzácie používa `previous_response_id`:  

```python
from openai import OpenAI

client = OpenAI()

MODEL = "gpt-6-luna"

previous_id = None

print("Chat (type 'quit' to exit)")
while True:
    user_text = input("You: ").strip()
    if user_text.lower() in ("quit", "exit"):
        break
    if not user_text:
        continue

    response = client.responses.create(
        model=MODEL,
        instructions="You are a friendly assistant. Keep answers short.",
        input=user_text,
        previous_response_id=previous_id,
    )
    previous_id = response.id

    print(f"AI: {response.output_text}\n")
```

Po každej odpovedi si zapamätáme jej `id` a v ďalšom kole ho odovzdáme v  
`previous_response_id`, vďaka čomu model vidí celý doterajší rozhovor.  
Všimnite si, že `instructions` posielame pri každom volaní, pretože sa z  
predchádzajúcej odpovede neprenášajú.  

Druhý spôsob dáva plnú kontrolu: históriu môžete ukladať do vlastnej databázy,  
skracovať ju či upravovať a nie ste závislí od toho, čo sa uchováva na strane  
OpenAI.  

```python
from openai import OpenAI

client = OpenAI()

MODEL = "gpt-6-luna"

history = [
    {
        "role": "system",
        "content": "You are a friendly assistant. Keep answers short.",
    }
]

print("Chat (type 'quit' to exit)")
while True:
    user_text = input("You: ").strip()
    if user_text.lower() in ("quit", "exit"):
        break
    if not user_text:
        continue

    history.append({"role": "user", "content": user_text})

    response = client.responses.create(model=MODEL, input=history)

    answer = response.output_text
    history.append({"role": "assistant", "content": answer})

    print(f"AI: {answer}\n")
```

V tomto variante si celú históriu držíme v zozname `history`. Po každej otázke  
do nej pridáme správu s rolou `user` a po odpovedi aj správu modelu s rolou  
`assistant`. Nevýhodou je, že história rastie, a s ňou aj počet vstupných  
tokenov, teda aj cena každého ďalšieho volania. Pri dlhých rozhovoroch preto  
staršie správy skracujte alebo ich nahraďte zhrnutím.  

## Štruktúrované výstupy

Modely bežne vracajú voľný text, ktorý sa programovo spracúva ťažko.  
**Štruktúrované výstupy** (structured outputs) zaručujú, že odpoveď zodpovedá  
schéme, ktorú ste definovali. Nemusíte tak parsovať text ani dúfať, že model  
dodrží požadovaný formát JSON. V Pythone schému najčastejšie zapíšete ako  
triedu knižnice Pydantic, ktorá sa inštaluje spolu s balíkom `openai`, a SDK  
sa postará o zvyšok.  

Nasledujúci príklad z voľného textu recenzie extrahuje štruktúrované údaje:  

```python
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()


class ReviewInfo(BaseModel):
    product: str
    sentiment: Literal["positive", "neutral", "negative"]
    rating_guess: int
    pros: list[str]
    cons: list[str]


review = """
I bought the X200 headphones two weeks ago. The sound is fantastic and the
battery lasts forever, but the ear cups get uncomfortable after an hour and
the app keeps crashing. Still, I would probably buy them again.
"""

response = client.responses.parse(
    model="gpt-6-luna",
    input=[
        {
            "role": "system",
            "content": (
                "Extract structured information from the product review. "
                "The rating_guess field is an integer from 1 to 5."
            ),
        },
        {"role": "user", "content": review},
    ],
    text_format=ReviewInfo,
)

info = response.output_parsed

if info is None:
    print("The model did not return a structured result.")
else:
    print(info.product, info.sentiment, info.rating_guess)
    print("Pros:", ", ".join(info.pros))
    print("Cons:", ", ".join(info.cons))
```

Metóda `responses.parse()` funguje ako `create()`, no navyše prijíma parameter  
`text_format` – triedu Pydantic. Model vygeneruje odpoveď v súlade so schémou  
a SDK ju automaticky prevedie na inštanciu `ReviewInfo`, ktorú nájdete vo  
vlastnosti `response.output_parsed`. Vďaka typu `Literal` je hodnota  
`sentiment` vždy jedna z troch povolených hodnôt. Ak model požiadavku  
odmietne, `output_parsed` môže byť `None`, preto tento prípad v produkčnom  
kóde ošetrite.  

Štruktúrované výstupy sa hodia na extrakciu údajov z textov, klasifikáciu,  
alebo aj na spracovanie riadkov z CSV súboru z predchádzajúceho príkladu do  
objektov. Majte však na pamäti, že schéma zaručuje **formát** odpovede, nie  
jej **pravdivosť**: model môže do správne štruktúrovaného poľa napísať  
nesprávnu hodnotu.  

## Volanie nástrojov (tool call)

Volanie nástroja (alebo funkcie) je mechanizmus, ktorý AI modelu umožňuje  
vyžiadať si externé údaje alebo vykonať akcie, ktoré sám nedokáže.  

Namiesto hádania model preruší generovanie textu a vydá štruktúrovanú  
požiadavku na použitie konkrétneho nástroja, ktorý ste definovali (napríklad  
dotaz do databázy, kalkulačku alebo volanie API). Aplikácia, v ktorej model  
beží, túto požiadavku zachytí, skutočný kód vykoná lokálne a výsledok vráti  
modelu, aby mohol sformulovať presnú konečnú odpoveď.  

Fungovanie volania funkcií si ukážeme na scenári, v ktorom model deleguje  
rozhodnutie externému nástroju. Model požiadame, aby preložil jednoduchý  
pozdrav do náhodne vybraného jazyka. Výber jazyka však nenecháme na modeli –  
poskytneme mu vlastný nástroj `get_random_language`. Nasledujúci kód ukazuje,  
ako nástroj definovať, spracovať požiadavku modelu na jeho vykonanie a  
odovzdať lokálny výsledok späť API, aby vygenerovalo konečný preklad:  

```python
import random

from openai import OpenAI

client = OpenAI()

MODEL = "gpt-6-luna"

LANGUAGES = [
    "Spanish", "Czech", "Hungarian", "French", "German",
    "Italian", "Slovak", "Polish", "Russian",
]

TOOLS = [{
    "type": "function",
    "name": "get_random_language",
    "description": "Returns the name of a randomly chosen language.",
    "parameters": {"type": "object", "properties": {}},
}]


def get_random_language() -> str:
    return random.choice(LANGUAGES)


def get_tool_calls(response):
    return [item for item in response.output if item.type == "function_call"]


response = client.responses.create(
    model=MODEL,
    input="Pick a random language and translate 'Hello, how are you?' into it",
    tools=TOOLS,
)

tool_calls = get_tool_calls(response)
while tool_calls:
    # Vykonáme všetky požadované volania a vrátime ich výsledky
    outputs = [
        {
            "type": "function_call_output",
            "call_id": tc.call_id,
            "output": get_random_language(),
        }
        for tc in tool_calls
    ]
    response = client.responses.create(
        model=MODEL,
        previous_response_id=response.id,
        tools=TOOLS,
        input=outputs,
    )
    tool_calls = get_tool_calls(response)

print(response.output_text)
```

V tomto kóde prvé volanie API spôsobí, že model zastaví generovanie a vyžiada  
si funkciu `get_random_language`. Požiadavku zachytíme filtrovaním  
`response.output` a spracujeme ju v cykle `while`. V ňom nástroj vykonáme  
lokálne – pomocou `random.choice()` – a výsledok pošleme späť API. Reťazením  
konverzácie cez `previous_response_id` a odovzdaním `function_call_output`  
model plynule pokračuje a vybraný jazyk použije vo výslednom preklade. Kód  
spracúva všetky požiadavky na nástroje z jednej odpovede, nielen prvú.  

## Praktický príklad: teplota v meste

Na záver časti o nástrojoch si zostavíme malú aplikáciu pre príkazový riadok,  
ktorá na otázku v prirodzenom jazyku ("Aké je teraz počasie v Tokiu?") odpovie  
aktuálnym počasím. Model si z otázky vyberie názov mesta a zavolá náš nástroj,  
ten zistí súradnice mesta a aktuálne počasie z bezplatného [Open-Meteo  
API](https://open-meteo.com) (nevyžaduje kľúč) a model výsledok zhrnie do  
odpovede.  

Oproti bežným ukážkam s tokmi Chat Completions je tu niekoľko zjednodušení:  

- používame Responses API a jediný nástroj `get_current_weather`, ktorý
  vyhľadá súradnice mesta aj počasie naraz,
- model nemusíme nútiť volať nástroj, sám sa rozhodne, kedy ho potrebuje,
  a výslednú odpoveď formuluje sám, takže odpadá vlastné formátovanie
  výpisu aj tabuľka opisov kódov počasia,
- chyby (napríklad neexistujúce mesto) vraciame modelu ako výsledok
  nástroja, aby ich vedel zrozumiteľne vysvetliť, namiesto vyhodenia výnimky,
- na HTTP požiadavky používame knižnicu `httpx`, ktorá sa inštaluje spolu s
  balíkom `openai`, takže netreba nič dopĺňať.

```python
"""Temperature CLI app: OpenAI tool calling + Open-Meteo API."""

import json
import sys

import httpx
from openai import OpenAI

client = OpenAI()

MODEL = "gpt-6-luna"

INSTRUCTIONS = (
    "You are a weather assistant. Use the get_current_weather tool to answer "
    "questions about the current weather or temperature. The weather_code "
    "field is a WMO weather code; describe it in words. Answer briefly. "
    "If the question is not about weather, say so."
)

TOOLS = [{
    "type": "function",
    "name": "get_current_weather",
    "description": "Get the current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city_name": {
                "type": "string",
                "description": "City name, e.g. 'Paris' or 'Bratislava'.",
            }
        },
        "required": ["city_name"],
    },
}]


def get_current_weather(city_name: str) -> dict:
    """Find the city's coordinates and return its current weather."""
    try:
        geo = httpx.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city_name, "count": 1},
            timeout=10,
        )
        geo.raise_for_status()
        results = geo.json().get("results")
        if not results:
            return {"error": f"City '{city_name}' not found."}
        city = results[0]

        weather = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "current_weather": "true",
            },
            timeout=10,
        )
        weather.raise_for_status()
        current = weather.json()["current_weather"]
    except httpx.HTTPError as e:
        return {"error": f"Weather service error: {e}"}

    return {
        "city": city["name"],
        "country": city.get("country", ""),
        "temperature_celsius": current["temperature"],
        "windspeed_kmh": current["windspeed"],
        "wind_direction_degrees": current["winddirection"],
        "weather_code": current["weathercode"],
        "time": current["time"],
    }


def get_tool_calls(response):
    return [item for item in response.output if item.type == "function_call"]


def answer_weather_question(query: str) -> str:
    response = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,
        input=query,
        tools=TOOLS,
    )

    tool_calls = get_tool_calls(response)
    while tool_calls:
        outputs = []
        for tc in tool_calls:
            result = get_current_weather(**json.loads(tc.arguments))
            outputs.append({
                "type": "function_call_output",
                "call_id": tc.call_id,
                "output": json.dumps(result),
            })

        response = client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            previous_response_id=response.id,
            tools=TOOLS,
            input=outputs,
        )
        tool_calls = get_tool_calls(response)

    return response.output_text


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Ask about the weather: ").strip()

    if not query:
        sys.exit("Error: no input provided")

    print(answer_weather_question(query))


if __name__ == "__main__":
    main()
```

Program môžete spustiť s otázkou v argumentoch alebo bez nich, vtedy sa na ňu  
opýta interaktívne:  

```bash
python weather.py "How hot is it in Tokyo?"
```

Funkcia `get_current_weather()` volá najprv geokódovacie API Open-Meteo, ktoré  
z názvu mesta vráti súradnice, a potom predpoveďové API s aktuálnym počasím.  
Výsledok vráti ako slovník, ktorý sa modelu odovzdá v podobe JSON. Schéma v  
zozname `TOOLS` modelu hovorí, že nástroj existuje a aký argument očakáva;  
popis parametra `city_name` mu pomáha vytiahnuť názov mesta aj z voľne  
formulovanej vety.  

Funkcia `answer_weather_question()` je rovnaký cyklus, aký poznáte z  
predchádzajúceho príkladu: kým odpoveď obsahuje `function_call`, vykonáme  
nástroj a výsledok pošleme späť cez `previous_response_id`. Pretože spracúvame  
všetky volania z odpovede, aplikácia zvládne aj otázku na viac miest naraz,  
napríklad "Compare the weather in Prague and Vienna". Pokyny (`instructions`)  
posielame pri každom volaní, lebo sa z predchádzajúcej odpovede neprenášajú.  
Keďže máme len jeden nástroj, nekontrolujeme `tc.name`; pri viacerých  
nástrojoch by ste podľa neho vybrali príslušnú funkciu.  

Výmenou za jednoduchosť sme sa vzdali pevne daného formátu výpisu: vzhľad  
odpovede teraz určuje model. Ak potrebujete presný, strojovo spracovateľný  
formát, skombinujte tento príklad so štruktúrovanými výstupmi z  
predchádzajúcej časti.  

## Analýza dát CSV

Skript načíta súbor CSV `data/users_data.csv`, spočíta dátové riadky (bez  
hlavičky) a celý text CSV vloží do jedinej výzvy v prirodzenom jazyku so  
žiadosťou o základnú analýzu dát. Inicializuje klienta OpenAI, zostaví výzvu  
(žiada štruktúru datasetu, základné štatistiky, vzory, pozorovania o kvalite  
dát a odporúčania), odošle ju do Responses API a zachytí odpoveď modelu.  

```python
import csv

from openai import OpenAI

client = OpenAI()

csv_file_path = "data/users_data.csv"

# Načítanie CSV a spočítanie dátových riadkov
with open(csv_file_path, newline="", encoding="utf-8") as file:
    csv_content = file.read()
    file.seek(0)
    row_count = sum(1 for _ in csv.reader(file)) - 1  # bez hlavičky

# Príprava výzvy pre LLM
prompt = f"""Please analyze the following CSV dataset containing {row_count} user records.

CSV Data:
{csv_content}

Please provide:
1. A summary of the dataset structure and key columns
2. Basic statistics (e.g., age distribution, gender breakdown, country distribution)
3. Any interesting patterns or insights you notice
4. Data quality observations (missing values, outliers, etc.)
5. Recommendations for further analysis

Keep your analysis clear and concise."""

print("Analyzing CSV data with LLM...")
print("-" * 80)

response = client.responses.create(
    model="gpt-6-luna",
    input=prompt
)

print(response.output_text)
print("-" * 80)
print(f"\nAnalysis completed for {row_count} records from {csv_file_path}")
```

Po volaní API skript vypíše analýzu modelu a krátku záverečnú správu. Ide o  
jednoduchú orchestráciu na rýchle, vysokoúrovňové prieskumné zhrnutia, nie o  
vyčerpávajúce štatistické spracovanie. Je určený na lokálne spustenie s  
nakonfigurovanými prístupovými údajmi API a najlepšie poslúži ako východisko  
pre hlbšiu analýzu. Keďže sa celý súbor vkladá do výzvy, hodí sa len pre dáta,  
ktoré sa zmestia do kontextového okna modelu. Nezabúdajte ani na to, že obsah  
súboru (v tomto prípade údaje o používateľoch) odosielate do OpenAI.  

## Streamovanie odpovede

Namiesto čakania na celú odpoveď môžete výstup prijímať postupne, počas  
generovania. Skript nižšie používa rovnakú analýzu CSV ako predchádzajúci  
príklad, no odpoveď streamuje, takže výsledok vidíte už po prvých  
vygenerovaných slovách. Je to vhodné najmä pri dlhých odpovediach a v  
interaktívnych aplikáciách.  

```python
import csv

from openai import OpenAI

client = OpenAI()

csv_file_path = "data/users_data.csv"

# Načítanie CSV a spočítanie dátových riadkov
with open(csv_file_path, newline="", encoding="utf-8") as file:
    csv_content = file.read()
    file.seek(0)
    row_count = sum(1 for _ in csv.reader(file)) - 1  # bez hlavičky

# Príprava výzvy pre LLM
prompt = f"""Please analyze the following CSV dataset containing {row_count} user records.

CSV Data:
{csv_content}

Please provide:
1. A summary of the dataset structure and key columns
2. Basic statistics (e.g., age distribution, gender breakdown, country distribution)
3. Any interesting patterns or insights you notice
4. Data quality observations (missing values, outliers, etc.)
5. Recommendations for further analysis

Keep your analysis clear and concise."""

print(f"Analyzing {row_count} records with streaming output...")
print("-" * 80)

# Streamovanie odpovede modelu
with client.responses.stream(
    model="gpt-6-luna",
    input=prompt
) as stream:
    for event in stream:
        # Text vypisujeme priebežne, ako sa generuje
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)

print("\n" + "-" * 80)
print(f"Analysis completed for {row_count} records from {csv_file_path}")
```

Skript otvorí kontext streamovania `client.responses.stream` s modelom  
`gpt-6-luna`, prechádza prichádzajúce udalosti a textové delty  
(`response.output_text.delta`) vypisuje v reálnom čase, ako ich model  
generuje. Na záver vypíše oddeľovač a krátku správu o dokončení analýzy pre  
spočítané záznamy.  

## Tokeny a náklady

Za používanie API sa platí podľa počtu **tokenov** – malých kúskov textu  
(zhruba slabika alebo krátke slovo), na ktoré model rozdeľuje vstup aj výstup.  
Účtujú sa zvlášť vstupné tokeny (výzva, história, priložené dáta) a výstupné  
tokeny (odpoveď vrátane reasoning tokenov). Výstupné tokeny sú zvyčajne  
niekoľkonásobne drahšie. Texty v slovenčine a ďalších jazykoch s diakritikou  
spravidla spotrebujú na rovnaký obsah viac tokenov než anglické.  

Skutočnú spotrebu zistíte z vlastnosti `response.usage`. Skript nižšie ju  
vypíše a odhadne cenu volania:  

```python
from openai import OpenAI

client = OpenAI()

# Ceny za 1 milión tokenov (USD) - overte v aktuálnom cenníku OpenAI
PRICES = {
    "gpt-6-luna": {"input": 0.10, "output": 0.50},
    "gpt-6-sol": {"input": 2.00, "output": 10.00},
}

MODEL = "gpt-6-luna"


def estimate_cost(model: str, usage) -> float:
    price = PRICES[model]
    return (
        usage.input_tokens * price["input"]
        + usage.output_tokens * price["output"]
    ) / 1_000_000


response = client.responses.create(
    model=MODEL,
    input="Explain what a hash table is in three sentences.",
    reasoning={"effort": "low"},
    max_output_tokens=1000,
)

if response.status == "incomplete":
    print("Warning: the response was cut off:",
          response.incomplete_details.reason)

usage = response.usage

print(response.output_text)
print("-" * 40)
print(f"Input tokens:  {usage.input_tokens}")
print(f"Output tokens: {usage.output_tokens}")
print(f"  reasoning:   {usage.output_tokens_details.reasoning_tokens}")
print(f"Total tokens:  {usage.total_tokens}")
print(f"Estimated cost: ${estimate_cost(MODEL, usage):.6f}")
```

Objekt `usage` obsahuje počet vstupných, výstupných a celkových tokenov, a pri  
reasoning modeloch aj počet tokenov použitých na interné uvažovanie. Funkcia  
`estimate_cost()` ich vynásobí cenou za milión tokenov. Ceny v slovníku  
`PRICES` sú len ilustračné, nájdete ich v cenníku OpenAI a menia sa, preto ich  
pravidelne kontrolujte.  

Parameter `max_output_tokens` obmedzuje dĺžku odpovede, a tým aj náklady.  
Pozor však: do limitu sa počítajú aj reasoning tokeny. Ak je limit príliš  
nízky, model ho môže vyčerpať uvažovaním skôr, než vygeneruje viditeľný text.  
Odpoveď má vtedy stav `incomplete`, čo skript vyššie kontroluje.  

Niekoľko zásad, ako náklady znížiť:  

- používajte najlacnejší model, ktorý úlohu zvláda (spravidla `gpt-6-luna`),
- pri jednoduchých úlohách znížte `reasoning.effort`,
- nastavte rozumný `max_output_tokens`,
- neposielajte zbytočné dáta a pri dlhých rozhovoroch skracujte históriu,
- dlhé opakujúce sa časti (napríklad systémové pokyny) dávajte na začiatok
  výzvy, aby ich mohla OpenAI ukladať do vyrovnávacej pamäte (prompt caching)
  a účtovať lacnejšie.

## Vyhľadávanie na webe

OpenAI ponúka natívny nástroj `web_search`, vďaka ktorému môže model pred  
odpoveďou vyhľadať aktuálne informácie na internete. Hodí sa pre otázky, na  
ktoré model nemá odpoveď v tréningových dátach, napríklad pri nedávnych  
udalostiach. Nástroj sa zapne jeho uvedením v parametri `tools`; o tom, či ho  
použije, rozhoduje model. Použitie nástroja môže byť spoplatnené zvlášť.  

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-6-luna",
    tools=[{"type": "web_search"}],
    input="What were the outcomes of the latest three matches in the Soccer World Cup 2026?",
)

print(response.output_text)
```

## Embeddings a sémantické vyhľadávanie

**Embedding** je číselná reprezentácia textu – vektor, teda zoznam stoviek či  
tisícok čísel, ktorý zachytáva jeho význam. Texty s podobným významom majú  
vektory blízko seba, aj keď nezdieľajú žiadne rovnaké slová. Na tom je  
postavené **sémantické vyhľadávanie**: namiesto hľadania kľúčových slov  
porovnávame význam otázky s významom dokumentov. Embeddingy sa využívajú aj  
pri odporúčaní, zhlukovaní a klasifikácii a sú základom techniky RAG  
(retrieval-augmented generation).  

Na embeddingy sa nepoužívajú chatové modely, ale samostatné embedding modely.  
`text-embedding-3-small` je lacný a dobrá predvolená voľba (1536 dimenzií),  
`text-embedding-3-large` je presnejší, no drahší (3072 dimenzií). Dĺžku  
vektora je možné skrátiť parametrom `dimensions`.  

Nasledujúci príklad vytvorí embeddingy pre malú zbierku dokumentov, vypočíta  
embedding otázky a nájde dokumenty s najpodobnejším významom:  

```python
import math

from openai import OpenAI

client = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"

documents = [
    "To reset your password, open the account settings page.",
    "Refunds are available within 14 days of purchase.",
    "Our support team is available Monday to Friday, 9:00-17:00.",
    "You can upgrade your subscription plan at any time.",
    "The mobile app supports both dark and light themes.",
]


def embed(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


# Embeddingy dokumentov vypočítame raz (jedno volanie API pre všetky texty)
doc_vectors = embed(documents)


def search(query: str, top_k: int = 3):
    query_vector = embed([query])[0]
    scored = [
        (cosine_similarity(query_vector, vector), doc)
        for vector, doc in zip(doc_vectors, documents)
    ]
    scored.sort(reverse=True)
    return scored[:top_k]


for score, doc in search("I forgot my login credentials, what now?"):
    print(f"{score:.3f}  {doc}")
```

Funkcia `embed()` odošle zoznam textov jedným volaním a vráti zoznam vektorov.  
Funkcia `cosine_similarity()` meria podobnosť dvoch vektorov ako kosínus uhla  
medzi nimi: hodnota bližšie k 1 znamená podobnejší význam. Otázka o  
zabudnutých prihlasovacích údajoch by mala ako najpodobnejší dokument nájsť  
návod na obnovu hesla, hoci s ním nezdieľa žiadne kľúčové slovo. Embeddingy  
OpenAI majú jednotkovú dĺžku, takže by na porovnanie stačil aj obyčajný  
skalárny súčin. Modely zvyčajne zvládajú aj porovnávanie naprieč jazykmi,  
takže otázku môžete položiť po slovensky, pričom `-large` model býva pri tom  
presnejší.  

Pri reálnom nasadení majte na pamäti tieto zásady:  

- embeddingy dokumentov nepočítajte pri každom dopyte znova, ale ich
  uložte (súbor, databáza, vektorová databáza ako pgvector, FAISS či Chroma),
- dokumenty aj otázky vždy vektorizujte **rovnakým modelom**, vektory
  rôznych modelov sa navzájom porovnávať nedajú,
- dlhé texty rozdeľte na menšie časti (chunky), aby sa zmestili do limitu
  modelu a aby boli výsledky presnejšie,
- nájdené dokumenty môžete vložiť do výzvy pre chatový model a získať
  odpoveď založenú na vašich dátach – to je princíp RAG.

## Príkazový riadok (shell)

Posledný príklad vytvára jednoduchého agenta, ktorý pomocou nástroja `shell`  
spúšťa príkazy na vašom počítači. Model navrhuje príkazy, aplikácia ich vykoná  
a výstup vráti modelu v cykle, kým model nedospeje k výslednej odpovedi. Keďže  
ide o zložitejšiu agentickú úlohu, použijeme model `gpt-6-sol`.  

> **Upozornenie:** model generuje príkazy, ktoré sa spúšťajú na vašom  
> počítači. Kód preto pred každým vykonaním žiada o potvrdenie. Toto  
> potvrdzovanie neodstraňujte, kým agenta nespúšťate v izolovanom prostredí  
> (napríklad v kontajneri).  

```python
import subprocess
from dataclasses import dataclass

from openai import OpenAI

MODEL = "gpt-6-sol"
SHELL_TOOL = {"type": "shell", "environment": {"type": "local"}}


@dataclass
class CmdResult:
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool


class ShellExecutor:
    def __init__(self, default_timeout: int = 60):
        self.default_timeout = default_timeout

    def run(self, cmd: str, timeout: int | None = None) -> CmdResult:
        t = timeout or self.default_timeout
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            out, err = p.communicate(timeout=t)
            return CmdResult(out, err, p.returncode, False)
        except subprocess.TimeoutExpired:
            p.kill()
            out, err = p.communicate()
            return CmdResult(out, err, p.returncode, True)


client = OpenAI()
executor = ShellExecutor()

# Úvodná požiadavka
response = client.responses.create(
    model=MODEL,
    instructions="You are a Linux system assistant. Use the shell tool to fulfill requests.",
    input=[
        {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "find me the largest pdf file in ~/Documents",
                }
            ],
        }
    ],
    tools=[SHELL_TOOL],
)

# --- ZAČIATOK CYKLU AGENTA ---
while True:
    shell_calls = [item for item in response.output if item.type == "shell_call"]

    if not shell_calls:
        break  # Model už nežiada ďalšie príkazy

    outputs = []

    for item in shell_calls:
        entries = []

        for command in item.action.commands:
            print(f"AI wants to run: {command}")

            # Príkaz sa vykoná až po potvrdení používateľom
            if input("Run this command? [y/N] ").strip().lower() != "y":
                entries.append({
                    "stdout": "",
                    "stderr": "Command rejected by the user.",
                    "outcome": {"type": "exit", "exit_code": 1},
                })
                continue

            result = executor.run(command)

            if result.timed_out:
                outcome = {"type": "timeout"}
            else:
                outcome = {"type": "exit", "exit_code": result.exit_code}

            entries.append({
                "stdout": result.stdout,
                "stderr": result.stderr,
                "outcome": outcome,
            })
            print(f"Command finished with outcome: {outcome}")

        # Jeden výstup na každé volanie nástroja (podľa call_id)
        outputs.append({
            "type": "shell_call_output",
            "call_id": item.call_id,
            "output": entries,
        })

    # Výsledky pošleme späť; previous_response_id zachová kontext
    response = client.responses.create(
        model=MODEL,
        previous_response_id=response.id,
        tools=[SHELL_TOOL],
        input=outputs,
    )
# --- KONIEC CYKLU AGENTA ---

# Výsledná odpoveď v prirodzenom jazyku
for item in response.output:
    if item.type == "message":
        for content in item.content:
            if content.type == "output_text":
                print(f"\nFinal Answer:\n{content.text}")
```

Trieda `ShellExecutor` spúšťa príkazy s časovým limitom a výsledok vracia ako  
`CmdResult`. Cyklus agenta kontroluje, či odpoveď obsahuje `shell_call`; ak  
áno, každý príkaz po potvrdení vykoná a výstup (`stdout`, `stderr` a výsledok  
– ukončenie s kódom alebo timeout) pošle späť cez `shell_call_output` spolu s  
`previous_response_id`. Keď model už nežiada ďalšie príkazy, cyklus sa skončí  
a vypíše sa jeho konečná odpoveď.
