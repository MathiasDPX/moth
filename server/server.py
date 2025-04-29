from flask_jwt_extended import JWTManager, jwt_required, set_access_cookies, unset_jwt_cookies, create_access_token, get_jwt_identity
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv
from psycopg2.errors import *
from os import getenv
import requests
import database
import dns_resolver
import re

load_dotenv()

app = Flask(__name__)
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_SECRET_KEY"] = getenv("SECRET","supersecret")
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]

jwt = JWTManager(app)

@app.route("/")
def index():
    return "<title>MOTH</title>"

@app.route("/api/load_mail", methods=["POST"])
@jwt_required()
def load_mail():
    data = request.json
    userid = get_jwt_identity()
    mailid = data.get("id")
    mailtype = data.get("type")
    if mailid is None or mailtype is None:
        return {"error": True, "message": "Missing parameters (id[int], type[sent/recv])"}
    
    if mailtype.lower() not in ["sent", "recv"]:
        return {"error": True, "message": "Unknown mail type"}

    if mailtype == "sent":
        mail = database.get_sent_mail(mailid)
    else:
        mail = database.get_recv_mail(mailid)

    addresses = database.get_addresses(userid)

    if mail[2] not in [list(address)[2] for address in list(addresses)]:
        return {"error": True, "message": "401 Forbidden"}
    else:
        return list(mail)

@app.route("/api/addresses", methods=["GET"])
@jwt_required()
def list_addresses():
    userid = get_jwt_identity()
    return database.get_addresses(userid)

@app.route("/api/create_user", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username is None or password is None:
        return {"error": True, "message": "Invalid parameters (username, password)"}

    try:
        id = database.add_user(username, password)
        return {"error": False, "message": "success", "id":id}
    except:
        return {"error": True, "message": "Unable to create user"}

@app.route("/api/load_mails", methods=["POST"])
@jwt_required()
def load_mails():
    userid = get_jwt_identity()
    mailtype = request.json.get("type")
    limit = request.json.get("limit", 50)
    offset = request.json.get("offset", 0)
    if mailtype is None:
        return {"error": True, "message": "Missing parameters (type[sent/recv])"}

    if mailtype.lower() not in ["sent", "recv"]:
        return {"error": True, "message": "Unknown mail type (sent/recv)"}

    return database.get_mails_for_users(userid, mailtype, limit=limit, offset=offset)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = database.login(data.get("username",""), data.get("password",""))
    if user == None:
        return {"error": True, "message":"Invalid username/password"}
    
    response = jsonify({"error": False, "message":"success"})
    access_token = create_access_token(identity=user[0])
    set_access_cookies(response, access_token)

    return response

def send_mail(author, destination, subject, body):
    user, domain = dns_resolver.parse_mail(destination)
    host = dns_resolver.get_host(domain)
    if host is None: return {"error": True, "message": f"Unable to find '{host}' mailserver"}

    send_data = {
        "author": author,
        "destination": destination,
        "subject": subject,
        "body": body
    }

    return requests.post(f"https://{host}/api/recv", json=send_data)

@app.route("/api/recv", methods=["POST"])
def api_recv_mail():
    data = request.json
    try:
        author = data["author"]
        dest = data["destination"]
        subject = data["subject"]
        body = data["body"]
    except:
        return {"error": True, "message": "Missing data (author, destination, subject, body)"}
    
    # TODO: Verify source
    
    try:
        database.recv_mail(author, dest, subject, body)
    except ForeignKeyViolation:
        send_mail("daemon@"+getenv("DOMAIN"), author, "Mail not delivered", f"We've received a mail from you from '{author}' to '{dest}' but we were unable to find the destination address. Please check the address and try again.")
        return {"error": True, "message": "destination not found"}

    return {"error": False, "message": "success"}

@app.route("/api/unclaim", methods=["POST"])
@jwt_required()
def unclaim_mail():
    data = request.json
    userid = get_jwt_identity()
    address = data.get("address")
    if address is None:
        return {"error": True, "message": "Missing parameters (address)"}
    
    count = database.unbind_address(address, userid)
    
    if count == 0:
        return {"error": True, "message": "This email isn't claimed"}
    else:
        return {"error": False, "message": "Email unclaimed"}

@app.route("/api/claim", methods=["POST"])
@jwt_required()
def claim_mail():
    data = request.json
    userid = get_jwt_identity()
    address = data.get("address")
    if address is None:
        return {"error": True, "message": "Missing parameters (address)"}

    if re.match(dns_resolver.ADDRESS_REGEX, address) is None:
        return {"error": True, "message": "Invalid address format"}

    try:
        user, domain = dns_resolver.parse_mail(address)
    except:
        return {"error": True, "message": "Invalid address format"}

    if user == "daemon":
        return {"error": True, "message": f"daemon is lock"}
    
    try:
        database.bind_address(userid, address)
    except UniqueViolation:
        return {"error": True, "message": "Already taken"}
    
    return {"error": False, "message": "success"}

@app.route("/autologin/<int:id>")
def autologin(id:int):
    user = database.get_user(id)
    if user == None:
        return {"error": True, "message":"User not found"}

    response = jsonify({"error": False, "message":"success", "user": database.get_user(id)})
    access_token = create_access_token(identity=user)
    set_access_cookies(response, access_token)

    return response

@app.route("/api/markasread", methods=["POST"])
@jwt_required()
def mark_as_read():
    data = request.json
    userid = get_jwt_identity()
    mailid = data.get("id")

    if mailid is None:
        return {"error": True, "message": "Missing parameters (id)"}

    if database.get_mail_destination_id(mailid) != userid:
        return {"error": True, "message": "401 Forbidden"}

    database.mark_as_read(mailid)
    return {"error": False, "message": "success"}

@app.route("/api/send", methods=["POST"])
@jwt_required()
def api_send_mail():
    data = request.json
    userid = get_jwt_identity()
    try:
        author = data["author"]
        dest = data["destination"]
        subject = data["subject"]
        body = data["body"]
    except:
        return {"error": True, "message": "Missing data (author, destination, subject, body)"}

    if author not in [address[2] for address in database.get_addresses(userid)]:
        return {"error": True, "message": "Can't use this address"}
    
    r = send_mail(author, dest, subject, body)

    if type(r) == dict:
        return r

    if r.status_code == 200:
        return r.json()

    abort(r.status_code)

@app.route("/api/logout", methods=["POST"])
def logout():
    response = jsonify({"error":False, "message": "success"})
    unset_jwt_cookies(response)
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0")