import discord
import products

class ChannelClient:
    def __init__(self,channel:discord.channel.TextChannel):
        self.channel : discord.channel.TextChannel = channel
        self.is_active = True
        self.price_rules = []
        self.buzzwords  = []
        self.sended_urls : list[str] = []
    
    def add_rule(self,rule):
        self.price_rules.append(rule)
    
    def remove_rule(self,rule):
        if rule in self.price_rules:
            self.price_rules.remove(rule)
    
    def add_buzzword(self,buzzword):
        self.buzzwords.append(buzzword)
    
    def remove_buzzword(self,buzzword):
        if buzzword in self.buzzwords:
            self.buzzwords.remove(buzzword)
    