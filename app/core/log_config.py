import os
import logging

log_level = "error"


def setup_logger(logger_name: str, log_file: str, level_str: str = 'INFO') -> logging.Logger:
    global log_level
    terminal_level_str = log_level if log_level else level_str
    file_level_str = 'info'

    terminal_level = getattr(logging, terminal_level_str.upper(), None)
    file_level = getattr(logging, file_level_str.upper(), None)

    if not isinstance(terminal_level, int) or not isinstance(file_level, int):
        raise ValueError(f"Invalid log level: {terminal_level_str} or {file_level_str}")

    logger = logging.getLogger(f"{logger_name}_{log_file}")

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_level)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(terminal_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
