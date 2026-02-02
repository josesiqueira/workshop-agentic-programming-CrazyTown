r"""
Lesson 13 MCP: Interactive CSV Query Agent using MCP

This version uses MCP (Model Context Protocol) to query the CSV file.
Instead of loading the entire CSV into the prompt (high input tokens),
the agent connects to an MCP server that provides tools to query the data.

The LLM only calls the tools it needs, significantly reducing input tokens.


Setup:

Install the dependencies
1. pip3 install "pydantic-ai-slim[mcp]"
2. pip3 install mcp
3. pip3 install dotenv

Run: python lesson13_mcp.py
"""

import asyncio
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv()

# MCP server that provides CSV query tools
csv_server = MCPServerStdio(
    'python',
    args=['lesson13_mcp_server.py'],
    timeout=30
)

# Create the query agent with MCP toolset
query_agent = Agent(
    'openai:gpt-5.2',
    toolsets=[csv_server],
    instructions="""
    You are a helpful assistant that answers questions about concert data.
    
    You have access to tools that can query a CSV database containing information 
    about bands, their genres, countries of origin, concert venues, locations, and dates.
    
    Available tools:
    - get_total_records: Get total count of records
    - list_all_bands: List all unique band names
    - list_all_genres: List genres with counts
    - list_all_countries: List countries with counts
    - get_bands_by_genre: Get bands matching a genre
    - get_bands_by_country: Get bands from a country
    - get_band_details: Get full details for a band
    - count_bands_by_genre: Count bands of a genre
    - search_records: Search all fields for a term
    
    Rules:
    - Use the appropriate tool to answer questions
    - Be precise and use tool results accurately
    - If no matching data is found, say so clearly
    - Be concise but helpful
    """,
)


async def main():
    print("MCP Query Agent - Token-Efficient CSV Queries")
    print("Using MCP server for on-demand data retrieval")
    print("Ask questions about the concert data. Type 'q' to exit.\n")
    
    # Use async context manager to manage MCP server connection
    async with query_agent:
        while True:
            try:
                # Get user input
                question = input("You: ").strip()
                
                # Check for exit
                if question.lower() == 'q':
                    print("Goodbye!")
                    break
                
                # Skip empty input
                if not question:
                    continue
                
                # Run the agent with the question
                result = await query_agent.run(question)
                
                print(f"\nAgent: {result.output}")
                print(f"[Tokens: {result.usage().input_tokens} in / {result.usage().output_tokens} out]\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())

# Ask @lesson13_mcp_server.py for "give me all the data", and ask @lesson13.py for the same question to see the difference in token usage.
# Can you explain why MCP is less token-efficient in this case?

# Your Capstone Project:

# Change the lesson12-async.py to ingest the data to a Knowledge Graph database (Neo4j). This Neo4j should be a containerized instance (Docker).
# Create a web application in which users can
# - upload images of concert posters
# - have the data extracted and enriched
# - store the data in the Neo4j database
# - query the database via a web interface using natural language (LLM-powered)
# - visualize the results (e.g., maps of concert locations, timelines, band connections etc.)
# Deploy the web application to a cloud platform (vercel, render, etc.)