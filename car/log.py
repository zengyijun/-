# 日志文件模块，用于将调用此模块的模块传入的参数写入到对应的日志文件中去
import logging

# 此字典代表日志的等级。当有函数传入参数的时候自动匹配
log_type = {"info":1, "warn":2, "error":3}

def init_logging(logname):
    global handler, logger
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler = None
    handler = logging.FileHandler("logfile/"+logname)
    handler.setLevel(level=logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s--%(message)s'))
    logger.addHandler(handler)

def write_tolog(arg, type='info'):
    type = log_type[type]
    if(type == 1):
        logger.info(arg)
        return True
    elif (type == 2):
        logger.warn(arg)
    elif (type == 3):
        logger.error(arg)