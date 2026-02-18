# Python a Ollama: pracujeme s lokálnymi jazykovými modelmi

V tomto článku si ukážeme, ako spúšťať výkonné jazykové modely menšej veľkosti
lokálne na vlastnom počítači pomocou nástroja Ollama a ako ich jednoducho a
prakticky integrovať do Python aplikácií.

## Ollama nástroj

**Ollama** je v súčasnosti najpopulárnejší open‑source nástroj na spúšťanie,
správu a používanie veľkých jazykových modelov lokálne na vlastnom počítači.
Umožňuje vývojárom, výskumníkom aj bežným nadšencom používať výkonné AI modely
bez odovzdávania dát do cloudu, bez mesačných poplatkov a bez závislosti na
internete.

Ollama výrazne zjednodušila celý proces práce s lokálnymi jazykovými modelmi.
Umožňuje jednoduché sťahovanie a spúšťanie modelov, správu VRAM/DRAM zdrojov,
a poskytuje konzistentné API kompatibilné s OpenAI. Ponúka tiež jednoduché REST
API a SDK pre Python a JavaScript/TypeScript.

Pri použití Ollama získavame nasledujúce výhody:

- Maximálne súkromie - žiadne dáta neopúšťajú váš počítač.
- Plne offline prevádzka.
- Výborná kompatibilita s OpenAI API.
- Podpora volania nástrojov, štruktúrovaných výstupov (JSON schema) a
  multimodálnych modelov.
- Veľmi jednoduchá integrácia do Pythonu, JS/TS, LangChain, LlamaIndex atď.

## Systémové požiadavky

Pre efektívnu prácu s Ollama je potrebné mať primeraný hardvér. Nasledujúca
tabuľka uvádza odporúčané konfigurácie pre rôzne veľkosti modelov:

| Veľkosť modelu | Minimálna RAM | Odporúčaná RAM | GPU VRAM (4-bit) | Typické použitie |
|---------------|---------------|----------------|------------------|------------------|
| 1-4B | 6-8 GB | 12-16 GB | — (stačí CPU) | testovanie, mobilné zariadenia |
| 7-9B | 10-12 GB | 16-24 GB | 6-8 GB | bežná práca, programovanie |
| 13-27B | 16-24 GB | 32-48 GB | 10-16 GB | vážne použitie, RAG, analýza |
| 32-70B+ | 32+ GB | 64+ GB | 20-40+ GB | takmer GPT-4 úroveň (s GPU) |

Ollama podporuje aj CPU, no pri väčších modeloch je potrebné mať GPU. Pre
optimálny výkon sa odporúča mať modernú NVIDIA kartu s podporou CUDA a aspoň
6 GB VRAM.

## Inštalácia

Proces inštalácie Ollama je jednoduchý. Na Linuxe môžeme použiť inštalačný
skript alebo Docker.

```bash
$ curl -fsSL https://ollama.com/install.sh | sh
```

Tento príkaz stiahne a nainštaluje Ollamu spolu s potrebnými závislosťami.

```bash
$ docker run -d --gpus all -v ollama:/johndoe/.ollama \
  -p 11434:11434 --name ollama ollama/ollama
```

Tento príkaz spustí Ollama v Docker kontajneri s prístupom k GPU a
perzistentným úložiskom.

## Základné CLI príkazy

Po inštalácii Ollama môžete používať nasledujúce príkazy v termináli:

- `ollama pull gemma2:9b` - Stiahnutie modelu
- `ollama run llama3.2:3b` - Spustenie modelu v interaktívnom režime
- `ollama list` - Zoznam nainštalovaných modelov
- `ollama ps` - Bežiace modely a spotreba zdrojov
- `ollama stop phi4` - Zastavenie bežiaceho modelu
- `ollama rm deepseek-r1:32b` - Odstránenie modelu (uvoľnenie miesta)
- `ollama create moj-model -f Modelfile` - Vytvorenie vlastného modelu z
  Modelfile
- `ollama show llama3.2` - Zobrazenie detailných informácií o modeli
- `ollama cp llama3.2 moj-zalozny-model` - Kopírovanie/premenovanie modelu
- `ollama serve` - Spustenie lokálneho servera
- `ollama --help` - Nápoveda pre všetky príkazy
- `ollama --version` - Verzia Ollama
- `ollama push meno/model` - Nahratie modelu do vlastného repozitára na
  ollama.com
- `ollama run llama3.2 --verbose` - Spustenie modelu so zobrazením štatistík
- `ollama run llama3.2 --format json` - Vynútenie odpovede modelu vo formáte
  JSON
- `ollama run llama3.2 --keepalive 1h` - Nastavenie času, počas ktorého ostane
  model v pamäti (VRAM)
- `ollama help run` - Podrobná nápoveda pre konkrétny príkaz

Tieto príkazy pokrývajú základnú správu modelov, ich spúšťanie a interakciu s
Ollama prostredníctvom terminálu. Práca s modelmi veľmi pripomína prácu s
kontajnermi v Dockeri, preto tí, ktorí sú s Dockerom oboznámení, sa budú cítiť
ako doma.

## Najpopulárnejšie modely v februári 2026

Nasledujúca tabuľka zobrazuje najpoužívanejšie modely, ktoré sú dostupné cez
Ollama:

| Poradie | Model | Veľkosť | Silné stránky |
|---------|-------|---------|---------------|
| 1 | qwen2.5-coder | 7B-32B | programovanie, matematika, dlhé kontexty |
| 2 | gemma3 / gemma3-it | 4B-27B | všestranný výkon / cena / rýchlosť |
| 3 | dolphin-llama3.1 | 8B-70B | agentické úlohy, tool calling |
| 4 | deepseek-r1 / deepseek-coder-v3 | 7B-67B | kódovanie, matematika, reasoning |
| 5 | phi-4 / phi-4-mini | 3.8B-14B | extrémne rýchly, dobrý reasoning |
| 6 | llama3.2 / llama3.1 | 1B-70B | stabilita, dlhodobo najviac fine-tunov |
| 7 | mistral-nemo / mistral-large-3 | 12B-123B | multimodálny, enterprise kvalita |

V našich príkladoch budeme používať model `gemma3:1b` a model
`ministral-3:3b`.

## Spustenie modelu Gemma 3

Gemma 3 je otvorený jazykový model od Google DeepMind, ktorý je dostupný vo
veľkostiach 270M, 1B, 4B, 12B a 27B parametrov. Jeho hlavné prednosti zahŕňajú
výborný pomer výkon/cena/rýchlosť, čo z neho robí všestranný model vhodný pre
väčšinu úloh. Napriek menšej veľkosti dosahuje prekvapivo kvalitné výsledky a
ponúka dobrú multijazyčnú podporu, vrátane slovenčiny. Variant 4B má nízke
hardvérové nároky a beží pohodlne aj na bežných počítačoch.

```bash
$ ollama pull gemma3:1b
$ ollama list
NAME         ID              SIZE      MODIFIED       
gemma3:1b    8648f39daa8f    815 MB    10 minutes ago  
$ ollama run gemma3:1b 
>>> Is Pluto a Planet? Okay, let's break down the complex
and fascinating question of whether Pluto is still a planet. The short answer
is: **mostly, but with a significant caveat.**
...
```

Pomocou týchto príkazov si stiahneme model `gemma3:1b` a spustíme ho. Po
spustení máme k dispozícii interaktívny režim, kde môžeme klásť otázky.

Model môžeme používať aj cez REST API, ktoré Ollama poskytuje na porte 11434.

```bash
$ xh :11434/api/chat model=gemma3:1b stream:=false messages:='[{"role": "user", "content": "What is the capital of Slovakia?"}]'
HTTP/1.1 200 OK
Content-Length: 367
Content-Type: application/json; charset=utf-8
Date: Mon, 26 Jan 2026 14:00:26 GMT

{
    "model": "gemma3:1b",
    "created_at": "2026-01-26T14:00:26.110078707Z",
    "message": {
        "role": "assistant",
        "content": "The capital of Slovakia is **Bratislava**. \n\nIt's a lovely city! 😊"
    },
    "done": true,
    "done_reason": "stop",
    "total_duration": 794772131,
    "load_duration": 194088768,
    "prompt_eval_count": 16,
    "prompt_eval_duration": 77271035,
    "eval_count": 21,
    "eval_duration": 510297773
}
```

Streamovanie vypneme pomocou parametra `stream:=false` a pošleme požiadavku na
endpoint `/api/chat`. Model nám vráti odpoveď vo formáte JSON, ktorá obsahuje
odpoveď a relevantné metadáta.

```bash
$ xh -b :11434/api/chat model=gemma3:1b messages:='[{"role": "user", "content": "Is Pluto a planet?"}]' | jq -j '.message.content'
```

Tento príkaz využíva nástroj `xh` na odoslanie požiadavky a `jq` na získanie
len textovej odpovede. Voľba `-b` nástroja `xh` znamená "body only"; zobrazí sa
len telo odpovede (bez HTTP hlavičiek). Pomocou voľby `-j` nástroja `jq` sa
zabezpečí, že výstup bude bez uvodzoviek a na jednom riadku.

Takto dostaneme len čistú textovú odpoveď bez JSON štruktúry a formátovania.

## Oficiálna knižnica ollama

Pre jazyk Python máme natívnu knižnicu `ollama`, ktorá poskytuje jednoduché API
špeciálne navrhnuté pre Ollama.

```bash
$ uv add -U ollama
```

Knižnicu si nainštalujeme pomocou `uv` nástroja. Namiesto `pip` nástroja sme
použili `uv` manažér. V súčasnosti je to pre prácu s modernými AI nástrojmi na
Linuxe nevyhnutnosť.

```python
import ollama

response = ollama.chat(
    model='gemma3:1b',
    messages=[
        {
            'role': 'system', 
            'content': 'You are a helpful assistant.'
        },
        {
            'role': 'user', 
            'content': 'Is Pluto a planet?'
        }
    ],
    options={'temperature': 0.15}
)

print(response['message']['content'])
```

V tomto príklade vytvoríme jednoduchý chat s modelom `gemma3:1b`. Nastavíme
systémovú správu, ktorá definuje správanie modelu, a používateľskú správu s
konkrétnou požiadavkou. Parameter `temperature` nastavený na 0.15 zabezpečí
viac deterministickejšie a konzistentnejšie odpovede. Výsledok dostaneme cez
slovníkový `content` kľúč.

### Streaming odpovede

Streamovanie je užitočné pri generovaní dlhších textov, pretože umožňuje
zobrazovať odpoveď postupne počas jej generovania.

```python
import ollama

stream = ollama.chat(
    model='gemma3:1b',
    messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
    stream=True,
)

for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)
```

Nastavením `stream=True` dostaneme iterovaný objekt, cez ktorý prechádzame v
cykle. Každý chunk obsahuje časť odpovede, ktorú okamžite vypíšeme bez nového
riadku (`end=''`) a s okamžitým vyprázdnením bufferu (`flush=True`), čo vytvára
plynulý efekt písania.

### Štruktúrované výstupy

V nedávnej dobe pribudla podpora štruktúrovaných výstupov, ktoré umožňujú
modelu generovať odpovede vo formáte JSON.

```bash
$ ollama pull ministral-3:3b
```

Keďže ide o náročnejšiu úlohu, použijeme väčší model `ministral-3:3b`.

```python
from ollama import chat

text = """
Extract information about people mentioned in the following text. For each
person, provide their name, age, and city of residence in a structured JSON
format. John Doe is a software engineer living in New York. He
is 30 years old and enjoys hiking and photography. Jane Smith is a graphic
designer based in San Francisco. She is 28 years old and loves painting and
traveling."""

response = chat(
  model='ministral-3:3b',
  messages=[{'role': 'user', 'content': text}],
  format='json'
)

print(response.message.content)
```

Parameter `format='json'` povie modelu aby generoval odpoveď vo formáte JSON.
Model sa pokúsi vytvoriť platnú JSON štruktúru s relevantnými informáciami
podľa zadania.

```bash
$ uv run python main.py 
{"people": [
    {
        "name": "John Doe",
        "age": 30,
        "city_of_residence": "New York"
    },
    {
        "name": "Jane Smith",
        "age": 28,
        "city_of_residence": "San Francisco"
    }
]}
```

### OpenAI-kompatibilné rozhranie

Ollama poskytuje kompatibilné rozhranie s OpenAI API, čo umožňuje jednoduchú
migráciu existujúceho kódu.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1", 
    api_key="ollama" # dummy hodnota - ignoruje sa
)  

response = client.responses.create(
    model="gemma3:1b", input="Write a haiku about a gray, winter day."
)

print(response.output_text)
```

Knižnica `openai` je široko používaná v komunite. Ollama poskytuje
kompatibilný API endpoint (`/v1`), čo umožňuje použiť existujúci kód určený pre
OpenAI bez väčších zmien. Stačí upraviť `base_url` na lokálny Ollama server.
Parameter `api_key` je ignorovaný (môže byť ľubovoľný), pretože lokálne Ollama
nevyžaduje autentifikáciu.

```bash
$ uv run python ollama_openai.py 
Snow falls soft and slow,
Gray light blankets all the land,
Quiet peace descends.
```

## Grounding

Jednou z najsilnejších funkcií Ollama je podpora *groundingu*, čo umožňuje
modelom pristupovať k externým dátam a nástrojom počas generovania odpovedí.
Ide o spôsob, ako model „uzemniť" v aktuálnych, overiteľných a externých
informáciách namiesto toho, aby sa spoliehal len na to, čo má naučené z
tréningu.

Jazykové modely sú skvelé v generovaní textu, ale ich vedomosti sú vždy len
tak aktuálne, ako dáta, na ktorých boli trénované. Grounding tento problém
rieši.

Ollama využíva svoj vlastné properietárne vyhľadávanie dostupné cez
`https://ollama.com/api/web_search` a `https://ollama.com/api/web_fetch`
endpointy.

```bash
export OLLAMA_API_KEY="my_secret_key"
```

Pre webové vyhľadávanie sa potrebujeme zaregistrovať na `ollama.com` a získať
API kľúč. Ollama umožňuje registráciu prostredníctvom Google alebo Github.
Následne nastavíme premennú prostredia `OLLAMA_API_KEY` s naším kľúčom.

```python
import ollama

response = ollama.web_search("What are Vedas?", max_results=6)

for result in response.results:
    print('--- Search Result ---')
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Content: {result.content}\n")
    print("---------------\n")

print(f"Total Results: {len(response.results)}")
```

Funkcia `ollama.web_search` vykoná webové vyhľadávanie a vráti zoznam
nájdených výsledkov. Počet výsledkov môžeme špecifikovať pomocou voľby
`max_results`.

```python
from ollama import web_fetch

result = web_fetch('https://docs.ollama.com/api/introduction')
print(result.content)
```

V prípade jedného zdroja môžeme použiť funkciu `ollama.web_fetch`, ktorá
načíta obsah zadaného URL a vráti ho ako text.

## Jednoduchá analýza dát

V nasledujúcom príklade ukážeme, ako môžeme použiť Ollama pre jednoduchú
analýzu dát. V tomto príklade budeme pracovať s dátami o používateľoch, ktoré
sú uložené v súbore `users.csv`:

```csv
id,first_name,last_name,email,occupation,salary,created_at
1,Jana,Nováková,jana.novakova@gmail.com,Software Engineer,3200.0,2026-01-01
2,Peter,Kováč,peter.kovac@example.com,Data Analyst,2800.0,2026-01-02
3,Lucia,Horváthová,lucia.horvathova@example.com,Project Manager,3500.0,2026-01-03
4,Martin,Tóth,martin.toth@example.com,UX Designer,3000.0,2026-01-04
5,Simona,Varga,simona.varga@example.com,QA Engineer,2700.0,2026-01-05
6,Marek,Polák,marek.polak@example.com,DevOps Engineer,3400.0,2026-01-06
7,Zuzana,Bartošová,zuzana.bartosova@example.com,HR Specialist,2500.0,2026-01-07
8,Tomáš,Urban,tomas.urban@example.com,Business Analyst,2900.0,2026-01-08
9,Barbora,Králová,barbora.kralova@simplemail.com,Marketing Manager,3300.0,2026-01-09
10,Jozef,Šimek,jozef.simek@example.com,System Administrator,3100.0,2026-01-10
11,Michaela,Dudová,michaela.dudova@example.com,Content Writer,2200.0,2026-01-11
12,Richard,Bielik,richard.bielik@example.com,Product Owner,3600.0,2026-01-12
13,Katarína,Farkašová,katarina.farkasova@gmail.com,Accountant,2600.0,2026-01-13
14,Andrej,Gregor,andrej.gregor@example.com,Network Engineer,3200.0,2026-01-14
15,Veronika,Kučerová,veronika.kucerova@gmail.com,Graphic Designer,2400.0,2026-01-15
16,Patrik,Holub,patrik.holub@gmail.com,Mobile Developer,3300.0,2026-01-16
17,Eva,Švecová,eva.svecova@example.com,Recruiter,2300.0,2026-01-17
18,Roman,Marek,roman.marek@simplemail.com,Database Administrator,3400.0,2026-01-18
19,Monika,Blažeková,monika.blazekova@example.com,Scrum Master,3100.0,2026-01-19
20,Filip,Klein,filip.klein@example.com,Web Developer,3000.0,2026-01-20
```

V súbore máme dvadsať záznamov o používateľoch vrátane ich platov. Naším
cieľom je vygenerovať report obsahujúci minimálny, maximálny, priemerný plat a
súčet platov.

```python
import ollama

file_name = 'users.csv'

with open(file_name, 'r', encoding='utf-8') as file:
    data = file.read()

    prompt = f"""Generate a report containing minimum, maximum,sum, and average of salaries 
    from the CSV data provided. Please provide the results in JSON format.\n\nData:\n{data}"""

    response = ollama.chat(
        model='ministral-3:3b',
        format='json',
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    print(response['message']['content'])
```

Príklad načíta obsah súboru `users.csv` a odosiela ho do modelu
`ministral-3:3b` spolu s požiadavkou na vygenerovanie štatistického reportu o
platoch.

```bash
$ uv run python data_analysis.py 
{"salary_statistics": {
    "minimum": 2200.0,
    "maximum": 3600.0,
    "sum": 48400.0,
    "average": 48400.0,
    "count": 20
    }
}
```

Model vráti odpoveď vo formáte JSON obsahujúcu požadované štatistiky o platoch.
V prípade sumy a priemeru platov sa model pomýlil. Na takúto úlohu je potrebné
teda použiť väčší model.

Všetky príklady z článku a mnohé ďalšie sú dostupné na GitHub repozitári
[github.com/janbodnar/Python-AI-Skolenie](https://github.com/janbodnar/Python-AI-Skolenie).

V nasledujúcich článkoch by som sa chcel venovať pokročilejším témam, ako je
tvorba agentov, fine tuning modelov, tvorba RAG systému, MCP serverov, alebo
hlbšej práci s dokumentmi.

---

> **Poznámka:** Pôvodný HTML obsah obsahoval JavaScript pre tlačidlá "Copy to
> clipboard" a CSS štýly pre tmavý/svetlý režim. Tieto interaktívne a vizuálne
> prvky neboli do Markdown formátu prevedené, keďže Markdown nepodporuje priame
> vkladanie JavaScriptu ani komplexného CSS. Pre zachovanie týchto funkcií by
> bolo potrebné použiť rozšírený Markdown renderer alebo pridať tieto prvky
> manuálne po konverzii.
