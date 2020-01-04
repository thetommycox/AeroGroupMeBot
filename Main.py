# IMPORTS
import os
import json
import requests
import wget
import urllib
import shutil
import datetime

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request

import GoogleDrive as GD
import Sanitization as san
import DateToolBox as dtb
import Memes


app = Flask(__name__)
Root = os.getenv('ROOT')
bot_id = os.getenv('GROUPME_BOT_ID')
group_id = os.getenv('GROUPME_GROUP_ID')
gm_access_token = os.getenv('GROUPME_ACCESS_TOKEN')
print(bot_id)
print('Update 2 code')
url = 'https://api.groupme.com/v3/bots/post'

mycreds = GD.MakeCreds(os.getenv('GD_ACCESS_TOKEN'),os.getenv('GD_CLIENT_SECRET'),os.getenv('GD_CLIENT_ID'),os.getenv('GD_REFRESH_TOKEN'),os.getenv('GD_TOKEN_EXPIRY'))
client_secrets = GD.MakeClient(os.getenv('GD_CLIENT_SECRET'),os.getenv('GD_CLIENT_ID'))
drive = GD.GetDrive()
GD.Setup(drive,Root)

# Called whenever the app's callback URL receives a POST request
# That'll happen every time a message is sent in the group
@app.route('/', methods=['POST'])
def webhook():
    # 'message' is an object that represents a single GroupMe message.
    message = request.get_json()
    print(message)
    print(dtb.IsInClass(drive,Root,message['created_at']))
    if (not sender_is_bot(message)) and (message['text']):
        message['text'] = message['text'].lower()
        CondenseResult,TypeResult,Nice,CommandType,attachment = san.Main(message['text'],message['attachments'])
        print(CommandType)
        if CommandType == 'ImageUpload':
            TempURL = attachment['url']
            FileName = str(message['created_at']) + '.' + TempURL.split('.')[-2]
            tempfile = wget.download(TempURL,FileName)
            if len(message['text'].upper().split()) > 1:
                FolderName = message['text'].upper().split()[1]
            else:
                FolderName = None
            GD.SortFile(drive,tempfile,message['created_at'],Root,FolderName)
            LikeMessage(message)
            

        elif (CommandType == 'FileUpload'):
            TempURL = "https://file.groupme.com/v1/%s/files/%s?token=%s"%(group_id,attachment['file_id'],gm_access_token)
            r = requests.get(TempURL)
            FileType = r.headers['content-type'].split('/')[1]
            print(r.headers['content-type'])
            if FileType == 'vnd.openxmlformats-officedocument.presentationml.presentation':
                FileType = 'pptx'
            elif FileType == 'vnd.ms-powerpoint':
                FileType = 'ppt'
            elif FileType == 'vnd.openxmlformats-officedocument.wordprocessingml.document':
                FileType = 'docx'
            elif FileType == 'msword':
                FileType = 'doc'
            elif FileType == 'vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                FileType = 'xlsx'
            elif FileType == 'vnd.ms-excel':
                FileType = 'xls'
            FileName = str(message['created_at']) + '.' + FileType
            TempFile = open(FileName, 'wb').write(r.content)

            if len(message['text'].upper().split()) > 1:
                FolderName = message['text'].upper().split()[1]
            else:
                FolderName = None
            GD.SortFile(drive,FileName,message['created_at'],Root,FolderName)
            LikeMessage(message)
            
        elif (CommandType == 'Update'):
            UpdateID = GD.FindOrCreateFolder(drive,[Root,'Bot Guts','Update.txt'])
            UpdateTextFile = drive.CreateFile({'id':UpdateID})
            UpdateText = UpdateTextFile.GetContentString()
            reply(UpdateText, bot_id)
            LikeMessage(message)

        elif (CommandType == 'Hartfield') and (dtb.IsInClass(drive,Root,message['created_at']) == 'AERO4510'):
            CounterID = GD.FindOrCreateFolder(drive,[Root,'Bot Guts','HartCounter.txt'])
            Counter = drive.CreateFile({'id':CounterID})
            
            date_time_obj = datetime.datetime.strptime(Counter['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')            
            print(date_time_obj)
            print(datetime.datetime.fromtimestamp(message['created_at']).date())
            if (date_time_obj.date() != datetime.datetime.fromtimestamp(message['created_at']).date()):
                Iteration = 0
            else:
                Iteration = int(Counter.GetContentString())
            Memes.GetHart(Iteration)
            HartPath = 'ModifiedHart.jpg'
            reply_with_image("Time for a 5 min lecture. Today's count: " + str(Iteration+1), HartPath)
            Counter.SetContentString(str(Iteration+1))
            Counter.Upload()

            TotalCounterID = GD.FindOrCreateFolder(drive,[Root,'Bot Guts','TotalHartCounter.txt'])
            TotalCounter = drive.CreateFile({'id':TotalCounterID})
            TotalIteration = int(TotalCounter.GetContentString())
            TotalCounter.SetContentString(str(TotalIteration+1))
            TotalCounter.Upload()

            LikeMessage(message)
        elif (CommandType == 'Hartfield') and (dtb.IsInClass(drive,Root,message['created_at']) == 'AERO4620'):
            CounterID = GD.FindOrCreateFolder(drive,[Root,'Bot Guts','MailenCounter.txt'])
            Counter = drive.CreateFile({'id':CounterID})
            
            date_time_obj = datetime.datetime.strptime(Counter['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')            
            print(date_time_obj)
            print(datetime.datetime.fromtimestamp(message['created_at']).date())
            if (date_time_obj.date() != datetime.datetime.fromtimestamp(message['created_at']).date()):
                Iteration = 0
            else:
                Iteration = int(Counter.GetContentString())
            Memes.GetMailen(Iteration)
            HartPath = 'ModifiedMailen.jpg'
            reply_with_image("I need more coffee. Today's count: " + str(Iteration+1), HartPath)
            Counter.SetContentString(str(Iteration+1))
            Counter.Upload()

            TotalCounterID = GD.FindOrCreateFolder(drive,[Root,'Bot Guts','TotalMailenCounter.txt'])
            TotalCounter = drive.CreateFile({'id':TotalCounterID})
            TotalIteration = int(TotalCounter.GetContentString())
            TotalCounter.SetContentString(str(TotalIteration+1))
            TotalCounter.Upload()

            LikeMessage(message)
        elif (CommandType == 'PostLink'):
            SharingLink = GD.FindOrCreateFolderLink(drive,[Root])['alternateLink']
            reply(SharingLink,bot_id)
            LikeMessage(message)
        if (Nice):
            reply('Nice.',bot_id)
    GD.UpdateEnvVars()
    return "ok", 200

################################################################################

# Send a message in the groupchat
def reply(msg,bot_id):
    url = 'https://api.groupme.com/v3/bots/post'
    data = {
                    'text'                  : msg,
                    'bot_id'                : bot_id

    } 
    #PostRequest = "https://api.groupme.com/v3/bots/post?bot_id=%s&text=%s&token=%s"%(bot_id,msg,gm_access_token)
    #requests.post(PostRequest)
    
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()
    print('Posted!')
    
def reply_with_image(msg, imgPath):
	url = 'https://api.groupme.com/v3/bots/post'
	urlOnGroupMeService = upload_image_to_groupme(imgPath)
	data = {
		'bot_id'		: bot_id,
		'text'			: msg,
		'picture_url'		: urlOnGroupMeService
	}
	request = Request(url, urlencode(data).encode())
	json = urlopen(request).read().decode()


def upload_image_to_groupme(imgPath):
    # Send Image
    headers = {'content-type': 'application/json'}
    url = 'https://image.groupme.com/pictures'
    files = {'file': open(imgPath, 'rb')}
    payload = {'access_token': gm_access_token}
    r = requests.post(url, files=files, params=payload)
    imageurl = r.json()['payload']['url']
    os.remove(imgPath)
    return imageurl


def LikeMessage(message):
    requests.post("https://api.groupme.com/v3/messages/%s/%s/like?token=%s"%(group_id,message['id'],gm_access_token))

# Checks whether the message sender is a bot
def sender_is_bot(message):
    return message['sender_type'] == "bot"


