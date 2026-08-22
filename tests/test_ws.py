import pytest
import pytest_asyncio
import httpx
import websockets
import json

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

USER_A = {"username": "test_user_a", "email": "test_a@test.com", "password": "password123"}
USER_B = {"username": "test_user_b", "email": "test_b@test.com", "password": "password123"}


async def register(client: httpx.AsyncClient, user: dict):
    await client.post(f"{BASE_URL}/auth/register", json=user)


async def get_token(client: httpx.AsyncClient, user: dict) -> str:
    r = await client.post(f"{BASE_URL}/auth/login", json=user)
    r.raise_for_status()
    return r.json()["token"]


@pytest.fixture(scope="module")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def tokens():
    async with httpx.AsyncClient() as client:
        await register(client, USER_A)
        await register(client, USER_B)
        token_a = await get_token(client, USER_A)
        token_b = await get_token(client, USER_B)
    return token_a, token_b


@pytest.mark.asyncio
async def test_ws_connect(tokens):
    token_a, _ = tokens
    async with websockets.connect(f"{WS_URL}/ws/1?token={token_a}") as ws:
        assert ws.open


@pytest.mark.asyncio
async def test_ws_send_message(tokens):
    token_a, token_b = tokens

    async with websockets.connect(f"{WS_URL}/ws/1?token={token_a}") as ws_a, \
               websockets.connect(f"{WS_URL}/ws/2?token={token_b}") as ws_b:

        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{BASE_URL}/users/me",
                headers={"Authorization": f"Bearer {token_b}"}
            )
            receiver_id = r.json()["id"]

        await ws_a.send(json.dumps({"receiver_id": receiver_id, "message": "hello from test"}))

        resp = json.loads(await ws_a.recv())
        assert resp["type"] == "message_sent"
        assert resp["receiver_id"] == receiver_id


@pytest.mark.asyncio
async def test_ws_receive_message(tokens):
    token_a, token_b = tokens

    async with websockets.connect(f"{WS_URL}/ws/1?token={token_a}") as ws_a, \
               websockets.connect(f"{WS_URL}/ws/2?token={token_b}") as ws_b:

        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{BASE_URL}/users/me",
                headers={"Authorization": f"Bearer {token_b}"}
            )
            receiver_id = r.json()["id"]

        await ws_a.send(json.dumps({"receiver_id": receiver_id, "message": "ping"}))

        msg = json.loads(await ws_b.recv())
        assert msg["type"] == "new_message"
        assert msg["message"] == "ping"
