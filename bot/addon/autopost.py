
import time

class AutoPost:
    def __init__(self, message, delay):
        self.message = message
        self.delay = delay
        self.last_publish_timestamp = 0

    def is_ready(self, now):
        return now >= ( self.last_publish_timestamp + self.delay )

    def set_publish_timestamp(self, now):
        self.last_publish_timestamp = now
    
    def is_cmd(self):
        return self.message.startswith("!")

class AutoPosts:
    def __init__(self):
        self.posts = []

    def get_ready_posts(self, now):
        posts = []

        for post in self.posts:
            if post.is_ready(now):
                posts.append(post)

        return posts
    
    def add_post(self, message, delay):
        post = AutoPost(message, delay)
        self.posts.append( post )

