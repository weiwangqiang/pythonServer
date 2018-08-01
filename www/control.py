# import RPi.GPIO as GPIO  # 导入树莓派提供的python模块
#
# import time  # 导入时间包，用于控制闪烁
#
#
# def switch(port, level=0):
#     GPIO.setmode(GPIO.BCM)  # 设置GPIO模式，BCM模式在所有数码派通用
#     GPIO.setup(port, GPIO.OUT)  # 设置GPIO18为电流输出
#     if level:
#         __on(port)
#     else:
#         __off(port)
#
#
# def __on(port):
#     while True:
#         GPIO.output(port, GPIO.HIGH)  # GPIO18 输出3.3V
#         time.sleep(0.5)  # 程序控制流程睡眠0.05秒
#
#
# def __off(port):
#     while True:
#         GPIO.output(port, GPIO.LOW)  # GPIO18 输出0V
#         time.sleep(0.5)  # 程序控制流程睡眠0.05秒
