from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

def MakeClient(client_secret,client_id):
    Text = '''{"installed":{"client_id":%s,"project_id":"quickstart-1564436220867","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":%s,"redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}'''%(client_id,client_secret)
    f = open("client_secrets.json","w+")
    f.write(Text)
    f.close()
    return f

def MakeCreds(access_token,client_secret,client_id,refresh_token,token_expiry):
    Text = """{"access_token": %s, "client_id": %s, "client_secret": %s, "refresh_token": %s, "token_expiry": %s, "token_uri": "https://oauth2.googleapis.com/token", "user_agent": null, "revoke_uri": "https://oauth2.googleapis.com/revoke", "id_token": null, "id_token_jwt": null, "token_response": {"access_token": %s, "expires_in": 3600, "refresh_token": %s, "scope": "https://www.googleapis.com/auth/drive", "token_type": "Bearer"}, "scopes": ["https://www.googleapis.com/auth/drive"], "token_info_uri": "https://oauth2.googleapis.com/tokeninfo", "invalid": false, "_class": "OAuth2Credentials", "_module": "oauth2client.client"}"""%(access_token,client_id,client_secret,refresh_token,token_expiry,access_token,refresh_token)
    f = open("mycreds.txt","w+")
    f.write(Text)
    f.close()
    return f

def UpdateEnvVars():
    f = open('mycreds.txt','r')
    c = f.read()
    s = c.split('"')
    os.environ["GD_ACCESS_TOKEN"] = s[3]
    os.environ["GD_CLIENT_SECRET"] = s[11]
    os.environ["GD_CLIENT_ID"] = s[7]
    os.environ["GD_REFRESH_TOKEN"] = s[15]
    os.environ["GD_TOKEN_EXPIRY"] = s[19]


def GetDrive():
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)
    return drive

def Startup(drive):
    search_list = []
    file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
    for file in file_list:
            if (file['title'] == 'Python Bot') and (file['explicitlyTrashed'] == False):
                    search_list.append(file)
    if len(search_list) == 0:
        # Create folder.
        folder_metadata = {
            'title' : 'Python Bot',
            # The mimetype defines this new file as a folder, so don't change this.
            'mimeType' : 'application/vnd.google-apps.folder'
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_id = folder['id'] 
    else:
        folder_id = search_list[0]['id']
    return folder_id

def UploadFile(drive,path,folder_id):
    f = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder_id}],'title': path})
    f.SetContentFile(path)
    f.Upload()
    return f



if __name__ == "__main__":
    0==0
##    path = 'dsmGaKWMeHXe9QuJtq_ys30PNfTGnMsRuHuo_MUzGCg.jpg'
##    drive = GetDrive()
##    folder_id = Startup(drive)
##    file = UploadFile(drive,path,folder_id)
