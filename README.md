simple-observers
================

Observers for use with the Twisted logging framework that only print what you
tell them to. In particular, they ignore timestamps and system. This can be
useful when you want to interop with other logging solutions like syslog, which
can be configured to handle timestamps in a uniform way for all your
applications.

Example usage with `twistd`

```bash

$ twistd --logger simple_observers.SimpleStdoutLogger -n web

```

This will log everything to stdout. If you want to preserve stderr you can use
`simple_observers.SimpleStreamLogger`.
