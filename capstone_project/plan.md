# Capstone Project: Concert Poster Knowledge Graph Application

## Executive Summary

This plan details the complete architecture for transforming `lesson12-async.py` into a full-stack web application that:
- Extracts concert information from poster images using AI
- Stores data in a Neo4j Knowledge Graph (containerized)
- Provides a web interface for uploads, natural language queries, and visualizations
- Deploys to a cloud platform

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Backend Architecture (Neo4j Integration)](#2-backend-architecture-neo4j-integration)
3. [Frontend/Web Application](#3-frontendweb-application)
4. [Deployment & Infrastructure](#4-deployment--infrastructure)
5. [Implementation Phases](#5-implementation-phases)
6. [Project Structure](#6-project-structure)

---

## 1. Project Overview

### Current State (lesson12-async.py)
- Watches folder for concert poster images
- Extraction agent: Extracts concert info (bands, venues, dates) from images
- Enrichment agent: Adds genre/country via web search
- Outputs to CSV file

### Target State
- **Database**: Neo4j Knowledge Graph (Docker container)
- **Web App**: Upload interface, NL query, visualizations
- **Visualizations**: Maps, timelines, band connection graphs
- **Deployment**: Cloud platform (Railway recommended)

---

## 2. Backend Architecture (Neo4j Integration)

### 2.1 Docker Setup

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:5.15-community
    container_name: concert-knowledge-graph
    ports:
      - "7474:7474"  # HTTP (Neo4j Browser)
      - "7687:7687"  # Bolt protocol
    environment:
      - NEO4J_AUTH=neo4j/your_secure_password
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_apoc_export_file_enabled=true
      - NEO4J_apoc_import_file_enabled=true
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7474"]
      interval: 30s
      timeout: 10s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=your_secure_password
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      neo4j:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads

volumes:
  neo4j_data:
  neo4j_logs:
```

### 2.2 Neo4j Data Model

#### Node Types

| Node Label | Properties | Description |
|------------|------------|-------------|
| **Band** | `name` (unique), `created_at` | Musical act/artist |
| **Concert** | `date`, `event_name`, `source_image`, `extracted_at` | Performance instance |
| **Venue** | `name` (unique) | Physical location |
| **Location** | `name` (unique), `latitude`, `longitude` | Geographic location |
| **Genre** | `name` (unique) | Music genre |
| **Country** | `name` (unique), `code` | Country of origin |

#### Relationships

```
(:Band)-[:PERFORMED_AT]->(:Concert)
(:Band)-[:PLAYS_GENRE]->(:Genre)
(:Band)-[:FROM_COUNTRY]->(:Country)
(:Concert)-[:HELD_AT]->(:Venue)
(:Venue)-[:LOCATED_IN]->(:Location)
(:Location)-[:IN_COUNTRY]->(:Country)
```

#### Visual Schema

```
                                    ┌──────────────┐
                                    │   Country    │
                                    └──────────────┘
                                           ▲
                         FROM_COUNTRY      │      IN_COUNTRY
                    ┌──────────────────────┼──────────────────┐
                    │                      │                  │
              ┌─────┴─────┐          ┌─────┴─────┐           │
              │   Band    │          │  Location │◄──────────┘
              └─────┬─────┘          └─────▲─────┘
                    │                      │
        PLAYS_GENRE │    PERFORMED_AT      │ LOCATED_IN
                    │         │            │
              ┌─────▼─────┐   │      ┌─────┴─────┐
              │   Genre   │   │      │   Venue   │
              └───────────┘   │      └─────▲─────┘
                              │            │
                              │    HELD_AT │
                        ┌─────▼────────────┴─────┐
                        │        Concert         │
                        └────────────────────────┘
```

### 2.3 Python Neo4j Integration

**db/neo4j_client.py:**
```python
import os
from contextlib import asynccontextmanager
from neo4j import AsyncGraphDatabase, AsyncDriver
from dotenv import load_dotenv

load_dotenv()

class Neo4jClient:
    """Async Neo4j database client with connection pooling"""

    _driver: AsyncDriver | None = None

    @classmethod
    async def get_driver(cls) -> AsyncDriver:
        if cls._driver is None:
            cls._driver = AsyncGraphDatabase.driver(
                os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                auth=(
                    os.getenv("NEO4J_USER", "neo4j"),
                    os.getenv("NEO4J_PASSWORD", "password")
                ),
                max_connection_pool_size=50,
            )
        return cls._driver

    @classmethod
    async def close(cls):
        if cls._driver:
            await cls._driver.close()
            cls._driver = None

    @classmethod
    @asynccontextmanager
    async def session(cls, database: str = "neo4j"):
        driver = await cls.get_driver()
        session = driver.session(database=database)
        try:
            yield session
        finally:
            await session.close()
```

**db/repositories.py:**
```python
from datetime import datetime
from typing import Optional
from .neo4j_client import Neo4jClient

class ConcertRepository:
    @staticmethod
    async def create_or_update_band(name: str, genre: str, country: str) -> dict:
        query = """
        MERGE (b:Band {name: $name})
        ON CREATE SET b.created_at = datetime()

        WITH b
        UNWIND split($genre, ';') AS genre_name
        WITH b, trim(genre_name) AS clean_genre
        WHERE clean_genre <> '' AND clean_genre <> 'Unknown'
        MERGE (g:Genre {name: clean_genre})
        MERGE (b)-[:PLAYS_GENRE]->(g)

        WITH DISTINCT b
        WHERE $country <> '' AND $country <> 'Unknown'
        MERGE (c:Country {name: $country})
        MERGE (b)-[:FROM_COUNTRY]->(c)

        RETURN b.name AS band_name
        """
        async with Neo4jClient.session() as session:
            result = await session.run(query, name=name, genre=genre, country=country)
            record = await result.single()
            return {"band_name": record["band_name"]} if record else {}

    @staticmethod
    async def create_concert(
        band_name: str, venue_name: str, location: str,
        date: str, event_name: Optional[str], source_image: str
    ) -> dict:
        query = """
        MERGE (b:Band {name: $band_name})
        CREATE (c:Concert {
            date: $date,
            event_name: $event_name,
            source_image: $source_image,
            extracted_at: datetime()
        })
        MERGE (b)-[:PERFORMED_AT]->(c)
        MERGE (v:Venue {name: $venue_name})
        MERGE (c)-[:HELD_AT]->(v)
        MERGE (l:Location {name: $location})
        MERGE (v)-[:LOCATED_IN]->(l)

        WITH c, l
        WHERE $location CONTAINS ','
        WITH c, l, trim(split($location, ',')[-1]) AS country_name
        MERGE (country:Country {name: country_name})
        MERGE (l)-[:IN_COUNTRY]->(country)

        RETURN c.date AS concert_date
        """
        async with Neo4jClient.session() as session:
            result = await session.run(query, **locals())
            record = await result.single()
            return dict(record) if record else {}
```

### 2.4 Pipeline Modification (CSV → Neo4j)

Replace `append_to_csv()` in the pipeline:

```python
async def save_to_neo4j(source_image: str, extraction: EnrichedConcertExtraction):
    """Save extracted concert data to Neo4j knowledge graph"""
    from db.repositories import ConcertRepository

    for band_info in extraction.bands:
        await ConcertRepository.create_or_update_band(
            name=band_info.band_name,
            genre=band_info.genre,
            country=band_info.country
        )
        for concert in band_info.concerts:
            await ConcertRepository.create_concert(
                band_name=band_info.band_name,
                venue_name=concert.venue,
                location=concert.location,
                date=concert.date,
                event_name=concert.event_name,
                source_image=source_image
            )
    print(f"   Saved to Neo4j knowledge graph")
```

### 2.5 Key Query Patterns

```cypher
-- Band connections (shared concerts)
MATCH (b1:Band)-[:PERFORMED_AT]->(c:Concert)<-[:PERFORMED_AT]-(b2:Band)
WHERE b1.name < b2.name
RETURN b1.name AS band1, b2.name AS band2, count(c) AS shared_concerts

-- Concerts by location (for map)
MATCH (c:Concert)-[:HELD_AT]->(v:Venue)-[:LOCATED_IN]->(l:Location)
RETURN l.name AS location, l.latitude, l.longitude, collect(v.name) AS venues

-- Timeline data
MATCH (b:Band)-[:PERFORMED_AT]->(c:Concert)-[:HELD_AT]->(v:Venue)
RETURN c.date, c.event_name, b.name AS band, v.name AS venue
ORDER BY c.date

-- Bands by genre
MATCH (b:Band)-[:PLAYS_GENRE]->(g:Genre)
WHERE toLower(g.name) CONTAINS toLower($genre)
RETURN b.name AS band, collect(g.name) AS genres
```

---

## 3. Frontend/Web Application

### 3.1 Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Backend** | FastAPI | Native async, Pydantic integration |
| **Templates** | Jinja2 + HTMX | Server-rendered, no build step |
| **Interactivity** | Alpine.js | Lightweight reactivity |
| **Styling** | TailwindCSS | Utility-first CSS |
| **Maps** | Leaflet.js | Open source, free tiles |
| **Timeline** | vis-timeline | Purpose-built for timelines |
| **Graph** | vis-network | Force-directed graphs |

### 3.2 Page Structure

```
/                      → Dashboard (stats, recent uploads)
/upload                → Image upload with progress
/explore               → Natural language query interface
/visualize/map         → Concert locations map
/visualize/timeline    → Event timeline
/visualize/graph       → Band connections graph
/bands                 → Band directory
/bands/{name}          → Band detail page
```

### 3.3 Image Upload Flow

```
User Browser                    FastAPI Server                    Background Worker
     |                               |                                   |
     |-- POST /upload (multipart) -->|                                   |
     |                               |-- validate file type/size         |
     |                               |-- save to uploads/                |
     |                               |-- queue for processing            |
     |<-- { task_id, stream_url } ---|                                   |
     |                               |                                   |
     |-- SSE /tasks/{id}/stream ---->|                                   |
     |                               |-- asyncio.Queue for status ------>|
     |                               |                                   |-- Agent 1: extract
     |<-- event: extracting ---------|<-- status update -----------------|
     |                               |                                   |-- Agent 2: enrich
     |<-- event: enriching ----------|<-- status update -----------------|
     |                               |                                   |-- Save to Neo4j
     |<-- event: complete -----------|<-- final data --------------------|
```

**Upload Endpoint:**
```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

router = APIRouter()

@router.post("/upload")
async def upload_poster(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type {suffix} not allowed")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")

    task_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{task_id}{suffix}"
    file_path.write_bytes(contents)

    asyncio.create_task(process_image_pipeline(task_id, file_path))

    return {"task_id": task_id, "stream_url": f"/tasks/{task_id}/stream"}
```

### 3.4 Natural Language Query Interface

**Query Agent:**
```python
from pydantic import BaseModel
from pydantic_ai import Agent

class CypherQuery(BaseModel):
    cypher: str
    parameters: dict = {}
    explanation: str

NEO4J_SCHEMA = """
Nodes: Band, Venue, Location, Genre, Country, Concert
Relationships: PERFORMED_AT, PLAYS_GENRE, FROM_COUNTRY, HELD_AT, LOCATED_IN, IN_COUNTRY
"""

cypher_agent = Agent(
    'openai:gpt-4o',
    output_type=CypherQuery,
    instructions=f"""
    Generate READ-ONLY Cypher queries for a concert database.
    Schema: {NEO4J_SCHEMA}

    Rules:
    1. Only MATCH, RETURN, WITH, WHERE, ORDER BY, LIMIT
    2. NEVER generate CREATE, DELETE, SET, REMOVE, MERGE
    3. Use parameters ($param) for user values
    4. Always include LIMIT (default 100)
    """,
)

async def execute_natural_language_query(question: str) -> dict:
    result = await cypher_agent.run(question)
    query = result.output

    # Safety check
    forbidden = ['CREATE', 'DELETE', 'SET', 'REMOVE', 'MERGE', 'DROP']
    if any(word in query.cypher.upper() for word in forbidden):
        raise ValueError("Query contains forbidden operations")

    async with Neo4jClient.session() as session:
        records = await session.run(query.cypher, query.parameters)
        data = [record.data() async for record in records]

    return {
        "question": question,
        "cypher": query.cypher,
        "explanation": query.explanation,
        "results": data
    }
```

### 3.5 Visualizations

#### Map (Leaflet.js)
```javascript
const map = L.map('concert-map').setView([61.5, 24.0], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

async function loadLocations() {
    const response = await fetch('/api/locations');
    const locations = await response.json();
    locations.forEach(loc => {
        L.marker([loc.latitude, loc.longitude])
            .bindPopup(`<b>${loc.venue}</b><br>${loc.city}`)
            .addTo(map);
    });
}
```

#### Timeline (vis-timeline)
```javascript
const container = document.getElementById('timeline');
const timeline = new vis.Timeline(container, [], {
    stack: true,
    showCurrentTime: true,
    zoomMin: 1000 * 60 * 60 * 24,     // 1 day
    zoomMax: 1000 * 60 * 60 * 24 * 365 // 1 year
});

async function loadTimeline() {
    const response = await fetch('/api/timeline');
    const events = await response.json();
    const items = events.map((e, idx) => ({
        id: idx,
        content: e.event_name || e.band_name,
        start: e.date_start,
        title: `${e.band_name} at ${e.venue}`
    }));
    timeline.setItems(items);
}
```

#### Band Network (vis-network)
```javascript
const network = new vis.Network(container, { nodes: [], edges: [] }, {
    nodes: { shape: 'dot', scaling: { min: 10, max: 30 } },
    edges: { smooth: { type: 'continuous' } },
    physics: { barnesHut: { gravitationalConstant: -2000 } }
});

async function loadNetwork(connectionType = 'event') {
    const response = await fetch(`/api/graph?connection_type=${connectionType}`);
    const data = await response.json();
    network.setData(data);
}
```

---

## 4. Deployment & Infrastructure

### 4.1 Platform Recommendation: Railway

| Platform | Python Backend | Neo4j Support | Free Tier |
|----------|----------------|---------------|-----------|
| **Railway** | Excellent | Plugin available | $5/month credit |
| **Render** | Excellent | External only | 750 hrs/month |
| **Vercel** | Limited (serverless) | External only | Not recommended |

**Why Railway:**
- Native Docker support
- Neo4j plugin available
- Persistent volumes for uploads
- Easy environment variable management
- $5/month free credit

### 4.2 Neo4j Hosting Options

| Environment | Recommendation |
|-------------|----------------|
| Development | Docker Compose (local) |
| Staging | Railway Neo4j plugin or Aura Free |
| Production | Neo4j Aura Professional ($65/month) |

**Neo4j Aura Free Tier:**
- 1 instance
- 200K nodes, 400K relationships
- 1GB storage

### 4.3 Production Dockerfile

```dockerfile
FROM python:3.12-slim as builder
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY src/ ./src/
RUN mkdir -p /app/uploads && chmod 755 /app/uploads
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.4 Environment Variables

```bash
# .env.example
OPENAI_API_KEY=sk-...
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
ENVIRONMENT=development
LOG_LEVEL=DEBUG
MAX_UPLOAD_SIZE_MB=10
RATE_LIMIT_REQUESTS=100
```

### 4.5 CI/CD Pipeline (GitHub Actions)

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      neo4j:
        image: neo4j:5.26-community
        ports: ["7687:7687"]
        env:
          NEO4J_AUTH: neo4j/testpassword
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: ruff check src/
      - run: pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g @railway/cli
      - run: railway up --detach
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

### 4.6 Security Checklist

- [ ] Store API keys in environment variables (never in code)
- [ ] Use parameterized Cypher queries (prevent injection)
- [ ] Validate file uploads (MIME type, size)
- [ ] Configure CORS for production domains
- [ ] Implement rate limiting
- [ ] Use TLS for Neo4j connections in production
- [ ] Set up health check endpoints

### 4.7 Cost Estimate

| Service | Monthly Cost (Light) | Monthly Cost (Production) |
|---------|---------------------|---------------------------|
| Railway | $5-15 | $20-50 |
| Neo4j Aura | $0 (Free) | $65+ (Professional) |
| OpenAI API | $5-20 | $50-200+ |
| Domain | ~$1 | ~$1 |
| **Total** | **~$10-40** | **~$135-315** |

---

## 5. Implementation Phases

### Phase 1: Infrastructure Setup (Week 1)
1. Create `docker-compose.yml` with Neo4j
2. Set up Neo4j schema (constraints, indexes)
3. Create `db/neo4j_client.py` and `db/repositories.py`
4. Test Neo4j connection locally

### Phase 2: Pipeline Migration (Week 1-2)
1. Refactor `lesson12-async.py` into modular structure
2. Replace `append_to_csv()` with `save_to_neo4j()`
3. Test extraction → enrichment → Neo4j flow
4. Verify data in Neo4j Browser

### Phase 3: Web Application (Week 2-3)
1. Create FastAPI application structure
2. Implement image upload endpoint with SSE progress
3. Create Jinja2 templates with HTMX/Alpine.js
4. Build dashboard and upload pages

### Phase 4: Query & Visualization (Week 3-4)
1. Implement NL-to-Cypher query agent
2. Create visualization API endpoints
3. Integrate Leaflet (map), vis-timeline, vis-network
4. Build explore and visualize pages

### Phase 5: Deployment (Week 4)
1. Set up Railway project
2. Configure Neo4j Aura or Railway plugin
3. Set up CI/CD pipeline
4. Deploy and verify
5. Configure monitoring and alerts

---

## 6. Project Structure

```
capstone_project/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── railway.toml
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry point
│   ├── config.py                  # Settings
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── neo4j_client.py        # Connection manager
│   │   ├── repositories.py        # Data access
│   │   └── init_schema.py         # Schema setup
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── extraction.py          # Image extraction agent
│   │   ├── enrichment.py          # Band enrichment agent
│   │   └── query.py               # NL-to-Cypher agent
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py              # Upload endpoints
│   │   ├── query.py               # Query endpoints
│   │   ├── visualizations.py      # Viz data endpoints
│   │   └── pages.py               # HTML page routes
│   │
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── upload.html
│       ├── explore.html
│       └── visualize/
│           ├── map.html
│           ├── timeline.html
│           └── graph.html
│
├── static/
│   ├── css/
│   └── js/
│
├── uploads/                       # Uploaded images (gitignored)
│
└── tests/
    ├── __init__.py
    ├── test_neo4j.py
    └── test_agents.py
```

---

## Dependencies (requirements.txt)

```
# Web Framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6
jinja2>=3.1.3
sse-starlette>=1.6.5

# AI/Agents
pydantic>=2.5.0
pydantic-ai>=0.0.10
openai>=1.0.0

# Database
neo4j>=5.15.0

# Utilities
python-dotenv>=1.0.0
watchdog>=6.0.0
aiofiles>=24.1.0

# Security
slowapi>=0.1.9
python-magic>=0.4.27
```

---

## Quick Start Commands

```bash
# Start Neo4j (development)
docker-compose up -d neo4j

# Initialize schema
python -m src.db.init_schema

# Run application (development)
uvicorn src.main:app --reload --port 8000

# Deploy to Railway
railway login
railway init
railway up
```

---

## Critical Files Reference

| File | Purpose |
|------|---------|
| `lesson12-async.py` | Base extraction/enrichment pipeline |
| `lesson13_mcp_server.py` | MCP tool patterns for queries |
| `lesson13.py` | Agent context injection pattern |
| `concerts-async.csv` | Sample data structure |
