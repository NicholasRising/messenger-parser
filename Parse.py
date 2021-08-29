import datetime as dt
import json
import os
import pytz
import re
import sys

TIMEZONE='America/New_York'

messageBlocks=[]
messageIndex=1
while os.path.exists(f'message_{messageIndex}.json'):
    messageBlocks.append(json.load(open(f'message_{messageIndex}.json','r')))
    messageIndex+=1
mode=sys.argv[1].lower()
if mode=='pattern':
    pattern=re.compile(sys.argv[2])
    senders={}
    total=0
    for messageBlock in messageBlocks:
        for message in messageBlock['messages']:
            if (message['type']=='Generic' or message['type']=='Share') and 'content' in message:
                if message['sender_name'] not in senders:
                    senders[message['sender_name']]=0
                count=len(pattern.findall(message['content']))
                senders[message['sender_name']]+=count
                total+=count
    for sender in sorted(senders,key=lambda sender:senders[sender])[::-1]:
        print(f'{sender}: {senders[sender]}')
    print(f'\nTotal: {total}')
elif mode=='detail':
    pattern=re.compile(sys.argv[2])
    messages=[]
    for messageBlock in messageBlocks:
        for message in messageBlock['messages']:
            if (message['type']=='Generic' or message['type']=='Share') and 'content' in message and pattern.findall(message['content']):
                user=message['sender_name']
                time=dt.datetime.utcfromtimestamp(int(message['timestamp_ms'])/1000).astimezone(pytz.timezone(TIMEZONE))
                messages.append(time.strftime(f'On %m/%d/%y at %H:%M:%S,')+f' {user} said:\n\n{message["content"]}\n')
    width=int(os.get_terminal_size()[0])
    print('\n'+'-'*width)
    for message in messages[::-1]:
        print(message+'\n'+'-'*width)
elif mode=='user':
    user=sys.argv[2]
    messages=[]
    for messageBlock in messageBlocks:
        for message in messageBlock['messages']:
            if message['sender_name']==user:
                time=dt.datetime.utcfromtimestamp(int(message['timestamp_ms'])/1000).astimezone(pytz.timezone(TIMEZONE))
                string=time.strftime(f'On %m/%d/%y at %H:%M:%S,')
                string+=f' {user}'
                if (message['type']=='Generic' or message['type']=='Share') and 'content' in message:
                    string+=f' said:\n\n{message["content"]}'
                elif message['type']=='Subscribe':
                    string+=f' added'
                    count=len(message["users"])
                    if count==0: # How tee eff you add 0 people to a group
                        string+=f' someone (IDK who LMAO I hate Facebook)'
                    elif count==1:
                        string+=f' {message["users"][0]["name"]}'
                    elif count==2:
                        string+=f' {message["users"][0]["name"]} and {message["users"][1]["name"]}'
                    else:
                        for added in message["users"][:-1]:
                            string+=f' {added["name"]},'
                        string+=f'and {message["users"][0]["name"]}'
                    string+=' to the group'
                elif 'photos' in message:
                    string+=f' sent a photo'
                messages.append(string+'\n')
    width=int(os.get_terminal_size()[0])
    print('\n'+'-'*width)
    for message in messages[::-1]:
        print(message+'\n'+'-'*width)