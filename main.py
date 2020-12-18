

from bot.interface import  irc
from bot import bot
import secrets.twitch


if __name__ == "__main__":
    print("Booting ...")

    username  = secrets.twitch.USERNAME
    app_id = secrets.twitch.APP_ID
    token     = secrets.twitch.OAUTH_TOKEN
    channels = [ "ricklesauceur" ]

    irc = irc.IRCInterface(username, app_id, token, channels)
    irc.start()

    bot = bot.Bot()
    bot.irc_interface = irc

    bot.start()

    print("Running forever ...")

    try:
        irc.run( forever = True )
    except KeyboardInterrupt:
        pass
