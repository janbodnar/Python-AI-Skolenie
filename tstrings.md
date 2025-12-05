# Python 3.14 Template Strings (t-strings)

Template strings, or t-strings, are a new feature introduced in Python 3.14  
that provide a safer and more powerful way to handle string interpolation.  
They are designed to improve safety, readability, and tooling support when  
working with strings that contain dynamic content.  

T-strings extend Python's string handling capabilities by providing a  
structured approach to string formatting. Unlike f-strings which immediately  
evaluate and produce a string, t-strings produce a `Template` object that  
captures both the literal parts and the interpolated values separately. This  
separation allows for inspection, validation, and transformation before the  
final string is rendered.  

---

## Comparison with Existing Approaches

Python offers several methods for string formatting. Each approach has its  
own characteristics, advantages, and use cases. Understanding the differences  
helps developers choose the right tool for each situation.  

**F-strings** (formatted string literals) were introduced in Python 3.6.  
They provide inline expression evaluation with concise syntax. F-strings are  
evaluated immediately and produce a string result. They are excellent for  
simple formatting tasks but offer no built-in type safety or validation.  

**str.format()** is an older, more verbose formatting method available since  
Python 2.6. It separates the template from the values and supports named  
placeholders. While flexible, it lacks the readability of f-strings and  
provides no type checking.  

**T-strings** (template strings) introduced in Python 3.14 offer a new  
paradigm. They produce a `Template` object containing the structure and  
values separately, enabling inspection, validation, and type-safe  
processing before producing the final string.  

| Feature         | f-strings                  | str.format()            | tstrings (3.14)                  |
|-----------------|----------------------------|-------------------------|----------------------------------|
| Syntax          | `f"{var}"`                 | `"{}".format(var)`      | `t"{var}"`                       |
| Type Safety     | None                       | None                    | Enforced type hints              |
| Readability     | High                       | Medium                  | High + explicit typing           |
| Tooling Support | Limited                    | Limited                 | Enhanced (IDE/type checkers)     |

---

## Purpose

T-strings were introduced to address several limitations of existing string  
formatting approaches. The primary goals include stronger type guarantees,  
better integration with static analysis tools, and prevention of runtime  
errors.  

In large codebases, type correctness is essential for maintaining code  
quality and preventing bugs. T-strings enable developers to define expected  
types for interpolated values, allowing type checkers and IDEs to catch  
errors before runtime.  

Template strings also provide enhanced security by allowing validation and  
sanitization of interpolated values. This is particularly valuable when  
building SQL queries, HTML content, or other outputs where injection  
attacks are a concern.  

The structured nature of t-strings enables advanced use cases such as  
lazy evaluation, custom formatting pipelines, and integration with  
logging and monitoring systems that need to inspect template structure.  

---

## Usage Examples

The following examples demonstrate t-strings from basic usage to advanced  
patterns. Each example builds on previous concepts to show the full  
capabilities of template strings.  

### Simple variable interpolation

A basic example showing how to interpolate a string variable into a  
template string.  

```python
from string.templatelib import Template

name = "Alice"
greeting = t"Hello there, {name}"
print(greeting)  # Output: Template with 'Hello there, Alice'
```

The template captures the literal text and the interpolated value. When  
printed or converted to a string, the template renders the complete text.  

### Integer substitution

Template strings handle integer values with automatic conversion to their  
string representation.  

```python
from string.templatelib import Template

age = 25
message = t"You are {age} years old"
print(message)  # Output: Template with 'You are 25 years old'
```

The integer value is stored in the template and converted only when the  
template is rendered, allowing for type inspection before output.  

### Float formatting

Floating-point numbers can be interpolated with optional format  
specifications for precision control.  

```python
from string.templatelib import Template

price = 19.99
total = 157.8934
formatted = t"Price: ${price:.2f}, Total: ${total:.2f}"
print(formatted)
```

Format specifications work similarly to f-strings, controlling decimal  
places and other formatting options within the template.  

### String concatenation

Multiple variables can be combined within a single template string for  
building complex messages.  

```python
from string.templatelib import Template

first_name = "John"
last_name = "Doe"
full = t"{first_name} {last_name}"
print(full)  # Output: Template with 'John Doe'
```

The template maintains all interpolated values separately, enabling  
individual access or modification before rendering.  

### Boolean values

Boolean values are converted to their string representation when  
interpolated into template strings.  

```python
from string.templatelib import Template

is_active = True
status = t"Account active: {is_active}"
print(status)  # Output: Template with 'Account active: True'
```

The boolean is stored as its original type in the template, converted  
only during final string rendering.  

### Arithmetic inside tstrings

Expressions including arithmetic operations can be evaluated directly  
within the interpolation braces.  

```python
from string.templatelib import Template

a = 10
b = 5
result = t"Sum: {a + b}, Product: {a * b}"
print(result)  # Output: Template with 'Sum: 15, Product: 50'
```

The expressions are evaluated when the template is created, and the  
results are stored as interpolated values.  

### Conditional expressions

Ternary conditional expressions enable dynamic content based on  
conditions evaluated at template creation time.  

```python
from string.templatelib import Template

score = 85
grade = t"Result: {'Pass' if score >= 60 else 'Fail'}"
print(grade)  # Output: Template with 'Result: Pass'
```

Complex conditional logic can be embedded directly in the template,  
though separate variables are often clearer for readability.  

### Function calls inside tstrings

Functions can be called within interpolation braces, and their return  
values are captured in the template.  

```python
from string.templatelib import Template

def greet(name):
    return f"Greetings, {name}"

user = "Developer"
message = t"{greet(user)}! Welcome aboard."
print(message)  # Output: Template with 'Greetings, Developer! Welcome aboard.'
```

This enables dynamic content generation while maintaining the structured  
nature of the template string.  

### Using type hints explicitly

Type hints can be used with variables to enable static type checking  
of values used in template strings.  

```python
from string.templatelib import Template

username: str = "admin"
port: int = 8080
config = t"User: {username}, Port: {port}"
print(config)
```

Type checkers can verify that interpolated values match expected types,  
catching potential errors during development.  

### Nested tstrings

Template strings can be nested, allowing for compositional template  
building patterns.  

```python
from string.templatelib import Template

inner = t"inner content"
outer = t"Outer with [{inner}] embedded"
print(outer)
```

The inner template is converted to its string representation when  
embedded in the outer template.  

### Date formatting

Date and time objects can be formatted within template strings using  
standard format specifications.  

```python
from string.templatelib import Template
from datetime import datetime

now = datetime.now()
timestamp = t"Current time: {now:%Y-%m-%d %H:%M:%S}"
print(timestamp)
```

Date format codes work within the interpolation braces, providing  
flexible date and time formatting.  

### Path manipulation

Path objects from pathlib integrate naturally with template strings  
for building file path messages.  

```python
from string.templatelib import Template
from pathlib import Path

file_path = Path("/home/user/documents")
message = t"Working directory: {file_path}"
print(message)
```

Path objects are converted to their string representation when the  
template is rendered.  

### Dictionary lookups

Dictionary values can be accessed directly within template string  
interpolation braces.  

```python
from string.templatelib import Template

user = {"name": "Alice", "role": "Admin"}
info = t"User {user['name']} has role {user['role']}"
print(info)
```

Square bracket notation works for dictionary access within the  
interpolation expression.  

### List indexing

List elements can be accessed by index within template string  
interpolation braces.  

```python
from string.templatelib import Template

colors = ["red", "green", "blue"]
favorite = t"First color: {colors[0]}, Last: {colors[-1]}"
print(favorite)
```

Both positive and negative indices are supported for list element  
access within templates.  

### String alignment and padding

Format specifications support alignment and padding for creating  
formatted output with consistent widths.  

```python
from string.templatelib import Template

item = "Apple"
price = 1.50
row = t"{item:<10} ${price:>6.2f}"
print(row)  # Output: Template with 'Apple      $  1.50'
```

The alignment operators `<`, `>`, and `^` control left, right, and  
center alignment respectively.  

### Custom class with __str__

Custom classes with defined `__str__` methods integrate with template  
strings through their string representation.  

```python
from string.templatelib import Template

class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price
    
    def __str__(self):
        return f"{self.name} (${self.price})"

item = Product("Widget", 29.99)
display = t"Featured: {item}"
print(display)  # Output: Template with 'Featured: Widget ($29.99)'
```

The `__str__` method is called when the template is rendered to produce  
the final string output.  

### Custom class with type-enforced attributes

Type hints on class attributes enable static type checking for values  
used in template string interpolation.  

```python
from string.templatelib import Template
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str

user = User("Bob", 30, "bob@example.com")
profile = t"Name: {user.name}, Age: {user.age}"
print(profile)
```

Type checkers verify that attribute access matches declared types,  
providing early error detection.  

### Complex arithmetic expressions

Template strings support complex mathematical expressions with multiple  
operators and parentheses.  

```python
from string.templatelib import Template
import math

radius = 5
area = t"Circle area: {math.pi * radius ** 2:.2f}"
circumference = t"Circumference: {2 * math.pi * radius:.2f}"
print(area)  # Output: Template with 'Circle area: 78.54'
print(circumference)  # Output: Template with 'Circumference: 31.42'
```

Mathematical functions and constants from the math module integrate  
naturally within template expressions.  

### Multi-line tstrings

Template strings can span multiple lines using triple quotes for  
longer formatted content.  

```python
from string.templatelib import Template

name = "Alice"
department = "Engineering"
report = t"""
Employee Report
---------------
Name: {name}
Department: {department}
"""
print(report)
```

Multi-line templates preserve line breaks and indentation as part of  
the literal content.  

### Escaping braces

Literal brace characters are included in template strings by doubling  
them.  

```python
from string.templatelib import Template

value = 42
output = t"The value {{value}} is {value}"
print(output)  # Output: Template with 'The value {value} is 42'
```

Double braces `{{` and `}}` produce single literal braces in the  
rendered output.  

### Integration with logging

Template strings work with logging systems, allowing structured log  
messages with inspectable components.  

```python
from string.templatelib import Template
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_id = 12345
action = "login"
log_message = t"User {user_id} performed {action}"
logger.info(str(log_message))
```

The template structure enables logging systems to extract and index  
individual values for analysis.  

### Integration with SQL queries (safe typing)

Template strings provide a foundation for building SQL query builders  
that prevent injection attacks through value separation.  

```python
from string.templatelib import Template

def build_safe_query(template):
    # Extract literal parts and values separately
    # Values can be sanitized or parameterized
    return str(template)

user_input = "Alice"
table = "users"
query_template = t"SELECT * FROM {table} WHERE name = {user_input}"
safe_query = build_safe_query(query_template)
print(safe_query)
```

The template structure allows SQL builders to properly parameterize  
values, preventing SQL injection vulnerabilities.  

### Integration with JSON serialization

Template strings can be used to build JSON structures with proper  
value handling and validation.  

```python
from string.templatelib import Template
import json

name = "Product A"
price = 29.99
quantity = 100

data = {
    "name": name,
    "price": price,
    "quantity": quantity
}
json_preview = t"JSON: {json.dumps(data, indent=2)}"
print(json_preview)
```

JSON serialization within templates enables preview and logging of  
structured data in readable formats.  

### Using tstrings in decorators

Template strings can be used within decorators for logging, validation,  
or documentation purposes.  

```python
from string.templatelib import Template
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        message = t"Calling {func.__name__} with args={args}"
        print(message)
        return func(*args, **kwargs)
    return wrapper

@log_call
def add(a, b):
    return a + b

result = add(3, 5)  # Output: Template with 'Calling add with args=(3, 5)'
print(result)  # Output: 8
```

Decorators can use templates to create structured logging and  
monitoring output.  

### Combining tstrings with dataclasses and type checking

Dataclasses combined with template strings enable type-safe,  
structured data presentation.  

```python
from string.templatelib import Template
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Order:
    order_id: int
    customer: str
    total: float
    created_at: datetime = field(default_factory=datetime.now)
    
    def summary(self):
        return t"""
Order Summary
-------------
ID: {self.order_id}
Customer: {self.customer}
Total: ${self.total:.2f}
Date: {self.created_at:%Y-%m-%d}
"""

order = Order(1001, "Alice", 149.99)
print(order.summary())
```

This pattern combines type safety from dataclasses with the structured  
output capabilities of template strings, enabling IDE support and  
static analysis across the entire data flow.  

---

## Summary

Python 3.14 t-strings represent a significant evolution in Python's string  
handling capabilities. They provide a structured approach to string  
interpolation that enables type safety, inspection, validation, and  
transformation of template content.  

Key benefits include enhanced IDE and type checker support, improved  
security through value separation, and flexible integration with logging,  
database queries, and serialization systems. T-strings maintain the  
readability of f-strings while adding the power of deferred evaluation  
and structured access to template components.  

For projects requiring type safety, security-conscious string handling,  
or advanced template processing, t-strings offer a powerful new tool  
that builds on Python's tradition of readable and maintainable code.  
