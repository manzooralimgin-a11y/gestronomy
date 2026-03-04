import asyncio
import argparse
import logging
import time

try:
    import websockets
except ImportError:
    logging.warning("websockets not installed. Run `pip install websockets` to load test.")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ws_load_tester")

async def ws_client(client_id: int, uri: str, duration: int):
    try:
        if 'websockets' not in globals():
            return
        async with websockets.connect(uri) as websocket:
            logger.info(f"Client {client_id} connected.")
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    await asyncio.wait_for(websocket.recv(), timeout=2.0)
                except asyncio.TimeoutError:
                    pass
                await asyncio.sleep(0.1)
                
            logger.info(f"Client {client_id} finished gracefully.")
    except Exception as e:
        logger.error(f"Client {client_id} failed: {e}")

async def run_load_test(connections: int, uri: str, duration: int):
    logger.info(f"Starting load test on {uri} with {connections} concurrent connections for {duration} seconds.")
    
    tasks = []
    for i in range(connections):
        tasks.append(ws_client(i, uri, duration))
        await asyncio.sleep(0.01)  # Stagger connections
        
    await asyncio.gather(*tasks)
    logger.info("Load test completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket Load Tester")
    parser.add_argument("--uri", type=str, default="ws://localhost:8000/api/dashboard/live", help="WebSocket URI")
    parser.add_argument("--connections", type=int, default=100, help="Number of concurrent connections")
    parser.add_argument("--duration", type=int, default=10, help="Duration of the test in seconds")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_load_test(args.connections, args.uri, args.duration))
    except KeyboardInterrupt:
        logger.info("Test interrupted.")
