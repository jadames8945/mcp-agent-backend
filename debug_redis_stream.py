#!/usr/bin/env python3
"""
Debug Redis Stream Script
Tests the Redis streaming functionality directly to isolate the issue
"""

import asyncio
import json
import time
import os
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

load_env()

async def test_redis_stream():
    """Test Redis streaming directly"""
    try:
        from common.services.redis_service import get_redis_client
        
        print("🔍 Testing Redis streaming directly...")
        
        # Get Redis client
        redis_client = await anext(get_redis_client())
        print("✅ Redis client connected")
        
        # Test channel
        test_channel = "chat_response_test_session_123"
        print(f"📡 Testing channel: {test_channel}")
        
        # Listen for messages on the channel
        print("👂 Listening for messages on Redis channel...")
        
        last_id = '0-0'
        start_time = time.time()
        timeout = 30  # 30 seconds
        
        while time.time() - start_time < timeout:
            try:
                # Read from the stream
                response = await redis_client.xread({test_channel: last_id}, block=2000, count=1)
                
                if response:
                    stream, messages = response[0]
                    for msg_id, msg in messages:
                        last_id = msg_id
                        print(f"📨 Redis message received:")
                        print(f"   ID: {msg_id}")
                        print(f"   Data: {msg}")
                        
                        # Try to parse the result if it exists
                        if b'result' in msg:
                            try:
                                result = json.loads(msg[b'result'].decode())
                                print(f"   Parsed result: {json.dumps(result, indent=2)}")
                            except:
                                print(f"   Raw result: {msg[b'result']}")
                        
                        if b'chunk' in msg:
                            chunk = msg[b'chunk'].decode()
                            print(f"   Chunk: {chunk}")
                            
                        if b'agent_name' in msg:
                            agent = msg[b'agent_name'].decode()
                            print(f"   Agent: {agent}")
                            
                        if b'progress' in msg:
                            progress = msg[b'progress'].decode()
                            print(f"   Progress: {progress}")
                            
                        print("-" * 50)
                        
                        # If we get a complete message, we can stop
                        if b'progress' in msg and msg[b'progress'].decode() == 'complete':
                            print("✅ Received complete message, stopping...")
                            return True
                else:
                    print("⏳ No messages in Redis stream, waiting...")
                    
            except Exception as e:
                print(f"❌ Error reading from Redis: {e}")
                break
                
        print("⏰ Timeout reached, no more messages")
        return False
        
    except Exception as e:
        print(f"❌ Failed to test Redis: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Starting Redis stream debug...")
    success = await test_redis_stream()
    
    if success:
        print("✅ Redis streaming test completed successfully")
    else:
        print("❌ Redis streaming test failed or incomplete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}") 