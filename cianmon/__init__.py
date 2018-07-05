

def show(klass, items):
    visible_fields  = klass.get_visible_fields()
    for item in items:
        for field in visible_fields:
            print(field, ': ', getattr(item, field))
