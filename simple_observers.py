import json
import sys

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

    def emit(self, eventDict):
        try:
            text = self.format_kv(**eventDict)
        except Exception, e:
            # Fallback to safe operation
            text = 'Parse error: %s. Original message: %s' % \
                    (repr(e), log.textFromEventDict(eventDict))

        if eventDict.get('isError'):
            f = self.err
        else:
            f = self.out

        util.untilConcludes(f.write, text + '\n')
        util.untilConcludes(f.flush)

    def format_kv(self, system=None, time=None, message=None, isError=False,
            failure=None, printed=None, **data):
        out = []

        if isError:
            level = 'error'
        else:
            level = 'info'

        if failure:
            exc_type = '%s.%s' % (failure.type.__module__, failure.type.__name__)
            exc_value = failure.getErrorMessage()

        if message:
            msg = message[0]
        elif failure:
            msg = '%s: %s' % (exc_type, exc_value)
        else:
            msg = None

        out = [
            ('level', level),
            ('msg', msg),
        ]

        if failure:
            out.extend([
                ('exc_type', exc_type),
                ('exc_value', exc_value),
            ])

        out.extend(sorted(data.items()))

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
