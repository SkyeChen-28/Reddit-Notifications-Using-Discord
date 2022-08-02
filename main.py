import discord as dc
from discord.ext import commands

from typing import Any
import asyncpraw as pr
from praw import Reddit
from prawcore import NotFound
import sys
import json
import asyncio
import nest_asyncio
from numpy import logical_and
import pandas as pd

# Datetime packages
from datetime import datetime as dt
from datetime import timedelta, tzinfo, date
from datetime import datetime as dt
# from datetime import timedelta
# from dateutil import parser
# from dateutil.parser import parse
from dateutil.tz import gettz
from typing import Collection, Union
import logging as log
import os

# Debugging async stuff
'''
loop = asyncio.get_event_loop()
y = loop.run_until_complete(x)
'''

class RedDiscConsts():
    def __init__(self, enter_fields = False):
        self.config_path = 'config.json'
        self.bot_admin = os.getenv('REDDIT_BOT_ADMIN')
        self.disc_bot_token = os.getenv('REDDISC_DISC_BOT')
        self.reddit_username = os.getenv('REDDISC_RED_USER')
                
        # Discord related constants
        self.intents = dc.Intents.default()
        self.COMMAND_PREFIX = '$' 
        
        # Error messages 
        self.SUBREDDIT_NOT_FOUND = 'Error, subreddit not found!'
        self.RESPONSE_TIMED_OUT = 'Response timed out, please send another command' 
        self.ENVVAR_NOT_SET = 'This was not saved into environment variables, you must do that manually'      
        
        if enter_fields:
            if (self.disc_bot_token is None):     
                warn_msg = 'No bot token in environment variable `REDDISC_DISC_BOT`.\n'
                warn_msg += 'It\'s recommended that you set that EnvVar as your bot\'s token\n'
                warn_msg += 'If you don\'t have a bot, create one here: https://discord.com/developers/applications/\n'
                log_and_print(warn_msg, terminal_print=True)
                self.disc_bot_token = input('Enter your bot token: ')   
                log_and_print(self.ENVVAR_NOT_SET)  
            if (self.bot_admin is None):
                warn_msg = 'No username set in environment variable `REDDIT_BOT_ADMIN`.\n'
                warn_msg += 'It\'s recommended that you set that EnvVar as your reddit username\n'
                log_and_print(warn_msg, terminal_print=True)
                self.bot_admin = input('Enter the bot_admin username: ')
                log_and_print(self.ENVVAR_NOT_SET)  
            if (self.disc_bot_token is None):
                warn_msg = 'No token set in environment variable `REDDISC_DISC_BOT`.\n'
                warn_msg += 'It\'s recommended that you set that EnvVar as your Discord bot\'s token\n'
                log_and_print(warn_msg, terminal_print=True)
                self.disc_bot_token = input('Enter the disc_bot_token: ')
                log_and_print(self.ENVVAR_NOT_SET)  
            if (self.reddit_username is None):
                warn_msg = 'No token set in environment variable `REDDISC_RED_USER`.\n'
                warn_msg += 'It\'s recommended that you set that EnvVar as your Reddit bot\'s username\n'
                log_and_print(warn_msg, terminal_print=True)
                self.reddit_username = input('Enter the reddit_username: ')
                log_and_print(self.ENVVAR_NOT_SET)  
            
    def init_discord_bot(self) -> dc.Client:
        # Initialize a Discord client
        disc_bot = commands.Bot(command_prefix=self.COMMAND_PREFIX, intents = self.intents)
        return disc_bot

    def init_reddit_bot(self) -> pr.Reddit:
        # Load necessary bot config data
        rdc = RedDiscConsts()
        bot_username = rdc.reddit_username
        bot_admin = rdc.bot_admin
        
        # Informative start up messages
        log_and_print('Setting up control for u/' + bot_username, terminal_print=True)
        log_and_print('Welcome u/' + bot_admin, terminal_print=True)
        
        # Load credentials from praw.ini to generate a Reddit instance
        try:
            reddit = pr.Reddit(bot_username)
        except:
            log_and_print("WARNING! praw.ini file not set up properly!")
            sys.exit("WARNING! praw.ini file not set up properly!")
            
        return reddit

def log_and_print(message: str, level: str = 'info', terminal_print: bool = True) -> None:
    '''
    str, str -> None
    
    Custom function for logging and printing a message. Function doesn't output anything.
    Possible levels:
    - debug
    - info
    - warning
    - error
    - critical
    '''
    
    if terminal_print:
        print(message)
    
    # Encode emojis differently    
    log_message = message#.encode('unicode_escape') # No longer required
    if level == 'debug':
        log.debug(log_message)
    elif level == 'info':
        log.info(log_message)
    elif level == 'warning':
        log.warning(log_message)
    elif level == 'error':
        log.error(log_message)
    elif level == 'critical':
        log.critical(log_message)
        
def utc_str_now() -> str:
    '''
    Returns the current time in UTC

    Returns:
        str: The current datetime
    '''
    return str(dt.utcnow()) + ' UTC' 
        
def read_config_file(config_dir: str) -> dict:
    '''
    Reads in the given ...config.json file

    Args:
        config_dir (str): File path to the ...config.json file

    Returns:
        dict: Contains the configuration parameters for the bot
    '''
    
    with open(config_dir) as fp:
        config_dict = json.load(fp)
    
    return config_dict

def update_config_file(config_dir: str, config_dict: dict) -> None:
    '''
    Updates the ...config.json file using config_dict

    Args:
        config_dir (str): File path to the ...config.json file
        config_dict (dict): Dictionary containing the config settings for the bot
    '''

    config_dict['last_modified_time'] = utc_str_now()
    with open(config_dir, mode = 'w') as fp:
        json.dump(config_dict, fp)   
        
def read_csv_set_idx(csv_file_path: str, idx_keys: Union[str, list] = None) -> pd.DataFrame:
    '''
    Reads in a csv as a Pandas Dataframe and sets the index to idx_keys

    Args:
        csv_file_path (str): Path to the csv file
        idx_keys (str, optional): Key column to set as index. Defaults to None. 
                                 If None, returns the dataframe with the 
                                 pandas default generated index.

    Returns:
        pd.DataFrame: Dataframe with it's index set to idx_keys
    '''
    if idx_keys is None:
        df = pd.read_csv(csv_file_path)
    else:
        df = pd.read_csv(csv_file_path).set_index(idx_keys)
    return df

def return_awaited_value(coroutine: asyncio.coroutine) -> Any:
  
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(coroutine)
    return result
    # Use the line below in debug console
    # result = return_awaited_value(x)
        
def sub_exists(sub) -> bool:
    bot_config = read_config_file(RedDiscConsts().config_path)
    bot_username = bot_config['metadata']['reddit_username']
    exists = True
    try:
        Reddit(bot_username).subreddits.search_by_name(sub, exact=True)
    except NotFound:
        exists = False
    return exists   
     
def user_exists(username) -> bool:
    bot_config = read_config_file(RedDiscConsts().config_path)
    bot_username = bot_config['metadata']['reddit_username']
    return not(Reddit(bot_username).username_available(username))

def sub_flairs(sub) -> list:
    bot_config = read_config_file(RedDiscConsts().config_path)
    bot_username = bot_config['metadata']['reddit_username']
    response = list(Reddit(bot_username).subreddit(sub).flair.link_templates)
    flairs = []
    for fl_dict in response:
        flairs.append(fl_dict['text'])

    return flairs   

def return_monitored_subreddits(comments) -> str:
    return comments.ag_frame.f_locals['function'].subreddit.display_name
    
def create_repair_files(bot_config: dict):
    filepaths = bot_config['dir_paths'].values()
    for fpath in filepaths:
        idx = fpath.rfind('/')
        dir_path = fpath[:idx]
        if not(os.path.exists(dir_path)):
            os.makedirs(dir_path)
            
        if not(os.path.exists(fpath)):            
            if fpath.endswith('.json'):
                new_json = {}
                new_json['last_modified_time'] = str(dt.utcnow()) + ' UTC'               
                with open(fpath, mode = 'w') as fp:
                    json.dump(new_json, fp)
            elif not(fpath.endswith('/')):
                with open(fpath, mode = 'w') as fp:
                    fp.write('')
            
            log_and_print(f'{fpath} created')
            
def red_monitoring_update(obj_type: str) -> dict:
    assert_msg = "`obj_type` must be one of ['subreddits', 'flairs', 'users']"
    assert obj_type in ['subreddits', 'flairs', 'users'], assert_msg
    
    # Load config file
    rdc = RedDiscConsts()
    config_path = rdc.config_path
    bot_config = read_config_file(config_path)
    guilds_conf = read_config_file(bot_config['dir_paths']['guilds_conf'])
    
    strs_to_monitor = {}
    for srv in guilds_conf:
        if srv == 'last_modified_time':
            continue 
        else:
            # for k in guilds_conf[srv]:
            if obj_type == 'users':
                users = set(guilds_conf[srv]['users_to_monitor'])
                for usr in users:
                    if usr not in strs_to_monitor:
                        strs_to_monitor[usr] = []
                    strs_to_monitor[usr].append(srv)
            else:
                subreddits = set(guilds_conf[srv]['subreddits_to_monitor'].keys())
                
                for sub in subreddits:
                    if obj_type == 'subreddits':
                        if sub not in strs_to_monitor:
                            strs_to_monitor[sub] = []
                        strs_to_monitor[sub].append(srv)
                    else:
                        flairs = set(guilds_conf[srv]['subreddits_to_monitor'][sub]['flairs_to_monitor'])
                        for fl in flairs:
                            if fl not in strs_to_monitor:
                                strs_to_monitor[fl] = []
                            strs_to_monitor[fl].append(srv)
                    
    return strs_to_monitor
                    
async def monitor_new_comments(reddit_instance: pr.Reddit, discord_instance: commands.Bot):
    # Load config file and necessary variables
    rdc = RedDiscConsts()
    config_path = rdc.config_path
    bot_config = read_config_file(config_path)
    pause_after = bot_config['static_settings']['pause_after']
    idle_time = bot_config['static_settings']['idle_time']
    guilds_conf = read_config_file(bot_config['dir_paths']['guilds_conf'])
    guilds_conf_lmt = guilds_conf['last_modified_time']
       
    # Extract the subreddits to monitor
    subreddits_to_monitor = red_monitoring_update('subreddits')
    print('Monitoring the following subreddits:')
    for sub in subreddits_to_monitor:
        print(f'- {sub}')
    subreddits_to_monitor = '+'.join(subreddits_to_monitor)
                
    # Monitor comments loop
    log_and_print('Monitoring Reddit comments')
    subreddit = await reddit_instance.subreddit(subreddits_to_monitor)
    comments = subreddit.stream.comments(skip_existing = True, pause_after=pause_after)
    async for comment in comments: 
        if comment is None:
            guilds_conf = read_config_file(bot_config['dir_paths']['guilds_conf'])
            if guilds_conf_lmt != guilds_conf['last_modified_time']:
                subreddits_to_monitor = red_monitoring_update('subreddits')
                log_and_print('Update - now monitoring the following subreddits:')
                for sub in subreddits_to_monitor:
                    log_and_print(f'- {sub}')
                subreddits_to_monitor = '+'.join(subreddits_to_monitor)
                comments = subreddit.stream.comments(skip_existing = True, pause_after=2)
                guilds_conf_lmt = guilds_conf['last_modified_time']
                
            log_and_print('No comment detected. Starting idle')
            await asyncio.sleep(idle_time)
            continue
        
        comment_url = comment.link_permalink + comment.id
        author_ori = comment.author.name
        author = author_ori.lower()
        body = comment.body
        log_and_print(f'New comment detected: {comment_url}')
        
        # Check if user is on monitor list
        monitored_users = red_monitoring_update('users')
        if author in monitored_users:
            srvs_to_send = monitored_users[author].copy()
            from_sub_ori = comment.subreddit.display_name
            from_sub = from_sub_ori.lower()
            for i in srvs_to_send:
                if from_sub not in guilds_conf[i]['subreddits_to_monitor']:
                    srvs_to_send.remove(i)
            
            # Send the comment to servers listed in srvs_to_send
            submission = comment.submission
            await submission.load()
            msg_body = f'**__r/{from_sub_ori}__**:\n'
            msg_body += f'New comment from __u/{author_ori}__ on a post titled **{submission.title}**:\n'
            body = body.replace('\n', '\n> ')
            msg_body += f'> {body}'
            msg_body += '\n'
            
            # Send parent comment too
            parent = await comment.parent()
            await parent.load()
            if type(parent) == pr.models.reddit.comment.Comment:
                msg_body += f'This was a reply to __u/{parent.author.name}__ who said:\n'
                replied_to_body = parent.body
                replied_to_body = replied_to_body.replace('\n', '\n> ')
                msg_body += f'> {replied_to_body}'
                msg_body += '\n'
            else:
                msg_body += f'This was a reply to the original post\n'
            
            msg_body += f'{comment_url}\n'
            dc_bot = discord_instance
            for srv in srvs_to_send:
                chan_id = int(guilds_conf[srv]['notification_channel'])
                channel = dc_bot.get_channel(int(chan_id))
                await channel.send(msg_body)
        
        # x = comment.parent()
        # import ipdb; ipdb.set_trace()
        # import pdb; pdb.set_trace()
        # return_awaited_value(x)
        print('')

def main():
    # red_monitoring_update('flairs')
    
    rdc = RedDiscConsts(True)
    
    # Initialize Discord Bot
    bot = rdc.init_discord_bot()
    disc_bot_token = rdc.disc_bot_token
    
    # Initialize Reddit Bot
    red_bot = rdc.init_reddit_bot()
        
    # Configure logging
    root_logger= log.getLogger()
    root_logger.setLevel(log.DEBUG) 
    today = str(date.today())
    deci_config = read_config_file(rdc.config_path)
    log_file_path = deci_config["dir_paths"]["log_file_dir"] + f"/rnd_log_{today}.log"
    handler = log.FileHandler(log_file_path, 
                            mode = 'a', 
                            encoding = 'utf-8',
                            ) 
    # handler.setStream(sys.stderr)
    handler.setFormatter(log.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
    root_logger.addHandler(handler)   
    root_logger.removeHandler(root_logger.handlers[0])   
        
    ## Load config.json
    with open('config.json') as f:
        bot_config = json.load(f)
        
    # Create/repair missing files
    create_repair_files(bot_config)
    
    # Discord commands
    @bot.event
    async def on_ready():
        '''
        This function executes when turned on if it was off before
        '''
        log_and_print(f'Logged in as {bot.user}', terminal_print=True)
        
    @bot.event
    async def on_guild_join(guild):
        '''
        This function executes when invited to a new server.
        
        Adds the server to guilds_conf.json
        '''
        
        # Read in the necessary variables from rnd_config
        rdc = RedDiscConsts()
        rnd_config = read_config_file(rdc.config_path)
        guilds_config_path = rnd_config['dir_paths']['guilds_conf']
        guilds_conf = read_config_file(guilds_config_path)
        
        guild_id = str(guild.id)
        guild_info = {
            'name': guild.name,
            'notification_channel': '',
            'subreddits_to_monitor': {}, # This will contain flairs_to_monitor
            'users_to_monitor': []
        }
        guilds_conf[guild_id] = guild_info
        update_config_file(guilds_config_path, guilds_conf)
        log_and_print(f'Added to `{guild.name}`')
        
    @bot.event
    async def on_guild_remove(guild):
        '''
        This function executes when removed from a server.
        
        Removes the server from guilds_conf.json
        '''
        
        # Read in the necessary variables from rnd_config
        rdc = RedDiscConsts()
        rnd_config = read_config_file(rdc.config_path)
        guilds_config_path = rnd_config['dir_paths']['guilds_conf']
        guilds_conf = read_config_file(guilds_config_path)
        
        guild_id = str(guild.id)
        popped_guild = guilds_conf.pop(guild_id)
        popped_guild_name = popped_guild['name']
        update_config_file(guilds_config_path, guilds_conf)  
        
        log_and_print(f'Removed from `{popped_guild_name}`')        
    
    @bot.command()
    async def echo(ctx, *text_to_echo: str):
        '''
        Replies with `text_to_echo`

        Args:
            ctx (Discord.Context): An object representing the message that called this command
            text_to_echo (str): The text you want the bot to echo
        '''
        text_to_echo = ' '.join(text_to_echo)
        log_and_print(f'echo(text_to_echo={text_to_echo}) was called')
        await ctx.reply(text_to_echo)
        log_and_print(f'Replied to {ctx.author.name} with: \n{text_to_echo}')
        
    @bot.command(brief = 'Sets the notification channel')
    async def set_channel(ctx, channel_link):
        '''
        Sets the channel as the one used for Reddit notifications. 
        
        Replies with a confirmation message
        
        WARNING: The bot will set the channel even if it has no permissions to
        read or message in that channel. I am too lazy to add anything to remedy this issue 
        so just be aware that it exists!

        Args:
            ctx (Discord.Context): An object representing the message that called this command
            channel_link (str): The channel you wish to set as the emailing channel. 
                                Must be a mention of the format `#<channel_name>`
        '''
        
        log_and_print(f'set_channel(channel_link={channel_link}) was called')
        try:
            channel_id = channel_link[2:-1]
            rdc = RedDiscConsts()
            bot_config = read_config_file(rdc.config_path)
            guilds_dir = bot_config['dir_paths']['guilds_conf']
            guilds_conf = read_config_file(guilds_dir)
            guild = str(ctx.guild.id)
            guilds_conf[guild]['notification_channel'] = channel_id
            update_config_file(guilds_dir, guilds_conf)
            reply_msg = f'{channel_link} has been successfully set as the notification channel!'
        except:
            if channel_link[:2] != '<#':
                reply_msg = f'Couldn\'t recognize channel. Try mentioning the channel by using `#<channel_name>`'
            else:
                reply_msg = f'Failed to set as the notification channel. Contact the bot developer for help.'      
        await ctx.reply(reply_msg)
        log_and_print(f'Replied to {ctx.author.name} with: \n{reply_msg}')
        
        
    @bot.command()
    async def add_subreddit(ctx, subreddit: str):
        # Read in the necessary variables from rnd_config
        rdc = RedDiscConsts()
        rnd_config = read_config_file(rdc.config_path)
        guilds_config_path = rnd_config['dir_paths']['guilds_conf']
        guilds_conf = read_config_file(guilds_config_path)
        
        if subreddit.startswith('r/'):
            subreddit = subreddit[2:]
        subreddit = subreddit.lower()
                
        if sub_exists(subreddit):
            srv_id = str(ctx.guild.id)
            guilds_conf[srv_id]['subreddits_to_monitor'][subreddit] = {'flairs_to_monitor': []}
            update_config_file(guilds_config_path, guilds_conf)   
            await ctx.reply(f'r/{subreddit} successfully added to monitoring list!')  
        else:
            await ctx.reply(f'r/{subreddit} not found')
    
    @bot.command()
    async def rm_subreddit(ctx, subreddit: str):
        # Read in the necessary variables from rnd_config
        rdc = RedDiscConsts()
        rnd_config = read_config_file(rdc.config_path)
        guilds_config_path = rnd_config['dir_paths']['guilds_conf']
        guilds_conf = read_config_file(guilds_config_path)
        
        if subreddit.startswith('r/'):
            subreddit = subreddit[2:].lower()
        subreddit = subreddit.lower()
        
        srv_id = str(ctx.guild.id)
        if subreddit in guilds_conf[srv_id]['subreddits_to_monitor']:
            guilds_conf[srv_id]['subreddits_to_monitor'].pop(subreddit)
            update_config_file(guilds_config_path, guilds_conf)
            await ctx.reply(f'r/{subreddit} successfully removed from monitoring list!')  
        else:
            await ctx.reply(f'r/{subreddit} not found in list of subreddits to monitor.')
            
        
    @bot.command()
    async def add_flair(ctx, subreddit: str = None):
        # Read in the necessary variables from rnd_config
        rdc = RedDiscConsts()
        rnd_config = read_config_file(rdc.config_path)
        guilds_config_path = rnd_config['dir_paths']['guilds_conf']
        guilds_conf = read_config_file(guilds_config_path)
        
        # Pick a subreddit to add flairs to
        srv_id = str(ctx.guild.id)
        subreddits = guilds_conf[srv_id]['subreddits_to_monitor'].keys()
        response = ''
        
        if subreddit is None:
            while True:
                reply_msg = 'Pick a subreddit to add flairs to:\n'
                for sub in subreddits:
                    reply_msg += f'- `{sub}`\n'
                try:
                    await ctx.reply(reply_msg)
                    response = await bot.wait_for('message', timeout = 60)
                    if response.content not in subreddits:
                        await ctx.send(rdc.SUBREDDIT_NOT_FOUND)
                    else:
                        subreddit = response.content
                        break
                except asyncio.TimeoutError:
                    await ctx.reply('Response timed out, please send another command')
        else:
            if subreddit not in subreddits:
                await ctx.reply(rdc.SUBREDDIT_NOT_FOUND)
                return
                        
        # Input a list of flairs to monitor
        flairs = sub_flairs(subreddit)
        reply_msg = 'List all the flairs you want to add, please seperate flairs with commas.\n'
        reply_msg += 'Available flairs (please copy and paste):\n'
        for fl in flairs:
            if fl not in guilds_conf[srv_id]['subreddits_to_monitor'][subreddit]['flairs_to_monitor']:
                reply_msg += f'- `{fl}`\n'
        try:
            await ctx.reply(reply_msg)
            response = await bot.wait_for('message', timeout = 60)
        except asyncio.TimeoutError:
            await ctx.reply(rdc.RESPONSE_TIMED_OUT)
                    
        # Process the flair input
        response_items = response.content.replace(' ', '')
        response_items = response_items.split(',')
        failed_items = []
        flairs_to_add = []
        for item in response_items:
            if item in flairs:
                flairs_to_add.append(item)
            else:
                failed_items.append(item)
                
        # Error message for invalid flairs
        if failed_items != []:
            reply_msg = 'The following flairs could not be added:\n'
            for i in failed_items:
                reply_msg += f'- `{i}`\n'
            await ctx.send(reply_msg)
                    
        # Edit guilds file and send confirmation reply
        guilds_conf[srv_id]['subreddits_to_monitor'][subreddit]['flairs_to_monitor'] += flairs_to_add
        update_config_file(guilds_config_path, guilds_conf)
        reply_msg = 'Successfully added the following flairs to the monitoring list:\n'
        for i in flairs_to_add:
            reply_msg += f'- `{i}`\n' 
        await ctx.reply(reply_msg)  
        
    @bot.command()
    async def rm_flair(ctx, subreddit: str = None):
        # Read in the necessary variables from rnd_config
        rdc = RedDiscConsts()
        rnd_config = read_config_file(rdc.config_path)
        guilds_config_path = rnd_config['dir_paths']['guilds_conf']
        guilds_conf = read_config_file(guilds_config_path)
        
        # Pick a subreddit to add flairs to
        srv_id = str(ctx.guild.id)
        subreddits = guilds_conf[srv_id]['subreddits_to_monitor'].keys()
        response = ''
        
        if subreddit is None:
            while True:
                reply_msg = 'Pick a subreddit to remove flairs from:\n'
                for sub in subreddits:
                    reply_msg += f'- `{sub}`\n'
                try:
                    await ctx.reply(reply_msg)
                    response = await bot.wait_for('message', timeout = 60)
                    if response.content not in subreddits:
                        await ctx.send(rdc.SUBREDDIT_NOT_FOUND)
                    else:
                        subreddit = response.content
                        break
                except asyncio.TimeoutError:
                    await ctx.reply(rdc.RESPONSE_TIMED_OUT)
        else:
            if subreddit not in subreddits:
                await ctx.reply(rdc.SUBREDDIT_NOT_FOUND)
                return
        
        # Input a list of flairs to remove
        flair_monitoring = guilds_conf[srv_id]['subreddits_to_monitor'][subreddit]['flairs_to_monitor']
        reply_msg = 'List all the flairs you want to remove, please seperate flairs with commas.\n'
        reply_msg += 'Available flairs (please copy and paste):\n'
        for fl in flair_monitoring:
            reply_msg += f'- `{fl}`\n'
        try:
            await ctx.reply(reply_msg)
            response = await bot.wait_for('message', timeout = 60)
        except asyncio.TimeoutError:
            await ctx.reply(rdc.RESPONSE_TIMED_OUT)
                    
        # Process the flair input
        response_items = response.content.replace(' ', '')
        response_items = response_items.split(',')
        failed_items = []
        flairs_to_rm = []
        for item in response_items:
            if item in flair_monitoring:
                flairs_to_rm.append(item)
            else:
                failed_items.append(item)
                
        # Error message for invalid flairs
        if failed_items != []:
            reply_msg = 'The following flairs could not be removed:\n'
            for i in failed_items:
                reply_msg += f'- `{i}`\n'
            await ctx.send(reply_msg)
            
        # Edit guilds file and send confirmation reply
        for flair in flairs_to_rm:
            guilds_conf[srv_id]['subreddits_to_monitor'][subreddit]['flairs_to_monitor'].remove(flair)
        update_config_file(guilds_config_path, guilds_conf)
        reply_msg = 'Successfully removed the following flairs from the monitoring list:\n'
        for i in flairs_to_rm:
            reply_msg += f'- `{i}`\n' 
        await ctx.reply(reply_msg)     
             
    @bot.command()
    async def add_reddit_user(ctx, user: str):
        # Read in the necessary variables from rnd_config
        rdc = RedDiscConsts()
        rnd_config = read_config_file(rdc.config_path)
        guilds_config_path = rnd_config['dir_paths']['guilds_conf']
        guilds_conf = read_config_file(guilds_config_path)
        
        if user.startswith('u/'):
            user = user[2:]
        user = user.lower()
            
        if user_exists(user):        
            srv_id = str(ctx.guild.id)
            guilds_conf[srv_id]['users_to_monitor'].append(user)
            update_config_file(guilds_config_path, guilds_conf)
            await ctx.reply(f'u/{user} successfully added to monitoring list!') 
        else: 
            await ctx.reply(f'u/{user} not found') 
        
    @bot.command()
    async def rm_reddit_user(ctx, user: str):
        # Read in the necessary variables from rnd_config
        rdc = RedDiscConsts()
        rnd_config = read_config_file(rdc.config_path)
        guilds_config_path = rnd_config['dir_paths']['guilds_conf']
        guilds_conf = read_config_file(guilds_config_path)
        
        if user.startswith('u/'):
            user = user[2:]
        user = user.lower()
        
        srv_id = str(ctx.guild.id)
        if user in guilds_conf[srv_id]['users_to_monitor']:
            guilds_conf[srv_id]['users_to_monitor'].remove(user)
            update_config_file(guilds_config_path, guilds_conf)
            await ctx.reply(f'u/{user} successfully removed from monitoring list!')  
        else:
            await ctx.reply(f'u/{user} not found in list of Reddit users to monitor.')

        
    # Run tasks asynchronously
    tasks = [
        asyncio.ensure_future(monitor_new_comments(red_bot, bot)), # Reddit bot
        asyncio.ensure_future(bot.start(disc_bot_token)), # Discord bot
    ]
    loop = asyncio.get_event_loop()
    # loop.set_debug(True)
    nest_asyncio.apply(loop)
    loop.run_until_complete(asyncio.wait(tasks))
    
if __name__ == '__main__':
    main()