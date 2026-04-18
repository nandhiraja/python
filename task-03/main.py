from core.model import Model
from field.types import CharField, IntegerField
from field.relation import ForeignKey

class User(Model):
    name = CharField(max_length=100)
    email = CharField(max_length=255, unique=True)
    age = IntegerField(nullable=True)

class Post(Model):
    title = CharField(max_length=200)
    author = ForeignKey(User, related_name="posts")

class order(Model):
    name=CharField(max_length=100)
    number =IntegerField(nullable=True)
    
order.create_table()
User.create_table()
Post.create_table()

alice = User(name="Alice", email="alice@example.com", age=30)
alice.save()

User.filter(age__gte=25).order_by("-name").all()