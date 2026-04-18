class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model":
            return super().__new__(cls, name, bases, attrs)

        fields = {}

        for key, value in attrs.items():
            if hasattr(value, "__class__") and "Field" in value.__class__.__name__:
                value.name = key
                fields[key] = value

        attrs["_fields"] = fields
        attrs["_table"] = name.lower()

        return super().__new__(cls, name, bases, attrs)