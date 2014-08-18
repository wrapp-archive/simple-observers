from sys import stdout
from twisted.python import log, util


class SimpleFileObserver(object):
    def __init__(self, f):
        self.write = f.write
        self.flush = f.flush

    def emit(self, eventDict):
        text = log.textFromEventDict(eventDict)
        if text is None:
            return

        text = text.replace("\n", "\n\t")

        util.untilConcludes(self.write, text + '\n')
        util.untilConcludes(self.flush)

    def start(self):
        """
        Start observing log events.
        """
        log.addObserver(self.emit)

    def stop(self):
        """
        Stop observing log events.
        """
        log.removeObserver(self.emit)


def SimpleStdoutLogger():
    return SimpleFileObserver(stdout).emit
