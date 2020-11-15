import discord
from discord.ext import commands

class loader_commands(commands.Cog):
    def __init__(self,client):
        self.client = client
    
    @commands.command(brief = "Load cog file")
    async def load(self,ctx,extension):
        self.client.load_extension(f"cogs.{extension}")
        await ctx.send("Load completed!")

    
    @commands.command(brief = "Unload cog file")
    async def unload(self,ctx,extension):
        self.client.unload_extension(f"cogs.{extension}")
        await ctx.send("Unload completed!")


def setup(client):
    client.add_cog(loader_commands(client))
        