import requests

class API:
    class URLs: 
        LOAD_MAIL="/api/load_mail"
        CREATE_USER="/api/create_user"
        LOAD_MAILS="/api/load_mails"
        LOGIN="/api/login"
        CLAIM="/api/claim"
        MARKASREAD="/api/markasread"
        UNCLAIM="/api/unclaim"
        SEND="/api/send"
        LOGOUT="/api/logout"
        LIST_ADDRESSES="/api/addresses"

    def __init__(self, host):
        self.HEADERS = {"Content-Type": "application/json"}
        self.host = host

    def register_mail(self, mail):
        r = requests.post(self.host+self.URLs.CLAIM, json={"address": mail}, headers=self.HEADERS)
        return r.json()
    
    def unregister_mail(self, mail):
        r = requests.post(self.host+self.URLs.UNCLAIM, json={"address": mail}, headers=self.HEADERS)
        return r.json()

    def send(self, author, destination, subject, body):
        data = {
            "author": author,
            "destination": destination,
            "subject": subject,
            "body": body
        }
        r = requests.post(self.host+self.URLs.SEND, headers=self.HEADERS, json=data)
        return r.json()


    def login(self, username, password):
        r = requests.post(self.host+self.URLs.LOGIN, headers=self.HEADERS, json={"username": username,"password": password})

        jwtoken = r.cookies.get("access_token_cookie")
        csrf = r.cookies.get("csrf_access_token")

        if jwtoken is not None:
            self.HEADERS['Authorization'] = f"Bearer {jwtoken}"
        
        if csrf is not None:
            self.HEADERS['X-CSRF-TOKEN'] = csrf

        return r.json()

    def list_addresses(self):
        return requests.get(self.host+self.URLs.LIST_ADDRESSES, headers=self.HEADERS).json()

    def load_mails(self, mailtype:str, limit:int=20, offset:int=0):
        data = {
            "type": mailtype,
            "limit": limit,
            "offset": offset
        }
        r = requests.post(self.host+self.URLs.LOAD_MAILS, headers=self.HEADERS, json=data)
        return r.json()
    
    def load_mail(self, id, mailtype):
        data = {
            "id": id,
            "type": mailtype
        }
        r = requests.post(self.host+self.URLs.LOAD_MAIL, headers=self.HEADERS, json=data)
        return r.json()
    
    def mark_as_read(self, id):
        r = requests.post(self.host+self.URLs.MARKASREAD, json={"id":id}, headers=self.HEADERS)
        return r.json()