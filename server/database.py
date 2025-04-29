from dotenv import load_dotenv
from os import getenv
import psycopg2
import hashlib

load_dotenv()

conn = psycopg2.connect(
    database=getenv("DB_DATABASE", "moth"),
    user=getenv("DB_USERNAME"),
    password=getenv("DB_PASSWORD"),
    host=getenv("DB_HOST", "localhost"),
    port=getenv("DB_PORT", 5342)
)
cur = conn.cursor()
conn.autocommit = True

def hash_password(password):
    if password == None: password=""
    m = hashlib.sha256()
    m.update(bytes(password, encoding="utf-8"))
    return m.hexdigest()

def add_user(username, password):
    hashed_pwd = hash_password(password)
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;", (username, hashed_pwd,))
    return cur.fetchone()

def unbind_address(address, userid):
    cur.execute("DELETE FROM addresses WHERE user_id=%s AND email=%s", (userid, address,))
    return cur.rowcount

def bind_address(userid, email):
    cur.execute("INSERT INTO addresses (user_id, email) VALUES (%s, %s) RETURNING id;", (userid, email))
    return cur.fetchone()

def get_user(userid):
    cur.execute("SELECT * FROM users WHERE id=%s LIMIT 1;", (userid, ))
    return cur.fetchone()

def login(username, password):
    hashed_password = hash_password(password)
    cur.execute("SELECT id FROM users WHERE username=%s AND password=%s LIMIT 1;", (username, hashed_password))
    return cur.fetchone()

def mark_as_read(mailid):
    cur.execute("UPDATE recv_mails SET readed=TRUE WHERE id=%s;", (mailid, ))

def get_mail_destination_id(mailid):
    cur.execute("SELECT destination FROM recv_mails WHERE id=%s LIMIT 1;", (mailid, ))
    cur.execute("SELECT user_id FROM addresses WHERE email=%s LIMIT 1;", (cur.fetchone(), ))
    return cur.fetchone()[0]

def get_addresses(userid):
    cur.execute("SELECT * FROM addresses WHERE user_id=%s;", (userid, ))
    return cur.fetchall()

def get_recv_mail(mailid):
    cur.execute("SELECT * FROM recv_mails WHERE id=%s LIMIT 1", (mailid, ))
    return cur.fetchone()

def get_sent_mail(mailid):
    cur.execute("SELECT * FROM sent_mails WHERE id=%s LIMIT 1", (mailid, ))
    return cur.fetchone()

def recv_mail(author, dest, subject, body):
    cur.execute("INSERT INTO recv_mails (author, destination, subject, body) VALUES (%s, %s, %s, %s) RETURNING id;", (author, dest, subject, body, ))
    return cur.fetchone()

def get_mails_for_users(userid, mailtype ,offset=0, limit=50):
    cur.execute(f"SELECT subject, id, readed FROM {mailtype}_mails WHERE destination IN (SELECT email FROM addresses WHERE addresses.user_id = %s) ORDER BY id DESC LIMIT %s OFFSET %s;", (userid, limit, offset))
    return cur.fetchall()

def get_mails_for_address(address, mailtype ,offset=0, limit=50):
    cur.execute(f"SELECT subject, id FROM {mailtype}_mails WHERE destination == %s LIMIT %s OFFSET %s;", (address, limit, offset))
    return cur.fetchall()

def send_mail(author, dest, subject, body):
    cur.execute("INSERT INTO sent_mails (author, destination, subject, body) VALUES (%s, %s, %s, %s) RETURNING id;", (author, dest, subject, body, ))
    return cur.fetchone()

if __name__ == "__main__":
    id = add_user("mathias", "joedalton")
    eid = bind_address(id, "mathias@mathiasd.fr")