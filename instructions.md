# Welcome to a GPT-Lab hands-on

Title: Agentic AI in a programmatic way

Description:

Build confidence and independence on your journey of programming your own AI agents. This hands-on tutorial will show a friendly evolutionary steps, from the beginning with curl, basic OpenAI API requests, to an agentic framework, pydantic models and structured responses. At the end, you will learn how to programmatically harness agentic AI to effectively build knowledge discovery, both from LLM queries or your own data, and to visualize it. The goal is to present motivations for the use of these tools while building useful applications tailored to different contexts.

For this presentation, the attendees must have basic programming background, python is necessary.
Important: this is a BYOK (Bring Your Own Key) presentation.

From 9.15 to 11.00

-----
Preamble

Have the .env file in source folder with API key

# How to program agents and extract useful data

At the end of this tutorial you will create a : @folder

All the workshop is available on GitHub : github link


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

Now we use Claude Haiku 4.5

https://docs.anthropic.com/en/docs/about-claude/models


We had to change much of the code

6. The need for agentic framework: One code -> various models

Introducing Pydantic AI

7. Retrieving structured information in JSON

The problem with it, many lines of code, difficult to maintain.

8. Retrieving structured information with pydantic BaseModels (from LLM queries)

The simplicity of ensuring strong data type

Pydantic is the most widely used data validation library for Python.

9. Retrieving structured information with pydantic BaseModels (from an external file)

10. Pydantic AI agent framework - Extracting structured information from an image

# too much 10. Ingesting this retrieved structured information to a knowledge graph database

# too much 11. Creating a MCP server to make the data in the database querible by the LLM

11. The agentic approach: agent observing a watch folder. Show the image from the book

Environment ──(observations/percepts)──> Agent ──(actions)──> Environment


To be credibly “agent-like,” you’d add at least:

> 1. Temporal continuity: a loop (runs over time)
> 2. Environment + actions: tools/actuators (search, database, filesystem, web, messaging, etc.)
> 3. State/memory: internal state across steps (conversation state, working memory, task state)
> 4. Goal/policy: an objective guiding action selection, not just answering once

12. The agentic approach: agent observing a watch folder + a external database.

13. Have a conversation with the data.


Recommended sources:
Book: Agentic Artificial intelligence, by Pascal Bornet
Youtube videos:
1. How to Build AI Agents with PydanticAI (Beginner Tutorial) - https://www.youtube.com/watch?v=zcYtSckecD8
2. Building AI Applications the Pydantic Way - https://www.youtube.com/watch?v=zJm5ou6tSxk
3. Simplify AI Schemas with Pydantic & OpenAI (No More Manual JSON!) - https://www.youtube.com/watch?v=3Z03fwH1I7s
4. https://platform.claude.com/docs/en/intro
5. https://platform.openai.com/docs/api-reference/introduction

