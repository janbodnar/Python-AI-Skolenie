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
