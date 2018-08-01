#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' url handlers '
import re
import time

import logging
from aiohttp import web
import asyncio, json, hashlib

from www import control
from www.apis import APIValueError, APIError, Page
from www.config_default import configs
from www.coroweb import get, post
from www.module.resultBean import ResultBean
from www.modules import User, Blog, next_id, Device

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs['session']['secret']
_SWITCH_ON = 1
_SWITCH_OFF = 0

_PERMISS_ADMIN = 1  # 管理员模式
_PERMISS_CHILD = 0  # child 模式


def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s' % (user.passwd, expires, _COOKIE_KEY)
    L = [expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


@post('/api/login')
@asyncio.coroutine
def authenticate(*, email, passwd):
    responseCode = 0
    if not email:
        responseCode = 1
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        responseCode = 1
        raise APIValueError('passwd', 'Invalid password.')
    users = yield from User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.email.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    result = ResultBean(0, user)
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@post('/api/register')
async def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    # if not passwd or not _RE_SHA1.match(passwd):
    #     raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    sha1_passwd = '%s:%s' % (email, passwd)
    user = User(name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest())
    await user.save()
    # make session cookie:
    print('---------------response -----------------')
    users = await User.findAll('email=?', [email])
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    result = ResultBean(0, users[0])
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 添加设备
@get('/api/device/add')
async def addDevice(*, name, kind, permissLevel=_PERMISS_CHILD):
    if not name or not name.strip():
        raise APIValueError('name')
    if not kind:
        raise APIValueError('kind')
    device = await Device.findAll('name=?', [name])
    if len(device) > 0:
        raise APIError('add:failed', 'device', 'device is already in use.')
    device = Device(name=name, kind=kind, status=_SWITCH_OFF, permissLevel=permissLevel)

    await device.save()
    device = await Device.findAll('name=?', [name])
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, device[0])
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 删除设备
@get('/api/device/delete')
async def deleteDevice(*, id):
    if not id or not id.strip():
        raise APIValueError('name')
    device = await Device.findAll('id=?', [id])
    if len(device) == 0:
        raise APIError('delete:failed', 'id', 'do not has id.')
    await device[0].remove()
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, "remove finish")
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 获取设备列表
@get('/api/device/list')
async def devicesList(*, kind):
    if not kind:
        raise APIValueError('kind')
    device = await Device.findAll("kind=?", [kind])
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, device)
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 获取设备详情
@get('/api/device/details')
async def devicesDetails(*, id):
    if not id:
        raise APIValueError('kind')
    device = await Device.findAll("id=?", [id])
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, device[0])
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 获取黑名单设备列表
@get('/api/device/list/permssion')
async def devicesListPermission():
    device = await Device.findAll("perLevel=?", [1])
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, device)
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 获取任务列列表
@get('/api/device/list/task')
async def devicesListTask():
    device = await Device.findAll("schedule=?", [1])
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, device)
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 更新设备名
@get('/api/device/update/name')
async def updateDeviceName(*, id, name):
    if not id or not id.strip():
        raise APIValueError('id')
    device = await Device.findAll("id=?", [id])
    if len(device) == 0:
        raise APIError('update:failed', 'device', 'do not has device.')
    device[0].name = name
    await device[0].update()
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, "update finish")
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 更新设备权限
@get('/api/device/update/permission')
async def updateDevicePer(*, id, perLevel):
    if not id or not id.strip():
        raise APIValueError('id')
    device = await Device.findAll("id=?", [id])
    if len(device) == 0:
        raise APIError('update:failed', 'device', 'do not has device.')
    device[0].perLevel = perLevel
    await device[0].update()
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, "update finish")
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 设备定时任务
@get('/api/device/update/timer')
async def updateDeviceTimer(*, id, week, time, task, schedule):
    if not id or not id.strip():
        raise APIValueError('id')
    device = await Device.findAll("id=?", [id])
    if len(device) == 0:
        raise APIError('update:failed', 'device', 'do not has device.')
    device[0].time = time
    device[0].week = week
    device[0].task = task
    device[0].schedule = schedule
    await device[0].update()
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, "success")
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 打开或者关闭设备
@get('/api/device/switch')
async def switchDevice(*, id, status):
    if not id or not id.strip():
        raise APIValueError('id')
    device = await Device.findAll("id=?", [id])
    if len(device) == 0:
        raise APIError('swicth:failed', 'device', 'do not has device.')
    if device[0].status == status:
        raise APIError('swicth:failed', 'device', 'device is in the same status')
    # control.switch(device[0].port,status)
    device[0].status = status
    await device[0].update()
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, "swicth finish")
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 更新用户名
@get('/api/user/update/name')
async def user_update_name(*, id,name):
    if not id or not id.strip():
        raise APIValueError('id')
    users = await User.findAll("id=?", [id])
    if len(users) == 0:
        raise APIError('swicth:failed', 'device', 'do not has device.')
    users[0].name = name
    await users[0].update()
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, "update success")
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 更新用户密码
@get('/api/user/update/password')
async def user_update_password(*, id, oldPass, newPas):
    if not id or not id.strip():
        raise APIValueError('id')
    users = await User.findAll("id=?", [id])
    if len(users) == 0:
        raise APIError('swicth:failed', 'device', 'do not has device.')
    sha1_passwd = '%s:%s' % (users[0].email, oldPass)
    sha_old = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest()
    if sha_old != users[0].passwd:
        r = web.Response()
        result = ResultBean(1, "oldpass erroe")
        r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
        return r
    sha1_passwd = '%s:%s' % (users[0].email, newPas)
    users[0].passwd = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest()
    await users[0].update()
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, "update success")
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r


# 更新管理员密码密码
@get('/api/user/admin/update/password')
async def user_admin_update_password(*, id, oldPass, newPas):
    if not id or not id.strip():
        raise APIValueError('id')
    users = await User.findAll("id=?", [id])
    if len(users) == 0:
        raise APIError('swicth:failed', 'device', 'do not has device.')
    if oldPass != users[0].perPasswd:
        r = web.Response()
        result = ResultBean(1, "oldpass erroe")
        r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
        return r
    users[0].perPasswd = newPas
    await users[0].update()
    r = web.Response()
    r.content_type = 'application/json'
    result = ResultBean(0, "update success")
    r.body = json.dumps(result, ensure_ascii=False).encode('utf-8')
    return r