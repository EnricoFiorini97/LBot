import discord
from discord import File
from discord.ext import commands
from discord.ext.commands import Bot
import os
from pathlib import Path

class DBot():
    def __init__(self, prefix = "/"):
        self.client = commands.Bot(command_prefix = prefix, intents = discord.Intents.all())
        self.config_loader()

    def config_loader(self):
        token_file_path = r"" + str(Path(os.getcwd()).parent) + os.path.sep + "config_files" + os.path.sep + "token.txt"
        
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.client.load_extension(f"cogs.{filename[:-3]}")

        self.client.run(open(token_file_path,"r").readline())

def main():
    DBot("$")

if __name__ == "__main__":  main()

