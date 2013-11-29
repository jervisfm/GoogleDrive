#!/usr/bin/python

__author__ = 'Jervis Muindi'
__date__ = 'November 2013'

class GFile(object):
    """Encapsulates a GFile Object"""
    def __init__(self):
        pass

class GDriveAuth(object):
    """Encapsulates OAUTH2 authentication details for Google Drive API. """
    def __init__(self, client_id, client_secret, oauth_scope, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.oauth_scope = oauth_scope
        self.redirect_uri = redirect_uri


class GDrive(object):
    """Represents a Google Drive object. """
    def __init__(self):
        pass
    
    def upload(src_file, dest_path=None):
        """Uploads the 'src_file' to the destination file.

        Args:
        src_file: the source file to be uploaded.
        dest_path: the destination folder path."""
        pass

    def download(src_file, dest_file):
        """Downloads the specified file from Drive onto a local file. 
        Args:
          src_file: the source file to be downloaded
          dest_file: the destination file to save downloaded file to. 
        """
        pass

    def list(file_path): 
        """Lists files in the given path."""
        pass


################################################

# Sample Test Code borrowed from 
# https://developers.google.com/drive/quickstart-python#step_3_set_up_the_sample

import httplib2
import pprint

import time

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import Credentials

# Copy your credentials from the console
CLIENT_ID = None
CLIENT_SECRET = None

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# Path to the file to upload
FILENAME = 'document.txt'

DRIVE_CLIENT_SECRET_JSON='drive_client_secret.json'

# Run through the OAuth flow and retrieve credentials
#flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
#authorize_url = flow.step1_get_authorize_url()
#print 'Go to the following link in your browser: ' + authorize_url
#code = raw_input('Enter verification code: ').strip()
#credentials = flow.step2_exchange(code)

print 'creating credentail from stored json'
cred_json=open(DRIVE_CLIENT_SECRET_JSON).read()

credentials = Credentials.new_from_json(cred_json)

print type(credentials)
print dir(credentials)
print credentials.to_json()
print credentials.__repr__()
# exit(0)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

drive_service = build('drive', 'v2', http=http)

# Insert a file
mimetype = 'text/plain'
# media_body = MediaFileUpload(FILENAME, mimetype=mimetype, resumable=True)
media_body = MediaFileUpload(FILENAME, resumable=True)
body = {
  'title': 'My document - json creds',
  'description': 'A test document',
   #'mimeType': mimetype
}


start = time.time()

file_req = drive_service.files().insert(body=body, media_body=media_body)
print file_req
file = file_req.execute()
print "Upload took %s secs" % (time.time() - start)


#pprint.pprint(file)
