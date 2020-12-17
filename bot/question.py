
import time
import random

class Question(object):
    def __init__(self):
        self._is_question_running = False
        self.start_time = 0
        self.total_time = 0
        self.winner = ""
        self.questions = {"Toto": "Toto"}
        self.available_questions = [ "Toto" ]
        self.question = ""
        self.answer = ""
        self.duration = 0
        self.delete_question_on_ask = False

    def get_current_question(self):
        return self.question

    def is_question_running(self):
        return self._is_question_running and self.is_timer_expired() == False

    def load_question(self, db):
        self.questions = self.questions | db
        self.available_questions.clear()
        self.available_questions = list(self.questions.keys())

    def ask_question(self, duration):
        self._is_question_running = True
        self.start_time = time.time()
        self.duration = duration

        self.question = random.choice(self.available_questions)

        if self.delete_question_on_ask:
            self.available_questions.remove( self.question )

        self.answer = self.questions[ self.question ]

        return self.question # return a question

    def stop_question(self, winner):
        self.total_time = time.time() - self.start_time
        self._is_question_running = False
        self.winner = winner

    def is_timer_expired(self):
        current_time = time.time()
        return current_time - self.start_time > self.duration

    def get_remaining_duration(self):
        current_time = time.time()
        remaining_duration = self.duration - self.get_elapsed_duration()

        print("{} {} {} {}", remaining_duration, self.duration, current_time, self.start_time)

        if remaining_duration < 0:
            remaining_duration = 0
        return remaining_duration

    def get_elapsed_duration(self):
        current_time = time.time()
        return current_time - self.start_time

    def try_question(self, source, answer):
        if self.is_timer_expired():
            self.stop_question("")
            return False

        if answer == self.answer:
            self.stop_question(source)
            return True

        return False


