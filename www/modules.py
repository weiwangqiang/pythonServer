#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Models for user, blog, comment.
'''

import time, uuid

from www.orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField, LongField


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    __table__ = 'user'

    id = IntegerField(primary_key=True, auto_increment=True)
    # id = StringField(primary_key=True, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    perLevel = IntegerField()#账号级别
    perPasswd = StringField(ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    # image = StringField(ddl='varchar(500)')
    # created_at = FloatField(default=time.time)


class Device(Model):
    __table__ = 'device'
    id = IntegerField(primary_key=True, auto_increment=True)
    name = StringField(ddl='varchar(50)')
    kind = IntegerField()
    status = IntegerField()
    perLevel = IntegerField()
    time = LongField()
    week = StringField()
    port = IntegerField()
    task = IntegerField()
    schedule = IntegerField()#是否有任务

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)


def main():
    use = User(name='wei', emaik='qweq', passwd='qedq')
    use.save()


if __name__ == '__main__':
    main()
