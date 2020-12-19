
import os
import json

class JsonDatabase(object):
    def __init__(self, name):
        self.root_dir = os.path.abspath("./local/")
        self.name = name
        self.data = {}

    def get_absolute_path(self):
        return os.path.join(self.root_dir, self.name + ".json")

    def save(self):
        with open( self.get_absolute_path(), 'w' ) as file:
            file.write( json.dumps( self.data ) )

    def load(self):
        try:
            with open( self.get_absolute_path() ) as file:
                data = file.readline() # 1 line block
                self.data = json.loads( data )
        except FileNotFoundError:
            pass


