from core.metaclass import ModelMeta
from db.connection import cursor, conn

class Model(metaclass=ModelMeta):

    def __init__(self, **kwargs):
        for field in self._fields:
            setattr(self, field, kwargs.get(field))

    @classmethod
    def create_table(cls):
        columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]

        for name, field in cls._fields.items():
            if field.__class__.__name__ == "CharField":
                col = f"{name} VARCHAR({field.max_length})"
            elif field.__class__.__name__ == "IntegerField":
                col = f"{name} INTEGER"
            else:
                continue

            if not field.nullable:
                col += " NOT NULL"
            if field.unique:
                col += " UNIQUE"

            columns.append(col)

        sql = f"CREATE TABLE IF NOT EXISTS {cls._table} ({', '.join(columns)});"
        print("SQL:", sql)

        cursor.execute(sql)
        conn.commit()
    def save(self):
        fields = []
        values = []

        for name in self._fields:
            fields.append(name)
            values.append(getattr(self, name))

        placeholders = ", ".join(["?"] * len(values))

        sql = f"INSERT INTO {self._table} ({', '.join(fields)}) VALUES ({placeholders})"
        print("SQL:", sql)

        cursor.execute(sql, values)
        conn.commit()

        self.id = cursor.lastrowid
    
    @classmethod
    def filter(cls, **kwargs):
        from query.queryset import QuerySet
        return QuerySet(cls).filter(**kwargs)