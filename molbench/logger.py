import logging
import os
import sys

logger = None

class MolbenchFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[1;32m',  # Green
        'INFO': '',  # No color
        'WARNING': '\033[3;33m',  # Orange
        'ERROR': '\033[1;31m',  # Red
        'CRITICAL': '\033[1;35m'  # Pink
    }
    RESET_SEQ = '\033[0m'

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            color_prefix = self.COLORS[levelname]
            record.msg = f"{color_prefix}{record.msg}{self.RESET_SEQ}"
        return super().format(record)


def __initlogger():
    global logger
    if logger is not None:
        return
    logger = logging.getLogger("molbench")
    logger.setLevel(os.environ.get("MOLBENCH_VERBOSE", "INFO"))
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(os.environ.get("MOLBENCH_VERBOSE", "INFO"))
    formatter = MolbenchFormatter()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

def debug(msg: str, cause=None):
    __initlogger()
    global logger
    if cause is None:
        logger.debug(msg)
    else:
        logger.debug(f"[{cause}] {msg}")

def info(msg: str, cause=None):
    __initlogger()
    global logger
    if cause is None:
        logger.info(msg)
    else:
        logger.info(f"[{cause}] {msg}")

def warning(msg: str, cause=None):
    __initlogger()
    global logger
    if cause is None:
        logger.warning(msg)
    else:
        logger.warning(f"[{cause}] {msg}")

def error(msg: str, cause=None, etype: str = ""):
    __initlogger()
    global logger
    if cause is None:
        logger.error(f"{msg} (Error type: {etype})")
    else:
        logger.warning(f"[{cause}] {msg} (Error type: {etype})")
    

def critical(msg: str, cause, linecontent: str, linenum: str, etype: str = ""):
    __initlogger()
    global logger
    msg0 = f" CRITICAL ERROR IN MOLBENCH EXECUTION [Place: {cause}]"
    msg_print = "=" * len(msg0) + f"\n{msg0}\n" + "=" * len(msg0) + "\n\n"
    msg_print += f"Error type:         {etype}\nLine Number:        {linenum}\n\n"
    msg_print += f"{linecontent}\n" + "^" * len(linecontent) + "\n"
    msg_print += msg + "\n\nExecution aborted."
    logger.critical(msg_print)
    sys.exit(-1)

