from textual.widgets import Header, Footer, Input, RichLog
from textual.containers import Container
from textual.app import ComposeResult
from textual.screen import Screen
from api import API

class CommandScreen(Screen):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1 2;
        grid-rows: 1fr auto;
        background: $surface;
    }
    
    Log {
        height: 100%;
        border: solid $accent;
        padding: 1 2;
    }
    
    .console {
        height: auto;
        margin: 1 0;
        padding: 0 2;
    }
    
    Input {
        margin: 0 2 1 2;
        width: 100%;
    }
    """

    def __init__(self, api:API):
        self.api = api
        super().__init__()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield RichLog(highlight=True, markup=True)
        yield Container(
            Input(placeholder="Type a command..."),
            classes="console"
        )

        yield Container()

        yield Footer(show_command_palette=False)
    
    def on_mount(self) -> None:
        """Event handler called when app is mounted."""
        self.query_one(Input).focus()
        self.log_message("[bold]Welcome to MOTH!")
        self.log_message("Type 'help' for available commands.")
    
    def log_message(self, message: str) -> None:
        """Write a message to the log with a newline."""
        self.query_one(RichLog).write(message)
    
    def process_command(self, input:str):
        command = input.split(" ")[0].lower()
        args = input.split(" ")[1:]
        
        if command == "help":
            self.log_message("[yellow]Available commands:[/yellow]")
            self.log_message("  help - Show this help message")
            self.log_message("  clear - Clear the console")
            self.log_message("  register - Register an email")
            self.log_message("  addresses - List user's emails")
            self.log_message("  unregister - Unregister an email")
            self.log_message("  quit - Exit the application")
        elif command == "clear":
            self.action_clear_log()
        elif command == "quit":
            self.app.exit()
        elif command == "register":
            if len(args) != 1:
                self.log_message(f"[red]Expected 1 argument, got {len(args)}[/red]")
                return
            
            resp = self.api.register_mail(args[0])
            if resp.get("error") == False:
                self.log_message(f"[green]Successfully claimed {args[0]}[/green]")
            else:
                self.log_message(f"[red]Unable to register {args[0]}[/red]")
                self.log_message(f'[red]Error message: {resp.get("message", "unknown error")}[/red]')
        elif command == "addresses":
            addresses = self.api.list_addresses()
            if len(addresses) == 0:
                self.log_message("You don't have any addresses")
            for address in addresses:
                self.log_message(f"[{address[0]}] {address[2]}")
        elif command == "unregister":
            if len(args) != 1:
                self.log_message(f"[red]Expected 1 argument, got {len(args)}[/red]")
                return
            
            resp = self.api.unregister_mail(args[0])
            if resp.get("error"):
                self.log_message(f"[red]Unable to unregister mail[/red]")
                self.log_message(f"[red]Error message: {resp.get('message', 'unknown error')}[/red]")
        else:
            self.log_message(f"[red]Unknown command: {command}[/red]")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Event handler called when user submits input."""
        command = event.value.strip()
        if not command: return
        
        # Display the command in the log
        self.log_message(f"> [cyan]{command}[/cyan]")
        self.process_command(command)
        self.query_one(Input).value = ""
    
    def action_clear_log(self) -> None:
        self.query_one(RichLog).clear()
        self.log_message("Console cleared.")