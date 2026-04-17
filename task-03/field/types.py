from .base import Field

class CharField(Field):
    def __init__(self, max_length, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

class IntegerField(Field):
    pass