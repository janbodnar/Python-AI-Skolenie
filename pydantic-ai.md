# Pydantic AI

Pydantic AI is a Python framework for building AI agents, made  
by the team behind Pydantic. It brings the same ergonomic, type-  
safe design that made FastAPI popular to the world of LLM apps.  

Pydantic AI is model-agnostic. It works with OpenAI, Anthropic,  
Gemini, DeepSeek, and many other providers through one unified  
interface, so switching models rarely means rewriting your code.  

The framework leans on Pydantic's validation engine to give you  
structured, typed outputs instead of raw text. This turns LLM  
calls into predictable, type-checked Python objects your IDE and  
type checker can actually understand.  

Agents in Pydantic AI can use tools, dynamic system prompts, and  
dependency injection to access external data and services. This  
keeps business logic separate from model orchestration logic.  

Other notable features include streaming responses, support for  
multi-agent and graph-based workflows, built-in support for MCP  
servers, and durable execution for long-running or human-in-the-  
loop tasks that must survive restarts or failures.  

For observability, Pydantic AI integrates tightly with Pydantic  
Logfire, giving real-time tracing, cost tracking, and debugging.  
Pydantic Evals supports systematic testing of agent behavior.  

Overall, Pydantic AI aims to bring production-grade reliability  
and developer ergonomics to LLM application development, much  
like FastAPI did for building web APIs in Python.

## Agent

An agent is a container that wraps a large language model  
together with everything needed to make it act on a task: a  
system prompt, a set of tools it can call, structured input and  
output types, and any dependencies it needs to do its job.  

Rather than calling an LLM once and parsing raw text back, an  
agent runs a loop. It sends a prompt to the model, lets the  
model decide whether to answer directly or call a tool, executes  
that tool if needed, feeds the result back to the model, and  
repeats until a final, validated response is produced.  

In Pydantic AI specifically, an agent is reusable, similar to a  
web app's router or a database connection pool. You typically  
create one agent per task type, then run it many times with  
different inputs across your application.  

More broadly in AI, an agent is any system that can perceive  
context, reason about what to do next, and take actions, often  
through tool calls, to accomplish a goal with some autonomy,  
rather than just generating a single static response.

## Simple agents

```python
from pydantic_ai import Agent, AgentRunResultEvent, AgentStreamEvent

agent = Agent('deepseek:deepseek-v4-flash')
result_sync = agent.run_sync('What is the capital of Italy?')
print(result_sync.output)

result_sync = agent.run_sync('What model are you?')
print(result_sync.output)
```

## Streaming

```python
import asyncio

from pydantic_ai import Agent

agent = Agent("deepseek:deepseek-v4-flash")


async def main():
    async with agent.run_stream('Where does "hello world" come from?') as result:
        async for message in result.stream_text(delta=True):
            print(message)


asyncio.run(main())
```

## Instructions

```python
# Import date for getting today's date
from datetime import date

# Import Agent (the core AI agent class) and RunContext (provides access to dependencies)
from pydantic_ai import Agent, RunContext

# Create an agent using DeepSeek V4 Flash model
# - deps_type=str means the dependency passed at runtime will be a string (the user's name)
# - instructions give the LLM a system-level directive for how to behave
agent = Agent(
  'deepseek:deepseek-v4-flash',
  deps_type=str,
  instructions="Use the customer's name while replying to them.",
)


# Register a dynamic instruction that injects the user's name into the prompt.
# The @agent.instructions decorator adds this function's return value as a prompt instruction.
# RunContext[str] gives access to the dependency (the name string) via ctx.deps.
@agent.instructions
def add_the_users_name(ctx: RunContext[str]) -> str:
  return f"The user's name is {ctx.deps}."


# Register another dynamic instruction that injects today's date.
# This function takes no arguments, so it's called without any runtime context.
@agent.instructions
def add_the_date() -> str:
  return f'The date is {date.today()}.'


# Run the agent synchronously with the user query and pass 'Frank' as the dependency.
# The agent will combine the static instructions, dynamic instructions, and the query.
result = agent.run_sync('What is the date?', deps='Frank')
print(result.output)
# > Hello Frank, the date today is 2032-01-02.
```


**Purpose:** Inject _static or dynamic text_ into the system prompt that the LLM  
sees before generating a response.

- They are **passive context** — just text added to the prompt.
- The LLM **reads them** and adjusts its behavior accordingly.
- They cannot perform actions, fetch live data, or compute values _during the conversation loop_.

**Example from your code:**

```python
@agent.instructions
def add_the_users_name(ctx: RunContext[str]) -> str:
    return f"The user's name is {ctx.deps}."
```

This adds `"The user's name is Frank."` into the system prompt. The LLM simply _knows_ the  
name — it didn't call a function to verify it.

Think of instructions as **"background info you give the AI before it speaks."**

**Purpose:** Give the LLM the _ability to call functions_ to get real-time data or perform actions.

- They are **active capabilities** — the LLM can _decide to invoke_ them mid-conversation.
- The LLM **calls them** when it needs information it doesn't already know.
- They return actual computed/retrieved values that the LLM incorporates.
  
 **Example from simple_tools.py:**
 
```python
@agent.tool_plain
def get_current_time() -> datetime:
    return datetime.now()
```

The LLM doesn't _guess_ the time — it _calls the tool_ to get the real current time.

Think of tools as **"things the AI can _do_ to get answers."**

## Key Difference at a Glance

| Aspect | Instructions | Tools |
|---|---|---|
| **Role** | Provide context/knowledge | Perform actions / fetch data |
| **When evaluated** | At prompt construction time (once) | On-demand, when the LLM chooses to call them |
| **LLM control** | The LLM just reads them | The LLM _decides_ whether to invoke them |
| **Side effects** | ❌ Cannot do I/O or mutate state | ✅ Can call APIs, query DBs, compute, etc. |
| **Return value** | Becomes part of the system prompt | Returned to the LLM as a function result |

In short: **instructions tell the AI what to know; tools let the AI do things.** 
You use instructions for static facts/behavior rules, and tools for anything that requires 
real computation or external data.

## Tools 

```python
from datetime import datetime
from pydantic_ai import Agent
import random

agent = Agent("deepseek:deepseek-v4-flash")


@agent.tool_plain
def get_current_time() -> datetime:
    return datetime.now()


@agent.tool_plain
def get_random_int(lower: int, upper: int) -> int:
    print("-- tool get_random_int called with lower:", lower, "upper:", upper)
    return random.randint(lower, upper)


result = agent.run_sync("What time is it?")
print(result.output)


result = agent.run_sync("Get a random integer between 1 and 10.")
print(result.output)
```

## Native search

```python
from pydantic_ai import Agent
from pydantic_ai.common_tools.web_fetch import web_fetch_tool

agent = Agent(
    'deepseek:deepseek-v4-flash',
    tools=[web_fetch_tool()],
    instructions='Fetch web pages and summarize their content.',
)

result = agent.run_sync('What is on https://hnonline.sk?')
print(result.output)
```

OpenAI. 

```python
from pydantic_ai import Agent, WebSearchTool
from pydantic_ai.capabilities import NativeTool

agent = Agent(
    "openai-responses:gpt-5.4-mini", capabilities=[NativeTool(WebSearchTool())]
)

result = agent.run_sync("Give me a sentence with the biggest news in AI this week.")
print(result.output)
```

## Duckduckgo search 

```python
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

agent = Agent(
    'deepseek:deepseek-v4-flash',
    tools=[duckduckgo_search_tool()],
    instructions='Search DuckDuckGo for the given query and return the results.',
)

result = agent.run_sync(
    'Aké sú súčasné volebné preferencie na Slovensku?'
)

print(result.output)
```

## Parallel agents

```python
import asyncio
import time

from pydantic_ai import Agent

# ── Define agents with different specializations ────────────────────────────

critic = Agent(
    "deepseek:deepseek-v4-flash",
    system_prompt=(
        "You are a harsh critic. Be concise and blunt. "
        "Identify weaknesses, flaws, and risks. Never praise."
    ),
)

optimist = Agent(
    "deepseek:deepseek-v4-flash",
    system_prompt=(
        "You are a relentless optimist. Be concise. "
        "Find the upside, opportunities, and best-case scenario in everything. "
        "Ignore downsides entirely."
    ),
)

pragmatist = Agent(
    "deepseek:deepseek-v4-flash",
    system_prompt=(
        "You are a pragmatic realist. Be concise. "
        "Give a balanced, practical assessment of what is most likely to happen. "
        "Acknowledge both upsides and downsides proportionally."
    ),
)

# ── Run all agents concurrently ─────────────────────────────────────────────


async def main():
    prompt = 'Should a startup raise VC funding or bootstrap?'

    async def run_agent(name: str, agent: Agent, prompt: str) -> tuple[str, str]:
        result = await agent.run(prompt)
        return name, result.output

    start = time.perf_counter()

    # Launch all three agents in parallel
    results = await asyncio.gather(
        run_agent("Critic", critic, prompt),
        run_agent("Optimist", optimist, prompt),
        run_agent("Pragmatist", pragmatist, prompt),
    )

    elapsed = time.perf_counter() - start

    for name, output in results:
        print(f"── {name} ──")
        print(output)
        print()

    print(f"Completed in {elapsed:.2f}s (all ran in parallel)")


if __name__ == "__main__":
    asyncio.run(main())
```

## Delegation

```python
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext
from pydantic_ai.common_tools.web_fetch import web_fetch_tool

# ── Structured types ───────────────────────────────────────────────────────

class ExtractedParagraphs(BaseModel):
    paragraphs: list[str] = Field(description="List of main body paragraphs")

class PageSummary(BaseModel):
    title: str = Field(description="Inferred title of the page")
    summary: str = Field(description="One-paragraph summary of the content")
    key_points: list[str] = Field(description="3-5 key takeaways")

class CrossPageAnalysis(BaseModel):
    common_themes: list[str] = Field(description="Themes appearing across multiple pages")
    differences: list[str] = Field(description="Notable differences or unique angles")
    overall_summary: str = Field(description="Synthesized overview of all pages")


# ── Agent 1: Web page fetcher ──────────────────────────────────────────────

fetch_agent = Agent(
    "deepseek:deepseek-v4-flash",
    tools=[web_fetch_tool()],
    system_prompt=(
        "Fetch the full content of the given URL. "
        "Return the complete text exactly as received — do not summarize or truncate."
    ),
)


# ── Agent 2: Paragraph extractor ───────────────────────────────────────────

extract_agent = Agent(
    "deepseek:deepseek-v4-flash",
    output_type=ExtractedParagraphs,
    retries={'output': 3},
    system_prompt=(
        "Extract all meaningful paragraph text from the provided page content. "
        "Skip navigation, headers, footers, ads, and boilerplate. "
        "Return only the main body paragraphs as a list. "
        "You MUST respond with a valid JSON object containing a 'paragraphs' array. "
        "Do NOT include any explanation, markdown fences, or text outside the JSON."
    ),
)


# ── Agent 3: Single-page summarizer ────────────────────────────────────────

summarize_agent = Agent(
    "deepseek:deepseek-v4-flash",
    output_type=PageSummary,
    retries={'output': 3},
    system_prompt=(
        "Analyze the provided paragraphs and produce a structured summary. "
        "Infer a meaningful title, write a concise summary, "
        "and list 3-5 key takeaways. "
        "You MUST respond with ONLY a valid JSON object with fields: "
        "title (str), summary (str), key_points (list[str]). "
        "No markdown fences, no explanation, no extra text."
    ),
)


# ── Agent 4: Cross-page analyst ────────────────────────────────────────────

cross_analysis_agent = Agent(
    "deepseek:deepseek-v4-flash",
    output_type=CrossPageAnalysis,
    retries={'output': 3},
    system_prompt=(
        "Compare and synthesize content from multiple web pages. "
        "Identify common themes, notable differences, and write an overall synthesis. "
        "You MUST respond with ONLY a valid JSON object with fields: "
        "common_themes (list[str]), differences (list[str]), overall_summary (str). "
        "No markdown fences, no explanation, no extra text."
    ),
)


# ── File writer tool ───────────────────────────────────────────────────────

@dataclass
class OutputDeps:
    output_dir: str


file_writer_agent = Agent(
    "deepseek:deepseek-v4-flash",
    deps_type=OutputDeps,
    system_prompt=(
        "You write structured data to the filesystem. "
        "Call the appropriate tool to persist results."
    ),
)


@file_writer_agent.tool
async def write_json_file(ctx: RunContext[OutputDeps], filename: str, data: str) -> str:
    """Write JSON data to a file. `data` must be a valid JSON string."""
    out_dir = Path(ctx.deps.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filepath = out_dir / filename
    filepath.write_text(data)
    return f"Written to {filepath}"


# ── Per-page pipeline ──────────────────────────────────────────────────────

async def process_page(url: str) -> dict:
    """Fetch → extract → summarize a single page."""
    print(f"  [{url}] Fetching...")
    fetch_result = await fetch_agent.run(f"Fetch the content of: {url}")
    print(f"  [{url}] Fetched {len(fetch_result.output)} chars, extracting...")

    extract_result = await extract_agent.run(
        f"Extract paragraphs from this page content:\n\n{fetch_result.output}"
    )
    paragraphs: ExtractedParagraphs = extract_result.output
    print(f"  [{url}] Extracted {len(paragraphs.paragraphs)} paragraphs, summarizing...")

    summary_result = await summarize_agent.run(
        f"Summarize these paragraphs from {url}:\n" + "\n".join(paragraphs.paragraphs)
    )
    page_summary: PageSummary = summary_result.output
    print(f"  [{url}] Done — '{page_summary.title}'")

    return {
        "url": url,
        "paragraph_count": len(paragraphs.paragraphs),
        "title": page_summary.title,
        "summary": page_summary.summary,
        "key_points": page_summary.key_points,
        "paragraphs": paragraphs.paragraphs,
    }


# ── Main orchestration ─────────────────────────────────────────────────────

async def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {__file__} <url1> <url2> ...", file=sys.stderr)
        print(f"Example: python {__file__} https://example.com https://httpbin.org/html", file=sys.stderr)
        sys.exit(1)

    if not os.getenv("DEEPSEEK_API_KEY"):
        print("Error: DEEPSEEK_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    urls = sys.argv[1:]
    output_dir = os.getenv("MULTIPAGE_OUTPUT_DIR", "/tmp/multipage_output")

    print(f"Processing {len(urls)} pages in parallel...\n")
    start = time.perf_counter()

    # Step 1+2+3 — process all pages concurrently
    page_results = await asyncio.gather(*[process_page(url) for url in urls])

    # Step 4 — cross-page analysis
    print(f"\nRunning cross-page analysis on {len(page_results)} pages...")
    summaries_text = "\n\n---\n\n".join(
        f"URL: {p['url']}\nTitle: {p['title']}\nSummary: {p['summary']}\nKey Points: {json.dumps(p['key_points'])}"
        for p in page_results
    )
    cross_result = await cross_analysis_agent.run(
        f"Analyze these page summaries and identify common themes, differences, and overall synthesis:\n\n{summaries_text}"
    )
    analysis: CrossPageAnalysis = cross_result.output

    # Step 5 — save everything
    print("Saving results...")
    report = {
        "pages": page_results,
        "cross_analysis": {
            "common_themes": analysis.common_themes,
            "differences": analysis.differences,
            "overall_summary": analysis.overall_summary,
        },
    }
    report_json = json.dumps(report, indent=2, ensure_ascii=False)

    await file_writer_agent.run(
        f"Call write_json_file with filename='multipage_report.json' and the following data:\n{report_json}",
        deps=OutputDeps(output_dir=output_dir),
    )

    elapsed = time.perf_counter() - start
    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"Report saved to {output_dir}/multipage_report.json")
    print(f"Common themes: {', '.join(analysis.common_themes)}")


if __name__ == "__main__":
    asyncio.run(main())
```

