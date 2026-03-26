from telethon import TelegramClient, events
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import asyncio

API_ID = 36223586
API_HASH = "5bea113a019bb397eca36fad2c1f753d"
SOURCE_CHANNEL = "@haberzade"
TARGET_CHANNEL = "@haberlersemedya"

SESSION_NAME = "forwarder_session"

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_message(event):
    try:
        if event.message.text and event.message.media:
            await client.send_message(TARGET_CHANNEL, event.message.text, file=event.message.media)
        elif event.message.text:
            await client.send_message(TARGET_CHANNEL, event.message.text)
        elif event.message.media:
            await client.send_message(TARGET_CHANNEL, file=event.message.media)
        print(f"[✓] Mesaj iletildi | ID: {event.message.id}")
    except Exception as e:
        print(f"[✗] Hata: {e}")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, format, *args):
        pass

async def main():
    print("Bot başlatılıyor...")
    await client.start()
    source = await client.get_entity(SOURCE_CHANNEL)
    target = await client.get_entity(TARGET_CHANNEL)
    print(f"[✓] Kaynak kanal : {source.title}")
    print(f"[✓] Hedef kanal  : {target.title}")
    print("Bot çalışıyor. Mesajlar bekleniyor...")
    server = HTTPServer(('0.0.0.0', 10000), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
