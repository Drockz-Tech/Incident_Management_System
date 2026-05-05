import base64
import urllib.request
import json

mermaid_code = """graph TD
    Client(Clients / Microservices) -->|10k+ signals/sec| IngestionAPI
    subgraph FastAPI Backend
        IngestionAPI(Ingestion API) --> RateLimiter(Redis Rate Limiting)
        RateLimiter -->|Token Bucket Pass| Queue(asyncio.Queue - Bounded)
        Queue -->|Workers Pull| Workers(Background Processors)
    end
    Workers -->|Raw Signal Dump| Mongo[(MongoDB)]
    Workers -->|Debounce & Deduplicate| Redis[(Redis)]
    Workers -->|Incident Creation| Postgres[(PostgreSQL)]
    Postgres --> FrontendAPI(Frontend API)
    FrontendAPI --> ReactUI(React / Vite Dashboard)
"""

# Mermaid ink uses base64 string of JSON
state = {
    "code": mermaid_code,
    "mermaid": "{\n  \"theme\": \"default\"\n}",
    "autoSync": True,
    "updateDiagram": True
}
json_state = json.dumps(state)
# standard base64 instead of urlsafe is sometimes preferred by mermaid.ink
encoded = base64.b64encode(json_state.encode('utf-8')).decode('utf-8')

url = f"https://mermaid.ink/img/{encoded}"
print("Downloading from mermaid.ink...")

req = urllib.request.Request(
    url, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0'
    }
)

with urllib.request.urlopen(req) as response, open("architecture.png", 'wb') as out_file:
    out_file.write(response.read())

print("Successfully generated and downloaded architecture.png")
