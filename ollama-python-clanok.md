# Ollama a Python: Kompletný sprievodca pre lokálne LLM

## Úvod

**Ollama** je open-source nástroj navrhnutý na spúšťanie, správu a interakciu s veľkými jazykovými modelmi (LLM) lokálne na vašom počítači. Umožňuje vývojárom a nadšencom do umelej inteligencie nasadiť výkonné modely bez spoliehania sa na cloudové služby, čím získavajú úplnú kontrolu nad súkromím dát a nákladmi.

Ollama zjednodušuje zložitosť spúšťania LLM tým, že spravuje sťahovanie modelov, pamäť a samotné spracovanie (inferenciu) prostredníctvom jednoduchého rozhrania príkazového riadka. Či už chcete experimentovať s populárnymi modelmi ako LLaMA, Mistral alebo DeepSeek, Ollama poskytuje bezproblémovú skúsenosť.

### Hlavné výhody
- **Súkromie a kontrola**: Modely bežia lokálne, žiadne dáta sa neposielajú na externé servery.
- **Nákladová efektívnosť**: Vyhnete sa poplatkom za cloudové API.
- **Offline prístup**: Možnosť používať AI bez pripojenia na internet.
- **Jednoduchá integrácia**: Skvelá podpora pre Python a JavaScript.

---

## Inštalácia

### Požiadavky na systém
- **RAM**: Aspoň 8 GB (16 GB odporúčaných pre väčšie modely).
- **Disk**: Minimálne 10 GB voľného miesta.
- **GPU (voliteľné)**: NVIDIA grafická karta s podporou CUDA pre rýchlejšie spracovanie.

### macOS
Ollama môžete nainštalovať stiahnutím oficiálneho inštalátora z [ollama.com/download](https://ollama.com/download) alebo pomocou Homebrew:
```bash
brew install ollama
```

### Windows
Stiahnite si `.exe` inštalátor z oficiálnej stránky a postupujte podľa pokynov. Ollama pobeží na pozadí ako služba.

### Linux
Na Linuxe môžete použiť jednoduchý inštalačný skript:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```
Následne spustite službu:
```bash
systemctl start ollama
```

---

## Práca s Ollama cez príkazový riadok (CLI)

Ollama poskytuje priamočiare rozhranie CLI. Tu sú najpoužívanejšie príkazy:

| Príkaz | Popis |
| --- | --- |
| `ollama run <model>` | Spustí model v interaktívnom režime |
| `ollama list` | Zoznam všetkých dostupných lokálnych modelov |
| `ollama pull <model>` | Stiahne model z registra Ollama |
| `ollama stop <model>` | Zastaví bežiaci model |
| `ollama rm <model>` | Odstráni model z lokálneho úložiska |

### Príklad spustenia modelu
Ak chcete začať četovať s modelom Llama 3, stačí zadať:
```bash
ollama run llama3
```

---

## Integrácia s Pythonom

Pre vývojárov je Ollama mimoriadne atraktívna vďaka jednoduchej integrácii. Existujú tri hlavné spôsoby, ako ju používať v Pythone.

### 1. Oficiálna knižnica `ollama`
Toto je najjednoduchší a najviac odporúčaný spôsob. Najprv si nainštalujte knižnicu:
```bash
pip install ollama
```

Príklad jednoduchého četu:
```python
import ollama

response = ollama.chat(model='llama3', messages=[
  {
    'role': 'user',
    'content': 'Prečo je obloha modrá?',
  },
])
print(response['message']['content'])
```

### 2. Použitie knižnice `requests` (REST API)
Ollama predvolene beží na porte `11434`. Môžete komunikovať priamo s jej API bez potreby špeciálnych knižníc.

```python
import requests
import json

url = "http://localhost:11434/api/generate"
payload = {
    "model": "llama3",
    "prompt": "Napíš krátku báseň o programovaní.",
    "stream": False
}

response = requests.post(url, json=payload)
print(response.json()["response"])
```

### 3. Použitie knižnice `openai`
Keďže Ollama podporuje rozhranie kompatibilné s OpenAI, môžete použiť oficiálnu OpenAI knižnicu. Stačí zmeniť `base_url`.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" # Kľúč nie je potrebný, ale knižnica ho vyžaduje
)

response = client.chat.completions.create(
    model="llama3",
    messages=[{"role": "user", "content": "Ahoj, ako sa máš?"}]
)

print(response.choices[0].message.content)
```

---

## Pokročilý príklad: Analýza dát s Phi4-mini

Ollama umožňuje používať aj menšie, vysoko efektívne modely ako **Phi4-mini**. Hoci tieto modely môžu robiť chyby, ich rýchlosť a nízke nároky na hardvér sú pôsobivé. Tu je príklad, ako použiť Ollama na analýzu CSV dát:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# Predpokladajme, že máme súbor 'zamestnanci.csv'
csv_data = """id,meno,plat
1,Ján,2500
2,Mária,3100
3,Peter,2800
4,Lucia,3500"""

prompt = f"""Z nasledujúcich CSV dát vygeneruj report, ktorý obsahuje
minimálny, maximálny, celkový a priemerný plat.\n\nDáta:\n{csv_data}"""

chat_completion = client.chat.completions.create(
    model='phi4-mini',
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print(chat_completion.choices[0].message.content)
```

---

## Záver

**Ollama** predstavuje revolúciu v tom, ako pristupujeme k veľkým jazykovým modelom. Vďaka nej už AI nie je výsadou obrovských dátových centier, ale nástrojom, ktorý môže bežať na každom modernom laptope. Kombinácia s Pythonom otvára nekonečné možnosti pre automatizáciu, analýzu dát a vývoj inteligentných aplikácií, a to všetko pri zachovaní maximálneho súkromia.

Ak ste tak ešte neurobili, stiahnite si Ollama a vyskúšajte si silu lokálnej AI ešte dnes!
