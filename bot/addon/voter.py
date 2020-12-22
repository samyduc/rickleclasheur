

import time


class Voter:
    def __init__(self, default_duration, tags):
        self.votes = dict.fromkeys(tags)
        self.start_time = 0
        self.duration = default_duration
        self.is_unique_vote = True

    def reset(self):
        self.voters = set()
        for k in self.votes:
            self.votes[k] = 0

    def restart(self):
        self.start_time = time.time()
        self.reset()

    def is_running(self):
        return self.start_time != 0

    def get_duration(self):
        return time.time() - self.start_time

    def vote(self, id, tag):
        if self.start_time == 0 or self.get_duration() >= self.duration:
            self.restart()

        if self.is_unique_vote:
            if id in self.voters:
                return False

        if tag in self.votes:
            self.votes[tag] += 1
            self.voters.add( id )
            return True

        return False

