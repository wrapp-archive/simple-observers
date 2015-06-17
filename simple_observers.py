import json
import sys

from twisted.python import log, util
from twisted.logger import formatEvent


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



class KeyValueFileObserver(SimpleFileObserver):
    ''' Returns a string of formatted key=value pairs.

    The string will include level, msg, and exc_*. Also includes any arbitrary
    data that was included in the eventDict except for certain common and
    uninteresting fields. All values in the key-value string are json-encoded.
    Complex objects like lists and dicts are ignored.

    For readability purposes the order of the fields is:

        * level
        * msg
        * exc_type, if present
        * exc_value, if present
        * arbitrary additional data sorted by key


    '''

    def emit(self, event):
        is_error = event.get('isError', False)
        try:
            text = self.format_kv(event)
        except Exception, e:
            text = 'Parse error: %s. Original message: %s' % \
                    (repr(e), formatEvent(event))
            is_error = True

        f = self.err if is_error else self.out

        util.untilConcludes(f.write, text + '\n')
        util.untilConcludes(f.flush)

    def format_kv(self, event):
        log_format = event.pop('log_format', None)
        failure = event.pop('failure', None)
        exc_type = failure and '%s.%s' % (failure.type.__module__, failure.type.__name__)
        exc_value = failure and failure.getErrorMessage()

        msg = log_format and log_format.format(**event)
        message = event.pop('message')
        if failure:
            msg = message if message else '%s: %s' % (exc_type, exc_value)
        if not msg:
            msg = message

        out = []

        if event.get('isError'):
            level = 'error'
        else:
            level = 'info'

        out = [
            ('level', level),
            ('msg', msg),
        ]

        if failure:
            out.extend([
                ('exc_type', exc_type),
                ('exc_value', exc_value),
            ])

        # Remove everything else that's prefixed with log_.
        event = {k: v for k, v in event.items() if not k.startswith('log_')}
        event.pop('message', None)
        event.pop('system', None)
        event.pop('format', None)
        event.pop('time', None)
        event.pop('isError', None)
        event.pop('failure', None)
        out.extend(sorted(event.items()))

        return ' '.join(["%s=%s" % (k, json.dumps(v)) for (k, v) in out if not self.is_complex(v)])

    def is_complex(self, v):
        return isinstance(v, list) or isinstance(v, dict)




def SimpleStdoutLogger():
    ''' Writes everything to stdout. '''
    return SimpleFileObserver(sys.stdout, sys.stdout).emit


def SimpleStreamLogger():
    ''' Writes output to stdout and errors to stderr. '''
    return SimpleFileObserver(sys.stdout, sys.stderr).emit


def KeyValueStdoutLogger():
    ''' Writes output to stdout as structured key=value logs (logfmt). '''
    return KeyValueFileObserver(sys.stdout, sys.stdout).emit


def KeyValueStreamLogger():
    ''' Writes output to stdout and errors to stderr as structured key=value
    logs (logfmt). '''
    return KeyValueFileObserver(sys.stdout, sys.stderr).emit
