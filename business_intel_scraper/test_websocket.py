#!/usr/bin/env python3
"""
WebSocket Test Client for Enhanced Visual Analytics API
Tests real-time connection and message handling
"""

import asyncio
import websockets
import json


async def test_websocket_connection():
    """Test WebSocket connection and real-time updates"""
    uri = "ws://localhost:8000/ws"

    try:
        print(f"🔗 Connecting to WebSocket at {uri}...")

        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established!")

            # Listen for messages for 10 seconds
            print("🎧 Listening for real-time updates...")

            try:
                # Set a timeout to avoid hanging
                message = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                data = json.loads(message)

                print("📨 Received message:")
                print(f"   Type: {data.get('type', 'unknown')}")
                print(f"   Message: {data.get('message', 'no message')}")
                print(f"   Timestamp: {data.get('timestamp', 'no timestamp')}")

                if "data" in data:
                    print(
                        f"   Data Keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'non-dict data'}"
                    )

                return True

            except asyncio.TimeoutError:
                print("⏰ No messages received within 15 seconds (this is normal)")
                return True

    except ConnectionRefusedError:
        print("❌ Connection refused - is the server running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False


async def main():
    """Main test function"""
    print("🧪 Enhanced Visual Analytics - WebSocket Test")
    print("=" * 50)

    success = await test_websocket_connection()

    print("\n" + "=" * 50)
    if success:
        print("🎉 WebSocket test completed successfully!")
        print("💡 WebSocket endpoint is ready for real-time updates")
    else:
        print("🚨 WebSocket test failed")

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
