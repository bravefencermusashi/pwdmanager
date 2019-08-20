import argparse
import getpass
import os

from pwdmanager.commands import (
    AddEntry,
    CommandException,
    ListEntries,
    RemoveEntry,
    ShowEntry,
    UpdateEntry,
)
from pwdmanager.database import DataBaseCryptException, create_db_manager


def create_arg_parser():
    parser = argparse.ArgumentParser(prog="pwdmanager")
    parser.add_argument(
        "-d",
        "--database",
        default=get_default_db_location(),
        help="specify where the database is located",
    )
    parser.add_argument(
        "-p", "--master-password", help="password to crypt and decrypt the database"
    )
    subparser = parser.add_subparsers(dest="command")
    subparser.required = True

    subparser_add = subparser.add_parser("add")
    subparser_add.add_argument("name", help="the name of the entry, must be unique")
    subparser_add.add_argument("login", help="the account login")
    subparser_add.add_argument("password", help="the account password")
    subparser_add.add_argument(
        "-a",
        "--alias",
        nargs="+",
        help="aliases for the account,"
        " to give alternative names to the entry, must be unique",
    )
    subparser_add.add_argument(
        "-t", "--tags", nargs="+", help="allow to categorize entries"
    )
    subparser_add.add_argument(
        "--login-alias", help="optional login alias for the account"
    )

    subparser_show = subparser.add_parser("show")
    subparser_show.add_argument("name", help="full name or alias of an entry")

    subparser_list = subparser.add_parser("list")
    subparser_list.add_argument(
        "search",
        nargs="?",
        help="string you want to look for in name and aliases of entries",
    )
    subparser_list.add_argument(
        "-t", "--tag", help="string you want to look for in tags of entries"
    )

    subparser_show = subparser.add_parser("rm")
    subparser_show.add_argument(
        "name", help="full name or alias of an entry you want to remove"
    )

    subparser_update = subparser.add_parser("update")
    subparser_update.add_argument(
        "name", help="full name or alias of an entry you want to update"
    )
    subparser_update.add_argument("-l", "--login", help="new login you want to set")
    subparser_update.add_argument(
        "-la", "--login-alias", help="new login alias you want to set"
    )
    subparser_update.add_argument(
        "-p", "--password", help="new password you want to set"
    )
    subparser_update.add_argument(
        "-aa", "--add-aliases", nargs="+", help="aliases you want to add"
    )
    subparser_update.add_argument(
        "-rma", "--remove-aliases", nargs="+", help="aliases you want to remove"
    )
    subparser_update.add_argument(
        "-at", "--add-tags", nargs="+", help="tags you want to add"
    )
    subparser_update.add_argument(
        "-rmt", "--remove-tags", nargs="+", help="tags you want to remove"
    )

    return parser


def get_default_db_location():
    return os.path.join(os.path.expanduser("~"), ".pwddb")


def create_addentry_command(args):
    command = AddEntry(args.name, args.login, args.password, args.login_alias)
    if args.alias:
        command.aliases = args.alias
    if args.tags:
        command.tags = args.tags

    return command


def create_showentry_command(args):
    return ShowEntry(args.name)


def create_listentries_command(args):
    return ListEntries(args.search, args.tag)


def create_remove_command(args):
    return RemoveEntry(args.name)


def create_update_command(args):
    command = UpdateEntry(args.name)
    if args.login_alias is not None:
        command.login_alias = args.login_alias
    if args.login:
        command.login = args.login
    if args.password:
        command.pwd = args.password
    if args.add_aliases:
        command.add_aliases = args.add_aliases
    if args.remove_aliases:
        command.rm_aliases = args.remove_aliases
    if args.add_tags:
        command.add_tags = args.add_tags
    if args.remove_tags:
        command.rm_tags = args.remove_tags

    return command


def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    master_pwd = args.master_password
    if not master_pwd:
        master_pwd = getpass.getpass()

    if args.command == "add":
        command = create_addentry_command(args)
    elif args.command == "show":
        command = create_showentry_command(args)
    elif args.command == "list":
        command = create_listentries_command(args)
    elif args.command == "rm":
        command = create_remove_command(args)
    elif args.command == "update":
        command = create_update_command(args)

    db_manager = create_db_manager(args.database, master_pwd)
    try:
        db = (
            db_manager.load_db()
            if os.path.exists(args.database)
            else db_manager.init_db()
        )
    except DataBaseCryptException as e:
        print("database cannot be loaded : {}".format(str(e)))
    else:
        try:
            print(command.check_execute_render(db))
        except CommandException as e:
            print("cannot execute command, message is: {}".format(str(e)))
        else:
            db_manager.save_db_if_needed()


if __name__ == "__main__":
    main()
