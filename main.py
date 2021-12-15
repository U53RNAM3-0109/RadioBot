#RadioBot

import discord
from discord.ext import commands
import logging
import datetime
import csv
import station_var
import os

admin_ids = [] #IDs of amdin users here (as integers)

#The following will write any error logs to a file.
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',
                              encoding='utf-8',
                              mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#Sets up bot
with open('prefix.txt', 'r') as f:
  pf = f.read()

client = commands.Bot(command_prefix=pf, case_insensitive=True)
client.help_command = None

#Runs command when ready
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f'{client.command_prefix}help on {len(client.guilds)} servers.'))
    print(f"""{client.user} is online.
----------------------------""")

#Adds a new channel to the dictionary
@client.command()
async def addchannel(ctx, channel_name : str):
    if channel_name not in station_var.valid_name_keys:
        print_log(ctx, 'addchannel - Success')
        print(f'''Adding channel "{channel_name}" to database.
    ID: {ctx.channel.id}
-----------------------------''')
        station_var.channel_names[channel_name] = ctx.channel.id
        await ctx.send("[Adding channel.]")
        
        print(station_var.guild_names)

        if str(ctx.guild.id) in station_var.guild_names.keys():
            print("Guild exists")
            print(station_var.guild_names[str(ctx.guild.id)])
            station_var.guild_names[str(ctx.guild.id)].append(channel_name)
            print(station_var.guild_names)
        
        else:
            print("Guild don't exist")
            station_var.guild_names[str(ctx.guild.id)] = [ctx.guild.name, channel_name]
            print(station_var.guild_names)
        
        update_ids()
    
    else:
        print_log(ctx, 'addchannel - failure')
        print('--------------------------')
        await ctx.send("[This name is already taken.]")

#Sends a message to a channel
@client.command()
async def contact(ctx, name : str, *, message):
    if name in station_var.valid_name_keys:
        print_log(ctx, 'contact - success')
        channel = client.get_channel(station_var.channel_names[name])
        await channel.send(f"{ctx.author}: {message}")
        print(f"""{ctx.author}: {message}
{name} {station_var.channel_names[name]}
------------------------------""")
    else:
        print_log(ctx, 'contact - failure')
        print('--------------------------')
        await ctx.send("[That name does not exist in the channel database.]")

#Remove a channel from the dict
@client.command()
async def removechannel(ctx, name : str):
    if ctx.author.id in admin_ids:
        if name != 'Station':
            if name in station_var.valid_name_keys:
                channel = client.get_channel(station_var.channel_names[name])
                await channel.send(f"[This channel has been removed.]")
                print(f"""{station_var.channel_names[name]} ({name})
            Removed from database by {ctx.author}.
    ------------------------------""")
                station_var.channel_names.pop(name, None)
                station_var.valid_name_keys.remove(name)
                update_ids()
            else:
                await ctx.send("[That channel does not exist in the database.]")
        else:
            await ctx.send("The Station will not be destroyed.")
            print(f'{ctx.author} attempted to destroy Station.')
    else:
      await ctx.send("Only RadioBot Admins can use this command.")
      print(f'{ctx.author} attempted to remove {name}.')

@client.command()
@commands.is_owner()
async def wipe(ctx):
    for i in station_var.valid_name_keys:
        if i == 'Station':
            continue
        channel = client.get_channel(station_var.channel_names[i])
        await channel.send(f"[This channel has been removed from the database.]")
        station_var.channel_names.pop(i, None)
    station_var.valid_name_keys = ['Station']
    update_ids()
    print("""All channels removed.
------------------------------""")
    print(station_var.channel_names)
    
#Kills the bot
@client.command()
async def kill(ctx):
    if ctx.author.id in admin_ids:
        await client.change_presence(status=discord.Status.offline)
        await ctx.send("[Going offline. Goodbye.]")
        quit()
    else:
      await ctx.send("Only RadioBot Admins can use this command.")
      print(f'{ctx.author} attempted to kill bot')

@client.command()
async def help(ctx):
    await ctx.send(f'''**-HELP MENU-**
This is a tool to message between channels, regardless of whether you have access to it.
This is done through the {client.command_prefix}contact command.

{client.command_prefix}contact <channel nickname> <message>
        Sends a message to the chosen channel, in the form of "username: <message>"

{client.command_prefix}addchannel <channel nickname>
        Creates a **single word** name for a channel.
        (This will be used to identify it when sending messages.)
        Once a name is used, it cannot be used again for another channel, so you may want to add the server name at the start to signify that it is yours.

{client.command_prefix}help
        This command shows this message.

{client.command_prefix}prefix
        Changes the bot's prefix. Only available to RadioBot Admins.
        (Currently just the creator.)

{client.command_prefix}removechannel <channel nickname>
        Removes the specified channel. Currrently only available to RadioBot Admins, but I am planning on expanding this to the person who linked the channel, too.

{client.command_prefix}display
        Displays a list of guild names, and the channels within them (that are in the database.)
        
{client.command_prefix}wipe
        Removes ALL channels from database. Only available to RadioBot Admins.

{client.command_prefix}kill
        Turns the bot off. Only available to RadioBot Admins.''')
    print(f'{ctx.author} asked for help.')
    print('--------------------------')

@client.command()
async def display(ctx):  #REWRITE
    for id in station_var.guild_names:
        send_string = ''
        for name in station_var.guild_names[id]:
            send_string += f'{name}\n    '
        await ctx.send(send_string)
        print(send_string)
    print(f'Displayed by {ctx.author}.')
    print('--------------------------')

@client.command()
async def prefix(ctx, pf : str):
    if ctx.author.id in admin_ids:
        client.command_prefix = pf
        print(f'{ctx.author} changed prefix to {pf}')
        await ctx.send('Prefix successfully changed.')
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f'{client.command_prefix}help on {len(client.guilds)} servers.'))
        with open('prefix.txt', 'w') as f:
            f.write(pf)
    else:
        print(f'{ctx.author} attempted to chang prefix to {pf}')
        await ctx.send('Only RadioBot Admins can do that.')

#########################
#Helper functions

def print_log(ctx, command):
    print(command)
    print(f"{ctx.author.name}    -    {ctx.author.id}")
    print(datetime.datetime.now())
    print(ctx.channel)

def message_clean(message):
    messsage = message.replace("'","").replace('"','').replace("(","").replace(")", "")
    return message.lower()

def restore_channel_ids():
    with open(station_var.filename, mode='r') as file:
        station_var.channel_names = {}
        station_var.valid_name_keys = []
        reader = csv.reader(file)
        for row in reader:
            station_var.channel_names[str(row[0])] = int(row[1])
            station_var.valid_name_keys.append(row[0])
    
    with open(station_var.guildfile, mode='r') as file:
      station_var.guild_names = {}
      reader = csv.reader(file)
      
      for row in reader:
          rowlist = []
          for i in range(len(row)-1):
              rowlist.append(row[i + 1])
          station_var.guild_names[str(row[0])] = rowlist

def save_channel_ids():
    with open(station_var.filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        for i in station_var.channel_names:
            row = [i, int(station_var.channel_names[i])]
            writer.writerow(row)
    
    with open(station_var.guildfile, mode='w', newline='') as file:
        writer = csv.writer(file)
        for i in station_var.guild_names:
            row = [i]
            for j in range(len(station_var.guild_names[i])):
                row.append(station_var.guild_names[i][j])

            writer.writerow(row)

def update_ids():
    save_channel_ids()
    restore_channel_ids()


##########################

print("Loading values.")

#Restore IDs from csv
restore_channel_ids()


token = os.environ['token']
client.run(token)
