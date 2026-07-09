# Inteligentní agenti v systémoch umelej inteligencie

**Inteligentný agent** (AI Agent) je autonómny softvérový systém, ktorý vníma svoje prostredie,  
spracováva informácie a vykonáva akcie s cieľom dosiahnuť stanovené ciele. Na rozdiel od bežného  
chatbota, ktorý len reaguje na vstupy, agent dokáže *samostatne plánovať, rozhodovať sa a iteratívne pracovať* na riešení úlohy.

> *Ak je LLM (jazykový model) „mozog“, potom agent je „mozog + ruky + nástroje + pamäť“.*

## Kľúčové charakteristiky agenta

| Vlastnosť | Popis | Príklad |
|-----------|-------|---------|
| **Autonómia** | Funguje bez neustáleho zásahu človeka | Agent sám rozhodne, kedy vyhľadá na webe |
| **Reaktivita** | Vníma prostredie a reaguje na zmeny | Ak sa zmení cena letenky, agent upozorní |
| **Proaktivita** | Koná účelovo, sleduje ciele | Agent sám navrhuje termíny stretnutí |
| **Sociálna schopnosť** | Komunikuje s inými agentmi alebo ľuďmi | Viac agentov spolupracuje na projekte |
| **Pamäť a učenie** | Ukladá kontext a zlepšuje sa so skúsenosťami | Agent si pamätá preferencie používateľa |

## Kde sa agenti používajú? (Praktické aplikácie)

### Výskum a vzdelávanie

- **Literárne rešerše**: Agenti prehľadávajú akademické databázy, syntetizujú závery a generujú prehľadové štúdie.
- **Tvorba učebných materiálov**: Automatické generovanie kvízov, zhrnutí kapitol alebo vysvetľujúcich príkladov.
- **Overovanie faktov**: Agenti porovnávajú tvrdenia s viacerými zdrojmi a označujú nekonzistencie.

### Biznis a produktivita

- **Customer support**: Pokročilí agenti riešia komplexné požiadavky zákazníkov (vrátenie tovaru, reklamácie) bez eskalácie na človeka.
- **Analýza dát**: Agenti spracúvajú tabuľky, generujú grafy a formulujú business insights.
- **Projektový manažment**: Automatické rozdeľovanie úloh, sledovanie deadlineov a koordinácia tímov.

### Vývoj a technické úlohy

- **Kódovanie a debugging**: Agenti píšu, testujú a opravujú kód (napr. GitHub Copilot Workspace, Devin).
- **Automatizácia workflow**: Spájanie rôznych API, plánovanie úloh, spracovanie dokumentov.
- **Kyberbezpečnosť**: Detekcia anomálií, simulácia útokov, automatická odpoveď na incidenty.

### Osobné použitie

- **Osobní asistenti**: Plánovanie dní, rezervácie, pripomienky, nákupné zoznamy.
- **Zdravie a wellness**: Sledovanie návykov, personalizované odporúčania, motivácia.
- **Kreatívna tvorba**: Spolupráca pri písaní textov, generovaní nápadov, úprave médií.

## 🤖 Druhy agentov a architektúry

### Podľa úrovne autonómie

| Typ | Popis | Príklad |
|-----|-------|---------|
| **Reaktívny agent** | Reaguje na vstupy podľa pevných pravidiel, bez pamäte | Jednoduchý chatbot s rozhodovacím stromom |
| **Agent s pamäťou** | Ukladá históriu interakcií a kontext | Osobný asistent, ktorý si pamätá preferencie |
| **Plánujúci agent** | Rozkladá ciele na podúlohy, vytvára stratégie | Deep Research agent, ktorý plánuje rešerš |
| **Učiaci sa agent** | Zlepšuje sa so skúsenosťami (RL, fine-tuning) | Agent na optimalizáciu reklamných kampaní |

### Podľa špecializácie

| Kategória | Funkcia | Typické nástroje |
|-----------|---------|-----------------|
| **Výskumný agent** | Hĺbkové vyhľadávanie, syntéza zdrojov | Qwen Deep Research, Perplexity Pro |
| **Kódovací agent** | Tvorba, testovanie a debugging kódu | GitHub Copilot, Cursor, Devin |
| **Dátový analytik** | Spracovanie tabuliek, vizualizácie, štatistiky | Julius AI, DataBot, NotebookLM |
| **Kreatívny agent** | Generovanie textu, obrázkov, nápadov | Claude Artifacts, Midjourney Bot |
| **Automatizačný agent** | Spájanie aplikácií, workflow automatizácia | Zapier Interfaces, Make AI, n8n |

### Subagenti a multi-agentné systémy

Komplexné úlohy často riešia **tímy špecializovaných subagentov**, ktorí spolupracujú pod vedením hlavného („manažérskeho“) agenta.

```
🎯 Hlavný agent (Planner)
   │
   ├── 🔍 Výskumný subagent → vyhľadáva fakty
   ├── ✍️ Pisateľský subagent → tvorí text
   ├── 🔎 Kontrolný subagent → overuje presnosť
   └── 🎨 Formátovací subagent → upravuje výstup
```

**Výhody multi-agentného prístupu:**

- ✅ **Modularita**: Každý subagent sa špecializuje na jednu úlohu
- ✅ **Škálovateľnosť**: Ľahko pridáte nového subagenta bez prepisu celého systému
- ✅ **Robustnosť**: Chyba jedného subagenta nemusí zlyhať celý proces
- ✅ **Transparentnosť**: Jednoduchšie sledovať, ktorý krok kto vykonal

**Príklady frameworkov pre multi-agentné systémy:**

| Framework | Popis | Odkaz |
|-----------|-------|-------|
| **LangGraph** (LangChain) | Vizuálne plánovanie workflow, stavové grafy | [langgraph.dev](https://langgraph.dev) |
| **AutoGen** (Microsoft) | Konverzácia medzi agentmi, rozširovanie funkcií | [github.com/microsoft/autogen](https://github.com/microsoft/autogen) |
| **CrewAI** | Jednoduchá definícia rolí a cieľov, rýchly štart | [crewai.com](https://crewai.com) |
| **CAMEL** | Výskumný multi-agent framework, škálovanie agentov | [github.com/camel-ai/camel](https://github.com/camel-ai/camel) |
| **OpenAI Agents SDK** | Oficiálny SDK od OpenAI na tvorbu agentov | [openai.github.io/openai-agents-python](https://openai.github.io/openai-agents-python) |
| **LlamaIndex Agents** | Práca s externými dátami, RAG pipeline | [llamaindex.ai](https://llamaindex.ai) |

## 🧠 Architektúra typického inteligentného agenta

```
┌─────────────────────────────────┐
│  🎯 Cieľ / Prompt od používateľa │
└─────────┬───────────────────────┘
          ▼
┌─────────────────────────────────┐
│  🧠 LLM „mozog“ (plánovanie)    │
│  • Rozklad úlohy na kroky        │
│  • Rozhodovanie o nástrojoch     │
└─────────┬───────────────────────┘
          ▼
┌─────────────────────────────────┐
│  🛠️ Nástroje (Tools)            │
│  • Web Search / API volania      │
│  • Kódovanie / Exec sandbox      │
│  • Práca so súbormi (PDF, CSV)   │
│  • Pamäť (vektorová DB, cache)   │
└─────────┬───────────────────────┘
          ▼
┌─────────────────────────────────┐
│  🔁 Iterácia a seba-korekcia    │
│  • Vyhodnotenie výsledku kroku   │
│  • Úprava plánu podľa feedbacku  │
└─────────┬───────────────────────┘
          ▼
┌─────────────────────────────────┐
│  📤 Výstup pre používateľa      │
│  • Text / Správa / Kód / Graf   │
│  • Zdroje a citácie              │
└─────────────────────────────────┘
```

> 💡 **Kľúčový koncept**: Agent nie je len „väčší model“. Je to **systém**, kde LLM slúži ako „riadiaca jednotka“,
> ktorá koordinuje nástroje, pamäť a iteratívne uvažovanie.

## � Najnovšie trendy a pojmy (2025–2026)

### Agentic AI – nový štandard

V roku 2025–2026 sa ustálil pojem **Agentic AI** (agentická umelá inteligencia) – označuje systémy, ktoré nielen generujú obsah, ale **samostatne rozhodujú, plánujú a konajú** v komplexnom prostredí bez neustáleho dohľadu človeka.

> *„AI agent nie je väčší model – je to systém, kde LLM slúži ako riadiaca jednotka, ktorá koordinuje nástroje, pamäť a iteratívne uvažovanie.“*

Hlavné črty agentickej AI:
- **Cieľové správanie** – agent si rozkladá úlohu na podciele
- **Používanie nástrojov** – volá API, vyhľadáva na webe, pracuje so súbormi
- **Pamäť a kontext** – uchováva históriu interakcií a učí sa z nej
- **Autonómne rozhodovanie** – bez nutnosti manuálneho zásahu

### Prečo neexistuje jednotná definícia?

Napriek obrovskému rozmachu agentov nepanuje v odbore zhoda na tom, čo presne agent je. Ako v marci 2025 poznamenal TechCrunch: *„No one knows what the hell an AI agent is.“*

Rôzne spoločnosti definujú agentov odlišne:
- **OpenAI**: „automatizované systémy, ktoré samostatne plnia úlohy v mene používateľa“
- **Microsoft**: odlišuje agentov (špecializované) od asistentov (všeobecné)
- **Anthropic**: pripúšťa oba významy – plne autonómne aj preddefinované workflow
- **Salesforce**: ponúka najširšiu definíciu so 6 kategóriami agentov

### 🔄 Paradigmy uvažovania agentov

Moderní agenti používajú pokročilé metódy uvažovania:

| Paradigma | Popis | Príklad |
|-----------|-------|---------|
| **ReAct** (Reasoning + Acting) | Agent striedavo uvažuje (Think) a koná (Act), po každom kroku vyhodnotí výsledok (Observe) | Think → API call → Observe → ďalší krok |
| **ReWOO** (Reasoning Without Observation) | Agent si vopred naplánuje celý postup, až potom vykonáva – šetrí tokeny a čas | Plán → Tool call → Výstup |
| **Chain-of-Thought** | Rozkladá zložitú otázku na postupnosť medzikrokov | „Najprv zistím X, potom vypočítam Y“ |

### 🚀 Nové významné agenty (2025–2026)

- **OpenAI Operator** (január 2025) – prvý agent od OpenAI, ktorý sám ovláda prehliadač a vykonáva úlohy na webe
- **ChatGPT Deep Research** (február 2025) – hĺbkový rešeršný agent, ktorý syntetizuje informácie z desiatok zdrojov
- **Manus** (marec 2025) – všeobecný agent, ktorý vzbudil pozornosť svojou samostatnosťou (MIT Technology Review)
- **Google Project Mariner** (december 2024) – agent ovládajúci prehliadač Chrome
- **Salesforce Agentforce 2dx** (marec 2025) – autonómny firemný agent pre podnikové systémy
- **AWS Amazon Connect Health** (marec 2026) – prvý HIPAA-certifikovaný agent pre zdravotníctvo
- **Quark** (Alibaba/Qwen) a **AutoGLM Rumination** (Zhipu AI) – čínski agenti, ktoré doháňajú západnú konkurenciu

### 🏢 Podnikové nasadenie agentov

Agentická AI preniká do firiem v nebývalej miere:

- **Salesforce Agentforce** – agenti autonómne spracúvajú požiadavky zákazníkov bez eskalácie
- **IBM watsonx Orchestrate** – platforma na tvorbu multi-agentných workflow
- **AWS Connect Health** (marec 2026) – AI agent pre automatizáciu administratívy v zdravotníctve (objednávanie, dokumentácia, overovanie pacientov)
- **Deloitte a IDC** – analytici varujú pred „misaligned expectations“ bez jednotnej definície agentov

## �🗂️ Tabuľka: Odporúčaní agenti na vyskúšanie (pre študentov a pedagógov)

| Agent / Platforma | Typ | Cena | Dostupnosť | Prečo vyskúšať | Odkaz |
|-------------------|-----|------|------------|----------------|-------|
| **Qwen Chat – Deep Research** | Výskumný agent | 🟢 Zadarmo | ✅ Globálne (web) | Plnohodnotný Deep Research zadarmo, export do PDF, slovenský kontext | [chat.qwen.ai](https://chat.qwen.ai) |
| **Perplexity AI – Pro Search** | Výskumný agent | 🟢 Free / 🟡 $20/mes. | ✅ Globálne | Rýchle, presné odpovede so zdrojmi, Focus Mode pre akademické zdroje | [perplexity.ai](https://perplexity.ai) |
| **Google NotebookLM** | Dátový/výskumný agent | 🟢 Zadarmo | ✅ Globálne | Výborná práca s nahranými PDF, automatické citácie, audio overview | [notebooklm.google.com](https://notebooklm.google.com) |
| **Cursor / GitHub Copilot** | Kódovací agent | 🟢 Free tier / 🟡 $10–20/mes. | ✅ Globálne | Interaktívne písanie a debugging kódu, vysvetľovanie chýb | [cursor.com](https://cursor.com) |
| **CrewAI (open-source)** | Multi-agent framework | 🟢 Zadarmo (self-hosted) | ✅ Globálne | Jednoduchá tvorba vlastných tímov agentov, ideálne na výuku architektúr | [crewai.com](https://crewai.com) |
| **Microsoft Copilot** | Všeobecný agent | 🟢 Free / 🟡 ~22 €/mes. | ✅ Globálne | Integrácia s Office, Bing Search, dobrý pomer cena/výkon | [copilot.microsoft.com](https://copilot.microsoft.com) |
| **Julius AI** | Dátový analytik | 🟢 Free tier / 🟡 Od $10/mes. | ✅ Globálne | Upload Excel/CSV → automatická analýza, grafy, insights | [julius.ai](https://julius.ai) |
| **Elicit** | Akademický výskumný agent | 🟢 Free tier / 🟡 ~10 €/mes. | ✅ Globálne | Špecializácia na peer-reviewed štúdie, extrakcia metód a záverov | [elicit.com](https://elicit.com) |
| **Zapier Interfaces + AI** | Automatizačný agent | 🟢 Free tier / 🟡 Od ~20 €/mes. | ✅ Globálne | Spájanie 5000+ appiek s AI logikou, bez kódovania | [zapier.com](https://zapier.com) |
| **LangGraph Playground** | Vývojársky nástroj | 🟢 Zadarmo (demo) | ✅ Globálne | Vizuálne plánovanie agentných workflow, ideálne na výuku | [langgraph.dev](https://langgraph.dev) |
| **OpenAI Operator** | Browser-use agent | 🟡 $200/mes. (Pro) | ✅ Obmedzené regióny | Prvý agent OpenAI – sám ovláda prehliadač a plní úlohy na webe | [operator.chatgpt.com](https://operator.chatgpt.com) |
| **Manus** | Všeobecný agent | 🟢 Free / 🟡 Od ~$10/mes. | ✅ Pozvánkový prístup | Revolučný samostatný agent, virálny v roku 2025 | [manus.im](https://manus.im) |
| **Salesforce Agentforce** | Podnikový agent | 🔵 Enterprise cena | ✅ Globálne | Autonómna AI pre firemné procesy a zákaznícku podporu | [salesforce.com/agentforce](https://www.salesforce.com/agentforce) |

### 🎨 Legenda cien

| Ikona | Význam |
|-------|--------|
| 🟢 | **Zadarmo** alebo veľkorysý free tier vhodný pre študentov |
| 🟡 | **Platená verzia** pre jednotlivcov (do ~25 €/mes.) |
| 🔵 | **Profesionálna/Enterprise** verzia (nad 25 €/mes.) |

### ⚠️ Riziká a výzvy agentickej AI

| Riziko | Popis |
|--------|-------|
| 🌀 **Nejednotná definícia** | Každá firma definuje agentov inak, čo sťažuje porovnávanie a očakávania |
| 🔁 **Nekonečné slučky** | Agent môže opakovane volať tie isté nástroje bez pokroku – vyžaduje sa ľudský dohľad |
| 💰 **Výpočtová náročnosť** | Trénovanie a beh agentov je drahý – komplexné úlohy môžu trvať hodiny až dni |
| 🔒 **Súkromie údajov** | Agenti pracujú s citlivými firemnými a osobnými údajmi – riziko únikov |
| 🤝 **Závislosť na multi-agente** | Zlyhanie jedného agenta v tíme môže spôsobiť systémový kolaps |
| 👁️ **Transparentnosť** | Rozhodovanie agentov je často „čierna skrinka“ – ťažko auditovateľné |

**Osvedčené postupy pre bezpečnú prácu s agentmi:**
- Vyžadovať **logovanie všetkých akcií** agenta
- Implementovať **možnosť prerušenia** (human-in-the-loop)
- Používať **unikátne identifikátory** agentov pre dohľadateľnosť
- Pred kritickými krokmi vyžadovať **potvrdenie človeka**

## 💬 Otázky a diskusia
