#!/usr/bin/env python

import os
import re
import sqlite3

from datetime import date


DATABASE_PATH = os.path.join(os.environ["HOME"], ".tasks.sqlite3")


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


class SQLite3TaskManager(object):
    def __init__(self, Task):
        self._cls = Task.add_manager(self)

    def add_database(self, database):
        self._db = database

    def to_create(self):
        return ("create table if not exists task (id integer "
                "primary key autoincrement, title text, due text)",
                "create unique index if not exists idx_task_title "
                "on task (title)")

    def to_update(self, task):
        return ("update task set title = ?, due = ? where id = ?",
                (task.title, task.due, task.pk))

    def to_insert(self, task):
        return ("insert into task (title, due) values (?, ?)",
                (task.title, task.due))

    def to_select(self, task, **kwargs):
        if "pk" in kwargs:
            q = ("select id, title, due from task where id = ?",
                 (kwargs["pk"],))
        elif "title" in kwargs:
            q = ("select id, title, due from task where title = ?",
                 (kwargs["title"],))
        else:
            q = None
        return q

    def save(self, task):
        connection = self._db.get_connection()
        cursor = connection.cursor()
        if task.pk:
            cursor.execute(*self.to_update(task))
            task.pk = cursor.lastrowid
        else:
            try:
                cursor.execute(*self.to_insert(task))
            except sqlite3.IntegrityError:
                # This could result in loss of data if the user creates
                # a duplicate object with less detail than the original.
                # It may be better to throw an exception and let the
                # user confirm that they mean to do this.  But, for now,
                # I'm going to let it stand as is.
                cursor.execute(*self.to_select(task, title=task.title))
                task.pk = cursor.fetchone()[0]
                self.save(task)
        cursor.close()
        connection.commit()
        return task


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
        self = self._manager.save(self)
        return self


def add_due_date_from_shortcut(task):
    due_date_shortcuts = {
        "today": date.today,
        "tomorrow": lambda: date.today() + timedelta(days=1),
        "yesterday": lambda: datetime.today() - timedelta(days=1),
    }
    for shortcut in re.findall(r"\^(\w+\s*)", task.title):
        sck = shortcut.lower().strip()  # short cut key
        if sck in due_date_shortcuts:
            task.title = task.title.replace("^{}".format(shortcut),
                                            "").strip()
            task.due = due_date_shortcuts[sck]()


preprocessors = (add_due_date_from_shortcut,)

database = SQLite3Database(DATABASE_PATH)
database.register(SQLite3TaskManager(Task.add_preprocessors(preprocessors)))
database.create()

task01 = Task("Get stuff done ^today #matt #is #awesome").save()
task02 = Task("Eat Food ALLL DAY ^today #matt #is #awesome").save()
task03 = Task("Ride my bike ALLL DAY ^today #matt #is #awesome").save()
task04 = Task("Ride my bike ALLL DAY asdf ^today #matt #is #awesome").save()
