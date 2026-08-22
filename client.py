import asyncio
import getpass
import httpx
import websockets
import json

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


async def login(username: str, email: str, password: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{BASE_URL}/auth/login", json={"username": username, "email": email, "password": password})
        r.raise_for_status()
        return r.json()["token"]


async def run_client(token: str, receiver_id: int | None = None, message: str | None = None):
    uri = f"{WS_URL}/ws/1?token={token}"
    async with websockets.connect(uri) as ws:
        print("Connected!")

        async def read_incoming():
            try:
                while True:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    print("<<", json.loads(msg))
            except (asyncio.TimeoutError, websockets.ConnectionClosed):
                pass

        await read_incoming()

        if receiver_id and message:
            await ws.send(json.dumps({"receiver_id": receiver_id, "message": message}))
            print(">> sent")
            resp = await ws.recv()
            print("<<", json.loads(resp))


if __name__ == "__main__":
    token = asyncio.run(login(
        input("Username: "),
        input("Email: "),
        getpass.getpass("Password: ")
    ))
    print("Logged in successfully")

    receiver_id = input("Receiver ID (enter to skip): ").strip()
    message = input("Message (enter to skip): ").strip()

    asyncio.run(run_client(
        token,
        int(receiver_id) if receiver_id else None,
        message if message else None
    ))
