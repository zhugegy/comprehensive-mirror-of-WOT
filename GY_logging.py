import os
import logging

# 日志配置 debug->info->warning->error->critical
# logging.debug("This is a debug")
def init(strLogFileName, strLogLevel):
    objLogLevel = logging.DEBUG

    if strLogLevel == "info":
        objLogLevel = logging.INFO
    elif strLogLevel == "warning":
        objLogLevel = logging.WARNING
    elif strLogLevel == "error":
        objLogLevel = logging.ERROR

    strExePath = os.getcwd() + "/"

    logging.basicConfig(
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        level= objLogLevel,
        handlers=[
            logging.FileHandler("{0}/{1}.log".format(strExePath, strLogFileName)),
            logging.StreamHandler()
        ])


def debug(message):
    "Automatically log the current function details."
    import inspect, logging
    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    func = inspect.currentframe().f_back.f_code
    # Dump the message + the name of this function to the log.
    logging.debug(
        " @ message content: " + message +
        " @ function name: " + func.co_name +
        " @ file name: " + func.co_filename +
        " @ line number" + str(func.co_firstlineno))

def info(message):
    "Automatically log the current function details."
    import inspect, logging
    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    func = inspect.currentframe().f_back.f_code
    # Dump the message + the name of this function to the log.
    logging.info(
        " @ message content: " + message +
        " @ function name: " + func.co_name +
        " @ file name: " + func.co_filename +
        " @ line number" + str(func.co_firstlineno))

def warning(message):
    "Automatically log the current function details."
    import inspect, logging
    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    func = inspect.currentframe().f_back.f_code
    # Dump the message + the name of this function to the log.
    logging.warning(
        " @ message content: " + message +
        " @ function name: " + func.co_name +
        " @ file name: " + func.co_filename +
        " @ line number" + str(func.co_firstlineno))

def error(message):
    "Automatically log the current function details."
    import inspect, logging
    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    func = inspect.currentframe().f_back.f_code
    # Dump the message + the name of this function to the log.
    logging.error(
        " @ message content: " + message +
        " @ function name: " + func.co_name +
        " @ file name: " + func.co_filename +
        " @ line number" + str(func.co_firstlineno))

def critical(message):
    "Automatically log the current function details."
    import inspect, logging
    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    func = inspect.currentframe().f_back.f_code
    # Dump the message + the name of this function to the log.
    logging.critical(
        " @ message content: " + message +
        " @ function name: " + func.co_name +
        " @ file name: " + func.co_filename +
        " @ line number" + str(func.co_firstlineno))
