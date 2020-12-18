import vlc

import os

class SoundInterface(object):
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.set_volume(70)

    def play_sound(self, relative_path):

        path = os.path.abspath(relative_path)
        print(path)

        media = self.instance.media_new(path)
        if not media:
            return

        self.player.set_media(media)
        self.player.play()

    def get_volume(self):
        return vlc.libvlc_audio_get_volume(self.player)  # volume 0..100

    def set_volume(self, volume):
        vlc.libvlc_audio_set_volume(self.player, volume)  # volume 0..100

        