from unittest.mock import MagicMock

import pytest

import commands, database


class TestCreateEntry:
    def test_perform_checks(self):
        db = database.Database(dict())
        arg_list = [(None, 'login', 'pwd'), ('name', None, 'pwd'), ('name', 'login', None)]
        for args in arg_list:
            com = commands.CreateEntry(*args)
            with pytest.raises(commands.CommandException, match='.*empty.*'):
                com.perform_checks(db)

        com = commands.CreateEntry('name', 'login', 'pwd')
        com.perform_checks(db)

        db.add_entry(database.DatabaseEntry('name', None, None))
        with pytest.raises(commands.CommandException, match='.*exists.*'):
            com.perform_checks(db)

        com = commands.CreateEntry('alias', 'login', 'pwd')
        com.perform_checks(db)

        db['name'].aliases = ['alias']
        with pytest.raises(commands.CommandException, match='.*exists.*'):
            com.perform_checks(db)

    def test_execute(self):
        db = database.Database(dict())
        command = commands.CreateEntry('name', 'login', 'pwd', 'login_alias')
        alias_list = ['alias1', 'alias2']
        command.aliases = alias_list
        tag_list = ['tag1', 'tag2']
        command.tags = tag_list

        assert len(db) == 0
        command.execute(db)
        assert len(db) == 1
        entry = db['name']
        assert entry.name == 'name'
        assert entry.login == 'login'
        assert entry.pwd == 'pwd'
        assert entry.login_alias == 'login_alias'
        assert entry.aliases == alias_list
        assert entry.tags == tag_list
        assert entry.creation_date
        assert entry.last_update_date

    def test_check_and_execute(self):
        command = commands.CreateEntry(None, None, None)
        command.perform_checks = MagicMock()
        command.execute = MagicMock()
        command.check_and_execute(None)

        assert command.perform_checks.call_count == 1
        assert command.execute.call_count == 1
