from textual.widgets import Header, Footer, Label, TextArea, Input, Select, Button
from textual.app import ComposeResult
from textual.screen import Screen
from threading import Thread
from textual import on
from api import *

class WriteScreen(Screen):
    CSS = """
        Screen {
            layout: grid;
        }
        Button {
            align: right bottom;
        }
        """

    def __init__(self, api:API):
        self.api = api
        super().__init__()

    def send_mail(self, author, destination, subject, body):
        self.notify("Sending...")
        try:
            addresses = self.api.list_addresses()
            av = ""
            dv = destination.value
            sv = subject.value
            bv = body.text

            for address in addresses:
                if address[0] == author.value:
                    av == address[2]

            if av == Select.BLANK or dv == "" or sv == "" or bv == "":
                self.notify(message="One or more input is empty", title="Error")
                return
            
            if av == dv:
                self.notify(title="Error", message="You can't send a mail to yourself")
                return

            resp = self.api.send(
                av,
                dv,
                sv,
                bv
            )
            if resp.get("error", True) == False:
                self.notify("Successfully send your mail!")
            else:
                self.notify(message=resp.get("message", "unknown error"), title="Error")
        except Exception as e:
            self.notify(title="Error", message=str(e))

    @on(Button.Pressed, "#send-btn")
    def send_message(self):
        author = self.screen.get_widget_by_id("from-input", Select)
        destination = self.screen.get_widget_by_id("to-input", Input)
        subject = self.screen.get_widget_by_id("subject-input", Input)
        body = self.screen.get_widget_by_id("body-input", TextArea)

        thread = Thread(target=self.send_mail, args=(author, destination, subject, body,))
        thread.start()
        thread.join()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"From: ")

        addresses = []

        for address in self.api.list_addresses():
            addresses.append([address[2], address[0]])

        yield Select(addresses, id="from-input")

        yield Label(f"To: ")
        yield Input("", id="to-input")

        yield Label(f"Subject: ")
        yield Input("", id="subject-input")

        yield Label("")
        yield Label("Body")
        yield TextArea(id="body-input")

        yield Button("Send", id="send-btn")
        yield Footer(show_command_palette=False)
    
    def on_mount(self) -> None:
        pass