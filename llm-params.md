# LLM parameters 

**Temperature** and **Top-p** are both parameters used to control the randomness and  
creativity of an LLM's output. While they aim to achieve a similar goal, they do so in  
fundamentally different ways. The general recommendation is to adjust one or the other,  
but not both, for a single task.


## Temperature

**Temperature** is a value that directly scales the **probability distribution** of all possible  
next words (tokens). 

* *Low Temperature (e.g., 0.2)*: This makes the model more **deterministic** and predictable. It amplifies  
  the probability of the most likely tokens, making the model more likely to choose them.  
  This is ideal for tasks where you need factual accuracy and consistency, like summarization or  
  technical writing. A temperature of 0 will always select the single most probable token.  

* *High Temperature (e.g., 0.8+)*: This flattens the probability distribution, giving less likely    
  tokens a higher chance of being selected. This introduces more randomness and creativity into the output,  
  making it suitable for tasks like creative writing, brainstorming, or generating varied responses.  
  However, a value that's too high can lead to incoherent or nonsensical text.  


## Top-p (Nucleus Sampling)

**Top-p**, also known as **nucleus sampling**, works by setting a **cumulative probability threshold**.   
nstead of affecting the entire distribution like temperature, it dynamically filters the list of  
possible next words. 

* **How it Works**: The model calculates the probability of all possible next tokens and sorts them  
  from most likely to least likely. It then selects the smallest group of tokens whose cumulative  
  probability adds up to at least `p`. For example, if `top_p` is set to 0.9, the model will consider only  
  the most likely tokens that collectively account for 90% of the total probability. The model then  
  randomly samples from this "nucleus" of tokens.  

* **Low Top-p (e.g., 0.1)**: This restricts the model to a very small set of the most probable tokens,  
  resulting in predictable and constrained text. This is useful for maintaining a consistent tone and style.   

* **High Top-p (e.g., 0.9+)**: This allows the model to consider a broader range of tokens, promoting more  
  diverse and nuanced outputs. This is often preferred over temperature for creative tasks because it adapts to  
  the context. In a situation where a few words are highly likely, `top_p` will select from a small group, but in a  
  situation with many plausible next words, it will expand the group accordingly.  



## For Factual and Technical Tasks

* *Goal*: Precision, consistency, and correctness.  
* *Tasks*: Summarization, factual Q&A, code generation, and technical  
  documentation.
* *Recommended Settings*:
    * *Temperature*: Low (0.0 to 0.4). This forces the model to be more  
      deterministic and select the most probable tokens.  
    * *Top-p*: Low (0.1 to 0.5). This narrows the pool of potential tokens,  
      making the output more focused and less likely to contain irrelevant  
      information. A temperature of 0 will produce the same output every time  
      for the same prompt, which is ideal for fact-checking.  


## For Creative and Brainstorming Tasks

* *Goal*: Diversity, creativity, and imaginative output.  
* *Tasks*: Creative writing, poetry, script writing, and brainstorming.  
* *Recommended Settings*:  
    * *Temperature*: High (0.7 to 1.0). This flattens the probability curve,  
      giving less likely tokens a chance to be selected and creating more  
      unexpected text.  
    * *Top-p*: High (0.8 to 0.95). This expands the "nucleus" of tokens,  
      allowing the model to choose from a wider variety of words. This is often  
      preferred over a high temperature alone as it maintains some coherence.  


## For Conversational Chatbots

* *Goal*: Natural, human-like, and engaging responses.  
* *Tasks*: General-purpose chatbots, customer service agents, and interactive  
  assistants.  
* *Recommended Settings*:  
    * *Temperature*: Moderate (0.5 to 0.7). This balances randomness with  
      predictability, avoiding repetitive responses while still keeping the  
      conversation on track.  
    * *Top-p*: Moderate (0.5 to 0.8). This ensures a good variety of language  
      without resorting to very unusual or nonsensical words.  


Remember, these are starting points. The ideal settings can vary between  
different models and use cases, so experimentation is key to finding the best  
combination for your specific needs.  

## Deepseek documentation

The default value of temperature is 1.0.

We recommend users to set the temperature according to their use  
case listed in below.

| Use Case                      | Temperature |
|-------------------------------|-------------|
| Coding / Math                 | 0.0         |
| Data Cleaning / Data Analysis | 1.0         |
| General Conversation          | 1.3         |
| Translation                   | 1.3         |
| Creative Writing / Poetry     | 1.5         |



## Example

```python
#!/usr/bin/python
"""
Temperature and Top-P Parameter Demo with OpenAI

This script demonstrates the practical effects of temperature and top_p parameters
on OpenAI model outputs using a simple, focused example.

Key Learning Points:
- Temperature (0.0-2.0): Controls overall randomness
  - 0.0 = deterministic, same output every time
  - 1.0 = balanced creativity
  - 2.0 = maximum randomness

- Top-P (0.0-1.0): Controls vocabulary diversity via nucleus sampling
  - 1.0 = consider all possible words
  - 0.5 = consider only top 50% most likely words
  - 0.1 = very focused, only top 10% most likely words
"""

import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def demonstrate_parameter_effects():
    """Demonstrate temperature and top_p effects with clear examples."""
    
    prompt = "Write exactly one creative sentence about coffee."
    
    print("=" * 70)
    print("OPENAI LLM PARAMETERS: TEMPERATURE & TOP-P DEMO")
    print("=" * 70)
    print(f"Prompt: {prompt}")
    print()
    
    # Test cases showing parameter effects
    test_cases = [
        # (temperature, top_p, description)
        (0.0, 1.0, "Deterministic (temp=0.0, top_p=1.0)"),
        (0.3, 1.0, "Conservative (temp=0.3, top_p=1.0)"),
        (0.7, 1.0, "Balanced (temp=0.7, top_p=1.0)"),
        (1.0, 1.0, "Creative (temp=1.0, top_p=1.0)"),
        (1.5, 1.0, "Very Creative (temp=1.5, top_p=1.0)"),
        (1.0, 0.5, "Focused Creative (temp=1.0, top_p=0.5)"),
        (2.0, 1.0, "Maximum Randomness (temp=2.0, top_p=1.0)"),
    ]
    
    for temp, top_p, description in test_cases:
        print(f"\n🎯 {description}")
        print("-" * 50)
        
        # Generate 3 samples for each setting
        for i in range(3):
            try:
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temp,
                    top_p=top_p,
                    max_tokens=300
                )
                
                result = response.choices[0].message.content.strip()
                print(f"  Sample {i+1}: {result}")
                
            except Exception as e:
                print(f"  Sample {i+1}: Error - {e}")

def interactive_demo():
    """Interactive mode for testing custom parameters."""
    
    print("\n" + "=" * 70)
    print("INTERACTIVE PARAMETER TESTING")
    print("=" * 70)
    
    prompt = input("\nEnter your prompt (or press Enter for default): ").strip()
    if not prompt:
        prompt = "Write a creative product name for a new smartphone app."
    
    while True:
        try:
            temp = float(input("\nEnter temperature (0.0-2.0): "))
            top_p = float(input("Enter top_p (0.0-1.0): "))
            
            print(f"\n🎯 Testing: temp={temp}, top_p={top_p}")
            print("-" * 40)
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                top_p=top_p,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content.strip()
            print(result)
            
            again = input("\nTry another combination? (y/n): ").lower()
            if again != 'y':
                break
                
        except ValueError:
            print("Please enter valid numbers")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("Error: DEEPSEEK_API_KEY environment variable not set")
        print("Please set your OpenAI API key: export DEEPSEEK_API_KEY='your-key'")
        exit(1)
    
    print("Choose demo mode:")
    print("1. Parameter effects demonstration")
    print("2. Interactive parameter testing")
    
    choice = input("Enter 1 or 2: ").strip()
    
    if choice == "1":
        demonstrate_parameter_effects()
    elif choice == "2":
        interactive_demo()
    else:
        print("Invalid choice. Running parameter effects demo...")
        demonstrate_parameter_effects()
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print("Key takeaways:")
    print("- Lower temperature = more predictable outputs")
    print("- Higher temperature = more creative/random outputs")
    print("- Lower top_p = more focused vocabulary")
    print("- Higher top_p = more diverse word choices")
```




