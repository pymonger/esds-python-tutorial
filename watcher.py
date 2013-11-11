#!/usr/bin/env python
import os, re, logging, pyinotify
from kombu import Connection, Exchange, Queue
from tornado.ioloop import IOLoop
from utils import ensure_dir

log_fmt = "[%(asctime)s %(name)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_fmt)
logger = logging.getLogger('watcher')
logger.setLevel(logging.DEBUG)

SIGNAL_RE = re.compile(r'^(.+)\.done$')

class StagedDataHandler(pyinotify.ProcessEvent):
    """Handle events on staging directory."""

    def handle(self, event):
        """Handle events."""

        # get event type
        mask = pyinotify.EventsCodes.maskname(event.mask)

        logger.info("got %s event for path %s" % (mask, event.pathname))

        # filter for signal files
        match = SIGNAL_RE.search(event.pathname)
        if not match: return

        # extract data file
        data_file = match.group(1)
          
        # enqueue job to rabbitmq
        with Connection('amqp://guest:guest@localhost:5672/%2F') as conn:
            conn.ensure_connection()
            exchange = Exchange('data_staged', type='direct')
            queue = Queue('data_staged', exchange, routing_key='data_staged')
            with conn.Producer() as producer:
                publish = conn.ensure(producer, producer.publish, max_retries=3)
                publish(data_file, routing_key='data_staged', declare=[queue])
                logger.info("Queued %s." % data_file)
                os.unlink(event.pathname)

    def process_IN_CREATE(self, event): self.handle(event)

    def process_IN_MOVED_TO(self, event): self.handle(event)

def watch(stage_dir):
    """Watch for raw data signal files and dispatch for processing."""

    # create handler
    ensure_dir(stage_dir)
    sdh = StagedDataHandler()

    # create manager
    wm = pyinotify.WatchManager()
    ioloop = IOLoop.instance() 

    # watch certain events
    mask = pyinotify.IN_MOVED_TO | pyinotify.IN_CREATE
    notifier = pyinotify.TornadoAsyncNotifier(wm, ioloop, None, sdh)
    wdd = wm.add_watch(stage_dir, mask, rec=True, auto_add=True)

    logger.info("Starting watcher.")

    # start ioloop
    ioloop.start()
    ioloop.close()
    notifier.stop()


if __name__ == "__main__":
    watch("/data/public/staging")
