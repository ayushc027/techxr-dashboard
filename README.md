# MySQL Explorer Tool

A Dockerized, secure, web-based MySQL database explorer built with Flask.

## Features
- Login-protected dashboard
- Browse tables and view structure
- View top 100 rows of any table
- Export data to CSV or Excel
- Docker support

## Setup (Without Docker)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Update MySQL credentials in `app.py`.

3. Run the app:
```bash
python app.py
```

## Setup with Docker

1. Build and run the container:
```bash
docker-compose up --build
```

2. Access the app at: `http://localhost:5000`

## Default Login
- Username: `admin`
- Password: `admin123`

## License
MIT License
