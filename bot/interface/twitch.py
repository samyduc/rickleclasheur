

import time

from bot import database
from secrets import web
import requests

import urllib.parse

class TwitchInterface(object):
    def __init__(self, username, channel_name, app_id, app_token, user_code):
        self.channel_id = ""
        self.channel_name = channel_name
        self.username = username
        self.user_id = ""
        self.stream_id = ""
        self.app_id = app_id
        self.app_token = app_token
        self.access_token = ""
        self.access_token_expiry_time = 0
        self.access_token_type = ""
        self.user_code = user_code
        self.user_token = ""
        self.user_token_expiry_time = 0
        self.user_token_refresh_code = 0
        self.scopes = [ "clips:edit", "channel:manage:broadcast", "channel:read:subscriptions", "user:edit", "user:edit:follows", "user:read:broadcast" ]
        self.registered_callback_url = web.WEB_DOMAIN + "/twitch_callback"
        
        self.channel_language = ""
        self.channel_title = ""
        self.channel_game_id = ""

        self.database = database.JsonDatabase("twitch")
        self.load()
        
    def load(self):
        self.database.load()

        if "user_code" in self.database.data:
            self.user_code = self.database.data["user_code"]       
        if "user_token" in self.database.data:
            self.user_token = self.database.data["user_token"]     
        if "user_token_refresh_code" in self.database.data:
            self.user_token_refresh_code = self.database.data["user_token_refresh_code"]
        if "user_token_expiry_time" in self.database.data:
            self.user_token_expiry_time = self.database.data["user_token_expiry_time"]  

    def save(self):
        self.database.data["user_code"] = self.user_code
        self.database.data["user_token"] = self.user_token
        self.database.data["user_token_refresh_code"] = self.user_token_refresh_code
        self.database.data["user_token_expiry_time"] = self.user_token_expiry_time 

        self.database.save()

    def get_server_auth_header(self):
        headers = {}

        headers["Authorization"] = "Bearer {}".format(self.access_token)
        headers["Client-Id"] = self.app_id
     
        return headers

    def get_client_auth_header(self):
        headers = {}

        headers["Authorization"] = "Bearer {}".format(self.user_token)
        headers["Client-Id"] = self.app_id
     
        return headers

    def get_scope_string(self):
        scopes = ""
        for scope in self.scopes:
            scopes += scope + ' '

        if len(scopes) > 0:
            scopes = scopes[:-1]

        return scopes

    def url_encode_query_string(self, query_string):
        url_encoded = urllib.parse.urlencode(query_string)
        url_encoded = url_encoded.replace('+', '%20')

        return url_encoded

    def setup_credentials(self):
        self.setup_app_credentials()
        self.setup_user_credentials()

    def setup_app_credentials(self):
        print("--- setup_app_credentials ---")

        url = "https://id.twitch.tv/oauth2/token"

        query_string = {}
        query_string["client_id"] = self.app_id
        query_string["client_secret"] = self.app_token
        query_string["grant_type"] = "client_credentials"
        query_string["scope"] = self.get_scope_string()

        url_encoded = self.url_encode_query_string(query_string)

        response = requests.post(url, data=url_encoded).json()

        self.access_token = response["access_token"]
        self.access_token_expiry_time = response["expires_in"] + time.time()
        self.access_token_type = response["token_type"]

    def setup_user_credentials(self):
        print("--- setup_user_credentials ---")

        # just to know which url to push to refresh the token
        self.setup_user_credentials_oauth()

        if self.user_token != "":
            self.refresh_user_credentials()
            return

        #self.setup_user_credentials_oauth()
        self.setup_user_credential_token()

    def setup_user_credential_token(self):
        print("--- setup_user_credential_token ---")

        url = "https://id.twitch.tv/oauth2/token"

        query_string = {}
        query_string["client_id"] = self.app_id
        query_string["client_secret"] = self.app_token
        query_string["code"] = self.user_code
        query_string["grant_type"] = "authorization_code"
        query_string["redirect_uri"] = self.registered_callback_url

        response = requests.post(url, params=query_string).json()
        print(response)

        if "status" in response and response["status"] != 200:
            print("--- setup_user_credential_token FAILED --- {}".format(response))
            return

        self.user_token = response["access_token"]
        self.user_token_refresh_code = response["refresh_token"]
        self.user_token_expiry_time = response["expires_in"] + time.time()

        self.save() # cache our tokens

    def refresh_user_credentials(self):
        print("--- refresh_user_credentials ---")

        url = "https://id.twitch.tv/oauth2/token"

        query_string = {}
        query_string["client_id"] = self.app_id
        query_string["client_secret"] = self.app_token
        query_string["refresh_token"] = self.user_token_refresh_code
        query_string["grant_type"] = "refresh_token"

        response = requests.post(url, params=query_string).json()
        print(response)

        if "status" in response and response["status"] != 200:
            print("--- refresh_user_credentials FAILED --- {}".format(response))
            return

        self.user_token = response["access_token"]
        self.user_token_refresh_code = response["refresh_token"]
        self.user_token_expiry_time = response["expires_in"] + time.time() 

        self.save() # cache our tokens

    def setup_user_credentials_oauth(self):
        print("--- setup_user_credentials_oauth ---")

        url = "https://id.twitch.tv/oauth2/authorize"

        query_string = {}
        query_string["client_id"] = self.app_id
        query_string["redirect_uri"] = self.registered_callback_url
        query_string["response_type"] = "code"
        query_string["scope"] = self.get_scope_string()

        url_encoded = self.url_encode_query_string(query_string)

        response = requests.get(url + "?" + url_encoded, params=url_encoded)

        print("---------- OAuth URL Token BEGIN --------------")
        print(response.url)
        print("---------- OAuth URL Token END --------------")

    def setup_stream_info(self):
        print("--- setup_stream_info ---")

        url = "https://api.twitch.tv/helix/streams"

        query_string = {}
        query_string["user_login"] = self.channel_name

        response = requests.get(url, headers=self.get_server_auth_header(), params=query_string).json()

        data = response["data"]

        if len(data) > 0:
            stream_info = data[0]
            self.stream_id = stream_info["id"]
            self.user_id = stream_info["user_id"]
            self.channel_language = stream_info["language"]
            self.channel_title = stream_info["title"]
            self.channel_game_id = stream_info["game_id"]

    def create_clip(self):
        print("--- create_clip ---")

        url = "https://api.twitch.tv/helix/clips"

        query_string = {}
        query_string["broadcaster_id"] = self.user_id
        query_string["has_delay"] = True

        response = requests.post(url, headers=self.get_client_auth_header(), params=query_string).json()

        if "status" in response and response["status"] != 200:
            print("--- create_clip FAILED --- {}".format(response))
            return response

        clip_url = response["data"][0]["edit_url"]
        clip_url = clip_url[:-len("/edit")]

        return clip_url

    def create_marker(self, description):
        print("--- create_marker ---")

        url = "https://api.twitch.tv/helix/streams/markers"

        query_string = {}
        query_string["user_id"] = self.user_id
        query_string["description"] = description

        response = requests.post(url, headers=self.get_client_auth_header(), params=query_string).json()
        print(response)

    def set_stream_info(self, title="", game_id=""):
        print("--- set_stream_info ---")

        url = "https://api.twitch.tv/helix/channels"

        query_string = {}
        query_string["broadcaster_id"] = self.user_id     

        data = {}
        if title != "":
            data["title"] = title
        if game_id != "":
            data["game_id"] = game_id

        response = requests.patch(url, headers=self.get_client_auth_header(), params=query_string, json=data).json()
        print(response)




