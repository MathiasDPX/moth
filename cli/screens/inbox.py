from textual.widgets import Header, Footer, ListView, ListItem, Label, Button
from textual.app import ComposeResult
from screens.mail import MailScreen
from textual.screen import Screen
from textual.events import Key
from textual import on
from api import *
import re


class InboxScreen(Screen):
    CSS = """
        Button {
            align: right bottom;
        }
        
        ListView {
            background: transparent;
        }
        
        #keybinds {
            background: #242F38;
            width: 100%;
        }

        ListView:focus-within {
            background: transparent;
        }
        """
    
    def __init__(self, api:API):        
        self.api = api
        self.page = 0
        super().__init__()

    @on(ListView.Selected)
    def on_item_selected(self, event: ListView.Selected) -> None:
        if "mail" in self.app.SCREENS.keys():
            del self.app.SCREENS["mail"]

        text = event.item.children[0].renderable
        mailid = re.match(r"(!| ) \((\d+)\)..+", text).group(2)
        mailscreen = MailScreen(self.api, mailid, "recv")
        self.app.push_screen(mailscreen)

    def on_mount(self) -> None:
        self.list_refresh()

    @on(Button.Pressed, "#refresh-btn")
    def list_refresh(self):
        listview:ListView = self.screen.get_child_by_type(ListView)
        listview.remove_children()

        mails = self.api.load_mails("recv", offset=20*self.page)
        for mail in mails:
            prefix = " "
            if not mail[2]:
                prefix = "!"

            widget = ListItem(Label(f"{prefix} ({mail[1]}) {mail[0]}"), markup=True)
            listview.mount(widget)

    @on(Key)
    def keypress(self, event:Key):
        char = event.character
        if char == "j":
            self.page += 1
        elif char == "k":
            if self.page != 0:
                self.page -= 1

        if char in ["k","j"]:
            self.list_refresh()
            self.notify(f"Switch to page {self.page+1}", timeout=1)


    def compose(self) -> ComposeResult:
        yield Header()
        
        yield ListView(ListItem(Label("Loading...")), id="mail-list")
        yield Button("Refresh", id="refresh-btn")
        
        yield Label(" [#F2A02C]k/j[/#F2A02C] Change page", id="keybinds")

        yield Footer(show_command_palette=False)