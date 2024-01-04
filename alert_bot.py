from discord.ext import tasks
from products import get_latest
from channel_client import ChannelClient, PriceRule
import discord
import json
import random

# Load credentials
with open('credentials.json', 'r') as file:
    creds = json.load(file)

TOKEN = creds["token"]

# Starter webhook
# hook_url = creds["hook_url"]
# webhook = DiscordWebhook(url=hook_url, content="!start")

# Load autostart channels
with open('channels.json', 'r') as file:
    auto_channels = json.load(file)


def add_channel_to_auto(channel, auto_channels):
    auto_channels['channel_ids'].append(channel.id)
    with open('channels.json', 'w') as file:
        json.dump(auto_channels, file, indent=4)


def remove_channel_from_auto(channel, auto_channels):
    if channel.id in auto_channels['channel_ids']:
        auto_channels['channel_ids'].remove(channel.id)
        with open('channels.json', 'w') as file:
            json.dump(auto_channels, file, indent=4)

class AlertBot:

  def __init__(self):
    intents = discord.Intents.default()
    intents.message_content = True
    self.client = discord.Client(intents=intents)
    self.channel_clients: dict[int, ChannelClient] = {}
    self.guess_game_on: bool = False
    self.guess_number: int = 0

  async def start_channels(self, auto_channel):
    for channel in self.client.get_all_channels():
      if channel.id in auto_channel['channel_ids']:
        self.channel_clients[channel.id] = ChannelClient(channel)
        await self.send_message(channel, "BOT START\n")

  async def send_message(self, channel: discord.channel.TextChannel,
                         reponse: str):
    try:
      message = await channel.send(reponse)
      return message
    except Exception as e:
      print(e)

  async def handle_message(self, message: discord.message.Message):
    content = str(message.content).split('\n')
    for user_message in content:
      # hi handler
      if user_message.lower().startswith('!hi'):
        await self.send_message(message.channel, f"Hi, {message.author.name}!")
      # help handler
      elif user_message.lower().startswith("!help"):
        with open('commands.txt', 'r') as file:
          await self.send_message(message.channel, file.read())
      elif user_message.lower().startswith("!bot "):
        await self.send_message(message.channel,
                                "**!bot** command is not used anymore.")
      # guess the number
      elif user_message.lower() == "!guess":
        await self.send_message(message.channel,
                                "Ich habe eine Zahl von 1-10. Rate sie!")
        self.guess_game_on = True
        self.guess_number = random.randint(1, 10)
      elif user_message.isnumeric() and self.guess_game_on:
        if int(user_message) == self.guess_number:
          response = "Richtig!\n"
        else:
          response = "Falsch!\n"
        response += f"Meine Zahl war {self.guess_number}."
        await self.send_message(message.channel, response)
        self.guess_game_on = False
      # default handler
      elif user_message.lower().startswith("!"):
        await self.handle_bot_message(message, user_message)

  async def handle_bot_message(self, message: discord.message.Message,
                               user_message: str):
    user_channel = message.channel
    cmd = str(user_message).split()

    # starts bot in channel
    if cmd[0] == "!start" and (user_channel.id not in self.channel_clients):
      add_channel_to_auto(user_channel, auto_channels)
      new_client = ChannelClient(user_channel)
      self.channel_clients[user_channel.id] = new_client
      print(f"{user_channel} starts bot")
      await self.send_message(user_channel, "BOT START\n")

    if user_channel.id not in self.channel_clients:
      return

    # since here, bot must be started in channel
    channel_client = self.channel_clients[user_channel.id]
    if cmd[0] == "!stop":
      self.channel_clients.pop(user_channel.id)
      remove_channel_from_auto(user_channel, auto_channels)
      print(f"{user_channel} stops bot")
      await self.send_message(user_channel, "BOT STOP\n")

    if cmd[0] == "!rules":
      msg = "The price rules are:\n"
      for i, v in enumerate(channel_client.price_rules, start=1):
        role, rule = v
        msg += f"{i}. {rule} Role: {role}\n"
      await self.send_message(user_channel, msg)

    if cmd[0] == "!buzzwords":
      msg = "The buzzwords are:\n"
      for i, v in enumerate(channel_client.buzzwords, start=1):
        role, word = v
        msg += f"{i}. {word} Role: {role}\n"
      await self.send_message(user_channel, msg)

    if cmd[0] == "!add" and cmd[1] == "rule":
      try:
        min_price, max_price = float(cmd[3]), float(cmd[4])
        min_disc = int(cmd[5])
        role = cmd[2]
        rule = PriceRule(min_price, max_price, min_disc)
        channel_client.add_rule(rule, role)
        await self.send_message(user_channel, f"New rule: {rule}")
      except:
        await self.send_message(
            user_channel, "*Invalid format*\n" +
            "!add rule <min price> <max price> <min discount> <role id>")

    if cmd[0] == "!add" and cmd[1] == "buzzword":
      word = ' '.join(cmd[3:])
      role = cmd[2]
      channel_client.add_buzzword(word, role)
      await self.send_message(user_channel, f"New buzzword: {word}")

    if cmd[0] == "!del" and cmd[1] == "rule":
      if cmd[2].isnumeric():
        index = int(cmd[2]) - 1
        rule = channel_client.pop_rule(index)
        if rule:
          await self.send_message(
              user_channel, f"Delete rule: {rule}\n" +
              "*Attention: a deletion change the index.*")
          return
      await self.send_message(user_channel, "*Invalid index*")

    if cmd[0] == "!del" and cmd[1] == "buzzword":
      if cmd[2].isnumeric():
        index = int(cmd[2]) - 1
        rule = channel_client.pop_buzzword(index)
        if rule:
          await self.send_message(
              user_channel, f"Delete buzzword: {rule}\n" +
              "*Attention: a deletion change the index*")
          return
      await self.send_message(user_channel, "*Invalid index*")

  def run(self):

    @tasks.loop(seconds=10)
    async def alert_loop():
      try:
        latest = list(get_latest())
        for prod in latest:
          for cc in self.channel_clients.values():
            valid, role = cc.product_valid(prod)
            if not valid: continue
            msg_text = f"{role}\n{prod}"
            message = await self.send_message(cc.channel, msg_text)
            cc.add_product_to_file(message.created_at, prod)
            print(f"Sent {prod.name[:20]} to {cc.channel}")

      except Exception as e:
        print("Loop error ", e)

    @self.client.event
    async def on_ready():
      print(f"{self.client.user} is running.")
      # Start channels from savefile
      await self.start_channels(auto_channels)
      alert_loop.start()

    @self.client.event
    async def on_message(message: discord.message.Message):
      if message.author == self.client.user:
        return
      #handle message
      try:
        await self.handle_message(message)
      except Exception as e:
        print(e)

    self.client.run(TOKEN)


if __name__ == "__main__":
    bot = AlertBot()
    bot.run()
