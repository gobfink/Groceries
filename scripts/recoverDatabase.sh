docker cp drop_db.sql acronymdb_db_1:drop_db.sql
docker cp create_db.sql acronymdb_db_1:create_db.sql
docker cp db_backup.sql acronymdb_db_1:db_backup.sql
docker exec acronymdb_db_1 /bin/sh -c 'mysql -uroot -pexample < drop_db.sql'
docker exec acronymdb_db_1 /bin/sh -c 'mysql -uroot -pexample < create_db.sql'
docker exec acronymdb_db_1 /bin/sh -c 'mysql -uroot -pexample -h db 'acronym' < db_backup.sql'
