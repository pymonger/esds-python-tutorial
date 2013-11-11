#!/usr/bin/env python
import os, re, logging, pyinotify, json, shutil
from kombu import Connection, Exchange, Queue
from kombu.common import eventloop
import numpy as N
from pyhdf.SD import SD
from pyes import ES

from utils import ensure_dir, get_logger


logger = get_logger('worker')


def callback(body, message):
    """Do actual work."""

    logger.info("body in callback() is %s" % body)

    # pull lat/lon, time
    path = body
    sd = SD(path)
    lat = N.array(sd.select('Latitude').get())
    lon = N.array(sd.select('Longitude').get())
    t = N.array(sd.select('Time').get())
    sd.end()
    #logger.info("lat: %s" % str(lat.shape))
    #logger.info("lon: %s" % str(lon.shape))
    #logger.info("time: %s" % str(t.shape))

    # build metadata json
    id = os.path.basename(path)
    md = {
        "id": id,
        "dataset": "AIRX2RET",
        "starttime": t[0,0],
        "endtime": t[44,29],
        "location": {
            "coordinates": [[
                [ lon[0,0], lat[0,0] ],
                [ lon[0,29], lat[0,29] ],
                [ lon[44,29], lat[44,29] ],
                [ lon[44,0], lat[44,0] ],
                [ lon[0,0], lat[0,0] ],
            ]], 
            "type": "polygon"
        }, 
        "urls": "http://mozart/data/public/products/%s" % id
    }

    # publish
    pub_dir = '/data/public/products'
    ensure_dir(pub_dir)
    shutil.move(path, os.path.join(pub_dir, id))

    # insert into ElasticSearch
    index = doctype = 'airs'
    conn = ES('http://localhost:9200')
    mapping = json.load(open('grq_mapping.json'))
    if not conn.indices.exists_index(index):
        conn.indices.create_index(index, mapping)
    conn.indices.put_mapping(doctype, mapping, index)
    ret = conn.index(md, index, doctype, md['id'])

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
    

if __name__ == "__main__": consume()    
