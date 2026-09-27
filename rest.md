# REST

## Čo je REST

REST je architektonický štýl pre webové služby. Vychádza z HTTP a používa
zdroje, ktoré sú dostupné cez adresy URL. Klient odošle požiadavku na server
a server vráti odpoveď, často vo formáte JSON.

REST nie je samostatný protokol ani konkrétna knižnica. Je to súbor pravidiel,
ktorý pomáha navrhovať jednoduché a predvídateľné API.

Typické vlastnosti REST API:

- Každý zdroj má vlastnú URL.
- HTTP metóda vyjadruje operáciu nad zdrojom.
- Každá požiadavka obsahuje všetko potrebné na jej spracovanie.
- Server si medzi požiadavkami nemusí pamätať stav klienta.
- Odpoveď obsahuje stavový kód a prípadne dáta.

## HTTP metódy

Najčastejšie používané metódy sú:

- `GET` načíta zdroj.
- `POST` vytvorí nový zdroj alebo spustí operáciu.
- `PUT` nahradí existujúci zdroj.
- `PATCH` zmení časť existujúceho zdroja.
- `DELETE` odstráni zdroj.

Napríklad API pre používateľov môže používať tieto adresy:

```text
GET    /users          zoznam používateľov
GET    /users/42       používateľ s identifikátorom 42
POST   /users          vytvorenie používateľa
PATCH  /users/42       zmena používateľa
DELETE /users/42       odstránenie používateľa
```

## Stavové kódy

HTTP odpoveď obsahuje stavový kód, ktorý stručne opisuje výsledok požiadavky.

- `200 OK` požiadavka bola úspešná.
- `201 Created` nový zdroj bol vytvorený.
- `400 Bad Request` požiadavka má nesprávny formát.
- `401 Unauthorized` chýba platná autentifikácia.
- `403 Forbidden` klient nemá potrebné oprávnenie.
- `404 Not Found` zdroj neexistuje.
- `429 Too Many Requests` klient odosiela príliš veľa požiadaviek.
- `500 Internal Server Error` chyba nastala na serveri.

## REST a JEV

JEV poskytuje HTTP API, ktoré prijíma požiadavku `POST` na adrese:

```text
https://api.typesafe.ai/v1/systemone
```

Požiadavka obsahuje model, vstupný stav a otázky. Odpoveď obsahuje odpovede
na tieto otázky v štruktúrovanom formáte. Klient preto nemusí spracovávať
voľný text, ale môže čítať konkrétne hodnoty zo známych polí.

## Python a modul requests

Modul `requests` je populárna Python knižnica na odosielanie HTTP požiadaviek.
Poskytuje pohodlné funkcie pre metódy `GET`, `POST`, `PUT` aj `DELETE`.
Vývojár musí sám pripraviť URL, hlavičky, telo požiadavky a spracovanie
odpovede.

Nasledujúci príklad odošle otázku JEV priamo cez REST API:

```python
import os
import sys

import requests

api_key = os.getenv("JEV_API_KEY")
if not api_key:
	sys.exit("JEV_API_KEY is not set.")

response = requests.post(
	"https://api.typesafe.ai/v1/systemone",
	headers={
		"Authorization": f"Bearer {api_key}",
		"Content-Type": "application/json",
	},
	json={
		"model": "jev-latest",
		"state": "Platba zlyhala trikrát a dnes je výplatný termín.",
		"questions": {
			"is_urgent": {
				"type": "noul",
				"instructions": "Vyžaduje tento problém urgentnú pozornosť?",
			}
		},
	},
	timeout=30,
)
response.raise_for_status()

urgency = response.json()["answers"]["is_urgent"]["noul"]
print(f"Pravdepodobnosť naliehavosti: {urgency:.1%}")
```

Hlavička `Authorization` posiela API kľúč. Hlavička `Content-Type` oznamuje,
že telo požiadavky je JSON. Parameter `json` v knižnici `requests` slovník
automaticky serializuje do JSON.

Volanie `raise_for_status()` vyvolá výnimku pri chybovom HTTP kóde. Vďaka tomu
sa chyba nespracuje ako bežná odpoveď. V skutočnej aplikácii je vhodné zachytiť
aj sieťové chyby, nastaviť primeraný timeout a podľa potreby použiť opakovanie.

## Vyššia úroveň: typesafe_sdk

Priame REST volanie poskytuje kontrolu, ale zároveň vyžaduje viac opakujúceho
sa kódu. Treba vytvoriť JSON, nastaviť hlavičky, skontrolovať stavový kód a
ručne nájsť odpoveď v slovníku.

Preto často používame vyššiu knižnicu, napríklad `typesafe_sdk`. Táto knižnica
je klientom nad HTTP API. Sieťovú komunikáciu vykonáva za nás a ponúka typy
`Noul`, `Choice`, `Score` a `TypeSafeClient`.

Rovnaké rozhodnutie môže cez SDK vyzerať takto:

```python
import os
import sys

from typesafe_sdk import Noul, TypeSafeClient

api_key = os.getenv("JEV_API_KEY")
if not api_key:
	sys.exit("JEV_API_KEY is not set.")

with TypeSafeClient(api_key=api_key, model="jev-latest") as client:
	response = client.system_one(
		state="Platba zlyhala trikrát a dnes je výplatný termín.",
		questions={
			"is_urgent": Noul(
				instructions="Vyžaduje tento problém urgentnú pozornosť?",
			)
		},
	)

urgency = response.nouls["is_urgent"].noul
print(f"Pravdepodobnosť naliehavosti: {urgency:.1%}")
```

SDK teda neskrýva REST API ani nemení jeho podstatu. Poskytuje pohodlnejšiu
vrstvu nad ním. Znižuje množstvo technického kódu, pomenúva typy otázok a
validuje štruktúru odpovedí ešte predtým, ako s nimi aplikácia pracuje.

## Kedy použiť ktorú vrstvu

Priame `requests` je vhodné, keď potrebujeme pochopiť API, použiť funkciu,
ktorú SDK ešte nepodporuje, alebo mať úplnú kontrolu nad HTTP požiadavkou.

Vyššia knižnica je vhodná, keď API používame pravidelne a chceme menej
opakujúceho sa kódu, lepšiu typovú kontrolu a jednoduchšie spracovanie odpovedí.
Obe možnosti používajú rovnaké HTTP API; rozdiel je v úrovni abstrakcie.
