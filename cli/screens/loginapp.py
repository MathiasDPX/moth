from textual.widgets import Label, Input, Button
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual import on
from api import *
import requests
import json

class MothLoginApp(App):
    TITLE = "MOTH - Login Page"
    CSS = """
        Screen {
            align: center middle;
        }
        Container {
            border: white;
            align: center middle;
            height: auto;
        }
        Input, Label {
            margin: 0 1;
        }
        .button-container {
            width: 100%;
            height: auto;
        }
        #login-btn, #signup-btn {
            width: 50%;
            margin: 0 1;
        }
        """

    def on_mount(self) -> None:
        try:
            data = json.load(open("config.json", "r", encoding="utf-8"))
        except:
            data = {}
        username = self.screen.get_widget_by_id("username-input", Input)
        host = self.screen.get_widget_by_id("host-input", Input)

        username.value = data.get("username","")
        host.value = data.get("host","")

    @on(Button.Pressed, "#login-btn")
    def login_btn(self):
        username = self.screen.get_widget_by_id("username-input", Input).value
        password = self.screen.get_widget_by_id("password-input", Input).value
        host = self.screen.get_widget_by_id("host-input", Input).value

        api = API("https://"+host)
        resp = api.login(username, password)

        if resp.get("error", False) == True:
            self.notify(resp.get("message"))
            return

        with open("config.json", "w+", encoding="utf-8") as f:
            data = {
                "host": "https://"+host,
                "username": username,
                "password": password
            }
            json.dump(data, f)

        self.app.exit()

    @on(Button.Pressed, "#signup-btn")
    def signup_btn(self):
        username = self.screen.get_widget_by_id("username-input", Input).value
        password = self.screen.get_widget_by_id("password-input", Input).value
        host = self.screen.get_widget_by_id("host-input", Input).value

        data = {"username": username,"password": password}
        resp = requests.post(f"https://{host}/api/create_user", json=data).json()

        if resp.get("error"):
            self.notify(title="Error", message=f"Unable to signup, {resp.get('message', 'unknown error')}", severity="error")
        else:
            self.notify(title="Sucess", message="You can now login")

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Username"),
            Input(placeholder="joe", id="username-input"),
            Label(""),
            Label("Password"),
            Input(id="password-input", password=True),
            Label(""),
            Label("Host"),
            Input(placeholder="mail.example.com", id="host-input"),
            Label(""),
            Horizontal(
                Button("Signup", id="signup-btn"),
                Button("Login", id="login-btn"),
                classes="button-container"
            ),
            name="Login"
        )

if __name__ == "__main__":    
    app = MothLoginApp()
    app.run()