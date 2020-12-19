
import requests
import time

from bot import database

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
        self.scopes = [ "clips:edit", "channel:manage:broadcast", "channel:read:subscription", "user:edit", "user:edit:follows", "user:read:broadcast" ]
        self.registered_callback_url = "https://northridge.deckard.fr:8080/twitch_callback" # todo: must be a setting
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
        query_string["scope"] = self.scopes

        response = requests.post(url, params=query_string).json()
        self.access_token = response["access_token"]
        self.access_token_expiry_time = response["expires_in"] + time.time()
        self.access_token_type = response["token_type"]

    def setup_user_credentials(self):
        print("--- setup_user_credentials ---")

        if self.user_token != "":
            self.refresh_user_credentials()
            return

        self.setup_user_credentials_oauth()
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
        query_string["scope"] = self.scopes

        response = requests.get(url, params=query_string)

        print("---------- OAuth URL Token BEGIN --------------")
        print(response.url)
        print("---------- OAuth URL Token END --------------")

    def setup_stream_info(self):
        url = "https://api.twitch.tv/helix/streams"

        query_string = {}
        query_string["user_login"] = self.channel_name

        response = requests.get(url, headers=self.get_server_auth_header(), params=query_string).json()
        stream_info = response["data"][0]
        self.stream_id = stream_info["id"]
        self.user_id = stream_info["user_id"]

    def create_clip(self):
        url = "https://api.twitch.tv/helix/clips"

        query_string = {}
        query_string["broadcaster_id"] = self.stream_id
        query_string["has_delay"] = True

        response = requests.post(url, headers=self.get_client_auth_header(), params=query_string).json()
        print(response)






