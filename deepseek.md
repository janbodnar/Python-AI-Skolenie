# DeepSeek v Pythone

DeepSeek je čínska spoločnosť zaoberajúca sa výskumom a vývojom umelej  
inteligencie. Jej jazykové modely zvládajú konverzáciu, programovanie,  
matematiku a prácu s textom vo viacerých jazykoch. Najnovším modelom  
ponúkaným cez API je **DeepSeek-V4.1-Flash**: rýchly model s podporou  
uvažovania a obrázkového vstupu.  

API DeepSeek používa formát kompatibilný s OpenAI. V Pythone preto môžeme  
použiť oficiálny balík `openai` a zmeniť adresu API. Volanie API však  
nie je to isté ako lokálne spustenie modelu: požiadavky sa odosielajú  
na servery DeepSeek a účtujú sa podľa aktuálneho cenníka.  

## Dostupné modely

Názov modelu v požiadavke je API alias; označenie vydania modelu  
sa môže zmeniť bez zmeny kódu. K 28. septembru 2026 platí:  

- `deepseek-flash` smeruje na **DeepSeek-V4.1-Flash**. Podporuje  
  uvažovanie, obrázky, JSON výstup aj volanie nástrojov.  
- `deepseek-v4-pro` je v dokumentácii zachovaný starší alias.  
  Oznámenie DeepSeeku uvádza, že od 14. septembra smeruje na V4.1-Flash,  
  kým nebude dostupný V4.1-Pro.  
- `deepseek-v4-flash` a `deepseek-v4-flash-vision-exp` sú staršie názvy.  
  Pre nové projekty použite namiesto nich `deepseek-flash`.  
- `deepseek-chat` a `deepseek-reasoner` označovali režimy starších  
    modelov, napríklad V3.2 a R1. Ich plánované vyradenie bolo  
    24. júla 2026; v novom kóde ich nepoužívajte.  

V4.1-Flash je model typu Mixture of Experts s 552 miliardami parametrov.  
Podľa technickej správy aktivuje pri spracovaní vstupu približne  
8 miliárd a pri generovaní výstupu 16 miliárd parametrov. Modelové  
váhy sú zverejnené na Hugging Face, no lokálne nasadenie vyžaduje  
vhodný hardvér a softvérovú podporu. Nižšie uvedené príklady používajú  
hosťované API.  

## Príprava prostredia

Nainštalujte klientsku knižnicu a nastavte API kľúč v premennej  
prostredia. Kľúč nevkladajte priamo do zdrojového kódu ani do Gitu.  

```bash
python -m pip install openai
export DEEPSEEK_API_KEY="váš-api-kľúč"
```

Vo Windows PowerShelli použite namiesto posledného riadku:

```powershell
$env:DEEPSEEK_API_KEY="váš-api-kľúč"
```

Vytvorenie klienta použijeme v každom príklade. Premenná prostredia  
musí byť nastavená ešte pred spustením programu.  

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"
```

Každý ďalší príklad obsahuje tento úvod, aby sa dal samostatne skopírovať
do nového súboru. Pred spustením príkladu musí byť nainštalovaný balík
`openai`, nastavená premenná `DEEPSEEK_API_KEY` a dostupné internetové
pripojenie.

## Prvý program

Najjednoduchší program odošle jednu otázku a vypíše odpoveď modelu.
Je vhodný ako prvý test nastavenia API.

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": "Napíš jednu zaujímavú vetu o Slovensku."},
    ],
)

print(response.choices[0].message.content)
```

## Otázka od používateľa

Otázku nemusíme zapísať priamo do programu. Funkcia `input()` ju načíta
z klávesnice, takže ten istý program môžeme použiť viackrát.

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"

question = input("Čo sa chcete opýtať? ")
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": question},
    ],
)

print(response.choices[0].message.content)
```

## Jednoduchý chat

Každá požiadavka obsahuje zoznam správ. Správa `system` určuje  
požadované správanie asistenta a správa `user` obsahuje otázku.  
Odpoveď nájdeme v prvom výbere (`choices[0]`).  

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Odpovedaj stručne po slovensky."},
        {"role": "user", "content": "Prečo má Mesiac fázy?"},
    ],
)

print(response.choices[0].message.content)
```

## Uvažovanie

Model môže pred odpoveďou použiť režim uvažovania. Zapína sa  
parametrom `thinking` v tele požiadavky; pri knižnici OpenAI  
ho odovzdávame cez `extra_body`. `reasoning_effort` nastavuje  
úsilie uvažovania. Programu zvyčajne stačí zobraziť konečnú odpoveď.  

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": "Vypočítaj 17 % z 240 a stručne uveď postup.",
        },
    ],
    reasoning_effort="high",
    extra_body={"thinking": {"type": "enabled"}},
)

print(response.choices[0].message.content)
```

## Postupné zobrazovanie odpovede

Pri `stream=True` prichádza odpoveď po častiach. To sa hodí  
pri dlhších odpovediach, pretože používateľ nemusí čakať na celý text.  

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"

stream = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": "Vysvetli rekurziu na príklade."},
    ],
    stream=True,
)

for chunk in stream:
    text = chunk.choices[0].delta.content
    if text:
        print(text, end="", flush=True)
print()
```

## Viacťahová konverzácia

Rozhranie Chat Completions je bezstavové: server si nepamätá  
predchádzajúce správy. História sa preto posiela znovu pri každom  
volaní. Po odpovedi asistenta ju pridáme do zoznamu `messages`.  

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"

messages = [
    {"role": "user", "content": "Ktorý vrch je najvyšší na Zemi?"},
]

response = client.chat.completions.create(model=MODEL, messages=messages)
answer = response.choices[0].message.content

print(answer)

messages.append({"role": "assistant", "content": answer})

messages.append({"role": "user", "content": "A ktorý je druhý najvyšší?"})
response = client.chat.completions.create(model=MODEL, messages=messages)
print(response.choices[0].message.content)
```

## Analýza nálady v JSON

Štruktúrovaný JSON výstup je užitočný, keď odpoveď ďalej spracúva  
program. V pokyne výslovne žiadame JSON a nastavíme `response_format`.  
Pred použitím výsledku ho aj tak overíme parserom.  

```python
import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": (
                "Vyhodnoť náladu recenzie a vráť iba JSON. Použi formát "
                '{"nálada": "pozitívna|neutrálna|negatívna", "skóre": 0.0}'
            ),
        },
        {
            "role": "user",
            "content": "Film ma rozosmial a herci boli výborní.",
        },
    ],
    response_format={"type": "json_object"},
    max_tokens=200,
)

result = json.loads(response.choices[0].message.content)
print(result["nálada"], result["skóre"])
```

## Práca s obrázkom

V4.1-Flash prijíma text aj obrázok v jednej správe. Pri lokálnom  
súbore ho zakódujeme ako Base64 a vložíme do dátovej URL. Tento  
príklad očakáva obrázok `graf.png` v aktuálnom priečinku.  
Pred spustením preto uložte obrázok PNG s týmto názvom do rovnakého
priečinka ako Python súbor.

```python
import os
import base64
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"

with open("graf.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode("ascii")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Opíš hlavný trend v tomto grafe."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded_image}"
                    },
                },
            ],
        },
    ],
)

print(response.choices[0].message.content)
```

## Volanie funkcie

Model vie navrhnúť volanie funkcie, ale funkciu sám nespúšťa.  
Náš program musí skontrolovať názov a argumenty, vykonať povolenú  
operáciu a poslať výsledok späť. Ukážka používa iba ukážkové údaje,  
nie živú predpoveď počasia.  

```python
import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)
MODEL = "deepseek-flash"

tools = [
    {
        "type": "function",
        "function": {
            "name": "zisti_pocasie",
            "description": "Vráti ukážkové počasie pre zadané mesto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mesto": {
                        "type": "string",
                        "description": "Názov mesta, napríklad Bratislava.",
                    },
                },
                "required": ["mesto"],
            },
        },
    },
]

messages = [
    {"role": "user", "content": "Aké je ukážkové počasie v Bratislave?"},
]
response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools,
    extra_body={"thinking": {"type": "disabled"}},
)
assistant_message = response.choices[0].message

if not assistant_message.tool_calls:
    print(assistant_message.content)
else:
    messages.append(assistant_message)
    for tool_call in assistant_message.tool_calls:
        if tool_call.function.name != "zisti_pocasie":
            raise ValueError("Model požiadal o nepovolenú funkciu.")

        arguments = json.loads(tool_call.function.arguments)
        city = arguments["mesto"]
        result = f"Ukážková predpoveď pre mesto {city}: slnečno, 20 °C."
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
        )

    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        extra_body={"thinking": {"type": "disabled"}},
    )
    print(final_response.choices[0].message.content)
```

## Zdroje

Dokumentácia sa mení spolu s API aliasmi, preto si pred nasadením  
overte aktuálne modely a limity v oficiálnych zdrojoch.  

- [Dokumentácia DeepSeek API][api]  
- [Modely a cenník][pricing]  
- [Oznámenie o DeepSeek-V4.1-Flash][release]  
- [Príklady práce s obrázkami][vision]  

[api]: https://api-docs.deepseek.com/
[pricing]: https://api-docs.deepseek.com/quick_start/pricing
[release]: https://api-docs.deepseek.com/news/news260910
[vision]: https://api-docs.deepseek.com/guides/vision
