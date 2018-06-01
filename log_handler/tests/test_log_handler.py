from __future__ import unicode_literals

import json
from time import sleep
import logging
from globus.cwlogger import cloudwatch_handler, GlobusSocketHandler

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(cloudwatch_handler)


def _get_events(queue):
    # Give the daemon flush thread time to catch up.
    sleep(1)
    events = []
    while not queue.empty():
        events.append(queue.get())
    # Ordering is not guaranteed, sort by timestamp
    events.sort(key=lambda evt: evt.timestamp)
    return events


def test_sending_string_events(daemon):
    log.error("Test error.")
    log.info("Test info.")
    log.warn("Test warn.")
    log.debug("Test debug.")
    events = _get_events(daemon.events)
    assert len(events) == 4
    assert events[0].unicode_message == 'Test error.'
    assert events[1].unicode_message == 'Test info.'
    assert events[2].unicode_message == 'Test warn.'
    assert events[3].unicode_message == 'Test debug.'


def test_sending_json_events(daemon):
    err = {'message': 'Test error.', 'id': 33, 'method': 'POST'}
    log.error(json.dumps(err))
    info = {'message': 'Ok', 'id': 12, 'method': 'GET'}
    log.info(json.dumps(info))
    events = _get_events(daemon.events)
    assert len(events) == 2
    assert json.loads(events[0].unicode_message) == err
    assert json.loads(events[1].unicode_message) == info


def test_sending_traceback(daemon):
    try:
        5 / 0
    except ZeroDivisionError as exc:
        log.exception(exc)
    events = _get_events(daemon.events)
    assert len(events) == 1
    assert len(events[0].unicode_message.splitlines()) == 5
