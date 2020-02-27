#! /bin/bash

. ./config.sh

echo "USE $database;" > $backup_file
docker exec $container_name mysqldump -u$user_name -p$password -h db "$database" >> $backup_file
