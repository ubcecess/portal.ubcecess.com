#!/usr/bin/python

from pony.orm import *

# Database + ORM

db = Database('sqlite', 'testdb.sqlite', create_db=True)

class Users(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    email = Required(str, unique=True)
    group = Required(str, default='unknown')
    locker = Optional("Lockers")
    documents = Set("Documents")


class Lockers(db.Entity):
    number = PrimaryKey(int, auto=True)
    available = Required(bool, default=1)
    paid = Required(bool, default=0)
    user = Optional(Users)


class Documents(db.Entity):
    url = PrimaryKey(str)
    name = Required(str)
    kind = Required(str, default='unknown')
    users = Set(Users)


# sql_debug(True)
db.generate_mapping(create_tables=True)
