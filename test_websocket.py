#!/usr/bin/env python3
"""
WebSocket Test Script for MCP Agent Backend
Tests the backend agent logic and Redis streaming functionality
"""

import asyncio
import json
import websockets
import time
import os
from typing import Dict, Any
from pathlib import Path

# Load environment variables
def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"📁 Loading environment from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"   {key}=***")
    else:
        print("⚠️ No .env file found, using system environment variables")

# Load environment variables first
load_env()

# Test configuration - corrected format
TEST_CONFIG = {
    "connections": [
        {
            "name": "default-mcp-server",
            "description": "Default MCP server with research tools",
            "transport": "sse",
            "url": "http://default-mcp-server:9000/sse",
            "connected": True
        }
    ]
}

# Test messages to verify different agent capabilities
TEST_MESSAGES = [
    "Hi",
    "Hi my name is John",
    "tell me a joke with my name",
    "get info on agentic ai and swlsx",
    "5+5 and info on diabetes"
]

class WebSocketTester:
    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.websocket = None
        self.test_results = []
        self.current_test = None
        
    async def connect(self):
        """Connect to the WebSocket endpoint"""
        try:
            print(f"🔌 Connecting to {self.websocket_url}...")
            self.websocket = await websockets.connect(self.websocket_url)
            print("✅ WebSocket connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the WebSocket"""
        if self.websocket:
            await self.websocket.close()
            print("🔌 WebSocket disconnected")
    
    async def send_message(self, message: str) -> bool:
        """Send a message to the WebSocket"""
        if not self.websocket:
            print("❌ WebSocket not connected")
            return False
        
        try:
            message_data = {
                "user_input": message,
                "mcp_config": TEST_CONFIG
            }
            print(f"📤 Sending message: {message}")
            print(f"📋 Message data: {json.dumps(message_data, indent=2)}")
            
            await self.websocket.send(json.dumps(message_data))
            return True
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False
    
    async def listen_for_responses(self, timeout: int = 30) -> Dict[str, Any]:
        """Listen for responses from the WebSocket"""
        if not self.websocket:
            return {}
        
        responses = {
            "processing": None,
            "streaming": [],
            "complete": None,
            "errors": [],
            "other": []
        }
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                try:
                    # Set a short timeout for receiving messages
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                    
                    print(f"📨 Received: {message}")
                    
                    try:
                        data = json.loads(message)
                        
                        if data.get("status") == "processing":
                            print(f"🔄 Processing started, result channel: {data.get('result_channel')}")
                            responses["processing"] = data
                            
                        elif data.get("progress") == "started":
                            print(f"🚀 Streaming started for agent: {data.get('agent_name')}")
                            responses["streaming"].append(data)
                            
                        elif data.get("progress") == "streaming" and data.get("chunk"):
                            print(f"📝 Streaming chunk: {data.get('chunk')}")
                            responses["streaming"].append(data)
                            
                        elif data.get("progress") == "complete":
                            print(f"✅ Message completed for agent: {data.get('agent_name')}")
                            responses["complete"] = data
                            break  # Test completed
                            
                        elif data.get("error"):
                            print(f"❌ Error received: {data.get('error')}")
                            responses["errors"].append(data)
                            
                        else:
                            print(f"📨 Other message: {data}")
                            responses["other"].append(data)
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse JSON: {e}")
                        responses["other"].append({"raw": message, "error": str(e)})
                        
                except asyncio.TimeoutError:
                    # No message received within 1 second, continue listening
                    continue
                    
        except Exception as e:
            print(f"❌ Error while listening: {e}")
            responses["errors"].append({"error": str(e)})
        
        return responses
    
    async def run_single_test(self, message: str, test_name: str) -> Dict[str, Any]:
        """Run a single test with the given message"""
        print(f"\n🧪 Running test: {test_name}")
        print(f"📝 Message: {message}")
        print("=" * 60)
        
        # Send the message
        if not await self.send_message(message):
            return {"success": False, "error": "Failed to send message"}
        
        # Listen for responses
        responses = await self.listen_for_responses()
        
        # Analyze results
        test_result = {
            "test_name": test_name,
            "message": message,
            "success": False,
            "responses": responses,
            "summary": ""
        }
        
        if responses["processing"]:
            test_result["summary"] += "✅ Processing started "
        else:
            test_result["summary"] += "❌ No processing status "
            
        if responses["streaming"]:
            test_result["summary"] += f"✅ {len(responses['streaming'])} streaming messages "
        else:
            test_result["summary"] += "❌ No streaming messages "
            
        if responses["complete"]:
            test_result["summary"] += "✅ Completed "
            test_result["success"] = True
        else:
            test_result["summary"] += "❌ Not completed "
            
        if responses["errors"]:
            test_result["summary"] += f"⚠️ {len(responses['errors'])} errors "
        
        print(f"📊 Test result: {test_result['summary']}")
        return test_result
    
    async def run_all_tests(self):
        """Run all test messages"""
        print("🚀 Starting WebSocket tests...")
        print(f"🔗 URL: {self.websocket_url}")
        print(f"🧪 Total tests: {len(TEST_MESSAGES)}")
        print(f"⚙️ Test config: {json.dumps(TEST_CONFIG, indent=2)}")
        
        if not await self.connect():
            return
        
        try:
            for i, message in enumerate(TEST_MESSAGES, 1):
                test_name = f"Test {i}: {message[:30]}{'...' if len(message) > 30 else ''}"
                result = await self.run_single_test(message, test_name)
                self.test_results.append(result)
                
                # Wait a bit between tests
                if i < len(TEST_MESSAGES):
                    print("⏳ Waiting 2 seconds before next test...")
                    await asyncio.sleep(2)
                    
        finally:
            await self.disconnect()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        successful_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        
        print(f"✅ Successful tests: {successful_tests}/{total_tests}")
        print(f"❌ Failed tests: {total_tests - successful_tests}/{total_tests}")
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test_name']}")
            print(f"   Summary: {result['summary']}")
            
            if result["responses"]["errors"]:
                print(f"   Errors: {len(result['responses']['errors'])}")
                
        print("=" * 80)

async def main():
    """Main function to run the WebSocket tests"""
    # Test with a simple session ID
    session_id = "test_session_123"
    websocket_url = f"ws://localhost:9889/tool-summary/ws/{session_id}"
    
    tester = WebSocketTester(websocket_url)
    await tester.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")