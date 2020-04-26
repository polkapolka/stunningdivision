# stunningdivision

## Startup

### Migrate
Run `docker-compose run app python manage.py migrate` to setup the database.

### Startup
Run `docker-compose up` to start the services.
The Django app will be available at `localhost:8000`.
`ngrok` will expose the app at a public url.
Hit `localhost:4040` to find the url.
