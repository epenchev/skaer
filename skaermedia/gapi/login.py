#!/usr/bin/env python3
#
# Skaer media server
# Copyright (c) 2019 Emil Penchev
#
# Project page:
#   http://skaermedia.org
#
# licensed under GNU GPL version 3 (or later)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

import os
import time
import sqlite3
import requests
from base64 import b64decode

from skaermedia.server import path_utils

import cherrypy
from cherrypy.process.plugins import BackgroundTask


class OauthClientError(Exception):
    pass


class OauthParams(object):

    def __init__(self):
        with sqlite3.connect(path_utils.get_databasepath()) as conn:
            r = conn.cursor().execute('SELECT '
                                      'base64_oauth_id, '
                                      'base64_oauth_secret FROM glogin').fetchone()
        b64id, b64secret = tuple(r)
        self._oauth_id = str(b64decode(b64id), 'utf-8')
        self._oauth_secret = str(b64decode(b64secret), 'utf-8')
        self._login = {}

    @property
    def id(self):
        """
        Get global Oauth id
        """
        return self._oauth_id

    @property
    def secret(self):
        """
        Get global Oauth secret
        """
        return self._oauth_secret

    def get_login(self):
        """ Get current verification url, user and device code from DB
            so user can register device with Google Oauth.

        """
        if 'verification_url' not in self._login:
            with sqlite3.connect(path_utils.get_databasepath()) as conn:
                r = conn.cursor().execute('SELECT verification_url, device_code, user_code from glogin').fetchone()
                url, device_code, user_code = tuple(r)
                self._login = {
                    'verification_url': url,
                    'device_code': device_code,
                    'user_code': user_code
                }
        return self._login

    def update_login(self, device_code, user_code, verf_url):
        """
        Update current Oauth verification url, user and device codes in the DB.
        """
        with sqlite3.connect(path_utils.get_databasepath()) as conn:
            conn.execute('UPDATE glogin SET device_code=?, user_code=?, verification_url=?',
                        (device_code, user_code, verf_url))
            self._login = {
                'verification_url': verf_url,
                'device_code': device_code,
                'user_code': user_code
            }


class OauthClient(object):

    def __init__(self):
        self._oauth_params = OauthParams()

    @staticmethod
    def post_request(url, data, headers):
        req_headers = {
            'Host': 'www.googleapis.com',
            'User-Agent': 'Mozilla/5.0 Firefox/66.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        if headers:
            req_headers.update(headers)
        try:
            result = requests.post(url, data=data, headers=req_headers)
            if result.status_code != requests.codes.ok:
                result.raise_for_status()
            # We always expect content-type to be application/json
            if result.headers.get('content-type', '').startswith('application/json'):
                json_data = result.json()
            else:
                raise OauthClientError('Unexpected content-type in response')
            return json_data
        except ValueError:
            raise OauthClientError('Missing json data in response')


    def request_device_and_user_code(self):
        """
        A step to obtain OAuth 2.0 access token.
        Send request to Google's authorization server
        that identifies the scopes that your application will request
        permission to access.
        Guide - https://developers.google.com/youtube/v3/guides/auth/devices

        """
        data = {
            'client_id': self._oauth_params.id,
            'scope': 'https://www.googleapis.com/auth/youtube'
        }

        url = 'https://accounts.google.com/o/oauth2/device/code'
        json_data = OauthClient.post_request(url, data, {'Host': 'accounts.google.com'})
        if 'error' in json_data:
            raise OauthClientError(str(json_data))
        OauthParams.update_login(json_data['device_code'], json_data['user_code'], json_data['verification_url'])

    def request_access_token(self, device_code):
        """
        Poll Google's authorization server.
        Sending Poll requests to Google's authorization server
        to determine when the user has responded to the authorization request.
        Guide - https://developers.google.com/youtube/v3/guides/auth/devices

        """
        data = {
            'client_id': self._oauth_params.id,
            'client_secret': self._oauth_params.secret,
            'code': device_code,
            'grant_type': 'http://oauth.net/grant_type/device/1.0'
        }

        url = 'https://www.googleapis.com/oauth2/v4/token'
        json_data = OauthClient.post_request(url, data, {'Host': 'www.googleapis.com'})
        if 'error' in json_data:
            if json_data['error'] != 'authorization_pending':
                raise OauthClientError(str(json_data))
        return json_data

    def refresh_access_token(self, refresh_token):
        """
        Refresh an access token if it has expired.
        One must use the refresh token
        which has been obtained with request_access_token function.
        Guide - https://developers.google.com/youtube/v3/guides/auth/devices

        """
        data = {
            'client_id': self._oauth_params.id,
            'client_secret': self._oauth_params.secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        url = 'https://www.googleapis.com/oauth2/v4/token'
        json_data = OauthClient.post_request(url, data, {'Host': 'www.googleapis.com'})
        if 'error' in json_data:
            raise OauthClientError(str(json_data))
        return json_data

    def revoke_token(self, refresh_token):
        """
        Revoke an access token, it can be either access or referesh token.
        Guide - https://developers.google.com/youtube/v3/guides/auth/devices

        """
        data = { 'token': refresh_token }
        url = 'https://accounts.google.com/o/oauth2/revoke'
        json_data = OauthClient.post_request(url, post_data, {'Host': 'accounts.google.com'})
        if 'error' in json_data:
            raise OauthClientError(str(json_data))


class OauthLoginService(object):

    def __init__(self, interval_sec):
        self._client = OauthClient()
        self._interval_sec = interval_sec

    @staticmethod
    def export_token(token_data):
        os.environ['access_token'] = token_data['access_token']
        if 'refresh_token' in token_data:
            os.environ['refresh_token'] = token_data['refresh_token']
        os.environ['expires_in'] =  str(int(time.time()) + int(token_data['expires_in']))

    def get_access_token(self):
        try:
            if not os.environ.get('access_token', ''):
                token_data = self._client.request_access_token()
                OauthLoginService.export_token(token_data)
            else:
                # Check if token has expired
                pass
        except OauthClientError as err:
            cherrypy.log(str(err), traceback=True)

    def run(self):
        self._client.request_device_and_user_code()
        # Run the service in a background task
        task = BackgroundTask(self._interval_sec, self.get_access_token)
        task.start()



def run_service():
    """ Run Google OAuth login procedure and update expired tokens. """

    def export_token(json_data):
        os.environ['access_token'] = json_data['access_token']
        if 'refresh_token' in json_data:
            os.environ['refresh_token'] = json_data['refresh_token']
        os.environ['expires_in'] =  str(int(time.time()) + int(json_data['expires_in']))

    def get_access_token(code, client, secret):
        try:
            if not os.environ.get('access_token', ''):
                json_data = request_access_token(code, client, secret)
                export_token(json_data)
                return
        except LoginError as err:
            cherrypy.log('Got error from request_access_token: %s' % str(err), traceback=True)
            return
        except KeyError as err:
            if json_data.get('error', '') != 'authorization_pending':
                cherrypy.log('Got Unexpected error', traceback=True)
            return
            # Refresh access token if is about to expire
            json_data = refresh_access_token(os.environ['refresh_token'], client, secret)
            export_token(json_data)

    interval_sec = 5
    client_id, client_secret = get_oauth_id_secret()
    try:
        json_data = request_device_and_user_code(client_id)
        device_code = json_data['device_code']
        user_code = json_data['user_code']
        verification_url = json_data['verification_url']
        with sqlite3.connect(path_utils.get_databasepath()) as conn:
            conn.execute('UPDATE glogin SET device_code=?, user_code=?, verification_url=?',
                         (device_code, user_code, verification_url))
        # Run the service in a background task
        task = BackgroundTask(interval_sec, get_access_token, [device_code, client_id, client_secret])
        task.start()
    except LoginError as err:
        cherrypy.log('Google failed: %s', err.message, traceback=True)
    except KeyError as err:
        cherrypy.log('Missing json values from API response %s' % str(err), traceback=True)




def api_post_request(url, post_data, headers):
    req_headers = {
        'Host': 'www.googleapis.com',
        'User-Agent': 'Mozilla/5.0 Firefox/66.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    if headers:
        req_headers.update(headers)

    try:
        result = requests.post(url, data=post_data, headers=req_headers)
        # We always expect content-type from google to be application/json
        if result.headers.get('content-type', '').startswith('application/json'):
            json_data = result.json()
        else:
            raise ApiError(result.status_code, 'Unexpected content-type in response')
        return json_data
    except ValueError:
        raise ApiError(result.status_code, 'Missing json data in response')

    if result.status_code != requests.codes.ok:
        raise ApiError(result.status_code, json_data)
       


def request_device_and_user_code(client_id):
    """
    A step to obtain OAuth 2.0 access token.
    Send request to Google's authorization server 
    that identifies the scopes that your application will request
    permission to access.
    Guide - https://developers.google.com/youtube/v3/guides/auth/devices

    """
    if not client_id:
        raise LoginError('Error no value for client_id')

    post_data = {
        'client_id': client_id,
        'scope': 'https://www.googleapis.com/auth/youtube'
    }

    url = 'https://accounts.google.com/o/oauth2/device/code'
    try:
        json_data = api_post_request(url, post_data, {'Host': 'accounts.google.com'})
        if 'error' in json_data:
            raise LoginError(json_data)
        return json_data
    except ApiError as err:
        raise LoginError('Login failed, HTTP status code:%s , data:%s' %
                        (err.status_code, err.message))



def request_access_token(code, client_id, client_secret):
    """
    Poll Google's authorization server.
    Sending Poll requests to Google's authorization server
    to determine when the user has responded to the authorization request.
    Guide - https://developers.google.com/youtube/v3/guides/auth/devices

    """
    if not code or not client_id or not client_secret:
        raise LoginError('Missing value for one of code, client_id or client_secret')

    post_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'http://oauth.net/grant_type/device/1.0'
    }

    url = 'https://www.googleapis.com/oauth2/v4/token'
    try:
        json_data = api_post_request(url, post_data, {'Host': 'www.googleapis.com'})
        if 'error' in json_data:
            if json_data['error'] != 'authorization_pending':
                raise LoginError(json_data)
        return json_data
    except ApiError as err:
        raise LoginError('Login failed, HTTP status code:%s , data:%s' %
                        (err.status_code, err.message))



def refresh_access_token(refresh_token, client_id, client_secret):
    """
    Refresh an access token if it has expired.
    One must use the refresh token
    which has been obtained with request_access_token function.
    Guide - https://developers.google.com/youtube/v3/guides/auth/devices

    """
    if not refresh_token or not client_id or not client_secret:
        raise LoginError('Missing value for one of refresh_token, client_id or client_secret')

    post_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }

    url = 'https://www.googleapis.com/oauth2/v4/token'
    try:
        json_data = api_post_request(url, post_data, {'Host': 'www.googleapis.com'})
        if 'error' in json_data:
            raise LoginError(json_data)
        return json_data
    except ApiError as err:
        raise LoginError('Login failed, HTTP status code:%s , data:%s' %
                        (err.status_code, err.message))



def revoke_token(refresh_token):
    """
    Revoke an access token, it can be either access or referesh token.
    Guide - https://developers.google.com/youtube/v3/guides/auth/devices

    """
    post_data = {'token': refresh_token}
    url = 'https://accounts.google.com/o/oauth2/revoke'
    try:
        json_data = api_post_request(url, post_data, {'Host': 'accounts.google.com'})
        if 'error' in json_data:
            raise LoginError(json_data)
    except ApiError as err:
        raise LoginError('Login failed, HTTP status code:%s , data:%s' %
                        (err.status_code, err.message))



def run_service():
    """ Run Google OAuth login procedure and update expired tokens. """

    def export_token(json_data):
        os.environ['access_token'] = json_data['access_token']
        if 'refresh_token' in json_data:
            os.environ['refresh_token'] = json_data['refresh_token']
        os.environ['expires_in'] =  str(int(time.time()) + int(json_data['expires_in']))

    def get_access_token(code, client, secret):
        try:
            if not os.environ.get('access_token', ''):
                json_data = request_access_token(code, client, secret)
                export_token(json_data)
                return
        except LoginError as err:
            cherrypy.log('Got error from request_access_token: %s' % str(err), traceback=True)
            return
        except KeyError as err:
            if json_data.get('error', '') != 'authorization_pending':
                cherrypy.log('Got Unexpected error', traceback=True)
            return
        # Refresh access token if is about to expire
            json_data = refresh_access_token(os.environ['refresh_token'], client, secret)
            export_token(json_data)

    interval_sec = 5
    client_id, client_secret = get_oauth_id_secret()
    try:
        json_data = request_device_and_user_code(client_id)
        device_code = json_data['device_code']
        user_code = json_data['user_code']
        verification_url = json_data['verification_url']
        with sqlite3.connect(path_utils.get_databasepath()) as conn:
            conn.execute('UPDATE glogin SET device_code=?, user_code=?, verification_url=?',
                         (device_code, user_code, verification_url))
        # Run the service in a background task
        task = BackgroundTask(interval_sec, get_access_token, [device_code, client_id, client_secret])
        task.start()
    except LoginError as err:
        cherrypy.log('Google failed: %s', err.message, traceback=True)
    except KeyError as err:
        cherrypy.log('Missing json values from API response %s' % str(err), traceback=True)



# Some testing examples

if __name__ == '__main__':
    client_id = ''
    client_secret = ''
    #json_data = request_device_and_user_code(client_id)
    device_code = ''
    #json_data = request_access_token(device_code, client_id, client_secret)
    json_data = refresh_access_token('', client_id, client_secret)
    #revoke_token('')
    print(json_data)


