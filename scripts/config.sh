#! /bin/bash
. ./config.sh.local
export container_name=groceries_db_1
export user_name=root
export database=groceries
export backup_file=db_backup.sql
export flask_container=groceries_flask_1

if [ -z "$password" ]
then  
  read -p "Enter database password: " -s password
  export password
fi  
