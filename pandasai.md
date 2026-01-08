# PandasAI

PandasAI is a Python library that integrates large language models (LLMs) with  
Pandas DataFrames, enabling you to interact with your data using natural language.  
Instead of writing complex Pandas code, you can ask questions in plain English and  
let PandasAI generate and execute the necessary code to answer them.  

This library bridges the gap between data analysis and conversational AI, making  
data exploration more intuitive and accessible to users of all skill levels.  

## What PandasAI Is

PandasAI is a wrapper around the Pandas library that adds natural language  
processing capabilities. It allows you to:  

- Query data using conversational prompts  
- Generate visualizations through simple text commands  
- Perform data transformations without writing code  
- Get insights and summaries from datasets automatically  

The library uses LLMs to translate your natural language queries into Pandas  
operations, execute them, and return the results. This makes data analysis more  
accessible while still leveraging the full power of Pandas.  

## How It Extends Pandas

PandasAI doesn't replace Pandas—it enhances it. Traditional Pandas requires you  
to know:  

- DataFrame methods and their syntax  
- How to chain operations  
- Proper indexing and filtering techniques  
- Aggregation and grouping patterns  

With PandasAI, you can express your intent in natural language:  

**Traditional Pandas:**  
```python
df[df['age'] > 30].groupby('country')['salary'].mean()
```

**PandasAI:**  
```python
agent.chat("What is the average salary by country for people over 30?")
```

The library understands your question, generates the appropriate Pandas code,  
executes it, and returns the answer. This dramatically reduces the learning curve  
for data analysis.  

## Use Cases and Benefits

**Common Use Cases:**  

- **Exploratory Data Analysis (EDA)**: Quickly understand dataset structure  
- **Business Intelligence**: Generate reports without SQL or complex code  
- **Data Quality Checks**: Ask questions about missing values or outliers  
- **Rapid Prototyping**: Test hypotheses without writing boilerplate code  
- **Teaching**: Help students learn data analysis concepts  

**Key Benefits:**  

- **Lower Barrier to Entry**: Non-programmers can analyze data  
- **Faster Insights**: Reduce time from question to answer  
- **Code Generation**: Learn Pandas by seeing generated code  
- **Flexibility**: Switch between natural language and traditional code  
- **Integration**: Works with existing Pandas workflows  


## Installation and Setup

### Basic Installation

Install PandasAI using pip:  

```bash
pip install pandasai
pip install pandasai-litellm
```

### Required Dependencies

PandasAI requires:  

- Python 3.9 or higher  
- pandas  
- An LLM provider (OpenAI, HuggingFace, or others)  

For OpenAI integration, install the OpenAI package:  

```bash
pip install openai
```

For visualization support, install matplotlib:  

```bash
pip install matplotlib plotly
```

### Environment Setup

You'll need an API key from your LLM provider. For OpenAI:  

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or set it in your Python code:  

```python
import os
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'
```


## Core Concepts

### Integration with Pandas DataFrames

PandasAI wraps standard Pandas DataFrames with an intelligent agent layer.  
You start with a regular DataFrame:  

```python
import pandas as pd

df = pd.DataFrame({
    'country': ['USA', 'UK', 'France', 'Germany'],
    'sales': [5000, 3200, 2900, 4100]
})
```

Then create a PandasAI agent that understands this data:  

```python
from pandasai import Agent

agent = Agent(df)
```

The agent maintains access to your DataFrame while providing natural language  
querying capabilities. You can still use traditional Pandas methods on the  
original DataFrame when needed.  

### LLM Integration for Data Analysis

PandasAI uses large language models to:  

1. **Understand Intent**: Parse your natural language question  
2. **Generate Code**: Create appropriate Pandas operations  
3. **Execute**: Run the generated code on your DataFrame  
4. **Format Results**: Present the answer in a readable format  

The LLM acts as a translator between human language and Pandas syntax. It  
considers the structure of your data, including column names and types, to  
generate accurate queries.  

### Key Classes and Functions

**Agent**: The main class for interacting with your data  

```python
from pandasai import Agent

agent = Agent(df, config={'llm': llm})
response = agent.chat("Your question here")
```

**LLM Configuration**: Specify which language model to use  

```python
# Configure PandasAI globally to use LiteLLM with OpenAI

llm = LiteLLM(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
pai.config.set({"llm": llm})
```

## PandasAI Usage Approaches

### DataFrame‑Bound Chat (`df.chat()`)

This approach attaches PandasAI capabilities directly to a DataFrame, enabling  
natural‑language queries without creating an explicit agent. It is lightweight  
and ideal for quick, one‑off interactions such as filtering, summarizing, or  
exploring data. Each query is handled independently, making this method well  
suited for exploratory analysis or notebook‑style workflows where minimal setup  
is preferred.

PandasAI automatically adds the `.chat()` method only to DataFrames that it  
creates through its own I/O helper functions. These helpers return a  
**SmartDataframe**, which includes natural‑language querying capabilities.  
DataFrames created directly with pandas (such as `pd.DataFrame()` or  
`pd.read_csv()`) do not receive this functionality unless wrapped manually with  
an `Agent`. The table below lists all PandasAI loaders that produce a wrapped  
DataFrame ready for conversational analysis.  

### Auto‑Wrapping Data Loaders in PandasAI 3.x

| Category   | Helper Function(s)            | Notes                                      |
|------------|-------------------------------|---------------------------------------------|
| CSV        | `pai.read_csv()`              | Loads CSV files into a SmartDataframe       |
| JSON       | `pai.read_json()`             | Supports standard JSON structures           |
| Excel      | `pai.read_excel()`            | Reads `.xls` and `.xlsx` files              |
| Parquet    | `pai.read_parquet()`          | For columnar Parquet datasets               |
| SQL        | `pai.read_sql()`              | Executes SQL queries and wraps results      |
|            | `pai.read_sql_table()`        | Reads entire SQL tables                     |
|            | `pai.read_sql_query()`        | Runs SQL queries and returns wrapped output |
| Clipboard  | `pai.read_clipboard()`        | Wraps data copied from the system clipboard |
| Pickle     | `pai.read_pickle()`           | Loads pickled DataFrames                    |
| Feather    | `pai.read_feather()`          | Reads Apache Feather format                 |
| ORC        | `pai.read_orc()`              | Loads ORC columnar files                    |
| HTML       | `pai.read_html()`             | Returns a list of wrapped DataFrames        |
| XML        | `pai.read_xml()`              | Parses XML into a wrapped DataFrame         |


### Agent‑Based Workflow (`Agent(df)`)

The Agent‑based approach creates a persistent object that holds the DataFrame,  
the LLM, configuration, and conversational context. It supports multi‑turn  
reasoning, custom tools, multiple datasets, and more complex workflows. This  
method is better suited for applications, pipelines, or scenarios where queries  
build on each other and require structured, reusable logic.  

### Comparison Table

| Feature                 | `df.chat()`                         | `Agent(df)`                     |
|-------------------------|--------------------------------------|---------------------------------|
| Ease of use             | Easiest, minimal setup               | More explicit and modular       |
| Context retention       | Limited                              | Strong multi‑turn memory        |
| Multiple DataFrames     | Not ideal                            | Fully supported                 |
| Custom tools/extensions | Limited                              | Designed for it                 |
| Production readiness    | Good for quick tasks                 | Better for complex apps         |
| Code style              | Implicit                             | Explicit and structured         |

### Choosing an Approach

Use `df.chat()` for simple, fast, and isolated queries during exploratory work.  
Use `Agent(df)` when you need context retention, multi‑step analysis,  
extensibility, or integration into a larger system.  


## SmartDataframe in PandasAI

A **SmartDataframe** is PandasAI’s enhanced DataFrame wrapper that adds  
natural‑language capabilities on top of a standard pandas DataFrame. When you  
load data using PandasAI’s own helper functions (such as `pai.read_csv()` or  
`pai.read_excel()`), the library automatically wraps the underlying pandas  
DataFrame in a SmartDataframe. This wrapper preserves all normal pandas  
operations while adding the `.chat()` method, enabling conversational queries  
powered by an LLM. SmartDataframes behave like regular DataFrames but include  
additional metadata, configuration, and logic required for PandasAI’s agent  
system.

### How to Detect a SmartDataframe

You can determine whether an object is a SmartDataframe by checking its class or  
by verifying the presence of the `.chat()` method. The examples below show the  
most common detection patterns:  

```python
import pandasai

# Method 1: Check the class name
type(df).__name__ == "SmartDataframe"

# Method 2: Check using isinstance
from pandasai.smart_dataframe import SmartDataframe
isinstance(df, SmartDataframe)

# Method 3: Check for the chat method
hasattr(df, "chat")
```

A SmartDataframe will return `True` for at least one of these checks, while a  
regular pandas DataFrame will not. This makes it easy to confirm whether a  
DataFrame has been auto‑wrapped by PandasAI or whether it needs to be wrapped  
manually using an `Agent`.  

## Basic Usage

This example shows how to load a dataset and get a summary using natural  
language queries.  

```python
import pandas as pd
import pandasai as pai
from pandasai import Agent
from pandasai_litellm.litellm import LiteLLM
import os

# Configure PandasAI globally to use LiteLLM with OpenAI
llm = LiteLLM(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
pai.config.set({"llm": llm})

df = pd.DataFrame(
    {
        "employee": ["Alice", "Bob", "Charlie", "Diana"],
        "department": ["Sales", "IT", "Sales", "HR"],
        "salary": [75000, 85000, 70000, 65000],
    }
)


agent = Agent(df)
response = agent.chat("What is the average salary by department?")
print(response)
```

The agent analyzes your DataFrame, understands that revenue equals price times  
units_sold, generates the code `df['price'] * df['units_sold']`, and returns  
the calculated results.  

Expected output: A summary showing revenue per product calculated as price  
multiplied by units sold.  


## Natural Language Queries

PandasAI excels at translating questions into data operations.  

### Filtering Data

```python
import pandas as pd
import pandasai as pai
from pandasai import Agent
from pandasai_litellm.litellm import LiteLLM
import os

llm = LiteLLM(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
pai.config.set({"llm": llm})

df = pd.DataFrame({
    'employee': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'department': ['Sales', 'IT', 'Sales', 'HR'],
    'salary': [75000, 85000, 70000, 65000],
    'years': [5, 3, 7, 2]
})

agent = Agent(df)

response = agent.chat("Show me employees in Sales with more than 5 years")
print(response)
```

The agent generates filtering logic based on multiple conditions and returns  
matching records.  

### Grouping and Aggregation

```python
response = agent.chat("What is the average salary by department?")
print(response)
```

This generates a groupby operation on department with mean aggregation on  
salary column, returning averaged values per department.  

### Transforming Data

```python
response = agent.chat("Add a bonus column that is 10% of salary")
print(response)
```

The agent creates a new column by calculating 10% of each salary value and  
adds it to the DataFrame.  


## Generating Visualizations

PandasAI can create charts and graphs from natural language requests.  

```python
import pandas as pd
import pandasai as pai
from pandasai import Agent
from pandasai_litellm.litellm import LiteLLM
import os

llm = LiteLLM(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
pai.config.set({"llm": llm})

df = pd.DataFrame({
    'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    'revenue': [45000, 52000, 48000, 61000, 58000],
    'expenses': [32000, 38000, 35000, 42000, 40000]
})

agent = Agent(df)

response = agent.chat(
    "Create a bar chart showing revenue and expenses by month. "
    "Save the plot to a file and return only the file path."
)

print(response)

```

This command generates appropriate plotting code using matplotlib or plotly,  
creates the visualization, and displays it.  

The agent selects the right chart type based on your request (bar chart, line  
chart, scatter plot, etc.) and configures axes, labels, and legends  
automatically.  

Expected behavior: A bar chart appears with months on the x-axis and two bars  
per month showing revenue and expenses side by side.  


## Advanced Example: Data Cleaning and Analysis

This example demonstrates a more sophisticated workflow combining multiple  
operations.  

```python
import pandas as pd
from pandasai import Agent

df = pd.DataFrame({
    'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', 
             '2024-01-05', '2024-01-06', '2024-01-07'],
    'temperature': [22.5, 23.1, None, 24.8, 25.2, 23.9, 22.8],
    'humidity': [65, 68, 70, None, 72, 69, 66],
    'sales': [1200, 1450, 1380, 1520, 1680, 1590, 1420]
})

agent = Agent(df)

# Step 1: Identify data quality issues
response = agent.chat("How many missing values are in each column?")
print("Missing values:", response)

# Step 2: Clean the data
response = agent.chat("Fill missing temperature and humidity values with the mean")
print("Data cleaned:", response)

# Step 3: Analyze relationships
response = agent.chat(
    "Is there a correlation between temperature and sales? Show the correlation coefficient"
)
print("Correlation analysis:", response)

# Step 4: Find patterns
response = agent.chat("Which day had the highest sales and what was the temperature?")
print("Pattern found:", response)

# Step 5: Visualize trends
agent.chat("Create a line plot showing temperature and sales over time")
```

This workflow demonstrates how PandasAI can handle complex analytical tasks:  

1. **Data Quality Assessment**: Identifies missing values  
2. **Data Cleaning**: Fills gaps with statistical methods  
3. **Statistical Analysis**: Calculates correlations  
4. **Pattern Detection**: Finds relationships in the data  
5. **Visualization**: Creates meaningful charts  

Expected output: The agent provides answers to each query, fills missing values  
with column means, calculates correlation coefficients, identifies the peak  
sales day, and generates a dual-axis line chart showing trends.  


## Automated Exploratory Data Analysis

PandasAI can perform comprehensive dataset exploration automatically.  

```python
import pandas as pd
from pandasai import Agent

df = pd.DataFrame({
    'customer_id': range(1, 101),
    'age': [25, 34, 28, 42, 35] * 20,
    'purchase_amount': [150, 220, 180, 310, 275] * 20,
    'region': ['North', 'South', 'East', 'West', 'North'] * 20
})

agent = Agent(df)

# Get comprehensive overview
response = agent.chat(
    "Provide a comprehensive summary including shape, data types, "
    "missing values, and basic statistics"
)
print(response)

# Identify outliers
response = agent.chat("Find any outliers in the purchase_amount column")
print(response)

# Distribution analysis
agent.chat("Show the distribution of customers by region with a pie chart")

# Statistical insights
response = agent.chat("What is the age distribution? Show quartiles")
print(response)
```

This example shows how PandasAI can automate common EDA tasks that would  
normally require multiple lines of Pandas code. The agent generates descriptive  
statistics, identifies anomalies, and creates visualizations to help you  
understand your data quickly.  


## Best Practices

### Effective Query Writing

**Be Specific**: Clear questions get better results  

```python
# Good
agent.chat("What is the average price of products in the Electronics category?")

# Less effective
agent.chat("Tell me about prices")
```

**Use Column Names**: Reference actual column names when possible  

```python
# Good
agent.chat("Group by department and sum the sales_amount")

# Acceptable
agent.chat("What are total sales by department?")
```

**Break Complex Queries**: Split multi-step questions  

```python
# Step by step
agent.chat("Filter for 2024 data")
agent.chat("Calculate monthly revenue from the filtered data")

# Instead of one complex query
```

### Performance Considerations

**Limit DataFrame Size**: PandasAI sends data context to the LLM  

- For large datasets, filter first or work with samples  
- Consider using only relevant columns  
- Be mindful of API costs with large context windows  

**Cache Common Queries**: Save results of expensive operations  

```python
# Cache results
monthly_summary = agent.chat("Calculate monthly totals")
# Use the cached result instead of re-querying
```

**Use Traditional Pandas When Appropriate**: Not every operation needs NL  

```python
# Simple operations are faster with regular Pandas
df.head()  # Instead of agent.chat("Show first 5 rows")
df.shape   # Instead of agent.chat("How many rows and columns?")
```

### When to Use PandasAI vs Standard Pandas

**Use PandasAI for:**  

- Exploratory questions without knowing exact syntax  
- Complex queries that require multiple operations  
- Generating visualizations quickly  
- Teaching or demonstrating data analysis  
- Prototyping and hypothesis testing  

**Use Standard Pandas for:**  

- Production code requiring reliability and speed  
- Simple operations (head, tail, shape, info)  
- Performance-critical applications  
- Situations without internet access  
- When you need complete control over execution  


## Limitations

### Current Constraints

**LLM Dependency**: Requires internet connection and API access  

- Cannot work offline  
- Subject to API rate limits and costs  
- Performance depends on LLM provider availability  

**Code Generation Accuracy**: May produce incorrect code  

- Complex queries can be misunderstood  
- Generated code should be reviewed for correctness  
- Edge cases might not be handled properly  

**Context Window Limits**: Large datasets may exceed LLM context  

- Full DataFrame schema might not fit in prompt  
- Very wide tables (many columns) can be problematic  
- Deep nested operations may confuse the model  

**Cost Considerations**: Each query consumes API tokens  

- Repeated queries add up  
- Large DataFrames increase token usage  
- Production use can become expensive  

### Not Ideal Scenarios

**When PandasAI May Not Be Ideal:**  

- **Production Systems**: Unpredictable execution time and costs  
- **Sensitive Data**: Sending data to external APIs raises privacy concerns  
- **High-Frequency Operations**: Too slow for real-time processing  
- **Deterministic Requirements**: LLM responses can vary  
- **Offline Environments**: No internet access available  
- **Large-Scale Processing**: Inefficient for big data workloads  

**Security and Privacy Concerns:**  

PandasAI sends your DataFrame schema and query to the LLM provider. Be cautious  
with:  

- Personal identifiable information (PII)  
- Confidential business data  
- Regulated data (HIPAA, GDPR compliance)  

For sensitive data, consider:  

- Using local LLM models  
- Anonymizing data before analysis  
- Using traditional Pandas instead  


## Conclusion

PandasAI represents a significant step forward in making data analysis more  
accessible. By combining the power of Pandas with the natural language  
understanding of large language models, it enables users to explore and analyze  
data through simple conversation.  

**Why PandasAI Is Useful:**  

- **Democratizes Data Analysis**: Non-programmers can work with data effectively  
- **Accelerates Workflows**: Reduces time from question to insight  
- **Educational Value**: Helps users learn Pandas by example  
- **Flexible Integration**: Works alongside existing Pandas code  
- **Reduces Cognitive Load**: No need to remember complex syntax  

**Future Potential:**  

As LLMs continue to improve, PandasAI will likely become more accurate and  
capable. Future developments may include:  

- Better understanding of complex analytical queries  
- Support for more data sources and formats  
- Enhanced visualization capabilities  
- Improved performance and reduced costs  
- Local model support for privacy-sensitive applications  
- Integration with broader data science ecosystems  

The library is part of a growing trend toward more intuitive, AI-powered  
development tools that make technical work accessible to a broader audience  
while empowering experts to work more efficiently.
