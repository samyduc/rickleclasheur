
import time
import random

class Question(object):
    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer = answer

    def __eq__(self, o):
        if not isinstance(o, Question):
            return NotImplemented
        return self.question == o.question and self.answer == o.answer

    def __hash__(self):
        return hash(self.question)


class Questioner(object):
    def __init__(self):
        self.winner = None
        # The set of questions not asked yet
        self._available_questions = set()
        # The set of questions already asked
        self._asked_questions = set()
        # The current question
        self.current_question = None
        now = time.monotonic()
        # The time when the last question was asked
        self._asked_time = now
        # The time from which it is too late to answer
        self._expiration = now

    def is_question_running(self):
        return self.current_question is not None and not self.is_timer_expired()

    def load_questions(self, db):
        self.questions = self.questions | db
        self.available_questions.clear()
        self.available_questions = list(self.questions.keys())

    def ask_question(self, duration):
        if len(self._available_questions) == 0:
            return None
        question = random.choice(tuple(self._available_questions))
        self.current_question = question
        self._available_questions.remove(question)
        self._asked_questions.add(question)
        now = time.monotonic()
        self._asked_time = now
        self._expiration = now + duration
        return question

    def stop_question(self, winner):
        self.current_question = None
        self.winner = winner

    def is_timer_expired(self):
        return time.monotonic() >= self._expiration

    def get_remaining_duration(self):
        return max(0, self._expiration - time.monotonic())

    def get_elapsed_duration(self):
        return time.monotonic() - self._asked_time

    def try_question(self, source, answer):
        if self.is_timer_expired():
            self.stop_question(None)
            return False

        if answer == self.answer:
            self.stop_question(source)
            return True

        return False

    def reset(self):
        self._available_questions |= self._asked_questions
        self._asked_questions.clear()
        self._current_question = None
