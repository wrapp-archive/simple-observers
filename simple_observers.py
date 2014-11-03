from sys import stdout, stderr
from twisted.python import log, util


class SimpleFileObserver(object):
    def __init__(self, out, err):
        self.out = out
        self.err = err

    def emit(self, eventDict):
        text = log.textFromEventDict(eventDict)
        if text is None:
            return

        text = text.replace("\n", "\n\t")

        if eventDict.get('isError'):
            f = self.err
        else:
            f = self.out

        util.untilConcludes(f.write, text + '\n')
        util.untilConcludes(f.flush)

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
    ''' Writes everything to stdout. '''
    return SimpleFileObserver(stdout, stdout).emit


def SimpleStreamLogger():
    ''' Writes output to stdout and errors to stderr. '''
    return SimpleFileObserver(stdout, stderr).emit
