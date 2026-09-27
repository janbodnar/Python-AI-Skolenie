# JEV  

JEV je model typu System One od spoločnosti TypeSafe AI. Namiesto tvorby textu  
vracia rýchle, štruktúrované rozhodnutia s pravdepodobnosťou. Je určený najmä  
na klasifikáciu, smerovanie a ďalšie rozhodnutia, pri ktorých sú možnosti  
známe vopred.  

JEV používa tri základné primitíva: `Choice` vyberie jednu možnosť zo zoznamu,  
`Score` priradí číselnú hodnotu zo stanoveného rozsahu a `Noul` vráti  
pravdepodobnosť odpovede áno alebo nie. Výsledok preto nie je voľný text, ale  
hodnota definovaná schémou.  

Model pracuje ako rýchly rozhodovací komponent v systéme. Je vhodný napríklad  
na filtrovanie, smerovanie požiadaviek, hodnotenie rizika alebo spracovanie  
veľkého množstva záznamov. Nie je určený na písanie e-mailov, sumarizáciu ani  
iné úlohy, pri ktorých treba vytvárať dlhší voľný text.  

JEV je dostupný cez HTTP API aj cez oficiálny Python SDK. Príklady nižšie  
používajú premennú prostredia `JEV_API_KEY` a model `jev-latest`.  

## Jednoduché rozhodnutie cez HTTP API  

Prvý príklad odošle požiadavku priamo pomocou knižnice `requests`. Model  
posúdi, či je zlyhaná platba naliehavá, a vráti pravdepodobnosť odpovede áno.  

```python
"""Make a simple structured decision with Jev using requests.

Usage:
    export JEV_API_KEY=...
    uv run python simple_requests.py
"""

import os
import sys

import requests

API_URL = "https://api.typesafe.ai/v1/systemone"

api_key = os.getenv("JEV_API_KEY")
if not api_key:
    sys.exit("JEV_API_KEY is not set.")

response = requests.post(
    API_URL,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "jev-latest",
        "state": "My payment has failed three times and payroll is due today.",
        "questions": {
            "is_urgent": {
                "type": "noul",
                "instructions": "Does this issue need urgent attention?",
            }
        },
    },
    timeout=30,
)
response.raise_for_status()

urgency = response.json()["answers"]["is_urgent"]["noul"]
print(f"Urgency probability: {urgency:.1%}")

if urgency > 0.8:
    print("Escalate this issue.")

```


## Jednoduché rozhodnutie cez Python SDK  

Tento príklad robí rovnaké rozhodnutie ako predchádzajúci, ale používa  
oficiálny Python SDK. Typ `Noul` pripraví otázku a klient spracuje odpoveď  
ako štruktúrovaný objekt.  

```python
"""Make a simple structured decision with Jev using the TypeSafe Python SDK.

Usage:
    export JEV_API_KEY=...
    uv run python simple_sdk.py
"""

import os
import sys

from typesafe_sdk import Noul, TypeSafeClient

api_key = os.getenv("JEV_API_KEY")
if not api_key:
    sys.exit("JEV_API_KEY is not set.")

with TypeSafeClient(api_key=api_key, model="jev-latest") as client:
    response = client.system_one(
        state="My payment has failed three times and payroll is due today.",
        questions={
            "is_urgent": Noul(
                instructions="Does this issue need urgent attention?",
            )
        },
    )

urgency = response.nouls["is_urgent"].noul
print(f"Urgency probability: {urgency:.1%}")

if urgency > 0.8:
    print("Escalate this issue.")
```


## Klasifikácia ticketov  

Príklad načíta podporné tikety zo súboru CSV a každý zaradí do jedného zo  
štyroch tímov: fakturácia, technická podpora, účet alebo doprava. Výsledky  
uloží do nového CSV súboru spolu s pravdepodobnosťou vybranej kategórie.  

```csv
ticket_id,subject,description,channel
1,Invoice not received,"I was charged on the 3rd but never got an invoice by email.",email
2,Refund request,"Please refund the duplicate payment made for order 88213.",email
3,Wrong amount charged,"My subscription was billed twice this month.",phone
4,Update payment method,"I need to change the credit card on file for my account.",web
5,Proration question,"Why was I charged a prorated amount after upgrading my plan?",chat
6,App crashes on startup,"The mobile app closes immediately after the splash screen on Android 14.",email
7,Cannot log in,"Incorrect password error even after resetting my credentials.",phone
8,Slow dashboard loading,"The reports dashboard takes over a minute to load for large accounts.",web
9,Export fails,"Downloading the CSV report returns a 500 server error.",chat
10,Sync not working,"Calendar events stopped syncing between the web app and my phone.",email
11,Change billing address,"Please update the address on my account to 12 Elm Street, Portland.",web
12,Delete my data,"I want my account and all associated personal data permanently deleted.",email
13,Two-factor setup,"How do I enable two-factor authentication on my profile?",chat
14,Merge duplicate accounts,"Two accounts were created with the same email by mistake.",phone
15,Transfer ownership,"I am leaving the company and need to transfer admin rights to a colleague.",email
16,Order never arrived,"My package was marked delivered 5 days ago but I never received it.",phone
17,Tracking link broken,"The tracking number in my confirmation email returns no results.",email
18,Wrong item shipped,"I ordered a blue medium shirt and received a green large one.",chat
19,Change delivery date,"Can I reschedule delivery to next Tuesday afternoon?",web
20,Missing accessories,"The charger was not included in the box with my new device.",email
```



```python
"""Classify support tickets with JEV's typed Choice question.

Usage:
    export JEV_API_KEY=...
    uv run python classify_tickets.py
"""

import csv
import os

from typesafe_sdk import Choice, TypeSafeClient

INPUT_FILE = "tickets.csv"
OUTPUT_FILE = "tickets_classified.csv"

CATEGORIES = {
    "billing": "Payments, invoices, refunds, charges, subscription plans",
    "technical": "Bugs, crashes, errors, login failures, performance, integrations",
    "account": "Profile settings, personal data, authentication setup, ownership transfer",
    "shipping": "Deliveries, packages, tracking, order fulfilment, wrong or missing items",
}

LABELS = {
    "billing": "Billing",
    "technical": "Technical",
    "account": "Account",
    "shipping": "Shipping",
}


def main() -> None:
    api_key = os.getenv("JEV_API_KEY")
    if not api_key:
        raise SystemExit("JEV_API_KEY is not set.")

    with open(INPUT_FILE, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise SystemExit(f"No rows found in {INPUT_FILE}.")

    category_question = Choice(
        instructions="Which team should handle this support ticket?",
        criteria=CATEGORIES,
    )
    results = []
    with TypeSafeClient(api_key=api_key, model="jev-latest") as client:
        for index, row in enumerate(rows, start=1):
            state = {
                "subject": row["subject"],
                "description": row["description"],
                "channel": row["channel"],
            }
            response = client.system_one(
                state=state,
                questions={"category": category_question},
            )
            answer = response.choices["category"]
            label = LABELS.get(answer.choice, answer.choice)
            results.append(
                {
                    **row,
                    "predicted_category": label,
                    "confidence": f"{answer.confidence:.2f}",
                }
            )
            print(
                f"[{index}/{len(rows)}] ticket {row['ticket_id']}: "
                f"{label} {answer.confidence:.2f}"
            )

    fieldnames = list(rows[0]) + ["predicted_category", "confidence"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    counts = {}
    for row in results:
        category = row["predicted_category"] or "(failed)"
        counts[category] = counts.get(category, 0) + 1
    print(f"\nWrote {len(results)} rows to {OUTPUT_FILE}")
    print("Distribution:", ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))


if __name__ == "__main__":
    main()
```

## Analýza sentimentu  

Tento príklad klasifikuje slovenské filmové recenzie pomocou `Choice` a meria  
aj silu vyjadreného názoru pomocou `Score`. Jedna požiadavka spracuje všetky  
recenzie a program vypíše sentiment aj intenzitu pre každý záznam.  

```python
"""Analyze Slovak movie-review sentiment with Jev's Choice and Score questions.

Usage:
    export JEV_API_KEY=...
    uv run python sentiment_analysis.py
"""

import os
import sys

from typesafe_sdk import Choice, Score, TypeSafeClient

slovak_movie_reviews = {
    1: "Príbeh bol úplne pútavý a herecké výkony brilantné. Nemohol som sa odtrhnúť ani na sekundu!",
    2: "Tempo bolo mimoriadne pomalé a postavy nemali žiadnu hĺbku. Nudil som sa už v polovici.",
    3: "Hoci vizuálne efekty boli ohromujúce, dej pôsobil predvídateľne a bez inšpirácie.",
    4: "Toto je filmové dielo, ktoré mi dojalo srdce. Každá scéna bola dokonalosť!",
    5: "Dialógy boli trápne a humor úplne zlyhal. Určite to nestojí za ten humbug.",
    6: "Bol to priemerný film - nie dobrý, ale ani úplná katastrofa. Niektoré časti ma bavili.",
    7: "Chemia medzi hlavnými postavami bola elektrizujúca a soundtrack fenomenálny!",
    8: "Film začal skvele, ale v druhej polovici sa úplne rozpadol. Veľké sklamanie.",
    9: "Vizualne ohromujúci film, ktorý dokonale spája akciu a emócie. Určite odporúčam!",
    10: "Premisa bola zaujímavá, ale realizácia bola slabá. Nedokázalo ma to zaujať.",
}

SENTIMENT_OPTIONS = {
    "negative": "The overall judgment of the film is unfavorable.",
    "mixed": "The review expresses a genuinely mixed or balanced judgment.",
    "positive": "The overall judgment of the film is favorable.",
}

INTENSITY_LEVELS = [
    "Little or no positive or negative feeling is expressed.",
    "A mild positive or negative opinion is expressed.",
    "A clear, moderately strong positive or negative opinion is expressed.",
    "A strong positive or negative reaction is expressed.",
    "An extremely emphatic positive or negative reaction is expressed.",
]

api_key = os.getenv("JEV_API_KEY")
if not api_key:
    sys.exit("JEV_API_KEY is not set.")

state = {"reviews": {str(review_id): text for review_id, text in slovak_movie_reviews.items()}}
questions = {}
for review_id in slovak_movie_reviews:
    questions[f"review_{review_id}_sentiment"] = Choice(
        instructions=f"Classify the overall sentiment of Slovak movie review {review_id}.",
        criteria=SENTIMENT_OPTIONS,
    )
    questions[f"review_{review_id}_intensity"] = Score(
        instructions=f"How strongly does Slovak movie review {review_id} express a positive or negative opinion?",
        criteria=INTENSITY_LEVELS,
    )

with TypeSafeClient(api_key=api_key, model="jev-latest") as client:
    response = client.system_one(state=state, questions=questions)

for review_id in slovak_movie_reviews:
    sentiment = response.choices[f"review_{review_id}_sentiment"]
    intensity = response.scores[f"review_{review_id}_intensity"]
    print(
        f"{review_id:>2}. {sentiment.choice:<8} "
        f"(confidence {sentiment.confidence:.0%}) | "
        f"intensity {intensity.score:.2f}/4 "
        f"(confidence {intensity.confidence:.0%})"
    )
```


## Odhad pohlavia podľa mena  

Príklad použije krstné meno, priezvisko a krajinu na výber kategórie `male`,  
`female` alebo `ambiguous`. Pri nízkej istote označí mužský alebo ženský  
výsledok ako nejednoznačný, aby nevytváral príliš sebavedomé tvrdenia.  


```csv
id,first_name,last_name,occupation,country,email
1,Alice,Johnson,Software Engineer,USA,alice.johnson@example.com
2,Bob,Smith,Data Scientist,Canada,bob.smith@example.com
3,Carlos,Mendez,Mechanical Engineer,Mexico,carlos.mendez@example.com
4,Diana,Novak,Product Manager,Slovakia,diana.novak@example.com
5,Ethan,Williams,DevOps Engineer,UK,ethan.williams@example.com
6,Fatima,Al-Hassan,UX Designer,UAE,fatima.alhassan@example.com
7,George,Papadopoulos,Architect,Greece,george.papadopoulos@example.com
8,Hannah,Müller,Accountant,Germany,hannah.muller@example.com
9,Ivan,Petrov,Cybersecurity Analyst,Russia,ivan.petrov@example.com
10,Julia,Costa,Marketing Manager,Brazil,julia.costa@example.com
11,Kevin,Tanaka,AI Researcher,Japan,kevin.tanaka@example.com
12,Laura,Bianchi,Graphic Designer,Italy,laura.bianchi@example.com
13,Mohammed,Rahman,Backend Developer,Bangladesh,mohammed.rahman@example.com
14,Nina,Svensson,Nurse,Sweden,nina.svensson@example.com
15,Oscar,Dubois,Financial Analyst,France,oscar.dubois@example.com
16,Priya,Sharma,Data Engineer,India,priya.sharma@example.com
17,Quentin,Leblanc,Game Developer,Belgium,quentin.leblanc@example.com
18,Rachel,Kim,Biologist,South Korea,rachel.kim@example.com
19,Stefan,Kowalski,Project Manager,Poland,stefan.kowalski@example.com
20,Tina,Nguyen,Frontend Developer,Vietnam,tina.nguyen@example.com
21,Umar,Abdi,Teacher,Kenya,umar.abdi@example.com
22,Vera,Popescu,Lawyer,Romania,vera.popescu@example.com
23,William,O'Brien,Cloud Architect,Ireland,william.obrien@example.com
24,Xiao,Liu,Robotics Engineer,China,xiao.liu@example.com
25,Yasmine,Benali,Journalist,Algeria,yasmine.benali@example.com
26,Zara,Ahmed,Pharmacist,Pakistan,zara.ahmed@example.com
27,Andrei,Volkov,Database Administrator,Ukraine,andrei.volkov@example.com
28,Beatriz,Santos,Civil Engineer,Portugal,beatriz.santos@example.com
29,Chen,Wei,Machine Learning Engineer,Taiwan,chen.wei@example.com
30,Daria,Horvat,HR Specialist,Croatia,daria.horvat@example.com
```


```python
"""Add a gender column to users.csv using JEV's typed Choice question.

Usage:
    export JEV_API_KEY=...
    uv run python infer_gender2.py
"""

import csv
import os

from typesafe_sdk import Choice, TypeSafeClient

INPUT_FILE = "users.csv"
OUTPUT_FILE = "users_with_gender2.csv"
AMBIGUOUS_THRESHOLD = 0.60

GENDER_OPTIONS = {
    "male": "The name is conventionally used by men.",
    "female": "The name is conventionally used by women.",
    "ambiguous": "The name has no reliable gender signal in its cultural context.",
}


def main() -> None:
    api_key = os.getenv("JEV_API_KEY")
    if not api_key:
        raise SystemExit("JEV_API_KEY is not set.")

    with open(INPUT_FILE, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise SystemExit(f"No rows found in {INPUT_FILE}.")

    gender_question = Choice(
        instructions="Which gender category does this name conventionally indicate?",
        criteria=GENDER_OPTIONS,
    )
    results = []
    with TypeSafeClient(api_key=api_key, model="jev-latest") as client:
        for index, row in enumerate(rows, start=1):
            state = {
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "country": row["country"],
            }
            response = client.system_one(
                state=state,
                questions={"gender": gender_question},
            )
            answer = response.choices["gender"]
            label = answer.choice
            if label in ("male", "female") and answer.confidence < AMBIGUOUS_THRESHOLD:
                label = f"ambiguous (model said {label})"

            results.append(
                {
                    **row,
                    "gender": label,
                    "confidence": f"{answer.confidence:.2f}",
                }
            )
            name = f"{row['first_name']} {row['last_name']}"
            print(f"[{index}/{len(rows)}] {name}: {label} {answer.confidence:.2f}")

    fieldnames = list(rows[0]) + ["gender", "confidence"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nWrote {len(results)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```


## Detekcia clickbaitu  

Príklad vyhodnotí titulky videí pomocou troch otázok typu `Noul`: či ide  
o clickbait, či titulok zamlčiava pointu a či obsahuje prehnané tvrdenie.  
Okrem výsledného skóre uloží aj neistý interval a pomocné skóre do CSV.  


```csv
id,author,title,date_published
yt_001,Tech Unboxed,"I Bought a $1,000 Mystery Box from the Dark Web (DON'T DO THIS!)",2026-09-18
yt_002,LifeHacks Daily,10 Secret iPhone Features Apple DOESN'T Want You to Know!,2026-09-18
yt_003,ProProductivity,How I Organize My Entire Life in Notion (2026 Setup),2026-09-17
yt_004,CodeWithChris,Mastering Python Pandas for Data Cleaning in 15 Minutes,2026-09-17
yt_005,Fitness Overhaul,Stop Doing Squats Like THIS (You're Ruining Your Knees!!),2026-09-16
yt_007,Wealth Mastery,DO NOT Buy a House in 2026 Until You Watch THIS Video!,2026-09-15
yt_008,HandyDan DIY,How to Fix a Leaking Kitchen Faucet in 10 Minutes,2026-09-15
yt_009,GamerRealm,I Played GTA 6 Early... AND IT'S NOT WHAT WE EXPECTED!,2026-09-14
yt_011,Data Wiz,"Excel Basics: VLOOKUP, XLOOKUP, and Pivot Tables Explained",2026-09-13
yt_015,ChallengeKing,I Tried Eating Only Gas Station Food for 30 Days (REGRET IT),2026-09-11
```

```python
"""Detect clickbait YouTube titles with JEV's typed Noul questions.

Usage:
    export JEV_API_KEY=...
    uv run python detect_clickbait.py
"""

import csv
import os

from typesafe_sdk import Noul, TypeSafeClient

INPUT_FILE = "yt_videos.csv"
OUTPUT_FILE = "yt_videos_scored.csv"
THRESHOLD = 0.5
BAND = 0.15


def main() -> None:
    api_key = os.getenv("JEV_API_KEY")
    if not api_key:
        raise SystemExit("JEV_API_KEY is not set.")

    with open(INPUT_FILE, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise SystemExit(f"No rows found in {INPUT_FILE}.")

    questions = {
        "is_clickbait": Noul(
            instructions=(
                "Is this title clickbait? Judge whether it uses curiosity gaps, "
                "withholding, sensational framing, shock, or manufactured urgency."
            ),
            criteria={
                "true": "Uses curiosity gaps, withholding, sensational or shock framing",
                "false": "States its subject plainly and is informative on its face",
            },
        ),
        "withholds_payoff": Noul(
            instructions=(
                "Does the title withhold the actual answer, result, or subject that it "
                "promises to deliver?"
            ),
            criteria={
                "true": "Withholds what the viewer would learn",
                "false": "Names the specific subject, result, or question up front",
            },
        ),
        "overstated_claim": Noul(
            instructions=(
                "Does the title make an implausible, absolute, or unverifiable claim?"
            ),
            criteria={
                "true": "Uses absolutes, scare framing, or implausible claims",
                "false": "Claims are proportionate and plausible",
            },
        ),
    }

    results = []
    with TypeSafeClient(api_key=api_key, model="jev-latest") as client:
        for index, row in enumerate(rows, start=1):
            response = client.system_one(
                state={"author": row["author"], "title": row["title"]},
                questions=questions,
            )
            scores = response.nouls
            score = scores["is_clickbait"].noul
            verdict = "uncertain" if abs(score - THRESHOLD) <= BAND else (
                "clickbait" if score > THRESHOLD else "not clickbait"
            )

            results.append({**row, "verdict": verdict, "score": f"{score:.2f}"})

            title = row["title"]
            if len(title) > 58:
                title = title[:55] + "..."
            print(
                f"[{index}/{len(rows)}] {row['id']}: {verdict:14s} {score:.2f} "
                f"(withhold {scores['withholds_payoff'].noul:.2f}, "
                f"overstate {scores['overstated_claim'].noul:.2f}) {title}"
            )

    fieldnames = list(rows[0]) + ["verdict", "score"]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    counts = {}
    for row in results:
        counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
    print(f"\nWrote {len(results)} rows to {OUTPUT_FILE}")
    print("Distribution:", ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))


if __name__ == "__main__":
    main()
```



## Smerovanie otázok  

Tento príklad používa JEV ako router. Pre každú otázku vyberie vhodný model  
podľa jej náročnosti a potom odošle otázku vybranému modelu cez OpenRouter.  
Výsledok obsahuje zvolený model aj istotu smerovania.  


```python
import os
import sys

import requests
from typesafe_sdk import Choice, TypeSafeClient

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

QUESTIONS = [
    "What is the capital of Slovakia?",
    "What is 18% of 250?",
    "Why does ice float on liquid water?",
    "Rewrite this sentence to be more concise: 'Due to the fact that it was raining, the event was postponed.'",
    "Write a Python function that removes duplicates from a list while preserving the original order.",
    "A fair coin is flipped three times. What is the probability of getting at least two heads?",
    "How do optimistic and pessimistic locking differ, and when would you choose each for a payment service?",
    "Design a zero-downtime migration from integer user IDs to UUIDs across several services and a shared database.",
    "An async order service occasionally charges a customer twice after a timeout and retry. Explain likely causes and propose safeguards.",
    "Given an algorithm that repeatedly splits an input into three equal parts and recursively processes two parts, derive its asymptotic time complexity and justify the result.",
]

MODEL_OPTIONS = {
    "deepseek/deepseek-v4.1-flash": (
        "Use for straightforward questions answerable with a fact, a short explanation, "
        "or a single reasoning step."
    ),
    "openai/gpt-6-sol": (
        "Use for moderately difficult questions needing several reasoning steps, "
        "code understanding, or synthesis."
    ),
    "anthropic/claude-opus-5.5": (
        "Use for the most difficult or ambiguous questions requiring deep analysis, "
        "complex reasoning, or sophisticated design."
    ),
}

jev_api_key = os.getenv("JEV_API_KEY")
if not jev_api_key:
    sys.exit("JEV_API_KEY is not set.")

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_api_key:
    sys.exit("OPENROUTER_API_KEY is not set.")

state = {"questions": {str(index): question for index, question in enumerate(QUESTIONS, start=1)}}
routing_questions = {
    f"route_{index}": Choice(
        instructions=(
            f"Choose the best model for answering question {index}. "
            "Base the choice on the question's difficulty and the model descriptions."
        ),
        criteria=MODEL_OPTIONS,
    )
    for index in range(1, len(QUESTIONS) + 1)
}

with TypeSafeClient(api_key=jev_api_key, model="jev-latest") as client:
    routing = client.system_one(state=state, questions=routing_questions)


def ask_openrouter(model: str, question: str) -> str:
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {openrouter_api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": question}],
            },
            timeout=120,
        )
        response.raise_for_status()
    except requests.HTTPError as error:
        details = error.response.text if error.response is not None else str(error)
        raise RuntimeError(f"OpenRouter returned an HTTP error: {details}") from error
    except requests.RequestException as error:
        raise RuntimeError(f"OpenRouter request failed: {error}") from error

    return response.json()["choices"][0]["message"]["content"]


for index, question in enumerate(QUESTIONS, start=1):
    decision = routing.choices[f"route_{index}"]
    answer = ask_openrouter(decision.choice, question)
    print(f"Q{index:02} -> {decision.choice} (routing confidence {decision.confidence:.0%})")
    print(answer)
    print()
```



## Hra Snake  

V tejto hre JEV rozhoduje o každom pohybe hada. Program mu pošle aktuálny stav  
hracej plochy a možné ťahy, potom skontroluje, či je vrátený ťah povolený.  
Lokálny kód teda vyhodnocuje pravidlá, ale samotný pohyb vyberá JEV.  


```python
"""JEv decides every single move, one step at a time.

This is snake_game2 without plan batching: one request, one move. The speed work
that still applies is kept, because none of it depends on planning ahead:

* API calls run on a worker thread, so the window never blocks on the network.
* One ``TypeSafeClient`` is reused instead of built per call.
* A tight retry policy caps each attempt, so a bad request fails fast.
* The next request is submitted in the same tick that a move is applied, so
  there is no idle gap between answers.

The cost of one step at a time is latency: the snake cannot move faster than the
API answers, roughly a quarter second per move, because the next board is unknown
until the current move is made. Local code only checks legality (walls, neck, own
body) and never chooses a move; every move played is an answer JEV gave.

Run with ``uv run python snake_game3.py`` after setting ``JEV_API_KEY``.
"""
import os
import random
import time
from concurrent.futures import Future, ThreadPoolExecutor

import arcade
from typesafe_sdk import Choice, RetryPolicy, TypeSafeClient

WINDOW_WIDTH = 832
WINDOW_HEIGHT = 720
CELL_SIZE = 32
BOARD_COLUMNS = 22
BOARD_ROWS = 16
# Board size in pixels, centred horizontally with a strip left at the bottom for status.
BOARD_WIDTH = BOARD_COLUMNS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE
BOARD_LEFT = (WINDOW_WIDTH - BOARD_WIDTH) // 2
BOARD_BOTTOM = 64

# Network policy: wait after a failure, give up after MAX_FAILURES, cap each attempt.
RETRY_DELAY = 1.0
MAX_FAILURES = 3
REQUEST_TIMEOUT = 12.0

# Cell deltas per move, plus the reverse of each so the snake cannot turn into itself.
DIRECTIONS = {"up": (0, 1), "right": (1, 0), "down": (0, -1), "left": (-1, 0)}
OPPOSITE = {"up": "down", "right": "left", "down": "up", "left": "right"}
ARROWS = {"up": "^", "right": ">", "down": "v", "left": "<"}

# Palette used by the board, grid lines, text, and warnings.
BACKGROUND = (15, 25, 29)
BOARD_COLOR = (20, 38, 40)
GRID_COLOR = (29, 51, 52)
TEXT_COLOR = (228, 241, 225)
MUTED_COLOR = (134, 165, 153)
ACCENT_COLOR = (131, 220, 91)
WARN_COLOR = (232, 146, 106)

LEGEND = {"H": "snake head", "o": "snake body", "A": "apple", ".": "empty"}

# The snake is a tuple of (column, row) cells, head first.
Snake = tuple[tuple[int, int], ...]
Cell = tuple[int, int]


def moves_for(snake: Snake, heading: str, apple: Cell) -> dict[str, tuple[Cell, bool]]:
    """Legal moves by the rules of Snake: no walls, no neck, no own body."""
    head_x, head_y = snake[0]
    moves: dict[str, tuple[Cell, bool]] = {}
    for name, (delta_x, delta_y) in DIRECTIONS.items():
        if name == OPPOSITE[heading]:
            continue  # reversing would run into the neck
        target = (head_x + delta_x, head_y + delta_y)
        if not (0 <= target[0] < BOARD_COLUMNS and 0 <= target[1] < BOARD_ROWS):
            continue  # off the board
        eats = target == apple
        # The tail vacates its cell on the same tick, unless the move eats the apple.
        occupied = set(snake) if eats else set(snake[:-1])
        if target not in occupied:
            moves[name] = (target, eats)
    return moves


def grid_rows(snake: Snake, apple: Cell) -> list[str]:
    """ASCII board, top row first, so JEV can see the whole position at once."""
    body = set(snake[1:])
    rows = []
    for row in range(BOARD_ROWS - 1, -1, -1):  # top row first
        rows.append(
            "".join(
                "H" if (column, row) == snake[0]
                else "A" if (column, row) == apple
                else "o" if (column, row) in body
                else "."
                for column in range(BOARD_COLUMNS)
            )
        )
    return rows


def board_signature(round_id: int, snake: Snake, apple: Cell) -> int:
    """Identity of a board, so an answer for an older one can be rejected."""
    # Stamped on a request and returned with the answer; compared again on arrival.
    return hash((round_id, tuple(snake), apple))


class JevSnake(arcade.Window):
    def __init__(self) -> None:

        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, "JEV Snake")
        arcade.set_background_color(BACKGROUND)

        # Sprites: head and body are rebuilt per move, the apple is moved in place.
        self.head_texture = arcade.load_texture("head32.png")
        self.body_texture = arcade.load_texture("dot32.png")
        self.apple_texture = arcade.load_texture("apple32.png")
        self.snake_sprites = arcade.SpriteList()
        self.apple_sprites = arcade.SpriteList()
        self.apple_sprite = arcade.Sprite(self.apple_texture)
        self.apple_sprites.append(self.apple_sprite)

        # One worker thread owns all API calls, so the window never blocks.
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="jev")
        self.api_key = os.getenv("JEV_API_KEY")
        self.random = random.Random()
        self._client: TypeSafeClient | None = None

        # Request/answer state: at most one pending future, plus the answer it produced.
        self.pending: Future[tuple[int, str | None, str | None]] | None = None
        self.decision: str | None = None
        self.last_choice: str | None = None
        self.history: list[str] = []
        self.note = ""
        self.retry_after = 0.0
        self.failures = 0
        self.error: str | None = None
        self.round_id = 0
        self.paused = False
        self.game_over = False
        self.won = False
        self.status = ""
        self._reset_round()

        # Labelled text objects are created once and only their strings change per frame.
        self._text_title = arcade.Text("JEv SNAKE", BOARD_LEFT, 672, TEXT_COLOR, 27, bold=True)
        self._text_score = arcade.Text("", BOARD_LEFT + BOARD_WIDTH, 672, TEXT_COLOR, 16, anchor_x="right")
        self._text_moves = arcade.Text("", BOARD_LEFT + BOARD_WIDTH, 644, MUTED_COLOR, 12, anchor_x="right")
        self._text_chosen = arcade.Text("", BOARD_LEFT, 616, ACCENT_COLOR, 15, bold=True)
        self._text_history = arcade.Text("", BOARD_LEFT + BOARD_WIDTH, 616, MUTED_COLOR, 13, anchor_x="right")
        self._text_status = arcade.Text("", BOARD_LEFT, 36, MUTED_COLOR, 12)
        self._text_pause = arcade.Text(
            "", BOARD_LEFT + BOARD_WIDTH, 36, MUTED_COLOR, 12, anchor_x="right"
        )
        self._text_error = arcade.Text("", BOARD_LEFT, 12, WARN_COLOR, 11)
        self._text_overlay = arcade.Text(
            "", WINDOW_WIDTH / 2, BOARD_BOTTOM + BOARD_HEIGHT / 2 + 12,
            TEXT_COLOR, 30, bold=True, anchor_x="center",
        )
        self._text_overlay_prompt = arcade.Text(
            "", WINDOW_WIDTH / 2, BOARD_BOTTOM + BOARD_HEIGHT / 2 - 22,
            ACCENT_COLOR, 13, bold=True, anchor_x="center",
        )
        self._text_overlay_note = arcade.Text(
            "", WINDOW_WIDTH / 2, BOARD_BOTTOM + BOARD_HEIGHT / 2 - 46,
            MUTED_COLOR, 12, anchor_x="center",
        )

    # ---------------------------------------------------------------- state

    def _reset_round(self) -> None:
        self.round_id += 1  # new round id invalidates any answer still in flight
        if self.pending is not None:
            self.pending.cancel()

        self.pending = None
        self.decision = None
        self.last_choice = None
        self.history = []
        self.note = ""
        self.retry_after = 0.0
        self.failures = 0
        self.error = None
        # Start as a three-cell snake in the middle, heading right.
        center = (BOARD_COLUMNS // 2, BOARD_ROWS // 2)
        self.snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
        self.direction = "right"
        self.score = 0
        self.jev_moves = 0
        self.paused = False
        self.game_over = False
        self.won = False

        self._place_apple()
        self._sync_sprites()
        self._refresh_status()

    def _place_apple(self) -> None:
        # Pick uniformly from the cells the snake does not occupy.
        free = [
            (column, row)
            for column in range(BOARD_COLUMNS)
            for row in range(BOARD_ROWS)
            if (column, row) not in set(self.snake)
        ]

        if not free:
            # No cell left for an apple: the board is cleared.
            self.won = True
            self.game_over = True
            return
        
        self.apple = self.random.choice(free)
        self.apple_sprite.center_x = self._screen_x(self.apple[0])
        self.apple_sprite.center_y = self._screen_y(self.apple[1])

    def _signature(self) -> int:
        """Signature of the board as it is right now."""
        return board_signature(self.round_id, tuple(self.snake), self.apple)

    def _screen_x(self, column: int) -> float:
        """Centre of a board column in window pixels."""
        return BOARD_LEFT + column * CELL_SIZE + CELL_SIZE / 2

    def _screen_y(self, row: int) -> float:
        """Centre of a board row in window pixels."""
        return BOARD_BOTTOM + row * CELL_SIZE + CELL_SIZE / 2

    def _sync_sprites(self) -> None:
        """Rebuild the snake sprites from the cell list (simple and correct at this size)."""
        self.snake_sprites.clear()
        for index, (column, row) in enumerate(self.snake):
            sprite = arcade.Sprite(self.head_texture if index == 0 else self.body_texture)
            sprite.center_x = self._screen_x(column)
            sprite.center_y = self._screen_y(row)
            if index == 0:
                # Point the head sprite along the current heading.
                sprite.angle = {"right": 0, "up": 90, "left": 180, "down": 270}[self.direction]
            self.snake_sprites.append(sprite)

    def _refresh_status(self) -> None:
        """Pick the one-line status message for the current game state."""
        if self.game_over:
            self.status = self.note or (
                "Board cleared - every cell is snake" if self.won else "Game over"
            )
        elif not self.api_key:
            self.status = "JEV_API_KEY is not set"
        elif self.failures >= MAX_FAILURES:
            self.status = f"JEV unreachable after {self.failures} tries - press R to retry"
        elif self.note:
            self.status = self.note
        elif self.decision is not None:
            self.status = f"JEV chose {self.decision.upper()} - applying it now"
        elif self.pending is not None:
            self.status = (
                f"JEV chose {self.last_choice.upper()} - choosing the next move"
                if self.last_choice
                else "JEV is choosing the next move"
            )
        else:
            self.status = (
                f"JEV chose {self.last_choice.upper()}"
                if self.last_choice
                else "Waiting for JEV"
            )

    # ------------------------------------------------------- JEv decisions

    def _client_for(self, api_key: str) -> TypeSafeClient:
        """Reuse one client on the worker thread instead of building one per call."""
        if self._client is None:
            self._client = TypeSafeClient(
                api_key=api_key,
                model="jev-latest",
                retry=RetryPolicy(max_retries=1, timeout=REQUEST_TIMEOUT),
            )
        return self._client

    def _ask(self, round_id: int, snake: Snake, heading: str, apple: Cell,
             score: int, api_key: str) -> tuple[int, str | None, str | None]:
        """Ask JEV for the next single move. Runs on the worker thread."""
        signature = board_signature(round_id, snake, apple)
        moves = moves_for(snake, heading, apple)
        if not moves:
            return signature, None, None  # trapped: an empty answer is not an error

        # Describe every legal move by how it changes the distance to the apple.
        head = snake[0]
        distance = abs(head[0] - apple[0]) + abs(head[1] - apple[1])
        criteria = {}
        for name, (cell, eats) in moves.items():
            if eats:
                criteria[name] = f"Move {name} to {list(cell)} and eat the apple now."
                continue
            change = abs(cell[0] - apple[0]) + abs(cell[1] - apple[1]) - distance
            relation = (
                f"closer by {-change}" if change < 0
                else f"farther by {change}" if change > 0
                else "the same distance"
            )
            criteria[name] = (
                f"Move {name} to {list(cell)}; it is {relation} (distance "
                f"{abs(cell[0] - apple[0]) + abs(cell[1] - apple[1])} instead of {distance})."
            )

        state = {
            # Everything JEV needs to judge the position: grid, goal, and options.
            "board": {"columns": BOARD_COLUMNS, "rows": BOARD_ROWS,
                      "grid_note": "top row first; cell (0,0) is the bottom-left"},
            "grid": grid_rows(snake, apple),
            "legend": LEGEND,
            "head": list(head),
            "apple": list(apple),
            "apple_offset": {"dx": apple[0] - head[0], "dy": apple[1] - head[1],
                             "note": "positive dx is right, positive dy is up"},
            "distance_to_apple": distance,
            "heading": heading,
            "length": len(snake),
            "score": score,
            "legal_moves": {name: {"next_head": list(cell), "eats_apple": eats}
                            for name, (cell, eats) in moves.items()},
        }
        # The model is the only pilot, so the rules and priorities are stated plainly.
        instructions = (
            """You are the only pilot of this snake and no local algorithm will correct you.
            Choose the next move only. Never hit a wall or your own body and never reverse
            into your neck. Getting to the apple quickly matters most: take a move that eats
            the apple, otherwise take one that makes your distance to the apple smaller. Move
            away only when every closer move is unsafe. Keep escape routes open."""
        )
        try:
            result = self._client_for(api_key).system_one(
                state=state,
                questions={"move": Choice(instructions=instructions, criteria=criteria)},
                timeout=REQUEST_TIMEOUT,
            )
            choice = result.choices["move"].choice
        except Exception as error:  # network, auth, quota, or SDK error
            return signature, None, f"{type(error).__name__}: {error}"

        if choice not in moves:
            return signature, None, f"JEN answered {choice!r}, which is not a legal move"
        return signature, choice, None

    # --------------------------------------------------------- game loop

    def _apply(self, direction: str) -> None:
        """Move the snake one cell in the chosen direction."""
        delta_x, delta_y = DIRECTIONS[direction]
        head = (self.snake[0][0] + delta_x, self.snake[0][1] + delta_y)
        eating = head == self.apple
        self.direction = direction
        self.snake.insert(0, head)
        if eating:
            self.score += 1  # grow: keep the tail cell
            self._place_apple()
        else:
            self.snake.pop()  # no growth: drop the tail
        self._sync_sprites()

    def _request_next(self, now: float) -> None:
        """Submit at most one request at a time, as soon as the board is settled."""
        if not self.api_key or self.pending is not None or self.failures >= MAX_FAILURES:
            return
        if now < self.retry_after:
            return  # still inside the back-off window
        self.pending = self.worker.submit(
            self._ask, self.round_id, tuple(self.snake), self.direction,
            self.apple, self.score, self.api_key,
        )

    def on_update(self, delta_time: float) -> None:
        del delta_time  # the pace is set by the API answer, not by time
        if self.paused or self.game_over:
            return
        now = time.monotonic()

        if not moves_for(tuple(self.snake), self.direction, self.apple):
            # Trapped: no legal move exists, so the round is over immediately.
            self.game_over = True
            self.decision = None
            if not self.won:
                self.note = "No legal moves left - the snake is trapped"
            self._refresh_status()
            return

        if self.pending is not None and self.pending.done():
            # Collect the worker's answer; it may be an error, or None if trapped.
            try:
                signature, direction, error = self.pending.result()
            except Exception as worker_error:
                signature, direction, error = None, None, (
                    f"{type(worker_error).__name__}: {worker_error}"
                )
            self.pending = None
            if error is not None:
                self.failures += 1
                self.error = error
                self.note = error
                self.retry_after = now + RETRY_DELAY
            elif direction is None:
                # The board JEV was asked about is already gone; simply ask again.
                self.failures = 0
                self.error = None
                self.note = "JEV's answer was for an older board; asking again"
                self.retry_after = now
            elif signature != self._signature():
                # The board changed while the answer was in flight, so drop it.
                self.note = "JEV's answer no longer fits the board; asking again"
                self.retry_after = now
            else:
                # Answer matches this board: accept it as the next move.
                self.failures = 0
                self.error = None
                self.note = ""
                self.decision = direction

        if self.decision is not None:
            moves = moves_for(tuple(self.snake), self.direction, self.apple)
            if self.decision in moves:
                # Record what JEV chose before it is cleared, so the display keeps it.
                self.last_choice = self.decision
                self.history.append(self.decision)
                del self.history[:-24]  # keep only the most recent moves
                self._apply(self.decision)
                self.jev_moves += 1
            else:
                self.note = f"JEV's move ({self.decision}) is not legal any more; re-asking"
            self.decision = None

        self._request_next(now)  # ask for the next move without waiting for a frame
        self._refresh_status()

    # ----------------------------------------------------------- rendering

    def on_draw(self) -> None:
        self.clear()
        # Update only the strings that can change, then draw the text objects.
        chosen = (
            f"{ARROWS[self.last_choice]}  {self.last_choice.upper()}"
            if self.last_choice
            else "waiting"
        )
        self._text_score.text = f"APPLES  {self.score:02}"
        self._text_moves.text = f"JEV MOVES  {self.jev_moves:03}"
        self._text_chosen.text = f"JEV CHOSE   {chosen}"
        self._text_history.text = "HISTORY   " + " ".join(
            ARROWS[move] for move in self.history[-14:]
        )
        self._text_status.text = self.status
        self._text_pause.text = "P  PAUSE" if not self.paused else "P  RESUME"
        self._text_error.text = self.error or ""
        self._text_overlay.text = (
            "BOARD CLEARED" if self.won else "PAUSED" if self.paused else "GAME OVER"
        ) if self.paused or self.game_over else ""
        self._text_overlay_prompt.text = (
            "R  PLAY AGAIN" if self.game_over else "P  CONTINUE"
        ) if self.paused or self.game_over else ""
        self._text_overlay_note.text = (
            self.note if self.game_over and not self.won and self.note else ""
        )

        self._text_title.draw()
        self._text_score.draw()
        self._text_moves.draw()
        self._text_chosen.draw()
        self._text_history.draw()

        arcade.draw_lbwh_rectangle_filled(
            BOARD_LEFT, BOARD_BOTTOM, BOARD_WIDTH, BOARD_HEIGHT, BOARD_COLOR
        )
        # Grid lines: one extra line on each axis closes the top and right edges.
        for column in range(BOARD_COLUMNS + 1):
            x = BOARD_LEFT + column * CELL_SIZE
            arcade.draw_line(x, BOARD_BOTTOM, x, BOARD_BOTTOM + BOARD_HEIGHT, GRID_COLOR, 1)
        for row in range(BOARD_ROWS + 1):
            y = BOARD_BOTTOM + row * CELL_SIZE
            arcade.draw_line(BOARD_LEFT, y, BOARD_LEFT + BOARD_WIDTH, y, GRID_COLOR, 1)

        self.apple_sprites.draw()
        self.snake_sprites.draw()
        self._text_status.draw()
        self._text_pause.draw()
        self._text_error.draw()

        # Pause / game-over overlay is only drawn when one of those states is active.
        if self.paused or self.game_over:
            self._text_overlay.draw()
            self._text_overlay_prompt.draw()
            self._text_overlay_note.draw()

    # ------------------------------------------------------------- input

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        del modifiers
        if symbol == arcade.key.P and not self.game_over:
            # P toggles pause; the game loop ignores updates while paused.
            self.paused = not self.paused
            self._refresh_status()
        elif symbol == arcade.key.R:
            # R re-reads the API key and starts a fresh round.
            self.api_key = os.getenv("JEV_API_KEY")
            self._reset_round()

    def on_close(self) -> None:
        # Stop the worker and the HTTP client so the process can exit cleanly.
        self.worker.shutdown(wait=False, cancel_futures=True)
        if self._client is not None:
            self._client.close()
            self._client = None
        super().on_close()


if __name__ == "__main__":
    JevSnake()
    arcade.run()
```
