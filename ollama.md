# Ollama a Python: lokálne jazykové modely

Ollama umožňuje spúšťať veľké jazykové modely (LLM) lokálne na počítači.  
Modely tak pracujú bez odosielania textu do cudzej cloudovej služby.  

Ollama sa postará o sťahovanie modelov, ich načítanie do pamäte aj inferenciu.  
Použiť môžete napríklad modely Llama, Mistral, Gemma alebo Phi.  

## Výhody

- dáta zostávajú na vašom počítači,
- používanie lokálneho modelu nemá poplatok za jednotlivé požiadavky,
- modely možno používať aj bez internetového pripojenia,
- rovnaký server môžete volať z rôznych programovacích jazykov,
- pomocou Modelfile si môžete pripraviť vlastný model.

## Inštalácia

Ollama je dostupná pre Linux, macOS aj Windows. Inštalátor nájdete na  
stránke [ollama.com/download](https://ollama.com/download). Na Linuxe môžete  
použiť aj tento príkaz:  

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Na macOS je alternatívou Homebrew:

```bash
brew install ollama
```

Po inštalácii overte dostupnosť programu:

```bash
ollama --version
```

Ak služba nebeží automaticky, na Linuxe ju môžete spustiť takto:

```bash
systemctl start ollama
```

## Modely a príkazový riadok

Model najprv stiahnite. Príklad používa menší model `llama3.2`, ktorý je
vhodný aj na počítače s obmedzenou pamäťou:

```bash
ollama pull llama3.2
ollama run llama3.2
```

Najčastejšie príkazy:

```bash
ollama list                 # nainštalované modely
ollama ps                   # práve načítané modely
ollama show llama3.2        # informácie o modeli
ollama stop llama3.2        # uvoľnenie pamäte
ollama rm llama3.2          # odstránenie modelu
```

Veľkosť modelu ovplyvňuje potrebnú RAM. Menší model býva pomalší alebo menej  
presný, ale je praktickejší na bežnom notebooku.  

## Spôsoby volania z Pythonu

Lokálny server Ollama štandardne počúva na adrese  
`http://localhost:11434`. Z Pythonu ho môžete volať tromi bežnými spôsobmi:  

1. pomocou HTTP požiadaviek a knižnice `requests`,
2. pomocou OpenAI knižnice cez OpenAI-kompatibilný endpoint,
3. pomocou oficiálnej knižnice `ollama`.

Prvé dve možnosti sú užitočné pri existujúcej aplikácii, ktorá ich používa.   
Knižnica `ollama` však poskytuje najpriamejšie rozhranie pre Ollamu.  

### 1. Jedna ukážka s knižnicou `requests`

Nainštalujte závislosť:

```bash
pip install requests
```

Endpoint `/api/generate` vráti jednu textovú odpoveď. Parameter `stream`
je nastavený na `False`, takže odpoveď spracujeme naraz:

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2",
        "prompt": "Vysvetli v dvoch vetách, čo je Python.",
        "stream": False,
    },
    timeout=120,
)
response.raise_for_status()
print(response.json()["response"])
```

### 2. Jedna ukážka s knižnicou `openai`

Ollama poskytuje aj OpenAI-kompatibilný endpoint. Nainštalujte knižnicu:

```bash
pip install openai
```

Hodnota `api_key` sa nekontroluje, ale klient ju vyžaduje:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

answer = client.chat.completions.create(
    model="llama3.2",
    messages=[
        {"role": "user", "content": "Napíš krátky pozdrav po slovensky."},
    ],
)
print(answer.choices[0].message.content)
```

### 3. Odporúčaná knižnica `ollama`

Nainštalujte oficiálnu Python knižnicu:

```bash
pip install ollama
```

Knižnica komunikuje s lokálnou službou a sprístupňuje operácie ako `chat`,
`generate`, `embed`, `list` a `pull`.

## Základný chat

Funkcia `chat` prijíma zoznam správ s rolami `system`, `user` a `assistant`:

```python
from ollama import chat

response = chat(
    model="llama3.2",
    messages=[
        {"role": "system", "content": "Odpovedaj stručne po slovensky."},
        {"role": "user", "content": "Čo je lokálny jazykový model?"},
    ],
)

print(response.message.content)
```

Pri novších verziách knižnice možno použiť aj objektovú klientskú triedu:

```python
from ollama import Client

client = Client(host="http://localhost:11434")
response = client.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Vymenuj tri ovocné druhy."}],
)
print(response.message.content)
```

## Streamovanie odpovede

Pri dlhšej odpovedi môžete text vypisovať postupne. Parameter `stream=True`
vracia iterátor jednotlivých častí odpovede:

```python
import ollama

stream = ollama.chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Napíš krátky príbeh."}],
    stream=True,
)

for part in stream:
    print(part["message"]["content"], end="", flush=True)
print()
```

## Zachovanie histórie rozhovoru

Ollama si históriu medzi volaniami automaticky nepamätá. Aplikácia ju musí
posielať znova v zozname `messages`:

```python
import ollama

messages = []

messages.append({"role": "user", "content": "Volám sa Jana."})
reply = ollama.chat(model="llama3.2", messages=messages)
messages.append(reply["message"])

messages.append({"role": "user", "content": "Ako sa volám?"})
reply = ollama.chat(model="llama3.2", messages=messages)
print(reply["message"]["content"])
```

## Ovládanie odpovede

Možnosti `options` umožňujú nastaviť napríklad teplotu alebo dĺžku kontextu. 
Nižšia teplota zvyčajne vedie k predvídateľnejšej odpovedi:  

```python
import ollama

response = ollama.generate(
    model="llama3.2",
    prompt="Vytvor názov pre aplikáciu na učenie jazykov.",
    options={
        "temperature": 0.3,
        "num_ctx": 2048,
    },
    keep_alive="5m",
)
print(response["response"])
```

Parameter `keep_alive` určuje, ako dlho má model zostať načítaný v pamäti.  
Po skončení práce môžete model uvoľniť hodnotou `keep_alive=0`.  

## Štruktúrovaný výstup vo formáte JSON

Parameter `format="json"` požiada model o JSON. Pokyn vo výzve stále uveďte,  
pretože modelu pomáha dodržať požadované kľúče:  

```python
import json
import ollama

response = ollama.chat(
    model="llama3.2",
    messages=[{
        "role": "user",
        "content": (
            "Z textu vyber meno a mesto. Vráť iba JSON s kľúčmi "
            "name a city. Peter býva v Žiline."
        ),
    }],
    format="json",
)

person = json.loads(response["message"]["content"])
print(person["name"], person["city"])
```

Pri kritických aplikáciách výstup vždy overte. Model môže vrátiť neplatný JSON  
alebo hodnoty, ktoré nezodpovedajú vstupnému textu.  

## Embeddingy a podobnosť textov

Embedding je vektorové znázornenie textu. Hodí sa napríklad na vyhľadávanie  
podobných dokumentov alebo na jednoduchý systém otázok a odpovedí.  

Najprv stiahnite embeddingový model:

```bash
ollama pull nomic-embed-text
```

Potom vytvorte vektory pre viac textov:

```python
import ollama

texts = [
    "Python je programovací jazyk.",
    "Ollama spúšťa modely lokálne.",
    "Bratislava je hlavné mesto Slovenska.",
]

result = ollama.embed(model="nomic-embed-text", input=texts)
for text, vector in zip(texts, result["embeddings"]):
    print(len(vector), text)
```

Na porovnanie dvoch vektorov môžete použiť kosínusovú podobnosť z knižnice
`numpy`:

```python
import numpy as np

first = result["embeddings"][0]
second = result["embeddings"][1]
similarity = np.dot(first, second) / (
    np.linalg.norm(first) * np.linalg.norm(second)
)
print(f"Podobnosť: {similarity:.3f}")
```

### Slovenské vyhľadávanie s `nomic-embed-text-v2-moe`

Model `nomic-embed-text-v2-moe` je viacjazyčný a podporuje aj slovenčinu.  
Pri dokumentoch použite prefix `search_document:` a pri otázke prefix  
`search_query:`. Model má maximálnu dĺžku vstupu 512 tokenov.  

Model najprv stiahnite:

```bash
ollama pull nomic-embed-text-v2-moe
```

Nasledujúci príklad nájde slovenský dokument najpodobnejší otázke:

```python
import numpy as np
import ollama

documents = [
    "search_document: Python je programovací jazyk.",
    "search_document: Ollama spúšťa jazykové modely lokálne.",
    "search_document: Bratislava je hlavné mesto Slovenska.",
]
query = "search_query: Kde sídli slovenské hlavné mesto?"

document_vectors = ollama.embed(
    model="nomic-embed-text-v2-moe",
    input=documents,
)["embeddings"]
query_vector = ollama.embed(
    model="nomic-embed-text-v2-moe",
    input=query,
)["embeddings"][0]

scores = [
    np.dot(query_vector, vector)
    / (np.linalg.norm(query_vector) * np.linalg.norm(vector))
    for vector in document_vectors
]
best_index = int(np.argmax(scores))
print(documents[best_index])
print(f"Podobnosť: {scores[best_index]:.3f}")
```

## Správa modelov cez Python

Knižnica `ollama` umožňuje získať zoznam modelov alebo stiahnuť model priamo
z programu:

```python
import ollama

models = ollama.list()
for model in models["models"]:
    print(model["name"], model.get("size", 0))

ollama.pull("llama3.2")
```

Sťahovanie veľkého modelu môže trvať dlho a môže spotrebovať veľa miesta na
disku. V produkcii je preto vhodné kontrolovať chyby a stav sťahovania.

## Spracovanie chýb

Sieťová služba nemusí bežať alebo model nemusí byť stiahnutý. Výnimku možno
zachytiť a používateľovi zobraziť zrozumiteľnú informáciu:

```python
import ollama

try:
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": "Ahoj!"}],
    )
except ollama.ResponseError as error:
    print(f"Ollama vrátila chybu {error.status_code}: {error.error}")
else:
    print(response["message"]["content"])
```

## Odporúčania

- Pred volaním skontrolujte, či služba Ollama beží.
- Pre opakovateľné úlohy nastavte vhodnú teplotu a obmedzte dĺžku odpovede.
- Pri streamovaní ošetrite prerušenie spojenia a čiastočne vypísaný text.
- Výstupy modelu validujte pred uložením do databázy alebo ďalším spracovaním.
- Model vyberajte podľa dostupnej RAM, rýchlosti a požadovanej kvality.
- Citlivé údaje neposielajte modelu bez dôvodu, aj keď beží lokálne.

## Záver

Ollama poskytuje jednoduchý spôsob, ako používať LLM bez cloudového API.
Na rýchlu integráciu možno použiť `requests` alebo `openai`, no knižnica
`ollama` ponúka najúplnejší prístup k lokálnemu serveru. Okrem chatu podporuje
streamovanie, JSON výstup, embeddingy aj správu modelov.
