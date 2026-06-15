Welcome to the **Google GenAI SDK**  

The Google GenAI SDK is the official, production-ready gateway  
for developers to integrate Google’s most advanced generative  
AI models into their applications. Also referred to as the  
`google-genai` library, this Software Development Kit (SDK)  
provides a unified, high-performance interface for accessing  
models like Gemini, allowing you to build AI-powered features  
without managing the underlying complexity of API calls.  

### Why Choose the Google GenAI SDK?  

As the recommended way to build with the Gemini API, the SDK  
has reached **General Availability (GA)** and is fully supported  
for production use. It represents a significant evolution from  
legacy libraries, offering a streamlined developer experience  
with a focus on consistency and performance. If you're using  
older libraries like `google-generativeai` for Python, migrating  
is highly encouraged, as legacy versions are deprecated. The SDK  
is actively maintained and provides access to the latest features,  
ensuring your applications benefit from ongoing advancements in  
Google's AI technology.  

### Key Features and Unified Design  

The core strength of the SDK lies in its **centralized architecture**  
In previous versions, managing different services (like generating  
text, handling files, or using chat features) required separate  
clients or inconsistent methods. The new SDK simplifies this by  
providing a single `Client` object that acts as a unified entry point  
for all API services, including model interactions, file uploads,  
caching, and fine-tuning. This design makes credential and  
configuration management straightforward, allowing you to focus on  
building your application's logic. The SDK supports synchronous and  
asynchronous operations and includes strong typing via Pydantic models  
(in Python) to improve code safety and developer experience.  

### Getting Started in Minutes  

The `google-genai` library is available for **Python, JavaScript/TypeScript,  
Go, Java, and C#**, allowing developers to work in their language of choice.  
Installation is simple using standard package managers:  

*   **Python**: `pip install google-genai`  
*   **JavaScript**: `npm install @google/genai`  
*   **Go**: `go get google.golang.org/genai`  
*   **Java**: (Maven) add `google-genai` dependency  
*   **C#**: `dotnet add package Google.GenAI`  

Once installed, creating a client and generating content is just a few  
lines of code. The library supports both the Gemini Developer API (via an  
API key) and enterprise-grade Vertex AI, allowing you to seamlessly scale  
from prototyping to production.  

```python  
from google import genai  
  
# Initialize client with your API key  
client = genai.Client(api_key='YOUR_API_KEY')  
  
# Generate content from a text prompt  
response = client.models.generate_content(  
    model='gemini-2.5-flash',  
    contents='Explain what a GenAI SDK is in one sentence.'  
)  
  
print(response.text)  
```  

Whether you're building a chatbot, a code assistant, a content generation  
tool, or a multimodal reasoning application, the Google GenAI SDK provides  
the robust, efficient, and future-proof foundation you need to bring your  
ideas to life. We invite you to dive in, explore the official quickstart  
guide, and start building the next generation of AI-powered applications.  
