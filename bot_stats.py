import discord
import json
import datetime

# Load credentials
with open('credentials.json', 'r') as file:
  creds = json.load(file)
TOKEN = creds["token"]

ALERTS_ID = 1063857337221263421

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

nye = datetime.datetime(2024, 1, 1)

new_sent_alerts = {}

# Bot alerts since 2024-01-01 00:00:00+01:00
async def get_bot_messages(channel:discord.TextChannel):
    async for message in channel.history(limit=None,after=nye,oldest_first=True):
        if message.author != client.user:
            continue
        if 'https://www.mydealz.de/deals/' not in message.content:
            continue
        timestamp = message.created_at.astimezone().replace(tzinfo=None)
        message_split = message.content.split('\n')
        url = list(filter(lambda x: x.startswith('https://www.mydealz.de/deals/'),
                          message_split))[0]
        product_code = url.split('-')[-1]
        if product_code in new_sent_alerts:
            continue
        new_sent_alerts[product_code] = {"datetime": str(timestamp),
                                     "url": url}
    return new_sent_alerts

def update_alerts_file(new_sent_alerts):
    # Load file
    with open('sent_alerts.json','r') as file:
        sent_alerts = json.load(file)
    # Add new alerts
    n_old = len(sent_alerts)
    print(f"Old alerts: {n_old}") 
    for product_code, dtu in new_sent_alerts.items():
        if product_code not in sent_alerts:
            sent_alerts[product_code] = dtu
    n_new = len(sent_alerts)
    print(f"New alerts: {n_new} ({n_new-n_old})")
    # write file
    with open('sent_alerts.json','w') as file:
        json.dump(sent_alerts, file, indent=4)

@client.event
async def on_ready():
    for channel in client.get_all_channels():
        if channel.id == ALERTS_ID:
            alerts_channel = channel
    new_sent_alerts = await get_bot_messages(alerts_channel)
    update_alerts_file(new_sent_alerts)
    await client.close()

client.run(TOKEN)
    

    