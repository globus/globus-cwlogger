from collections import namedtuple
from time import sleep
import multiprocessing
import logging
import sys

import pytest

from globus_cw_daemon import daemon as cw_daemon
from globus_cw_daemon.config import Config
LogWriter = cw_daemon.cwlogs.LogWriter


if sys.version_info[0] < 3:
    import ConfigParser as configparser
    from StringIO import StringIO
    import mock
else:
    import configparser
    from io import StringIO
    from unittest import mock


daemon_config = """
[general]

local_log_level = info
heartbeats = False
heartbeat_interval = 2
stream_name = dummy_stream
group_name = dummy_group
"""
testconfig = configparser.ConfigParser()
testconfig.readfp(StringIO(daemon_config))

DaemonFixture = namedtuple("DaemonFixture", 'events')


@mock.patch('globus_cw_daemon.cwlogs.boto', mock.Mock())
def fixture_daemon():
    cw_daemon.main(Config(testconfig))


@pytest.fixture(scope="session")
def _daemon():
    captured_events = multiprocessing.Queue()

    def push_to_queue(self, events):
        for evt in events:
            captured_events.put(evt)

    with mock.patch.object(LogWriter, 'upload_events', push_to_queue):
        proc = multiprocessing.Process(target=fixture_daemon)
        proc.start()
        # Give it a little time to start up before yielding control
        sleep(0.1)
        yield DaemonFixture(captured_events)
        proc.terminate()
        proc.join()


@pytest.fixture
def daemon(_daemon):
    # Clear any leftover events so we start fresh
    # for each test.
    while not _daemon.events.empty():
        _daemon.events.get()
    return _daemon
