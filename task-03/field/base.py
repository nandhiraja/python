class Field:
    def __init__(self, nullable=False, unique=False):
        self.name = None
        self.nullable = nullable
        self.unique = unique

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value