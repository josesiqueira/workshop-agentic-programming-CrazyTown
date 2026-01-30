r"""
Lesson 9: Introducing Pydantic AI agentic framework - Quickly switch between Anthropic and OpenAI and other LLMs

Setup:

Always create a virtual environment
1. python -m venv venv
2. source venv/bin/activate # On Windows use `venv\Scripts\activate`
3. deactivate # To exit the virtual environment

Install the dependencies
1. pip3 install pydantic_ai
2. pip3 install dotenv

You can, however, install dependencies through pip freeze and a requirements.txt file:
1. pip3 freeze > requirements.txt
2. pip3 install -r requirements.txt
"""

# -- RUN WITH OPENAI INSTEAD --

# from pydantic_ai import Agent
# from dotenv import load_dotenv

# load_dotenv()

# agent = Agent(  
#     'openai:gpt-5.2',
#     instructions='Be concise, reply with one sentence.',  
# )

# result = agent.run_sync('How do you say: Always check: your AI responses, in finnish?')  
# print(result.output)

# -- RUN WITH ANTHROPIC --

from pydantic_ai import Agent
from dotenv import load_dotenv

load_dotenv()

agent = Agent(  
    'anthropic:claude-haiku-4-5',
    instructions='Be concise, reply with one sentence.',  
)

result = agent.run_sync('Do I still need to learn programming in 2026?')  
print(result.output)

