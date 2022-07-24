import json
import os
import Create_Refresh_Token as crt
import time

def main():
    config_path = 'config.json'
    in_path = 'setup/sample_praw.ini'
    out_path = 'praw.ini'
    
    # Read in the config file
    with open(config_path) as f:
        bot_config = json.load(f)
    version = bot_config['metadata']['version']
    
    with open(in_path, mode = 'r') as fp, open(out_path, mode = 'w') as rf:
        # Read in the sample praw ini file
        data = fp.read()
        
        # Append the bot's authentication info, 
        # Prompt user if it's not found in environment variables
        
        reddit_username = os.getenv('REDDISC_RED_USER')
        if reddit_username is None:
            print('No value detected in the environment variable REDDISC_RED_USER')
            reddit_username = input('Enter the Reddit username of the bot without the u/:\n')
        data += f'\n[{reddit_username}]\n'  
              
        client_id = os.getenv('REDDISC_RED_APP_ID')
        if client_id is None:
            print('No value detected in the environment variable REDDISC_RED_APP_ID')
            client_id = input('Enter the web app ID of the Reddit bot:\n')
        data += f'client_id={client_id}\n'
        
        client_secret = os.getenv('REDDISC_RED_SECRET')
        if client_secret is None:
            print('No value detected in the environment variable REDDISC_RED_SECRET')
            client_secret = input('Enter the API Secret of the Reddit bot:\n')
        data += f'client_secret={client_secret}\n'
        
        user_agent = f'reddit:{client_id}:{version} (by /u/{reddit_username})'
        data += f'user_agent={user_agent}\n'
        
        # Write out data required for Create_Refresh_Token first
        rf.write(data)
        
    if not(os.path.exists('Authentication')):
        os.mkdir('Authentication')
    crt.main(USERNAME = reddit_username)
    with open("Authentication/Refresh Token.txt", "r") as f:
        refresh_token = f.read()
    data += f'refresh_token={refresh_token}\n'

    with open(out_path, mode = 'w') as outp:
        # Write the new data to praw.ini
        outp.write(data)
        
if __name__ == '__main__':
    main()