FROM python:3.11

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIPENV_VENV_IN_PROJECT 1

# Set up working directory
WORKDIR /usr/src/app

# Install Pipenv
RUN pip install --upgrade pip && pip install pipenv
COPY Pipfile Pipfile.lock ./

# Install dependencies
COPY Pipfile Pipfile.lock /usr/src/app/
RUN pipenv install --system --deploy --ignore-pipfile


# Copy the rest of the code
COPY . /usr/src/app

# Expose the port
EXPOSE 8000

# Before running the application, apply migrations
RUN python manage.py migrate

# Populate the database with some sample data
RUN python populate_db.py

# Run the application
CMD ["pipenv", "run", "uvicorn", "letschatbackend.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
