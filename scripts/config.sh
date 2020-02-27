#! /bin/bash

export container_name=groceries_db_1
export user_name=root
export database=groceries
export backup_file=db_backup.sql

read -p "Enter database password: " -s password
export password
