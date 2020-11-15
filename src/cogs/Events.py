from io import IOBase
import discord
from discord.ext import commands, tasks 
from discord.ext.commands import Bot
from itertools import cycle

class my_events(commands.Cog):
    
    def __init__(self,client):
        self.client = client
        self.game_list = cycle(["MTGArena", "Chess", "Rubik's Cube", "Pokémon Blue", "Call of Duty"])


    #Event Login
    @commands.Cog.listener()
    async def on_ready(self):
        #self.client.remove_command("help")
        await self.client.change_presence(activity = discord.Game(name = "Chess"))
        print("Logged on as:", self.client.user)
        self.change_status.start()


    #Event command not found
    @commands.Cog.listener()
    async def on_command_error(self,ctx, error):
        print(error)

        if "Member" in str(error) and "not found" in str(error):
            await ctx.send("Error - User not found.")

        elif "Role" in str(error) and "not found" in str(error):
            await ctx.send("Error - Role not found")

        elif "ExtensionAlreadyLoaded" in str(error):
            await ctx.send("Error - File alredy loaded.")

        elif "ExtensionNotLoaded" in str(error) or "ExtensionNotFound" in str(error):
            await ctx.send("Error - Command list don't exists.")

        elif "You are missing Manage Roles permission(s) to run this command." == str(error):
            await ctx.send("Looks like you don't have the perm.")

        else:
            await ctx.send("Error - Command not found. Run {}help.".format(ctx.prefix))

    #Member function, need channel
    @commands.Cog.listener()
    async def on_member_join(self,member):
        channel = discord.utils.get(self.client.guilds[0].text_channels, name = "welcome")
        await channel.send(f"Hi {member.name}, welcome to my Discord server!")
        #setup member basic role to user
        role = discord.utils.get(member.guild.roles,name = "user")
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        channel = discord.utils.get(self.client.guilds[0].text_channels, name = "welcome")
        await channel.send(f"Bye bye {member.name}!")


    #React to message, decorator listen to not ovverride command - BUG: run commands twice 
    @commands.Cog.listener()
    async def on_message(self,ctx):
        # No while true thanks
        if ctx.author == self.client.user:  return
        #print(ctx)

    @tasks.loop(seconds = 6)
    async def change_status(self):
        await self.client.change_presence(activity = discord.Game(next(self.game_list)))
        
def setup(client):
    client.add_cog(my_events(client))
    