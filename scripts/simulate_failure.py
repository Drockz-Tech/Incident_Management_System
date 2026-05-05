import asyncio
import aiohttp
import time

API_URL = "http://localhost:8000/api/signals"

async def send_signal(session, component, error_type, message):
    payload = {
        "component_id": component,
        "error_type": error_type,
        "latency_ms": 1500.0,
        "message": message,
        "metadata": {"source": "failure_simulation"}
    }
    try:
        async with session.post(API_URL, json=payload) as response:
            return response.status
    except Exception as e:
        return str(e)

async def simulate_outage():
    async with aiohttp.ClientSession() as session:
        print("--- Initiating Failure Simulation Scenario ---")
        
        # 1. Simulating RDBMS Outage (Burst of ConnectionRefused errors)
        print("\n[Phase 1] Simulating RDBMS Outage (PostgreSQL DB1)")
        rdbms_tasks = []
        for i in range(500):
            rdbms_tasks.append(send_signal(session, "RDBMS_CLUSTER_PRIMARY", "ConnectionRefused", f"Failed to connect to primary DB instance - attempt {i}"))
        
        results = await asyncio.gather(*rdbms_tasks)
        success_count = sum(1 for r in results if r == 200)
        rate_limited = sum(1 for r in results if r == 429)
        print(f"> Sent 500 RDBMS failure signals. Success: {success_count}, Rate Limited: {rate_limited}")
        
        print("\n> Waiting 5 seconds before cascading failure...")
        time.sleep(5)
        
        # 2. Simulating cascading MCP failure (due to RDBMS being down)
        print("\n[Phase 2] Simulating MCP (Master Control Program) cascading failure")
        mcp_tasks = []
        for i in range(200):
            mcp_tasks.append(send_signal(session, "MCP_CORE_SERVICES", "Timeout", f"Timeout waiting for RDBMS response - request {i}"))
        
        results = await asyncio.gather(*mcp_tasks)
        success_count = sum(1 for r in results if r == 200)
        rate_limited = sum(1 for r in results if r == 429)
        print(f"> Sent 200 MCP failure signals. Success: {success_count}, Rate Limited: {rate_limited}")

if __name__ == "__main__":
    asyncio.run(simulate_outage())
