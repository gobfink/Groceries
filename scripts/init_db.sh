sudo docker exec groceries_flask_1 flask db init
sudo docker exec groceries_flask_1 flask db migrate
sudo docker exec groceries_flask_1 flask db upgrade
