# Prompts, Specs, and Plans

## Initial System Objective
The goal was to engineer a high-throughput, resilient Incident Management System (IMS) for a distributed stack. The system is designed to handle 10,000 signals per second using Python (FastAPI) with asynchronous queues and Redis-based rate limiting/debouncing. The mission-critical workflow includes stateful incident tracking and a mandatory Root Cause Analysis (RCA) process. The implementation features a high-performance, responsive React frontend.

## Step-by-Step Evolution and Prompts

### 1. Building Resilient Incident Management
**Prompt/Spec Received:** Create the foundation of the Incident Management System. Build a robust FastAPI backend capable of ingesting high volumes of failure signals. Implement rate-limiting via Redis, and an `asyncio.Queue` for absorbing traffic bursts. Persist raw data to MongoDB and processed incidents to PostgreSQL. Create a React frontend to visualize these alerts.
**Outcome:** Scaffolded backend using FastAPI, `motor` for Mongo, `asyncpg`/SQLAlchemy for Postgres, and `redis.asyncio` for Redis. Implemented token-bucket rate-limiting. Scaffolded frontend using React/Vite with Tailwind CSS.

### 2. Running Incident Management System
**Prompt/Spec Received:** Setup docker-compose and initialize the stack. Ensure the system handles concurrent load.
**Outcome:** Created `docker-compose.yml` to spin up PostgreSQL, MongoDB, and Redis concurrently, establishing the necessary infrastructure.

### 3. Launching Incident Management System
**Prompt/Spec Received:** Run the infrastructure and execute the backend and frontend components to ensure end-to-end functionality.
**Outcome:** Installed dependencies, confirmed DB connections, and refined API endpoints for incident retrieval and RCA submission via the React interface.

### 4. Optimizing Incident Processing System
**Prompt/Spec Received:** Enhance the resilience and data integrity of the ingestion pipeline. Specifically, prevent Out of Memory (OOM) errors by implementing a bounded `asyncio.Queue` and establish a linking mechanism between incoming signals and their Work Items in the NoSQL database.
**Outcome:** Upgraded `asyncio.Queue` with a bounded `maxsize` to drop excess traffic gracefully instead of crashing. Tied incoming signals to structured `WorkItems` using UUID reference keys across MongoDB and PostgreSQL.

### 5. Finalizing Submission Guidelines
**Prompt/Spec Received:** 
1. Codebase: A single repository containing /backend and /frontend.
2. README.md: Must include an Architecture Diagram, setup instructions (Docker Compose), and a section on how you handled Backpressure.
3. Sample Data: Provide a script or JSON file to mock a failure event across the stack (e.g., simulating an RDBMS outage followed by an MCP failure).
4. Prompts/Spec/Plans: All markdowns and prompts used to create this repository should be checked in.
5. Bonus points for any creative additions done.

**Outcome:** Created `scripts/simulate_failure.py` for cascading failure simulation, updated `README.md` with Mermaid architecture diagrams, and generated this `prompts.md` document tracking the conversational history and specifications.
