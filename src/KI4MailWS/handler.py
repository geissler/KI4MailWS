import logging
import os
import time

"""
Simple logging handler class which creates a separate file for each process instance to write its log messages into
"""


class KI4MailWSHandler(logging.FileHandler):
    def __init__(self, path, mode):
        if not os.path.isdir(path):
            os.mkdir(path)

        filename = "/{}_{}.log".format(time.strftime("%y-%m-%d %H-%M", time.localtime()), str(os.getpid()))
        super(KI4MailWSHandler, self).__init__(path + filename, mode)
