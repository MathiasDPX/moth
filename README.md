# MOTH
MOTH stands for **M**ail **O**ver **T**ransport **H**TTP

![Hackatime badge](https://hackatime-badge.hackclub.com/U080HHYN0JD/moth?label=spent)

Basiclly, a mail clone through HTTP(s) that you can install to use with your own domain or borrow someone else domain

### Requirements
- Python 3.11
- Postgresql database


### Installation
1. Run `psql [login arguments] -f database.sql`
2. Configure `.env` with database credentials and secrets
3. Run `server.py` with Flask or any WSGI server like waitress