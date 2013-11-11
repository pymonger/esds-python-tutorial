#!/usr/bin/env python
import os, re, logging, pyinotify
from kombu import Connection, Exchange, Queue
from kombu.common import eventloop

from utils import get_logger

logger = get_logger('worker')


def callback(body, message):
    """Do actual work."""

    logger.info("body in callback() is %s" % body)
    message.ack()


def consume():
    """Consume jobs from queue and do work."""

    try:
        with Connection('amqp://guest:guest@localhost:5672/%2F') as conn:
            conn.ensure_connection()
            exchange = Exchange('data_staged', type='direct')
            queue = Queue('data_staged', exchange, routing_key='data_staged')
            channel = conn.channel()
            channel.basic_qos(0, 1, False)
            logger.info("Starting worker.")
            with conn.Consumer(queue, channel, callbacks=[callback]) as consumer:
                for _ in eventloop(conn, timeout=1, ignore_timeouts=True):
                    pass
    except KeyboardInterrupt:
        logger.info("Worker was shut down.")
    

if __name__ == "__main__":
    consume()    
