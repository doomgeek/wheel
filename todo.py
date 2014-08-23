#!/usr/bin/env python

import re
import sqlite3

from datetime import date


class SQLite3Database(object):
    def __init__(self, path):
        self._connection = sqlite3.connect(path)
        self._managers = []

    def register(self, manager):
        manager.add_database(self)
        self._managers.append(manager)

    def create(self):
        cursor = self._connection.cursor()
        for manager in self._managers:
            for query in manager.to_create():
                cursor.execute(query)
        cursor.close()

    def get_connection(self):
        return self._connection


class TaskSQLManager(object):
    def __init__(self, Task):
        self._cls = Task.add_manager(self)

    def add_database(self, database):
        self._db = database

    def to_create(self):
        return ("create table task (id integer primary key autoincrement, "
                "                   title text, due text)",)

    def to_insert(self, task):
        return ("insert into task (title, due) values (?, ?)",
                (task.title, task.due))

    def save(self, task):
        connection = self._db.get_connection()
        cursor = connection.cursor()
        cursor.execute(*self.to_insert(task))
        _id = cursor.lastrowid
        cursor.close()
        return _id


class Task(object):
    def __init__(self, title, due=None, pk=None):
        self.title = title
        self.due = due
        self.pk = pk
        for func in self._preprocessors:
            func(self)

    @classmethod
    def add_preprocessors(cls, preprocessors):
        cls._preprocessors = preprocessors
        return cls

    @classmethod
    def add_manager(cls, manager):
        cls._manager = manager
        return cls

    def save(self):
        self.pk = self._manager.save(self)
        return self


def add_due_date_from_shortcut(task):
    due_date_shortcuts = {
        "today": date.today,
        "tomorrow": lambda: date.today() + timedelta(days=1),
        "yesterday": lambda: datetime.today() - timedelta(days=1),
    }
    for shortcut in re.findall(r"\^(\w+)", task.title):
        sck = shortcut.lower()  # short cut key
        if sck in due_date_shortcuts:
            task.title = task.title.replace("^{}".format(shortcut),
                                            "").strip()
            task.due = due_date_shortcuts[sck]()


preprocessors = (add_due_date_from_shortcut,)

database = SQLite3Database(":memory:")
database.register(TaskSQLManager(Task.add_preprocessors(preprocessors)))
database.create()

task01 = Task("Get stuff done ^today #matt #is #awesome").save()
task02 = Task("Eat Food ALLL DAY ^today #matt #is #awesome").save()
task03 = Task("Ride my bike ALLL DAY ^today #matt #is #awesome").save()
task04 = Task("Ride my bike ALLL DAY asdf ^today #matt #is #awesome").save()

import pdb; pdb.set_trace()
