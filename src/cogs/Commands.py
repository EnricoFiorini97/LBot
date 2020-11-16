from io import IOBase
import discord
from discord import File, Permissions
from discord.ext import commands
from discord.ext.commands import Bot
import re
import os
import random 
import aiohttp
import json
from pathlib import Path
import requests
import sys

class my_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name = "ping", brief = "Return latency")
    async def ping(self, ctx):
        await ctx.send(f"pong! {round (self.client.latency * 1000)}ms")

    @commands.command(name = "gay", brief = "Return sender is gay")
    async def gay(self,ctx):
        await ctx.send(ctx.message.author.mention + " is gay!")

    @commands.command(name = "8ball", aliases = ["eight_ball", "eightball", "8-ball"], pass_context = True, brief = "Random answer to a question")
    async def eight_ball(self, ctx):
        ans = [
              "That is a resounding no",
              "It is not looking likely",
              "Too hard to tell",
              "It is quite possible",
              "Definitely"
              ]
        await ctx.send(random.choice(ans) + ", " + ctx.message.author.mention)

    @commands.command(name = "upload", brief = "Upload files")
    async def upload(self,ctx,*,args = None):
        if not args:    
            await ctx.send("Command syntax: upload <file>")
        try:
            await ctx.send(file = discord.File(str(Path(os.getcwd()).parent) + os.path.sep + "file" + os.path.sep + args))
        except IOError:
            await ctx.send("Upload failed!")
        
    @commands.command(name = "download", brief = "Download file")
    async def download(self,ctx,*,args = None):
        if not args:    
            await ctx.send("Command syntax: download <file>")
        try:
            file_name = args.split(r"/")[-1]
            open(str(Path(os.getcwd()).parent) + os.path.sep + "file" + os.path.sep + file_name,"wb").write(requests.get(args).content)
            await ctx.send("Download completed!")
        except IOError:
            await ctx.send("Download failed")

    @commands.command(name = "bitcoin", brief = "Return actual price of Bitcoin")
    @commands.has_role("mod")
    async def bitcoin(self,ctx):
        url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
        async with aiohttp.ClientSession() as session:  # Async HTTP request
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            await ctx.send("Bitcoin price is: $" + response["bpi"]["USD"]["rate"])
        
    @commands.command(name = "shutdown", brief = "Shutdown bot")
    async def shutdown(self, ctx):
        await ctx.send("Shutdown completed!")
        sys.exit(0)

    @commands.command(brief = "Delete last X message")
    async def clear(self, ctx, amount : str):
        try:
            await ctx.channel.purge(limit = int(amount))
        except:
            await ctx.send("Command syntax: clear <number>")

    @commands.command(brief = "Kick user")
    async def kick(self,ctx, member : discord.Member, *, reason = None):
        await member.kick(reason = reason)
        await ctx.send(f"Kicked {member.mention}")

    @commands.command(brief = "Ban user")
    async def ban(self, ctx, member : discord.Member, *, reason = None):
        await member.ban(reason = reason)
        await ctx.send(f"Banned {member.mention}")

    @commands.command(brief = "Unban user")
    async def unban(self, ctx, *, member):
        if not re.match("(.*)#(\d{4})",member):
            await ctx.send(f"Command syntax: unban <username>#<discriminator>")
            return
        banned_users = await ctx.guild.bans()
        name, discriminator = member.split("#")
        for ban_entry in banned_users:
            if ban_entry.user.name == name and ban_entry.user.discriminator == discriminator:
                await ctx.guild.unban(ban_entry.user)
                await ctx.send(f"Unbanned {ban_entry.user.mention}")
                return
        await ctx.send(f"User not banned")

    @commands.command()
    @commands.has_role("mod")
    async def addrole(self, ctx, member : discord.Member, role : discord.Role):
        await member.add_roles(role)

    @commands.command()
    @commands.has_role("mod")
    async def rmrole(self, ctx, member : discord.Member, role : discord.Role):  
        await member.remove_roles(role)

    @commands.command()
    @commands.has_role("mod")
    async def createrole(self, ctx, role):
        await ctx.guild.create_role(name = role)

    @commands.command()
    @commands.has_role("mod")
    async def deleterole(self, ctx, role : discord.Role):
        await role.delete()

    @commands.command()
    @commands.has_role("mod")
<<<<<<< HEAD
    async def addpermission(self, ctx, role: discord.Role, single_permission):
        perms = Permissions()
        eval("perms.update(" + str(single_permission) +" = True)")
        await role.edit(permissions = perms)
        #print(getattr(role.permissions,"send_messages"))
        await ctx.send("Permission table altered.")
    
    @commands.command()
    @commands.has_role("mod")
    async def rmpermission(self, ctx, role: discord.Role, single_permission):
        perms = Permissions()
        eval("perms.update(" + str(single_permission) +" = False)")
        await role.edit(permissions = perms)
        await ctx.send("Permission table altered.")
=======
    async def setuprole(self, ctx, role: discord.Role):
        await ctx.send("Work in progress...")
>>>>>>> 2ad272aa0bc338840293cfea3b227dcc01a36edb

def setup(client):
    client.add_cog(my_commands(client))