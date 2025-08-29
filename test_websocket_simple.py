#!/usr/bin/env python3
import asyncio
import json
import websockets

async def test_websocket():
    uri = "ws://localhost:9889/tool-summary/ws/test-session"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected")
            
            message = {
                "type": "message",
                "content": "Get information on ticker SWLSX"
            }
            
            await websocket.send(json.dumps(message))
            print("✅ Message sent")
            
            response = await websocket.recv()
            print(f"✅ Response received: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 