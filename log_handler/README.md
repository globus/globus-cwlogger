# Globus CWLogger - Log Handler

What is this?

This a customized version of the Python [`logging.handlers.SocketHandler`](https://docs.python.org/3/library/logging.handlers.html#sockethandler)
designed to send log records to the Globus CWLogger daemon for forwarding to Amazon CloudWatch.

## Setup

Install from Github:

`pip install git+ssh://git@github.com/globus/globus-cwlogger.git@loghandler#egg=globus_cw_loghandler&subdirectory=log_handler`

If the application using this log handler lives under a `globus.` package namespace, you will need to include following snippet
in your `globus/__init__.py` so the two packages can co-exist under `globus`.


```python
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
```

[Refer to Python docs for more details.](https://docs.python.org/3/library/pkgutil.html#pkgutil.extend_path)

## Usage

For simple situations, this package includes a pre-configured instance you can just attach directly to a logger:

```python
import logging

from globus.cwlogger import cloudwatch_handler

log = logging.getLogger()
log.addHandler(cloudwatch_handler)

# This record will get sent to the CWLogger daemon.
log.error("Something bad happened!")
```

In a more complex setup, it might be desirable to specify your logging in a JSON or a YAML config file and generate [a configuration dictionary.](https://docs.python.org/3/library/logging.config.html#logging-config-api)

For example, something like:

```yaml
version: 1
formatters:
  myjson:
    format: '{"time": "%(asctime)s", "logger_name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: simple
    stream: ext://sys.stdout
  cloudwatch:
    class: globus.cwlogger.GlobusSocketHandler
    formatter: myjson
    host: '\0org.globus.cwlogs'
loggers:
  auditLogger:
    level: INFO
    handlers: [cloudwatch]
    propagate: no
root:
  level: WARNING
  handlers: [console, cloudwatch]


```

The important parameters here are the `class` and `host` that specifies a socket address where the CWLogger Daemon is listening.

See the [Python Logging HOWTO for more information.](https://docs.python.org/3/howto/logging.html)
