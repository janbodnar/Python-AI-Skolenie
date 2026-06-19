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
