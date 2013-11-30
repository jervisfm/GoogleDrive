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
            self.oauth_scope = self.DEFAULT_OAUTH_SCOPE

        if not redirect_uri:
            self.redirect_uri = self.DEFAULT_REDIRECT_URI

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
        print 'Go to the following link in your browser and authorize the App:\n %s \n' % authorize_url
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
            cred_file = self.DEFAULT_CRED_FILEPATH

        contents = credentials.to_json()
        with  open(cred_file, "w") as f:
            f.write(contents)
        
        return True

    @staticmethod
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
    """Represents a Google Drive object that can be used
    to upload/download files """
    def __init__(self, credentials):
        """ Initializes a Google Drive object with given crednetials.
        
        Args:
           credentials: Google credentials object. Identifies the drive
           to which files are to upload to / downloaded from. 
        """

        if not credentials:
            raise ValueError ("Must Specify credentials to Google drive")

        self.creds = credentials
        
        # Create the Drive Service API object
        http = httplib2.Http()
        http = credentials.authorize(http)
        self.drive = build('drive', 'v2', http=http)
    
    def upload(self, src_file, dest_path=None, num_retries=3, title=None, description=None,
               progress_cb=None):
        """Uploads the 'src_file' to the destination file.
        
        Note that in Google Drive, filenames are not unique identifier; i.e.
        if two files with the same names can co-exist and this is the default
        state of things when a new file is uploaded that matches an existing
        file. So, there is no risk of overwriting accidental overwrite.
        
        Args:
           src_file: (string) the source file to be uploaded.
           dest_path: (string) the destination folder path. If not specified, then upload
           will be to the root drive.
           num_retries: (int) Number of times to try and upload the file.
           title: (string). Optional. Specifies the name of the file in Google Drive. If not
           set, filename name used will be same as that of 'src_file'
           description: (string) Optional. Sets a description of the file. 
           progress_cb: (function) Python function that takes 1 argument, a python dictionary.
           This is a callback that will be called to report progress of the upload back to the
           caller. The supplied dictionary will have the following keys:
           * 'bytes_sent': # of bytes server has received so far
           * 'percent_done': # What percent of the upload has been completed
           * 'duration' : # of seconds that had elapsed to get to this stage.
           """

        if not src_file:
            raise ValueError("src_file was not specified")
        
        creds = self.creds
        drive = self.drive

        if not title:
            title=src_file

        if description is None:
            description = ''

        # Code below uses Google Python API Client library. 
        # Specific file of interest: http.py (https://code.google.com/p/google-api-python-client/source/browse/apiclient/http.py)

        # For now, don't explicitly set MIME/type. 
        # Google seems to auto-detect it anyway. 
        mimetype = ''

        # Do the upload in pieces to improve robustness against upload errors. 
        # API docs say chunk size should be multiple of 256KB. (https://developers.google.com/drive/manage-uploads#resume-upload)
        # We do it in 1MB pieces here. 
        chunksize = 4 * (256 * 1024)
        

        media_body = MediaFileUpload(src_file, resumable=True, chunksize=chunksize)
        body = dict(title=src_file,
                    description=description)
        
        request = drive.files().insert(body=body, media_body=media_body)
        
        
        response = None
        bytes_sent = 0
        start_time = time.time()
        while response is None:
            # next_chunk() returns None response whilst there is still data to process. 
            status, response = request.next_chunk(num_retries=num_retries)
            if status and progress_cb is not None:
                bytes_sent += chunksize
                duration = time.time() - start_time
                percent_done = status.progress() * 100
                progress_dict = dict(bytes_sent=bytes_sent,
                                     duration=duration,
                                     percent_done=percent_done)
                progress_cb(progress_dict)
        return response

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


def test_gauth():
    # Test the Auth Flow
    client_id = raw_input('client id: ').strip()
    client_secret = raw_input('client secret: ').strip()
    
    print 'Testing Auth Flow'
    gauth = GDriveAuth(client_id, client_secret)
    creds = gauth.get_credentials()
    print creds
    
    dest_file= 'test_creds_file.json'
    if gauth.save_credentials(creds, dest_file):
        print "creds saved successfully"
    else:
        print "creds NOT saved"

def test_gupload():
    cred_file = 'drive_client_secret.json'
    creds = GDriveAuth.read_credentials_from_file(cred_file)
    gdrive = GDrive(creds)
    src_file = 'document.txt'
    
    def print_status_cb(s):
        print "%s \n************\n" % s
        

    gdrive.upload(src_file, progress_cb = print_status_cb)

def test_code():
    # Test some of the code
    # test_gauth()
    test_gupload()

if __name__ == '__main__':
    test_code()
    exit(0)


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
