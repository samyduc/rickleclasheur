

import time

from .addon import question
from .addon import voter
from .addon import greeter

class Channel(object):
    def __init__(self, name):
        self.name = name
        self.users = {}

        self.hype_voter = voter.Voter(30, ["clutch", "choke"])
        self.hype_voter.is_unique_vote = False

        self.questioner = question.Questioner()

        self.questioner.load_questions((
            question.Question(
                'Pas très aimé des citadins, enfants et vieux aiment l’attirer, il peuple pourtant toits et jardins, des escrocs, il est le jouet.',
                'pigeon'
            ),
            question.Question(
                'Mûr à point, l’été il est fauché, fauché, on l’est de n’en point avoir.',
                'Le blé'
            ),
            question.Question(
                'C’est un petit air léger qui nous ravit l’été, sans « R », elle est glaciale, car plutôt hivernale.',
                'La brise'
            ),
            question.Question(
                'On la tourne pour avancer, mais quand on l’est, cela signifie « être branché ».',
                'La page'
            ),
            question.Question(
                'C’est la partie intégrante d’un pont, le rendre, c’est en avoir ras le bol, contre les taches, c’est une protection.',
                'Le tablier'
            )
        ))
        #self.greeter = greeter.Greeter()
        self.greeter = None

    def add_user(self, source):
        user = User(source)
        self.users[source] = user

        if self.greeter:
            self.greeter.greet_add(user)    

    def greet(self):
        if self.greeter:
            return self.greeter.greet()
        return [] 


class User(object):
    def __init__(self, name):
        self.name = name
        self.join_time = time.time()
