"""
Telegram Userbot — Otomatik Yorum
===================================
Belirtilen kanallarda yeni gönderi yayınlandığında
kişisel hesaptan otomatik 👍🏻 yorumu bırakır.

KURULUM:
  pip install telethon

KULLANIM:
  1. CONFIG bölümünü doldurun.
  2. python telegram_userbot.py
  3. İlk çalıştırmada telefon numarası ve doğrulama kodu istenir.
     Bu bilgiler session dosyasına kaydedilir, bir daha sorulmaz.
"""

from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDiscussionMessageRequest
import logging
import asyncio

# ─────────────────────────────────────────────
#  ⚙️  CONFIG — Sadece bu bölümü düzenleyin
# ─────────────────────────────────────────────

API_ID   = 32545802                        # my.telegram.org'dan alınan API ID (integer)
API_HASH = "1d1063236292e8b67d009da190b531dc"  # my.telegram.org'dan alınan API Hash

# Yorum yapılacak kanallar (username veya sayısal ID)
# Örnek: ["@kanal1", "@kanal2", -1001234567890]
HEDEF_KANALLAR = ['@bpthaber' , '@baku_es' , '@sondakikahaberlere' , '@depremturkk' ]


# Bırakılacak sabit yorum
YORUM_MESAJI = "👍🏻"

# Yorum göndermeden önce bekleme süresi (saniye) — ani işlem görünmemesi için
BEKLEME_SURESI = 3

# ─────────────────────────────────────────────
#  Loglama
# ─────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  Client
# ─────────────────────────────────────────────

client = TelegramClient("userbot_session", API_ID, API_HASH)

# ─────────────────────────────────────────────
#  Kanal listesini normalize et
# ─────────────────────────────────────────────

def normalize(channel):
    if isinstance(channel, int):
        return channel
    channel = channel.strip()
    if not channel.startswith("@"):
        channel = "@" + channel
    return channel.lower()

HEDEF_NORMALIZED = [normalize(k) for k in HEDEF_KANALLAR]


def hedef_mi(chat) -> bool:
    """Gelen mesajın kanalı hedef listesinde mi?"""
    if hasattr(chat, "username") and chat.username:
        if f"@{chat.username.lower()}" in HEDEF_NORMALIZED:
            return True
    if chat.id in HEDEF_NORMALIZED:
        return True
    return False


# ─────────────────────────────────────────────
#  Yeni gönderi handler
# ─────────────────────────────────────────────

@client.on(events.NewMessage(func=lambda e: e.is_channel and not e.is_group))
async def yeni_gonderi(event):
    chat = await event.get_chat()

    if not hedef_mi(chat):
        return

    kanal_adi = getattr(chat, "username", None) or str(chat.id)
    gonderi_id = event.message.id

    logger.info(f"📢 Yeni gönderi: @{kanal_adi} | ID: {gonderi_id}")

    await asyncio.sleep(BEKLEME_SURESI)

    try:
        # Kanalın bağlı tartışma grubundaki mesajı bul
        discussion = await client(GetDiscussionMessageRequest(
            peer=chat,
            msg_id=gonderi_id,
        ))

        # Tartışma grubuna ve ilgili mesaja yanıt olarak yorumu gönder
        group_peer  = discussion.chats[0]
        linked_msg  = discussion.messages[0]

        await client.send_message(
            entity=group_peer,
            message=YORUM_MESAJI,
            reply_to=linked_msg.id,
        )

        logger.info(f"✅ Yorum gönderildi: @{kanal_adi} / gönderi {gonderi_id}")

    except Exception as e:
        logger.error(f"❌ Hata — @{kanal_adi} / {gonderi_id}: {e}")


# ─────────────────────────────────────────────
#  Ana fonksiyon
# ─────────────────────────────────────────────

async def main():
    if API_ID == 0 or API_HASH == "BURAYA_API_HASH_YAZIN":
        raise ValueError("⛔ Lütfen API_ID ve API_HASH değerlerini girin!")

    await client.start()
    logger.info("✅ Userbot çalışıyor. Durdurmak için CTRL+C")
    logger.info(f"👀 Takip edilen kanallar: {HEDEF_KANALLAR}")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
