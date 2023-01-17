from discord.ext import tasks
from products import Product,get_latest
from channel_client import ChannelClient, PriceRule
import discord
import json
import random


# Load credentials
with open('credentials.json','r') as file:
    creds = json.load(file)

TOKEN = creds["test_token"]


class AlertBot:
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents = intents)
        self.channel_clients:dict[str,ChannelClient] = {}
        self.guess_game_on: bool= False
        self.guess_number : int = 0

    async def send_message(self,channel:discord.channel.TextChannel, reponse:str):
        try:
            await channel.send(reponse)
        except Exception as e:
            print(e)
    
    async def handle_message(self,message:discord.message.Message):
        content = str(message.content).split('\n')
        for user_message in content:
            # help handler
            if user_message.lower().startswith("!help"):
                with open('commands.txt','r') as file:
                    await self.send_message(message.channel,file.read())
            elif user_message.lower().startswith("!bot "):
                await self.send_message(message.channel,"**!bot** command is not used anymore.")
            # guess the number
            elif user_message.lower() == "!guess" and not self.guess_game_on:
                await self.send_message(message.channel,"Ich habe eine Zahl von 1-10. Rate sie!")
                self.guess_game_on = True
                self.guess_number = random.randint(1,10)
            elif user_message.isnumeric() and self.guess_game_on:
                if int(user_message) == self.guess_number:
                    response = "Richtig!\n"
                else:
                    response = "Falsch!\n"
                response += f"Meine Zahl war {self.guess_number}."
                await self.send_message(message.channel,response)
                self.guess_game_on = False
            # default handler
            elif user_message.lower().startswith("!"):
                await self.handle_bot_message(message,user_message)
            

    async def handle_bot_message(self,message:discord.message.Message,user_message:str):
        user_channel = message.channel
        cmd = str(user_message).split()
        while len(cmd) < 7:
            cmd.append('#')
        
        # starts bot in channel 
        if cmd[0] == "!start":
            if user_channel.id not in self.channel_clients:
                new_client = ChannelClient(user_channel)
                self.channel_clients[user_channel.id] = new_client
                print(f"{user_channel} starts bot")
                await self.send_message(user_channel,"BOT START\n")
        
        if user_channel.id not in self.channel_clients:
            return

        # since here, bot must be started in channel
        channel_client = self.channel_clients[user_channel.id]
        if cmd[0] == "!stop":
            self.channel_clients.pop(user_channel.id)
            print(f"{user_channel} stops bot")
            await self.send_message(user_channel,"BOT STOP\n")
        
        if cmd[0] == "!rules":
            msg = "The price rules are:\n"
            for i,v in enumerate(channel_client.price_rules,start=1):
                role,rule = v
                msg += f"{i}. {rule} Role: {role}\n"
            await self.send_message(user_channel,msg)
        
        if cmd[0] == "!buzzwords":
            msg = "The buzzwords are:\n"
            for i,v in enumerate(channel_client.buzzwords,start=1):
                role,word = v
                msg += f"{i}. {word} Role: {role}\n"
            await self.send_message(user_channel,msg)
        
        if cmd[0] == "!add" and cmd[1] == "rule":
            try:
                min_price, max_price = float(cmd[2]), float(cmd[3])
                min_disc = int(cmd[4])
                role = cmd[5]
                rule = PriceRule(min_price,max_price,min_disc)
                channel_client.add_rule(rule,role)
                await self.send_message(user_channel,f"New rule: {rule}")
            except:
                await self.send_message(user_channel,"*Invalid format*\n"+
                "bot add rule <min price> <max price> <min discount> <role id>")
        
        if cmd[0] == "!add" and cmd[1] == "buzzword":
            word = cmd[2]
            role = cmd[3]
            channel_client.add_buzzword(word,role)
            await self.send_message(user_channel,f"New buzzword: {word}")
        
        if cmd[0] == "!del" and cmd[1] == "rule":
            if cmd[2].isnumeric():
                index = int(cmd[2])-1
                rule = channel_client.pop_rule(index)
                if rule:
                    await self.send_message(user_channel,f"Delete rule: {rule}\n"+
                    "*Attention: a deletion change the index.*")
                    return
            await self.send_message(user_channel,"*Invalid index*")

        if cmd[0] == "!del" and cmd[1] == "buzzword":
            if cmd[2].isnumeric():
                index = int(cmd[2])-1
                rule = channel_client.pop_buzzword(index)
                if rule:
                    await self.send_message(user_channel,f"Delete buzzword: {rule}\n"+
                    "*Attention: a deletion change the index*")
                    return
            await self.send_message(user_channel,"*Invalid index*")
    

    def run(self):
        @tasks.loop(seconds=10)
        async def alert_loop():
            try:
                latest = list(get_latest())
            except Exception as e:
                print("Error in scraping:\n"+e)
            for prod in latest:
                for cc in self.channel_clients.values():
                    valid,role = cc.product_valid(prod)
                    if not valid: continue
                    msg = f"{role}\n{prod}"
                    await self.send_message(cc.channel,msg)
                    print(f"Sent {prod.name[:20]} to {cc.channel}")
                    cc.sended_urls.append(prod.url)
        
        @self.client.event
        async def on_ready():
            print(f"{self.client.user} is running.")
            alert_loop.start()
        
        @self.client.event
        async def on_message(message: discord.message.Message):
            print(f"{message.author} ({message.channel}): {message.content} ({message.created_at})\n")
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