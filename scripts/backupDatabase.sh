echo "USE acronym;" > db_backup.sql
docker exec acronymdb_db_1 mysqldump -uroot -pexample -h db 'acronym' >> db_backup.sql
