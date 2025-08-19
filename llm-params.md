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

* **Low Top-p (e.g., 0.1)**: This restricts the model to a very small set of the most probable tokens, resulting  
   in predictable and constrained text. This is useful for maintaining a consistent tone and style.  

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



