from textual.screen import Screen
from textual.widgets import Input, Markdown, Header, Footer
from textual.containers import Container, VerticalScroll
from textual import on, work
import logging
import os
from ..llm import ChatAPI

logger = logging.getLogger(__name__)


class ChatBotScreen(Screen):
    """Chat interface screen"""

    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        api_key = os.getenv("OPEN_ROUTER_KEY")
        if not api_key:
            logger.warning(ValueError("OPEN_ROUTER_KEY environment variable not set"))
        chat_api = ChatAPI(api_key)
        self.chat_api = chat_api

    def compose(self):
        container = Container(
            Header(),
            Input(id="user-input", placeholder="Type your message..."),
            VerticalScroll(Markdown(id="chat-container"), id="answerbox"),
            Footer(),
        )
        yield container

    @on(Input.Submitted)
    def handle_input(self, event: Input.Submitted) -> None:
        """Handle user input submission"""
        input_widget = self.query_one("#user-input", Input)
        user_message = input_widget.value
        input_widget.value = ""

        self.update_chat_display()

        # Start async processing
        self.get_bot_response(user_message)

    @work
    async def get_bot_response(self, message: str) -> None:
        """Worker to get bot response asynchronously"""
        try:
            response = await self.chat_api.send_message(message)
            self.update_chat_display()
        except Exception as e:
            logger.error(f"Error getting bot response: {e}")
            self.update_chat_display()

    def update_chat_display(self) -> None:
        """Update the markdown display with the conversation"""
        chat_container = self.query_one("#chat-container", Markdown)
        chat_container.update(self.chat_api.get_chat_history_markup())
