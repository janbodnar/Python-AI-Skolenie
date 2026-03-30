# Kapitola: Ollama – Spúšťanie veľkých jazykových modelov lokálne

## Úvod do Ollamy

**Ollama** je open-source nástroj navrhnutý na spúšťanie, správu a interakciu s veľkými  
jazykovými modelmi (LLM) priamo na vašom počítači. Umožňuje vývojárom, výskumníkom aj  
hobby nadšencom nasadzovať výkonné AI modely bez závislosti na cloudových službách, čím 
získavajú úplnú kontrolu nad súkromím dát a ich využitím.

Ollama zjednodušuje komplexnosť spúšťania LLM tým, že automaticky vybavuje sťahovanie modelov,  
správu pamäte a inferenciu prostredníctvom jednoduchého príkazového riadku. Či už chcete   
experimentovať s populárnymi modelmi ako **LLaMA**, **Mistral**, alebo vlastnými trénovanými  
modelmi, Ollama poskytuje bezproblémové prostredie.

## Prečo vývojári používajú Ollamu

| Výhoda | Popis |
|--------|-------|
| **Súkromie a kontrola** | Modely bežia lokálne, dáta neopúšťajú váš počítač |
| **Úspora nákladov** | Žiadne mesačné poplatky za cloudové API |
| **Experimentovanie** | Jednoduché testovanie rôznych modelov a konfigurácií |
| **Offline prístup** | AI funkcie dostupné aj bez internetu |
| **Prispôsobenie** | Vlastné modely vytvorené pomocou Modelfiles |

---

## Podporované platformy

Ollama je dostupná pre všetky hlavné operačné systémy:

- **macOS** (Apple Silicon aj Intel)
- **Windows** (Windows 10 a novšie)
- **Linux** (Ubuntu, Debian, Fedora a ďalšie distribúcie)

### Lokálny vs. Cloud režim

Ollama je primárne navrhnutá na **lokálne spustenie**, čo znamená, že LLM bežia priamo  
na vašom hardvéri. Podporuje však aj nasadenie v cloudových prostrediach, keď potrebujete 
škálovať výkon alebo zdieľať prístup s tímom. REST API umožňuje integráciu s akoukoľvek  
aplikáciou, či už beží lokálne alebo v cloude.

## Inštalácia Ollamy

### Systémové požiadavky

Pred inštaláciou sa uistite, že váš systém spĺňa tieto požiadavky:

| Komponent | Požiadavka |
|-----------|------------|
| **RAM** | Minimálne 8 GB (16 GB+ odporúčané pre väčšie modely) |
| **Disk** | Minimálne 10 GB pre aplikáciu a modely |
| **GPU** | Voliteľné: NVIDIA GPU s CUDA podporou pre rýchlejšiu inferenciu |

### Inštalácia na macOS

**Oficiálny inštalátor:**
1. Stiahnite inštalátor z [ollama.com/download](https://ollama.com/download)
2. Otvorte stiahnutý `.dmg` súbor
3. Presuňte Ollamu do priečinka Applications
4. Spustite Ollamu z Applications

**Pomocou Homebrew:**
```bash
brew install ollama
```

**Overenie inštalácie:**
```bash
ollama --version
```

### Inštalácia na Windows

1. Stiahnite inštalátor z [ollama.com/download](https://ollama.com/download)
2. Spustite `.exe` inštalátor
3. Postupujte podľa inštalačného sprievodcu
4. Ollama sa automaticky spustí ako služba na pozadí

**Overenie inštalácie (PowerShell alebo Command Prompt):**
```bash
ollama --version
```

### Inštalácia na Linux

**Pomocou inštalačného skriptu:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Tento skript stiahne a nainštaluje Ollamu, nastaví službu a nakonfiguruje potrebné oprávnenia.

**Spustenie služby:**
```bash
systemctl start ollama
```

**Overenie inštalácie:**
```bash
ollama --version
```

> **Tip pre Linux:** Pre GPU podporu sa uistite, že máte nainštalované NVIDIA ovládače a CUDA toolkit.
>  Ollama ich automaticky detekuje a využije.

---

## Základné príkazy Ollamy

Ollama poskytuje jednoduché CLI (Command Line Interface) na správu modelov a spúšťanie inferencie.

| Príkaz | Popis |
|--------|-------|
| `ollama run <model>` | Spustí model interaktívne |
| `ollama list` | Zoznam všetkých dostupných modelov |
| `ollama pull <model>` | Stiahne model z registry Ollamy |
| `ollama ps` | Zobrazí bežiace modely a procesy |
| `ollama stop <model>` | Zastaví bežiaci model |
| `ollama create <model>` | Vytvorí nový model z Modelfile |
| `ollama delete <model>` | Odstráni model z lokálneho úložiska |

### Príklady použitia

**Spustenie modelu interaktívne:**
```bash
ollama run llama2
```

**Stiahnutie modelu z registry:**
```bash
ollama pull mistral
```

**Zoznam nainštalovaných modelov:**
```bash
ollama list
```

**Odstránenie modelu:**
```bash
ollama delete llama2
```

---

## Integrácia s Pythonom

Ollama expose REST API na adrese `http://localhost:11434`, ktoré môžete využiť na integráciu s Python aplikáciami.  

### REST API Príklad

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "llama2", "prompt": "Hello there!"}
)

for line in response.iter_lines():
    if line:
        print(line.decode("utf-8"))
```

Endpoint `/api/generate` prijíma JSON payload s názvom modelu a promptom. Odpoveď je streamovaná riadok po riadku.  

### Non-Streaming Request

```python
import requests
import json

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama2",
        "prompt": "What is the capital of France?",
        "stream": False
    }
)

data = response.json()
print(data["response"])
```

### Chat Endpoint Príklad

```python
import requests
import json

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "phi4-mini",
        "messages": messages,
        "stream": False
    }
)

data = response.json()
print(data["message"]["content"])
```

### Streaming Chat Response

```python
import requests
import json

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France? Answer in one sentence."}
]

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "phi4-mini",
        "messages": messages,
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line)
        if "message" in data and "content" in data["message"]:
            print(data["message"]["content"], end="", flush=True)
print()
```

### Zoznam dostupných modelov cez API

```python
import requests

response = requests.get("http://localhost:11434/api/tags")
data = response.json()

for model in data["models"]:
    print(f"Model: {model['name']}, Size: {model['size']}")
```

---

## Použitie OpenAI Knížnice s Ollamou

Ollama poskytuje OpenAI-kompatibilný API endpoint na `http://localhost:11434/v1`. To vám umožňuje používať  
oficiálnu OpenAI Python knižnicu na interakciu s lokálnymi modelmi.

### Jednoduchý Chat

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

response = client.chat.completions.create(
    model="llama2",
    messages=[
        {"role": "user", "content": "Hello there!"}
    ]
)

print(response.choices[0].message.content)
```

### Chat so System Promptom

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]

response = client.chat.completions.create(
    model="llama2",
    messages=messages
)

print(response.choices[0].message.content)
```

### Streaming Odpoveď

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

stream = client.chat.completions.create(
    model="llama2",
    messages=[
        {"role": "user", "content": "Tell me a short story."}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

### Teplota a Ďalšie Parametre

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

response = client.chat.completions.create(
    model="llama2",
    messages=[
        {"role": "user", "content": "Write a creative poem about the moon."}
    ],
    temperature=0.9,
    max_tokens=200
)

print(response.choices[0].message.content)
```

| Parameter | Popis |
|-----------|-------|
| `temperature` | Kontroluje náhodnosť (0.2 = deterministické, 0.9 = kreatívne) |
| `max_tokens` | Obmedzuje dĺžku odpovede |
| `top_p` | Alternatíva k temperature pre sampling |

---

## Štruktúrovaný Výstup (Structured Output)

Štruktúrovaný výstup je mechanizmus, ktorý núti AI model poskytovať odpovede v špecifickom,  
predvídateľnom formáte – typicky JSON – namiesto obyčajného konverzačného textu.  

Zabezpečuje, že výstup dodržiava prísnu **schému** (blueprint kľúčov a dátových typov), čo robí  
dáta okamžite čitateľné pre počítače na automatizáciu, databázy alebo integráciu aplikácií.  

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

Tento kód demonštruje použitie štruktúrovaného výstupu s lokálnym LLM. Namiesto rozvláčného odstavca  
parameter `format='json'` núti model vrátiť dáta, ktoré váš kód môže okamžite spracovať.

---

## Zhrnutie

| Téma | Kľúčové body |
|------|--------------|
| **Čo je Ollama** | Nástroj na lokálne spúšťanie LLM modelov |
| **Výhody** | Súkromie, úspora nákladov, offline prístup |
| **Inštalácia** | Dostupná pre macOS, Windows, Linux |
| **Príkazy** | `run`, `pull`, `list`, `create`, `delete` |
| **Python integrácia** | REST API aj OpenAI-kompatibilný endpoint |
| **Štruktúrovaný výstup** | JSON formát pre automatizáciu |


## Otázky a diskusia
