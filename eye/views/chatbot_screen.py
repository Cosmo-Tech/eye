from textual.screen import Screen
from textual.widgets import Static, Input, Markdown, Header, Footer
from textual.containers import Container, VerticalScroll
from textual import on

class ChatBotScreen(Screen):
    """Chat interface screen"""

    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager


    def compose(self):
        input_widget = Input(placeholder="The answer to life, the university, and everything?", id="user-input")
        input_widget.can_focus = True
        response_widget = Markdown("", id="chat-history")
        yield Header()
        container = Container(
            input_widget,
            VerticalScroll(
                response_widget
            ), id="chat-container"
        )
        yield Footer()
        container.can_focus = True
        yield container

    @on(Input.Submitted)
    def on_input(self, event: Input.Submitted):
        user_message = event.value
        response = "42"
        chat_history = self.query_one("#chat-history", Markdown)
        chat_history.update(f"**User:** {user_message}\n**Bot:** {response}")
        
