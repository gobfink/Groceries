#! /bin/bash
. ./config.sh

drop_cmd="DROP DATABASE $database;"
drop_file=drop_db.sql

create_cmd="CREATE DATABASE $database COLLATE utf8mb4_0900_ai_ci;"
create_file=create_db.sql

backup_file=db_backup.sql

echo "Writing $drop_cmd to $drop_file"
echo $drop_cmd > $drop_file

echo "Writing $create_cmd to $create_file"
echo $create_cmd > $create_file

echo "Copying $drop_file, $create_file, and $backup_file to $container_name"
docker cp $drop_file $container_name:$drop_file
docker cp $create_file $container_name:$create_file
docker cp $backup_file $container_name:$backup_file

echo "Running $drop_file on $container_name"
docker exec $container_name /bin/sh -c "mysql -u$user_name -p$password < $drop_file"

echo "Running $create_file on $container_name"
docker exec $container_name /bin/sh -c "mysql -u$user_name -p$password < $create_file"

echo "Running $backup_file on $container_name"
docker exec $container_name /bin/sh -c "mysql -u$user_name -p$password -h db $database < $backup_file"
