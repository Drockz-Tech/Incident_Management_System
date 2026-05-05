import asyncio
import aiohttp
import random
import time

API_URL = "http://localhost:8000/api/signals"

COMPONENTS = ["RDBMS_CLUSTER_01", "CACHE_CLUSTER_01", "API_GATEWAY_01", "MCP_HOST_02"]
ERRORS = ["Timeout", "ConnectionRefused", "OutOfMemory", "HighLatency"]

async def send_signal(session, component, i):
    payload = {
        "component_id": component,
        "error_type": random.choice(ERRORS),
        "latency_ms": random.uniform(10.0, 5000.0),
        "message": f"Simulated error {i} on {component}",
        "metadata": {"source": "simulation_script"}
    }
    try:
        async with session.post(API_URL, json=payload) as response:
            return response.status
    except Exception as e:
        return str(e)

async def simulate_burst(burst_size=1000):
    async with aiohttp.ClientSession() as session:
        target_component = random.choice(COMPONENTS)
        print(f"Simulating failure on {target_component} with {burst_size} signals...")
        
        start_time = time.time()
        tasks = []
        for i in range(burst_size):
            tasks.append(send_signal(session, target_component, i))
            
        results = await asyncio.gather(*tasks)
        
        duration = time.time() - start_time
        success_count = sum(1 for r in results if r == 200)
        rate_limited = sum(1 for r in results if r == 429)
        
        print(f"Sent {burst_size} signals in {duration:.2f} seconds.")
        print(f"Success: {success_count}, Rate Limited: {rate_limited}")

if __name__ == "__main__":
    print("Starting traffic simulation. Press Ctrl+C to stop.")
    try:
        while True:
            asyncio.run(simulate_burst(random.randint(100, 1000)))
            time.sleep(3)
    except KeyboardInterrupt:
        print("Simulation stopped.")
