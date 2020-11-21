#Cose da fare:
    #Gestione playlists
    #fondere comandi, regexp start for " $"
    #usare dizionario per queue, lista per gestione random su indici
import asyncio
import discord
import youtube_dl
from discord.ext import commands
import os
from pathlib import Path
import random
from youtube_search import YoutubeSearch
import re
youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
                                    "format": "bestaudio/best",
                                    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
                                    "restrictfilenames": True,
                                    "noplaylist": True,
                                    "nocheckcertificate": True,
                                    "ignoreerrors": False,
                                    "logtostderr": False,
                                    "quiet": True,
                                    "no_warnings": True,
                                    "default_search": "auto",
                                    "source_address": "0.0.0.0" #setup to IPv4
                                    }
ffmpeg_options = {
                                "options": "-vn",
                                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"

                              }
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume = 0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get("title")
        self.url = data.get("url")
        self.duration = data.get("duration")

    @classmethod
    async def from_url( cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if "entries" in data:
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []
        self.running = False
        self.skipper = False
        self.shuff = False
        self.volume = 0.5

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel"""
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        channel = ctx.author.voice.channel
        await channel.connect()
        await self.client.ws.voice_state(ctx.guild.id, channel.id, self_deaf = True)

    @commands.command()
    async def skip(self,ctx):
        """Skip current song"""
        self.skipper = True

    @commands.command()
    async def shuffler(self,ctx):
        random.shuffle(self.queue)
        await ctx.invoke(self.client.get_command("stop"))
        self.shuff = True
        await ctx.invoke(self.client.get_command("join"))
        await ctx.invoke(self.client.get_command("yt"))

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(str(Path(os.getcwd()).parent) + os.path.sep + "file" + os.path.sep + query))
        ctx.voice_client.play(source)#, after=lambda e: print("Player error: %s" % e) if e else None)

        await ctx.send("Now playing: {}".format(query))

    @commands.command()
    async def yt(self, ctx, url = "", hidden = True):
        """Plays from a url"""
        #self.queue.append("https://www.youtube.com/watch?v=j0YXfeNxJJ0")
        #self.queue.append("https://www.youtube.com/watch?v=6Ejga4kJUts")
        actual_song = 0
        while actual_song < len(self.queue):
            player = await YTDLSource.from_url(self.queue[actual_song], loop=self.client.loop, stream=True)
            ctx.voice_client.play(player)#, after=lambda e: print("Player error: %s" % e) if e else None)
            await ctx.send("Now playing: {}".format(player.title))
            
            #override volume
            await ctx.invoke(self.client.get_command("volume_bot"), volume=self.volume*100)

            i = 0
            while i < (player.duration):    
                await asyncio.sleep(1)
                sec = (player.duration - i) % 60
                minut = (player.duration - i) // 60
                print("Song " + str(actual_song+1) + "/" + str(len(self.queue)) + "\t" + player.title + "\t" + str(minut) + ":" + str(sec))
               
                if self.skipper:
                    i = player.duration - 1
                    self.skipper = False
                    ctx.voice_client.stop()

                if self.shuff:
                    self.shuff = False
                    i = player.duration - 1
                    actual_song = -1
                
                if not ctx.voice_client.is_playing():
                    i -= 1


                i += 1
            if actual_song != -1:
                del self.queue[actual_song]
            else:
                actual_song = 0

        self.running = False
        #await ctx.invoke(self.client.get_command("stop"))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url"""
        pattern_url = "[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
        if not re.search(pattern_url,url):
            try:
                results = YoutubeSearch(url, max_results=1).to_dict()
                url = "https://www.youtube.com" + results[0]["url_suffix"]
                #del results[0]
            except:
                ctx.send("0 match for current research")
                return
        self.queue.append(url)
        if not self.running:
            self.running = True
            await ctx.invoke(self.client.get_command("yt"), url = url)
        else:
            player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
            await ctx.send(str(player.title) + " adding to queue")
        '''player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
        ctx.voice_client.play(player)#, after=lambda e: print("Player error: %s" % e) if e else None)
        await ctx.send("Now playing: {}".format(player.title))'''

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player"s volume"""
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        self.volume = volume / 100
        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def volume_bot(self, ctx, volume: int,hidden = True):
        """Changes the player"s volume only for bot invoke, not print messages."""
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        self.volume = volume / 100
        ctx.voice_client.source.volume = volume / 100

    @commands.command()
    async def queue(self,ctx):
        """Print queue"""
        if self.queue:
            out = "Elements in queue:\n"
            for q in self.queue:
                app = ytdl.extract_info(q)["title"]
                out += str(app) + '\n'
            await ctx.send(out)
        else:
            await ctx.send("Empty queue!")

    @commands.command()
    async def pause(self,ctx):
        if not ctx.voice_client.is_paused():
            ctx.voice_client.pause()
        else:
            await ctx.send('Nothing in pause!')

    @commands.command()
    async def resume(self,ctx):
        if not ctx.voice_client.is_playing():
            ctx.voice_client.resume()
        else:
            await ctx.send('Nothing to resume!')


    @commands.command()
    async def repeat(self,ctx):
        if self.running:
            self.queue.insert(1,self.queue[0])
            await ctx.send("Repeat current song.")
        else:
            await ctx.send("No song to repeat.")
    
    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()
        self.skipper = True
    
    @play.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                #raise commands.CommandError("Author not connected to a voice channel.")
        #elif ctx.voice_client.is_playing():
        #    await ctx.send("Adding queue ")

def setup(client):
    client.add_cog(Music(client))