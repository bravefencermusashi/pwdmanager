from unittest.mock import MagicMock

import pytest

from pwdmanager import commands, database


class TestCreateEntry:
    def test_perform_checks(self):
        db = database.Database()
        arg_list = [
            (None, "login", "pwd"),
            ("name", None, "pwd"),
            ("name", "login", None),
        ]
        for args in arg_list:
            com = commands.AddEntry(*args)
            with pytest.raises(commands.CommandException, match=".*empty.*"):
                com.perform_checks(db)

        com = commands.AddEntry("name", "login", "pwd")
        com.perform_checks(db)

        db.add_entry(database.DatabaseEntry("name", None, None))
        with pytest.raises(commands.CommandException, match=".*exists.*"):
            com.perform_checks(db)

        com = commands.AddEntry("alias", "login", "pwd")
        com.perform_checks(db)

        db["name"].aliases = ["alias"]
        with pytest.raises(commands.CommandException, match=".*exists.*"):
            com.perform_checks(db)

    def test_execute(self):
        db = database.Database()
        command = commands.AddEntry("name", "login", "pwd", "login_alias")
        alias_list = ["alias1", "alias2"]
        command.aliases = alias_list
        tag_list = ["tag1", "tag2"]
        command.tags = tag_list

        assert len(db) == 0
        command.execute(db)
        assert len(db) == 1
        entry = db["name"]
        assert entry.name == "name"
        assert entry.login == "login"
        assert entry.pwd == "pwd"
        assert entry.login_alias == "login_alias"
        assert entry.aliases == alias_list
        assert entry.tags == tag_list
        assert entry.creation_date
        assert entry.last_update_date

    def test_check_and_execute(self):
        command = commands.AddEntry(None, None, None)
        command.perform_checks = MagicMock()
        command.execute = MagicMock()
        command.execute.return_value = "execute_returned"
        command.render = MagicMock()
        command.render.return_value = "render_returned"

        res = command.check_execute_render(None)

        assert command.perform_checks.call_count == 1
        assert command.execute.call_count == 1
        command.render.assert_called_with("execute_returned")
        assert res == "render_returned"


class TestShowEntry:
    def test_perform_checks(self):
        com = commands.ShowEntry("search")
        com.perform_checks(None)

        com.search = None
        with pytest.raises(commands.CommandException, match=".*empty.*"):
            com.perform_checks(None)

        com.search = ""
        with pytest.raises(commands.CommandException, match=".*empty.*"):
            com.perform_checks(None)

    def test_execute(self):
        com = commands.ShowEntry("search")

        db = database.Database(dict())
        assert not com.execute(db)
        test_entry = database.DatabaseEntry("test", None, None)
        db.add_entry(test_entry)
        assert not com.execute(db)
        search_entry = database.DatabaseEntry("search", None, None)
        db.add_entry(search_entry)
        assert com.execute(db) == search_entry
        com.search = "search_alias"
        assert not com.execute(db)
        test_entry.aliases.add("search_alias")
        assert com.execute(db) == test_entry

    def test_render(self):
        com = commands.ShowEntry("search")

        assert not com.render(None)
        assert com.render(database.DatabaseEntry("test", None, None))


class TestListEntries:
    def test_perform_checks(self):
        com = commands.ListEntries("search")
        com.perform_checks(None)

    def test_execute(self):
        db = database.Database(dict())
        com = commands.ListEntries("search")
        assert not com.execute(db)

        db.find_matching_entries = MagicMock()
        db.find_matching_entries.return_value = "returned"

        assert com.execute(db) == "returned"

    def test_render(self):
        com = commands.ListEntries("search")
        assert com.render(None)
        assert com.render(
            [
                database.DatabaseEntry("n", "l", "p"),
                database.DatabaseEntry("nn", "ll", "pp"),
            ]
        )


class TestRemoveEntry:
    def test_perform_checks(self):
        com = commands.RemoveEntry("")
        with pytest.raises(commands.CommandException):
            com.perform_checks(None)
        com.name = "search"
        com.perform_checks(None)

    def test_execute(self):
        db = MagicMock()
        com = commands.RemoveEntry("search")
        com.execute(db)
        db.__delitem__.assert_called_with(com.name)

    def test_render(self):
        com = commands.RemoveEntry("search")
        msg_true = com.render(True)
        msg_false = com.render(False)
        assert msg_false and msg_true
        assert msg_false != msg_true


class TestUpdateEntry:
    def test_perform_checks(self):
        com = commands.UpdateEntry("")
        db = database.Database()
        with pytest.raises(commands.CommandException):
            com.perform_checks(db)

        com.name_or_alias = "name"
        com.perform_checks(db)

        entry1 = database.DatabaseEntry("entry1", None, None)
        db.add_entry(entry1)

        com.name_or_alias = "entry1"
        com.add_aliases = ["entry2"]
        com.perform_checks(db)

        entry2 = database.DatabaseEntry("entry2", None, None)
        entry2.aliases = {"alias2"}
        db.add_entry(entry2)

        com.name_or_alias = "not existing entry"
        com.add_aliases = ["entry2"]
        com.perform_checks(db)

        com.name_or_alias = "entry1"
        com.add_aliases = ["entry2"]
        with pytest.raises(commands.CommandException):
            com.perform_checks(db)

        com.rm_aliases = ["entry2"]
        com.perform_checks(db)

        com.add_aliases = ["alias2"]
        with pytest.raises(commands.CommandException):
            com.perform_checks(db)

    def test_execute(self):
        db = database.Database()
        com = commands.UpdateEntry("name")
        com.pwd = "new_pwd"

        assert not com.execute(db)[0]
        assert not db.modified
        entry = database.DatabaseEntry("name", "login", "old_pwd")
        init_update_date = "update_date"
        entry.last_update_date = init_update_date
        db.add_entry(entry)
        res = com.execute(db)
        assert res[0]
        assert res[1] == entry.name
        assert entry.pwd == com.pwd
        assert db.modified
        assert entry.last_update_date != init_update_date

        com.add_aliases.extend(["alias_to_keep", "alias_to_rm"])
        com.rm_aliases.append("alias_to_rm")
        com.add_tags.extend(["tag_to_keep", "tag_to_rm"])
        com.rm_tags.append("tag_to_rm")
        res = com.execute(db)
        assert res[0]
        assert res[1] == entry.name
        assert entry.aliases == {"alias_to_keep"}
        assert entry.tags == {"tag_to_keep"}

        com = commands.UpdateEntry("alias_to_keep")
        com.login = "new_login"
        com.login_alias = "new_login_alias"
        res = com.execute(db)
        assert res[0]
        assert res[1] == entry.name
        assert entry.login == com.login
        assert entry.login_alias == com.login_alias

    def test_render(self):
        com = commands.UpdateEntry("search")
        msg_true = com.render((True, ""))
        msg_false = com.render((False, ""))
        assert msg_false and msg_true
        assert msg_false != msg_true
