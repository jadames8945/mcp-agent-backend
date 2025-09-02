import asyncio
import json
import websockets
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_websocket_progress():
    uri = "ws://localhost:9889/tool-summary/ws"
    
    print("🔌 Connecting to WebSocket...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Wait for session establishment
            session_message = await websocket.recv()
            session_data = json.loads(session_message)
            print(f"📋 Session established: {session_data}")
            
            session_id = session_data.get("session_id")
            
            # Test message 1: Simple calculation
            print("\n🧮 Testing calculation: 5*5")
            test_message_1 = {
                "user_input": "Calculate 5*5",
                "mcp_config": {
                    "id": "test_config_1",
                    "user_id": "test_user",
                    "name": "Test Configuration",
                    "description": "Test MCP server configuration",
                    "connections": [
                        {
                            "name": "calculator",
                            "description": "Calculator MCP server",
                            "connected": True,
                            "transport": "streamable_http",
                            "url": "http://localhost:9000"
                        }
                    ]
                }
            }
            
            await websocket.send(json.dumps(test_message_1))
            print("📤 Sent calculation test message")
            
            # Listen for messages
            message_count = 0
            while message_count < 20:  # Limit to prevent infinite loop
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    message_data = json.loads(message)
                    message_count += 1
                    
                    print(f"\n📨 Message {message_count}:")
                    print(f"   Raw message: {message_data}")
                    
                    # Check for different message types
                    if 'progress' in message_data:
                        print(f"   Progress: {message_data['progress']}")
                    if 'agent_name' in message_data:
                        print(f"   Agent: {message_data['agent_name']}")
                    if 'chunk' in message_data:
                        chunk = message_data['chunk']
                        if chunk:
                            print(f"   Chunk: {chunk[:100]}...")
                        else:
                            print(f"   Chunk: (empty)")
                    if 'tool_name' in message_data:
                        print(f"   Tool: {message_data['tool_name']}")
                        print(f"   Step: {message_data.get('progress_step')}/{message_data.get('tool_len')}")
                        print(f"   Message: {message_data.get('message', 'N/A')}")
                    if 'status' in message_data:
                        print(f"   Status: {message_data['status']}")
                    if 'result_channel' in message_data:
                        print(f"   Result Channel: {message_data['result_channel']}")
                    
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
            
            # Wait a bit before next test
            await asyncio.sleep(2)
            
            # Test message 2: Stock information
            print("\n📈 Testing stock info: SWLSX")
            test_message_2 = {
                "user_input": "Get information on ticker SWLSX",
                "mcp_config": {
                    "id": "test_config_2",
                    "user_id": "test_user",
                    "name": "Test Configuration",
                    "description": "Test MCP server configuration",
                    "connections": [
                        {
                            "name": "finance",
                            "description": "Finance MCP server",
                            "connected": True,
                            "transport": "streamable_http",
                            "url": "http://localhost:9000"
                        }
                    ]
                }
            }
            
            await websocket.send(json.dumps(test_message_2))
            print("📤 Sent stock info test message")
            
            # Listen for messages for second test
            message_count = 0
            while message_count < 20:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    message_data = json.loads(message)
                    message_count += 1
                    
                    print(f"\n📨 Message {message_count}:")
                    print(f"   Raw message: {message_data}")
                    
                    # Check for different message types
                    if 'progress' in message_data:
                        print(f"   Progress: {message_data['progress']}")
                    if 'agent_name' in message_data:
                        print(f"   Agent: {message_data['agent_name']}")
                    if 'chunk' in message_data:
                        chunk = message_data['chunk']
                        if chunk:
                            print(f"   Chunk: {chunk[:100]}...")
                        else:
                            print(f"   Chunk: (empty)")
                    if 'tool_name' in message_data:
                        print(f"   Tool: {message_data['tool_name']}")
                        print(f"   Step: {message_data.get('progress_step')}/{message_data.get('tool_len')}")
                        print(f"   Message: {message_data.get('message', 'N/A')}")
                    if 'status' in message_data:
                        print(f"   Status: {message_data['status']}")
                    if 'result_channel' in message_data:
                        print(f"   Result Channel: {message_data['result_channel']}")
                    
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
            
            print("\n🎉 Test completed!")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_progress())
