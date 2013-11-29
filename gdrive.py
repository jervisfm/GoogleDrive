#!/usr/bin/python

__author__ = 'Jervis Muindi'
__date__ = 'November 2013'

import httplib2
import time

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import Credentials

class GFile(object):
    """Encapsulates a GFile Object"""
    def __init__(self):
        pass

class GDriveAuth(object):
    """Encapsulates OAUTH2 authentication details for Google Drive API. 
    
    Also provides methods for obtaining user credentials that can be saved and 
    re-used to perfrom requests on behalf of the user.
    
    """
    
    # Request Full Drive Permission Access scope. 
    # See https://developers.google.com/drive/scopes for more details
    DEFAULT_OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
    
    # Redirect URI for installed apps
    DEFAULT_REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
    
    # Default Save location for user auth token credentials
    DEFAULT_CRED_FILEPATH = "~/.drive_auth"

    def __init__(self, client_id, client_secret, oauth_scope=None, redirect_uri=None):
        self.client_id = client_id
        self.client_secret = client_secret

        # Use Default Values if no user-supplied values exist

        if not oauth_scope:
            self.oauth_scope = DEFAULT_OAUTH_SCOPE

        if not reduce_uri:
            self.redirect_uri = DEFAULT_REDIRECT_URI

    def get_credentials(self):
        """Walks a user through a step-by-step guide in creating 
        credential auth tokens.

        The process is as follows:
        *  App Asks user to go to a URL that has requested permissions
        * User reviews permission request and approves it, receving an auth token
        * App asks for Auth token user obtained, and creates a credentials object
        """
        # Run through the OAuth flow and retrieve user credentials
        flow = OAuth2WebServerFlow(self.client_id, 
                                   self.client_secret, 
                                   self.oauth_scope, 
                                   self.redirect_uri)

        authorize_url = flow.step1_get_authorize_url()
        print 'Go to the following link in your browser and authorize the App: %s \n' % authorize_url
        code = raw_input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)
        return credentials

    @staticmethod
    def save_credentials(credentials, cred_file):
        """Write the given credentials to file. 
        Args:
           credentials: Google Credential object to be saved.
           cred_file: (string) the filepath to put the credentials in

        Returns: true iff save was successful. 
        """
        if not credentials:
            raise ValueError("credentials not specified")

        if not cred_file:
            # Use a default credentials file.
            cred_file = DEFAULT_CRED_FILEPATH

        contents = credentials.to_json()
        with  open(cred_file, "w") as f:
            f.write(contents)
        
        return True

    def read_credentials_from_file(file_path):
        """ Reads serialized credentials from given file and reconstructs
        the matching Google Credential object.
        
        Args:
           file_path: (string) path to json file containing serialized
           Credential object.

        Returns:
          A Google Credentials object iff successful.
        """

        if not file_path:
            raise ValueError("file path was not specified")

        with open(file_path, "r") as f:
            # Read entire file to memory
            contents = f.read()
            return Credentials.new_from_json(contents)


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
