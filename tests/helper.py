import database


def create_full_json_repr(name='test_name'):
    json_repr = {
        'name': name,
        'login': 'test_login',
        'pwd': 'test_pwd',
        'login_alias': 'test_login_alias',
        'aliases': ['alias1', 'alias2'],
        'tags': ['tag1', 'tag2'],
        'creation_date': 'test_creation_date',
        'last_update_date': 'test_last_update_date'
    }

    return json_repr


def create_min_json_repr(name='test_name'):
    json_repr = {
        'name': name,
        'login': 'test_login',
        'pwd': 'test_pwd',
        'creation_date': 'test_creation_date',
        'last_update_date': 'test_last_update_date'
    }

    return json_repr


def get_full_entry(name='test_name'):
    return database.create_database_entry(create_full_json_repr(name))


def create_min_entry(name='test_name'):
    return database.create_database_entry(create_min_json_repr(name))
