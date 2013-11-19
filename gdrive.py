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
      dest_path: the destination folder path
    """
        pass

    def download(src_file, dest_file):
    """Downloads the specified file from Drive onto a local file. 
    Args:
      src_file: the source file to be uploaded
      dest_file: the destination file to save downloaded file to. 
    """
        pass

    def list(file_path): 
    """Lists files in the given path."""
        pass

