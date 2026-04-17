from .base import Field

class ForeignKey(Field):
    def __init__(self, to, related_name=None):
        super().__init__()
        self.to = to
        self.related_name = related_name