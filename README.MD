# Lets Chat Backend
- This is the backend of a simple game that allow players to answer fun questions on lobbies. 
- The backend is built with Django and uses Redis as a message broker.
- The frontend is built with React and uses Vite as a bundler.

## Installation
1. After cloning the repository it is recommended to create a virtual environment and install the dependencies. Here is an example on how to do it:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory of the project and add the following environment variables (This is not required for a development environment, but is is recommended for hosting the backend):

```bash
SECRET_KEY=<your_secret_key>
SERVER_IP=<your_server_ip>
```

3. Create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser:

```bash
python manage.py createsuperuser
```

5. Run the following command to start the backend server:

```bash
uvicorn lobbies.asgi:application --host 0.0.0.0 --port 8000
```

6. Alternatively, you can use the provided 'docker-compose.yml' file to start the backend server using Docker:

```bash
docker-compose up -d
```

## Populate the Database
The backend uses a SQLite database to store the data. To populate the database with some sample data you can use the provided 'populate_db.py' script. The script will read the 'questions.csv' file and create questions and answers in the database. An example file is provided in the same directory. But feel free to modify it to your liking.

To run the script, open a terminal and navigate to the root directory of the project. Then run the following command:

```bash
python populate_db.py
```

This will create questions and answers in the database. You can then use the provided 'populate_db.py' script to populate the database with your own questions and answers.