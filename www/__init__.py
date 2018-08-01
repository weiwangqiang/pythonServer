import asyncio

import time

"""
作为测试类
"""
from www.modules import User
from www.orm import create_pool


async def main(loop):
    await create_pool(loop, **database)
    user = User()
    user.id = 1
    user.name = 'ZhouXiaorui_miao'
    await user.save()
    user = await User.find(1)
    return user

loop = asyncio.get_event_loop()
database = {
    'host':'localhost', #数据库的地址
    'user':'root',
    'password':'123456',
    'db':'python'
}
if __name__ == '__main__':
    task = asyncio.ensure_future(main(loop))
    res = loop.run_until_complete(task)
    print(res)