from textual.widgets import Header, Footer, Label, MarkdownViewer
from textual.app import ComposeResult
from textual.screen import Screen
from api import API

class MailScreen(Screen):
    CSS = """"""

    def __init__(self, api:API, mailid, mailtype):
        self.mailid = mailid
        self.api = api
        self.mailtype = mailtype
        self.data = api.load_mail(mailid, mailtype)

        api.mark_as_read(mailid)

        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(f"From: {self.data[1]}")
        yield Label(f"To: {self.data[2]}")
        yield Label(f"Subject: {self.data[3]}")
        yield Label("")
        yield MarkdownViewer(self.data[4], open_links=False)
        yield Footer(show_command_palette=False)
    
    def on_mount(self) -> None:
        pass