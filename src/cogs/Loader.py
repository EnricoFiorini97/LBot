import discord
from discord.ext import commands

class commands_loader(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(brief = "Load cog file", hidden = True)
    async def load(self, ctx, extension):
        self.client.load_extension(f"cogs.{extension}")
        await ctx.send("Load completed!")
        
    @commands.command(brief = "Unload cog file", hidden = True)
    async def unload(self, ctx, extension):
        if extension != "Loader":
            self.client.unload_extension(f"cogs.{extension}")
            await ctx.send("Unload completed!")
        else:
            await ctx.send("Can't unload file Loader!")

def setup(client):
    client.add_cog(commands_loader(client))
        