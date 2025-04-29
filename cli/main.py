from textual.app import App, ComposeResult
from screens.loginapp import MothLoginApp
from textual.widgets import Footer
from screens import *
from api import *
import json

class MothApp(App):
    TITLE = "MOTH"

    BINDINGS = [
        ("ctrl+t", "push_screen('commands')", "Terminal"),
        ("ctrl+i", "push_screen('inbox')", "Inbox"),
        ("ctrl+w", "push_screen('writer')", "Send mail")
    ]

    def __init__(self, api):
        self.api = api
        super().__init__()

    def on_mount(self) -> None:
        self.install_screen(CommandScreen(self.api), name="commands")
        self.install_screen(InboxScreen(self.api), name="inbox")
        self.install_screen(WriteScreen(self.api), name="writer")
        self.push_screen("inbox")

    def compose(self) -> ComposeResult:
        yield Footer(show_command_palette=False)

if __name__ == "__main__":
    try:
        data = json.load(open("config.json", "r", encoding="utf-8"))
    except:
        data = {}

    try:
        api = API(data.get("host", "127.0.0.1:5000"))
        resp = api.login(data.get("username"), data.get("password"))
    except:
        resp = {"error": True}

    if resp.get("error", False) == False:
        app = MothApp(api)
        app.run()
    else:
        app = MothLoginApp()
        app.run()
        print("You can restart to login")