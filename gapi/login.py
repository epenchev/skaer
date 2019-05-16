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
import requests
from base64 import b64decode
from cherrypy.process.plugins import BackgroundTask


key_sets = {
    'id': b'ODE5MjIzNTA2MjM0LWtoZjlxaDRsODl2YW4wZjZuOXBxa3Nwb2F0bms2NnNiLmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29t',
    'secret': b'X1Y4eG45RUxiYzh6cnJJTV94cW80Tm5R'
}


class ApiError(Exception):
    """ An exception for the rest api errors. """

    def __init__(self, status_code, message):
        Exception.__init__(self, )
        self._status_code = status_code
        self._message = message

    @property
    def status_code(self):
        return self._status_code

    @property
    def message(self):
        return self._message



class LoginError(Exception):
    """ An exception for the login errors. """

    def __init__(self, message):
        Exception.__init__(self, message)
        self._message = message

    @property
    def message(self):
        return self._message



def api_post_request(url, post_data, headers):
    req_headers = {
        'Host': 'www.googleapis.com',
        'User-Agent': 'Mozilla/5.0 Firefox/66.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    # apply custom headers setup
    if headers:
        req_headers.update(headers)

    result = requests.post(url, data=post_data, headers=req_headers)
    try:
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
        os.environ['refresh_token'] = json_data['refresh_token']
        os.environ['expires_in'] =  str(int(time.time()) + int(json_data['expires_in']))

    def get_access_token(code, client, secret):
        try:
            if not os.environ.get('access_token', ''):
                json_data = request_access_token(code, client, secret)
                export_token(json_data)
                return
        except LoginError as err:
            print('Got error from request_access_token: %s' % str(err))
            return
        except KeyError as err:
            if json_data.get('error', '') == 'authorization_pending':
                print('Waiting user to authorize app')
            else:
                print('Unexpected error')
            return
        # Refresh access token if is about to expire
        if (int(os.environ['expires_in']) - int(time.time())) <= 100:
            json_data = refresh_access_token(os.environ['refresh_token'], client, secret)
            export_token(json_data)

    interval_sec = 5 
    client_id = str(b64decode(key_sets['id']), 'utf-8')
    client_secret = str(b64decode(key_sets['secret']), 'utf-8')
    try:
        json_data = request_device_and_user_code(client_id)
        device_code = json_data['device_code']
        print('Login to %s with %s' % (json_data['verification_url'], json_data['user_code']))
        # Run the service in a background task
        task = BackgroundTask(interval_sec, get_access_token, [device_code, client_id, client_secret])
        task.start()
    except LoginError as err:
        print('Google failed: %s', err.message)
    except KeyError as err:
        print('Missing json values from API response %s' % str(err))



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


