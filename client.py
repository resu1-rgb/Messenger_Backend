import asyncio
import json
import websockets
import requests

class MessengerClient:
    def __init__(self, user_id: int, base_url: str = "http://localhost:8000", token: str = None):
        self.user_id = user_id
        self.base_url = base_url
        self.token = token
        self.websocket = None
        
    async def connect(self):
        """Подключение к WebSocket серверу"""
        ws_url = f"ws://localhost:8000/ws/{self.user_id}"
        self.websocket = await websockets.connect(ws_url)
        print(f"[{self.user_id}] Connected to chat server")
        
        # Запускаем задачу для прослушивания входящих сообщений
        asyncio.create_task(self.listen_messages())
        
    async def listen_messages(self):
        """Слушает входящие сообщения от сервера"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                msg_type = data.get("type")
                
                if msg_type == "new_message":
                    print(f"\n[{data['from']}]: {data['message']} (at {data['created_at']})")
                elif msg_type == "history":
                    print(f"\n[History from {data['from']}]: {data['message']} (at {data['created_at']})")
                elif msg_type == "message_sent":
                    print(f"\n[System] Message {data['message_id']} delivered to {data['receiver_id']}")
                else:
                    print(f"\n[System] Unknown message type: {data}")
                    
        except websockets.ConnectionClosed:
            print("[System] Connection closed")
        except Exception as e:
            print(f"[Error] {e}")
    
    async def send_message(self, receiver_id: int, content: str):
        """Отправляет сообщение через WebSocket"""
        if not self.websocket:
            print("Not connected!")
            return
        
        message = {
            "receiver_id": receiver_id,
            "message": content
        }
        await self.websocket.send(json.dumps(message))
        print(f"[{self.user_id} -> {receiver_id}]: {content}")
    
    def login(self, username: str, email: str, password: str):
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "email": email, "password": password}
        )
        if response.status_code == 200:
            self.token = response.json().get("token")
            print(f"[{self.user_id}] Logged in successfully")
        else:
            print(f"Login failed: {response.status_code} {response.text}")

    def get_history(self, other_user_id: int):
        """Получает историю переписки с другим пользователем через HTTP"""
        if not self.token:
            print("Authentication required for history")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/messages/history/{other_user_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            messages = response.json()
            print(f"\n--- History with {other_user_id} ---")
            for msg in messages:
                sender = "Me" if msg['user_id'] == self.user_id else f"User {msg['user_id']}"
                print(f"[{sender}]: {msg['message']} (at {msg['created_at']})")
            print("--- End of history ---\n")
        else:
            print(f"Failed to get history: {response.status_code}")
    
    async def close(self):
        """Закрывает соединение"""
        if self.websocket:
            await self.websocket.close()
            print("Connection closed")

# Пример использования клиента
async def main():
    # Создаем клиента для пользователя с ID=1 (в реальном проекте токен берется после логина)
    client1 = MessengerClient(user_id=1)
    client1.login("resul", "resul@gmail.com", "21102000098")
    await client1.connect()
    
    # Отправляем сообщение пользователю 2
    await client1.send_message(2, "Привет, мир!")
    
    # Получаем историю (в отдельной задаче, чтобы не блокировать)
    await asyncio.sleep(1)  # Даем время на получение сообщений
    client1.get_history(2)
    
    # Держим соединение открытым для прослушивания
    await asyncio.sleep(30)
    await client1.close()

if __name__ == "__main__":
    asyncio.run(main())