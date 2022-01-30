[![Django CI](https://github.com/KNehe/swimmy/actions/workflows/django.yml/badge.svg)](https://github.com/KNehe/swimmy/actions/workflows/django.yml)

## SWIMMY API

- A Django API for a swimming pool manager to help manage their pools and expose resources to client apps.

## Setting up

- Clone this repository ```git clone https://github.com/KNehe/swimmy.git```.
- Create a `.env` file in the project's root directory and add the following variables.

```
DEBUG=
SECRET_KEY=
```

- The following variables are required to upload a swimming pool's image and thumbnail to [AWS S3](https://aws.amazon.com/s3/)
```
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_FILE_OVERWRITE=
AWS_QUERYSTRING_AUTH=
AWS_S3_SIGNATURE_VERSION=
AWS_S3_REGION_NAME=
```
- The variables below are used to send emails to users using [Sendgrid](https://sendgrid.com/)
```
FRONTEND_URL= e.g FRONTEND_URL=https://yourdomain.com/users/reset_password_confirm
FROM_EMAIL=
SENDGRID_API_KEY=
EMAIL_HOST=smtp.sendgrid.net
EMAIL_USE_TLS=
EMAIL_PORT=
```
- The variables below are used by PostgreSQL
```
DB_NAME_DEV=
DB_USERNAME=
DB_USER_PASSWORD=
DB_HOST=
DB_PORT=
```
- Add all your client app origins
```
CORS_ALLOWED_ORIGINS= e.g CORS_ALLOWED_ORIGINS=http://localhost:3000,http://yourdomain.com
```
- Create a [virtual environment](https://docs.python.org/3/library/venv.html) and activate it
- Run `pip install -r requirements.txt`
- Run `python manage.py runserver`

## Documentation
- Read the docs at `http://127.0.0.1:8000/api/v1/swagger/`
or
- `http://127.0.0.1:8000/api/v1/redoc/`

## Features

- JWT authentication(access and refresh tokens), register user.
- JWT verification
- Authorization (staff, users, object owners)
- Create and manage pools
- Book a pool, update, remove a booking
- View recent user's recent bookings
- Rate a pool, update, remove a rating
- View all user's ratings
- Pagination
- Pool image upload to AWS S3
- Password reset request and confirmation
- Swagger and Redoc documentation

***NOTE***: Payments for a booking are made on the frontend through a Payment Gateway like [PayPal](https://developer.paypal.com/).On success, the required payload is sent to the appropiate API endpoint.