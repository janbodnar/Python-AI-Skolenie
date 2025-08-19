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
