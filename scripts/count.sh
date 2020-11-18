#!/bin/bash
. ./config.sh
file=count.sql
echo "Copying $file to $container_name"
docker cp $file $container_name:$file
docker exec $container_name /bin/sh -c "mysql -u$user_name -p$password -h db $database < $file"
