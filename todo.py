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
            task["due"] = due_date_shortcuts[sck]()
    return task


def add_tags(task):
    title = task["title"]
    for tag in re.findall("#(\w+)", title):
        if "tags" not in task:
            task["tags"] = []
        task["tags"].append(tag)
    return task


preprocessors = [
    add_due_date_from_shortcut,
#    add_tags,
]


class Task(object):
    def __init__(self, title):
        task = {"title": title}
        for func in preprocessors:
            task = func(task)
        return task






def save_task(task, db):


print create_task("Get stuff done ^today #matt #is #awesome")
