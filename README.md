# stunningdivision

## Startup

### Migrate
Run `docker-compose run app python ReachCare/manage.py migrate` to setup the database.
Run `docker-compose run app python ReachCare/manage.py makemigrations` to add new migrations.

### Startup
Run `docker-compose up` to start the services.
The Django app will be available at `localhost:8000`.
`ngrok` will expose the app at a public url.
Hit `localhost:4040` to find the url.

If you get a db connection error. Try starting the db before the rest of the services:
`docker-compose up -d db`. Then wait a few seconds. Then start everything up:
`docker-compose up`

### Tests
Run the tests with: `docker-compose run app python ReachCare/manage.py test core`
