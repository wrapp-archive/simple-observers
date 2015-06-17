from cStringIO import StringIO
from mock import patch
from simple_observers import KeyValueFileObserver, SimpleFileObserver
from twisted.python.failure import Failure
from twisted.python.log import LogPublisher, err as logerr


log = None


def setup(module):
    module.log = LogPublisher()
    module.log.err = err



class TestSimpleFileObserver(object):
    def setup(self):
        self.out = StringIO()
        self.err = StringIO()
        self.observer = SimpleFileObserver(self.out, self.err)
        log.addObserver(self.observer.emit)

    def teardown(self):
        log.removeObserver(self.observer.emit)

    def test_out(self):
        log.msg('hello')
        assert read(self.out) == 'hello\n'

    def test_err(self):
        log.err('hello')
        assert read(self.err) == "'hello'\n"

    def test_failure(self):
        log.err(failure())
        msg = read(self.err).strip()
        assert msg.startswith('Unhandled Error')
        assert msg.endswith('exceptions.ZeroDivisionError: integer division or modulo by zero')

    def test_with_failure_and_context(self):
        log.err(failure(), 'Woops!')
        msg = read(self.err).strip()
        assert msg.startswith('Woops!')
        assert msg.endswith('exceptions.ZeroDivisionError: integer division or modulo by zero')



class TestKeyValueFileObserver(object):
    def setup(self):
        self.out = StringIO()
        self.err = StringIO()
        self.observer = KeyValueFileObserver(self.out, self.err)
        log.addObserver(self.observer.emit)

    def teardown(self):
        log.removeObserver(self.observer.emit)

    def test_out(self):
        log.msg('hello')
        assert read(self.out) == 'level="info" msg="hello"\n'

    def test_kwargs(self):
        log.msg('hello', myvar='myvalue')
        assert read(self.out) == 'level="info" msg="hello" myvar="myvalue"\n'

    def test_ignores_complex_types(self):
        log.msg('hello', mydict={}, mylist=[])
        assert read(self.out) == 'level="info" msg="hello"\n'

    def test_escapes_strings(self):
        log.msg('hello', data='the "green" fox')
        assert read(self.out) == 'level="info" msg="hello" data="the \\"green\\" fox"\n'

    def test_err(self):
        log.err('hello')
        assert read(self.err) == '''level="error" msg="'hello'" why=null\n'''

    def test_failure(self):
        log.err(failure())
        assert read(self.err) == 'level="error" msg="exceptions.ZeroDivisionError: integer division or modulo by zero" exc_type="exceptions.ZeroDivisionError" exc_value="integer division or modulo by zero" why=null\n'

    def test_with_failure_and_context(self):
        log.err(failure(), 'Woops!')
        assert read(self.err) == 'level="error" msg="exceptions.ZeroDivisionError: integer division or modulo by zero" exc_type="exceptions.ZeroDivisionError" exc_value="integer division or modulo by zero" why="Woops!"\n'

    def test_error_while_formatting(self):
        with patch.object(self.observer, 'format_kv', side_effect=ValueError):
            log.msg('hello')
        assert read(self.err) == 'Parse error: ValueError(). Original message: hello\n'



def read(fobj):
    fobj.reset()
    return fobj.read()


def failure():
    try:
        1/0
    except:
        return Failure()


def err(*args, **kwargs):
    with patch('twisted.python.log.msg', log.msg):
        logerr(*args, **kwargs)
