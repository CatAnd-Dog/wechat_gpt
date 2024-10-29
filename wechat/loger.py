# logger.py
import logging

def setup_logger(name):
    """
    配置并返回一个日志记录器。
    参数:
        name (str): 日志记录器的名字，通常是 __name__ 传递。
    返回:
        logging.Logger: 配置好的日志记录器。
    """
    # 创建日志记录器，设置日志级别
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 创建日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 创建控制台处理器，并设置级别和格式
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(ch)

    return logger
