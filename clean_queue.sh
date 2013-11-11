#!/bin/bash

curl -i -u guest:guest -H "content-type:application/json" -XDELETE "http://localhost:15672/api/queues/%2f/$1"
