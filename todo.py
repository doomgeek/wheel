#!/usr/bin/env python

import re
import sqlite3

from datetime import date


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
            task.set_due(due_date_shortcuts[sck]())


preprocessors = [
    add_due_date_from_shortcut,
]


class Task(object):
    def __init__(self, title, due=None):
        self.set_title(title)
        self.set_due(due)
        for func in preprocessors:
            func(self)

    def set_title(self, title):
        self.title = title

    def set_due(self, due):
        self.due = due

    def to_sql(self):
        return ("insert into task (title, due) values (?, ?)", (self.title,
                                                                self.due))


task = Task("Get stuff done ^today #matt #is #awesome")
print task.to_sql()
