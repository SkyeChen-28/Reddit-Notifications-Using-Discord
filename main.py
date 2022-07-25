from typing import Any
import asyncpraw as pr
import sys
import json
import asyncio
# import pdb
import nest_asyncio
# import pandas as pd
# from datetime import datetime as dt
# from datetime import timedelta
# from dateutil.parser import parse
# from dateutil.tz import gettz
# import logging as log
# import os

# Debugging async stuff
'''
loop = asyncio.get_event_loop()
y = loop.run_until_complete(x)
'''

class RedDiscConsts():
    def __init__(self) -> None:
        pass
    
# Create missing directories 
# if not(os.path.exists('DynamicMemoryFiles')):
#         os.mkdir('DynamicMemoryFiles')

def return_awaited_value(coroutine: asyncio.coroutine) -> Any:
  
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(coroutine)
    return result
    # Use the line below in debug console
    # result = return_awaited_value(x)
    
async def activate_bot(bot_config: dict) -> None:
    
    # Load necessary bot config data
    bot_username = bot_config['metadata']['reddit_username']
    bot_admin = bot_config['metadata']['bot_admin']
    
    # Informative start up messages
    print('Setting up control for u/' + bot_username)
    print('Welcome u/' + bot_admin)
    
    # Load credentials from praw.ini to generate a Reddit instance
    try:
        reddit = pr.Reddit(bot_username)
    except:
        print("WARNING! praw.ini file not set up properly!")
        sys.exit("WARNING! praw.ini file not set up properly!")
        
    await monitor_new_comments(reddit)
    
async def monitor_new_comments(reddit_instance: pr.Reddit):
    subreddit = await reddit_instance.subreddit('TheDragonPrince')
    comments = subreddit.stream.comments(skip_existing = True, pause_after=16)
    async for comment in comments: 
        if comment is None:
            print('No comment detected. Starting idle')
            continue
        comment_url = comment.link_permalink + comment.id
        author = comment.author.name
        print(comment_url)
        x = comment.parent()
        # import ipdb; ipdb.set_trace()
        # import pdb; pdb.set_trace()
        # return_awaited_value(x)
        print('')

def main():
    ## Load config.json
    with open('config.json') as f:
        bot_config = json.load(f)
    
    # Run tasks asynchronously
    tasks = [
        asyncio.ensure_future(activate_bot(bot_config)), # 
    ]
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    nest_asyncio.apply(loop)
    loop.run_until_complete(asyncio.wait(tasks))
    
if __name__ == '__main__':
    main()