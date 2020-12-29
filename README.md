# Groceries
The goal of this is to scrape different websites grocery prices
It then will calculate things such as price per ounce. 
And then store them over time in a database and allow queries 

# Installation instructions
- Clone the repository
- cd to Groceries
- Run "startcore.sh" to start the core containers
- Create a database called "groceries" in adminer (port 8081)
- Run "scripts/init_db.sh" to run the flask commands to create the structure of the database
- Now you can spin up the various crawlers by starting start scripts in main directory
- You can stop the various crawler scripts using the drop scripts in the main directory 


# Database updates (after the database groceries is initialized) 
Updates the the data structure are performed via changing the models.py class in flask/code/app
Use the helper script -- scripts/update_db.sh -- to upgrade your db using the flask db commands
