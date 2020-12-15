

import bot.ircconnector
import bot.bot
import secrets.twitch


if __name__ == "__main__":
    print("Booting ...")

    username  = secrets.twitch.USERNAME
    app_id = secrets.twitch.APP_ID
    token     = secrets.twitch.OAUTH_TOKEN
    channels = [ "ricklesauceur" ]

    irc = bot.ircconnector.IRCConnector(username, app_id, token, channels)
    irc.start()

    bot = bot.bot.Bot()
    bot.add_connector(irc)

    bot.start()

    print("Running forever ...")

    try:
        irc.run( forever = True )
    except KeyboardInterrupt:
        pass
