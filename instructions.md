# Welcome to a GPT-Lab hands-on

Title: Agentic AI in a programmatic way

Description:

Build confidence and independence on your journey of programming your own AI agents. This hands-on tutorial will show a friendly evolutionary steps, from the beginning with curl, basic OpenAI API requests, to an agentic framework, pydantic models and structured responses. At the end, you will learn how to programmatically harness agentic AI to effectively build knowledge discovery, both from LLM queries or your own data, and to visualize it. The goal is to present motivations for the use of these tools while building useful applications tailored to different contexts.

For this presentation, the attendees must have basic programming background, python is necessary.
Important: this is a BYOK (Bring Your Own Key) presentation.

From 9.15 to 11.00

# GitHub link is : 
https://github.com/josesiqueira/workshop-agentic-programming-CrazyTown
-----
Preamble

Have the .env file in source folder with API key

# How to program agents and extract useful data

At the end of this tutorial you will create a : @folder

1.  a) The curl approach

        The simplest.

    b) The curl approach with web search

        More accurate!



2. The single API call to an LLM through python - ChatCompletions

It is tied to the OpenAI library



3. The single API call to an LLM through python - Responses API + Tool

Still tied to the OpenAI library, but now with a tool!

Chat Completions API was the old way, since March 2025 we have Responses API

# The Key Difference between Chat Completions and Responses API

| Feature             | Chat Completions         | Responses API                      |
|---------------------|--------------------------|-------------------------------------|
| State management    | You handle it            | OpenAI can handle it               |
| Built-in tools      | ❌                       | ✅ web search, file search, etc.   |
| Retrievable by ID   | Only with `store=True`   | Yes, by default                    |
| Complexity          | Simpler                  | More features                      |




4. Changing the model of the single API call to an LLM through python

Now we use Anthropic Claude Haiku 4.5

https://docs.anthropic.com/en/docs/about-claude/models


We had to change much of the code

6. Anthropic Responses API with Tool Calls + Allowed domains and Location

7. Structured information retrieval with OpenAI

8. Structured information retrieval with OpenAI + Pydantic BaseModel

9. Introducing Pydantic AI agentic framework - Quickly switch between Anthropic and OpenAI and other LLMs

10. Pydantic AI agentic framework - Extracting structured information from an image

11. The agentic approach: agent observing a watch folder. Show the image from the book

Different automation levels.
There is no unified agent definition.

Environment ──(observations/percepts)──> Agent ──(actions)──> Environment

To be credibly “agent-like,” you’d add at least:

> 1. Temporal continuity: a loop (runs over time)
> 2. Environment + actions: tools/actuators (search, database, filesystem, web, messaging, etc.)
> 3. State/memory: internal state across steps (conversation state, working memory, task state)
> 4. Goal/policy: an objective guiding action selection, not just answering once

12. The agentic approach: two agents
12.-async, Agents in paralell.

13. Have a conversation with the data - CSV in the input

14. Have a conversation with the data - FastMCP approach


Recommended sources:

1. Book: Agentic Artificial intelligence, by Pascal Bornet
    https://www.adlibris.com/fi/kirja/agentic-artificial-intelligence-harnessing-ai-agents-to-reinvent-business-work-and-life-9789819816224

2. YT: How to Build AI Agents with PydanticAI (Beginner Tutorial) - 
    https://www.youtube.com/watch?v=zcYtSckecD8

3. YT: Building AI Applications the Pydantic Way - 
    https://www.youtube.com/watch?v=zJm5ou6tSxk

4. YT: Simplify AI Schemas with Pydantic & OpenAI (No More Manual JSON!) - 
    https://www.youtube.com/watch?v=3Z03fwH1I7s

5. YT: MCP Crash Course: What Python Developers Need to Know - 
    https://www.youtube.com/watch?v=5xqFjh56AwM

6. Claude Docs
    https://platform.claude.com/docs/en/intro

7. OpenAI Reference API Docs
    https://platform.openai.com/docs/api-reference/introduction

8. Pydantic AI Docs
    https://ai.pydantic.dev/

9. FastMCP Docs
    https://gofastmcp.com/getting-started/welcome
