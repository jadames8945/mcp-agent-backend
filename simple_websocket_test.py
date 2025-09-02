import asyncio
import json
import websockets
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_websocket():
    uri = "ws://localhost:9889/tool-summary/ws"
    
    print("🔌 Connecting to WebSocket...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Wait for session establishment
            session_message = await websocket.recv()
            session_data = json.loads(session_message)
            print(f"📋 Session established: {session_data}")
            
            # Test with the CORRECT config format
            test_message = {
                "user_input": "Get information on ticker SWLSX",
                "mcp_config": {
                    "id": "68a76a41172dacb00cd81239",
                    "user_id": "68a760ed5d16c20b6243ea61",
                    "name": "Default Configuration",
                    "description": "Default MCP server configuration",
                    "connections": [
                        {
                            "connected": True,
                            "description": "Default MCP server connection",
                            "name": "default",
                            "transport": "sse",
                            "url": "http://default-mcp-server:9000/sse"
                        }
                    ]
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Sent test message with correct config")
            
            # Listen for all messages
            message_count = 0
            while message_count < 30:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    message_data = json.loads(message)
                    message_count += 1
                    
                    print(f"\n📨 Message {message_count}:")
                    print(f"   Progress: {message_data.get('progress', 'N/A')}")
                    print(f"   Agent: {message_data.get('agent_name', 'N/A')}")
                    
                    # Check for progress_update messages specifically
                    if message_data.get('progress') == 'progress_update':
                        print(f"   🎯 PROGRESS UPDATE FOUND!")
                        print(f"   Tool: {message_data.get('tool_name', 'N/A')}")
                        print(f"   Step: {message_data.get('progress_step', 'N/A')}/{message_data.get('tool_len', 'N/A')}")
                        print(f"   Message: {message_data.get('message', 'N/A')}")
                    
                    if message_data.get('chunk'):
                        print(f"   Chunk: {message_data['chunk'][:100]}...")
                    
                    # Stop if we get a complete message
                    if message_data.get("progress") == "complete":
                        print("✅ Received complete message, stopping...")
                        break
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for message")
                    break
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
            
            print(f"\n🎉 Test completed! Received {message_count} messages total.")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
