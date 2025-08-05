# LiteLLM


## Calculate cost of request

```python
import litellm

# track_cost_callback

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def track_cost_callback(
    kwargs,                 # kwargs to completion
    completion_response,    # response from completion
    start_time, end_time    # start/end time
):
    # print(kwargs)
    try:
        response_cost = kwargs.get("response_cost", 0)
        # print('completion response:', completion_response)
        print("The cost: ", response_cost)
        print(start_time, end_time)
        print(end_time - start_time, "seconds")
    except Exception as e:
        print("Error in tracking cost:", e)


# set custom callback function
litellm.success_callback = [track_cost_callback]

response = litellm.completion(
    model="deepseek/deepseek-chat",
    messages=[
        {"role": "user", "content": "What is the capital of Slovakia?"}
    ],
)

print(response.choices[0].message.content)
```
