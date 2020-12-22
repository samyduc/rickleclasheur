
import random

class DialogMood:
    MOOD = [ "ANGRY", "SUSPICIOUS", "NEUTRAL", "FRIENDLY", "LOVING" ]

class DialogCache(object):
    def __init__(self):
        pass

class DialogUser(object):
    def __init__(self, name):
        self.name = name
        self.mood = len(DialogMood.MOOD) / 2

class DialogEngine(object):

    def __init__(self, my_name):

        self.my_name = my_name

        self.sentences = [ "crizxShy", 
            "Rickkkk le Classssheeeurrrr", 
            "Meilleur joueur Apex world de ta maman", 
            "I am the best",
            "@Maisyzx can't aim straight",
            "lel lel lel lel",
            "season 7 best season",
            "T'es rien moche",
            "T'es rien vilain",
            "gourgandine",
            "béééé béééé béééé béééé béééé",
            "j'taime po toaa",
            "un jour tu auras peut etre du niveau",
            "Est-ce que tu pourrais écarter un petit peu les gambettes ?",
            "t'es rien moche toi t'es",
        ]

        self.vipsWatch = { "maisyzx", "crizx", "kikiknowss", "azeria__", "ricklesauceur", "mesryah" }
        self.vipsWatch.add(self.my_name)

        self.customResponseOnTrigger = {
            "hasemal": [ "@Hasemal u sad n lonely boy" ],
        }

        self.personal_text = [
            "T'es rien vilain",
            "lache moi",
            "On se connait ?",
            "1v1 sur firing range ?",
            "parles a ricky",
            "béééé",
            "un jour tu auras peut etre du niveau",
            "Je ne parle pas avec les joueurs charges rifle",
            "Viens là je te claque le beignet !!!",
            "Mais vous etes qui vous ?"
        ]
        # bot should respond if someone speak directly to him

        self.user_cache = {}

    def track_user(self, source, message_split):
        if source in self.user_cache:
            pass

    def extract_vips(self, source, message_split):

        quoted_vips = set()

        for word in message_split:
            if word.startswith('@'):
                if word[1:] in self.vipsWatch:
                    quoted_vips.add( word[1:] )
            elif word in self.vipsWatch:
                quoted_vips.add( word )

        if source in self.vipsWatch:
            quoted_vips.add( source )

        return list( quoted_vips )

    def extract_trigger(self, source, message_split):

        triggers = set()

        for word in message_split:
            if word in self.customResponseOnTrigger:
                triggers.add(triggers)

        if source in self.customResponseOnTrigger:
            triggers.add(source)

        return list(triggers)

    def process(self, source, message):
        
        if source == self.my_name:
            # ignore myself
            return None

        message_split = message.split()
        quoted_vips = self.extract_vips( source, message_split)
        triggers = self.extract_trigger( source, message_split )

        if self.my_name in quoted_vips:
            self.track_user(source, message_split)

            sentence = random.choice( self.personal_text )
            finale_sentence = "@{} ".format( source ) + sentence
            return (finale_sentence,)

        for trigger in triggers:
            sentence = random.choice( self.customResponseOnTrigger[trigger] )
            return (sentence,)

        if len( quoted_vips ) > 0:
            sentence = random.choice( self.sentences )
            finale_sentence = ( "@{} " * len(quoted_vips) ).format(*quoted_vips) + sentence
            return (finale_sentence,)
        
        return None