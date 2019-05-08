import requests


def request_device_and_user_code(client_id=''):
    """
    A step to obtain OAuth 2.0 access token.
    Send request to Google's authorization server 
    that identifies the scopes that your application will request
    permission to access.
    """
    # Guide - https://developers.google.com/youtube/v3/guides/auth/devices
    headers = {
        'Host': 'accounts.google.com',
        'User-Agent': 'Mozilla/5.0 Firefox/66.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    post_data = {
        'client_id': client_id,
        'scope': 'email profile'
    }

    # TODO raise an error if client_id is empty

    url = 'https://accounts.google.com/o/oauth2/device/code'
    result = requests.post(url, data=post_data, headers=headers)
    try:
        json_data = result.json()
        if 'error' in json_data:
            json_data.update({'code': str(result.status_code)})
            raise RuntimeError(json_data)
    except ValueError:
        json_data = None

    if result.status_code != requests.codes.ok:
        raise RuntimeError('Login Failed')

    if result.headers.get('content-type', '').startswith('application/json'):
        if json_data:
            return json_data
        else:
            return result.json()
    else:
        raise RuntimeError('Login Failed: Unexpected content-type in response')


def request_access_token(code, client_id, client_secret):
    """
    Poll Google's authorization server.
    Sending Poll requests to Google's authorization server
    to determine when the user has responded to the authorization request.
    """
    # https://developers.google.com/youtube/v3/guides/auth/devices
    headers = {
        'Host': 'www.googleapis.com',
        'User-Agent': 'Mozilla/5.0 Firefox/66.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # TODO raise an error if client_id or client_secret are empty
    post_data = {
        'client_id': client_id.strip(),
        'client_secret': client_secret.strip(),
        'code': code.strip(),
        'grant_type': 'http://oauth.net/grant_type/device/1.0'
    }

    url = r'https://www.googleapis.com/oauth2/v4/token'
    result = requests.post(url, data=post_data, headers=headers)
    print(result)
    authorization_pending = False
    try:
        print('here 0')
        json_data = result.json()
        print('here 1')
        print(result)
        if 'error' in json_data:
            if json_data['error'] != 'authorization_pending':
                json_data.update({'code': str(result.status_code)})
                raise RuntimeError(json_data)
            else:
                authorization_pending = True
    except ValueError:
        json_data = None
        print('No json')

    # Debug Emo
    print(json_data)

    if (result.status_code != requests.codes.ok) and not authorization_pending:
       raise RuntimeError('Login Failed: Code %s' % str(result.status_code))

    if result.headers.get('content-type', '').startswith('application/json'):
        if json_data:
            return json_data
        else:
            return result.json()
    else:
       raise RuntimeError('Login Failed: Unexpected content-type in response')



def revoke(self, refresh_token):
    # https://developers.google.com/youtube/v3/guides/auth/devices
    headers = {
        'Host': 'accounts.google.com',
        'User-Agent': 'Mozilla/5.0 Firefox/66.0',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    post_data = {'token': refresh_token}

    # url
    url = 'https://accounts.google.com/o/oauth2/revoke'

    result = requests.post(url, data=post_data, headers=headers, verify=self._verify)

    try:
        json_data = result.json()
        if 'error' in json_data:
            context.log_error('Revoke failed: Code: |%s| JSON: |%s|' % (str(result.status_code), json_data))
            json_data.update({'code': str(result.status_code)})
            raise LoginException(json_data)
    except ValueError:
        json_data = None

    if result.status_code != requests.codes.ok:
        response_dump = self._get_response_dump(result, json_data)
        context.log_error('Revoke failed: Code: |%s| Response dump: |%s|' % (str(result.status_code), response_dump))
        raise LoginException('Logout Failed')


def refresh_token(self, refresh_token, client_id='', client_secret=''):
    # https://developers.google.com/youtube/v3/guides/auth/devices
    headers = {'Host': 'www.googleapis.com',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
               'Content-Type': 'application/x-www-form-urlencoded'}

    client_id = client_id or self._config['id']
    client_secret = client_secret or self._config['secret']

    post_data = {'client_id': client_id,
                 'client_secret': client_secret,
                 'refresh_token': refresh_token,
                 'grant_type': 'refresh_token'}

    # url
    url = 'https://www.googleapis.com/oauth2/v4/token'

    config_type = self._get_config_type(client_id, client_secret)
    context.log_debug('Refresh token: Config: |%s| Client id [:5]: |%s| Client secret [:5]: |%s|' %
                      (config_type, client_id[:5], client_secret[:5]))

    result = requests.post(url, data=post_data, headers=headers, verify=self._verify)

    try:
        json_data = result.json()
        if 'error' in json_data:
            context.log_error('Refresh Failed: Code: |%s| JSON: |%s|' % (str(result.status_code), json_data))
            json_data.update({'code': str(result.status_code)})
            raise LoginException(json_data)
    except ValueError:
        json_data = None

    if result.status_code != requests.codes.ok:
        response_dump = self._get_response_dump(result, json_data)
        context.log_error('Refresh failed: Config: |%s| Client id [:5]: |%s| Client secret [:5]: |%s| Code: |%s| Response dump |%s|' %
                          (config_type, client_id[:5], client_secret[:5], str(result.status_code), response_dump))
        raise LoginException('Login Failed')

    if result.headers.get('content-type', '').startswith('application/json'):
        if not json_data:
            json_data = result.json()
        access_token = json_data['access_token']
        expires_in = time.time() + int(json_data.get('expires_in', 3600))
        return access_token, expires_in

    return '', ''


if __name__ == '__main__':
    client_id = ''
    client_secret = ''
    #json_data = request_device_and_user_code(client_id)

    device_code = ''
    json_data = request_access_token(device_code, client_id, client_secret)
    print(json_data)


