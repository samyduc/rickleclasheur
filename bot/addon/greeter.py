


import time


class Greeter(object):
    def __init__(self):
        self.should_greet = False
        self.to_greets_time = 0
        self.to_greets = []
        self.to_greets_wait_time = 120

    def greet_add(self, user):
        if self.to_greets_time == 0 :
            self.to_greets_time = time.time()
        self.to_greets.append( user )

    def greet_clear(self):
        self.to_greets = []
        self.to_greets_time = 0

    def greet(self):
        if self.to_greets_time == 0:
            return []

        current_time = time.time()
        diff = current_time - self.to_greets_time

        if( diff >= self.to_greets_wait_time ):
            return self.to_greets
        return []