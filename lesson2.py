r"""
Lesson 2: Your First API Call with the OpenAI Python SDK - Chat Completions


A Single Inference Call (Not an Agent)

This is a stateless, one-shot query to an LLM. The model receives a prompt,
generates a response, and forgets everything. There's no loop, no tools,
no memory—just a direct request-response pattern.

Key characteristics of a single inference call:
- One request → one response
- No memory between calls
- No tools or actions
- Reactive (answers only when asked)
- Stateless

Question: Is this an AI Agent? Why or why not?

---

Setup:

Always create a virtual environment
1. python -m venv venv
2. source venv/bin/activate # On Windows use `venv\Scripts\activate`
3. deactivate # To exit the virtual environment

Install the dependencies
1. pip3 install openai
2. pip3 install dotenv

You can, however, install dependencies through pip freeze and a requirements.txt file:
1. pip3 freeze > requirements.txt
2. pip3 install -r requirements.txt
"""

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[
        {"role": "user", "content": "Where is Crazy Town in Tampere located?"}
    ]
)

# What is this response?
print(response)

# What is the type of this response?
print(type(response))

#What is the message content?
print(response.choices[0].message.content)

# What is this response message content?
#print(response.choices[0].message.content)

# Alternative way using the Responses API
# https://api.openai.com/v1/responses/{response_id}


"""
jose@jose-pc:~/Documents/Crazy Town$ python3 lesson2.py 
ChatCompletion(id='chatcmpl-D3TYcqil9ut3H1uD0qieLElsk19ii', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Crazy Town Tampere (the coworking/community hub) is located in **Finlayson area**, at:\n\n**Crazy Town Tampere (Finlayson)  \nVäinö Linnan aukio 13, 33210 Tampere, Finland**\n\nIt’s in the old Finlayson factory complex, near the city center.', refusal=None, role='assistant', annotations=[], audio=None, function_call=None, tool_calls=None))], created=1769720974, model='gpt-5.2-2025-12-11', object='chat.completion', service_tier='default', system_fingerprint=None, usage=CompletionUsage(completion_tokens=71, prompt_tokens=15, total_tokens=86, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=0, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0)))
<class 'openai.types.chat.chat_completion.ChatCompletion'>
Crazy Town Tampere (the coworking/community hub) is located in **Finlayson area**, at:

**Crazy Town Tampere (Finlayson)  
Väinö Linnan aukio 13, 33210 Tampere, Finland**

It’s in the old Finlayson factory complex, near the city center.
"""