import logging
import logging.config


def setup_logging():
    """
    配置日志系统。

    此函数配置了应用程序的日志记录方式，包括控制台输出和文件记录。
    日志级别设置为INFO，这意味着INFO级别及以上的日志信息将被记录。
    """

    # 定义日志配置字典
    logging_config = {
        # 配置版本号，必须存在且值为1
        'version': 1,

        # 不禁用已存在的日志器
        'disable_existing_loggers': False,

        # 定义日志格式
        'formatters': {
            'standard': {
                # 标准日志格式，包括时间戳、日志级别、记录器名称和消息
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },

        # 定义处理器，即日志信息如何被发送到目的地
        'handlers': {
            'console': {
                # 控制台处理器，用于在控制台显示日志
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },

            'file': {
                # 文件处理器，用于将日志记录到文件中
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'formatter': 'standard',
                # 日志文件名为app.log
                'filename': 'app.log',
                # 文件打开模式为追加
                'mode': 'a',
            },
        },

        # 定义各个日志器的处理方式
        'loggers': {
            '': {  # 根日志器
                # 使用的处理器列表
                'handlers': ['console', 'file'],
                # 设置日志级别为INFO
                'level': 'INFO',
                # 是否传递给父日志器
                'propagate': True
            },
        }
    }

    # 使用字典配置日志系统
    logging.config.dictConfig(logging_config)
