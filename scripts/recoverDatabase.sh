#! /bin/bash
. ./config.sh

docker cp drop_db.sql $container_name:drop_db.sql
docker cp create_db.sql $container_name:create_db.sql
docker cp db_backup.sql $container_name:db_backup.sql
docker exec $container_name /bin/sh -c "mysql -u$user_name -p$password < drop_db.sql"
docker exec $container_name /bin/sh -c "mysql -u$user_name -p$password < create_db.sql"
docker exec $container_name /bin/sh -c "mysql -u$user_name -p$password -h db $database < db_backup.sql"
