from pyrogram import Client, filters, types
from credentials import API_ID, API_HASH, PHONE_NUMBER, SOURCE_CHANNELS, CHANNEL, TARGET_MESSAGES

app = Client("session", api_id=API_ID, api_hash=API_HASH,
             phone_number=PHONE_NUMBER)

@app.on_message(filters.chat(SOURCE_CHANNELS))
def new_channel_post(client: Client, message: types.Message):
    for msg in TARGET_MESSAGES:
        if message.text.lower().find(msg) >= 0:
            message.forward(CHANNEL)
            break

if __name__ == '__main__':
    print('Bot is running')
    app.run()