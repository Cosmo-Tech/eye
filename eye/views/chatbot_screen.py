from textual.screen import Screen
from textual.widgets import Input, Markdown, Header, Footer
from textual.containers import Container
from textual import on, work
from ollama import AsyncClient
from textual.worker import get_current_worker
import logging

logger = logging.getLogger(__name__)

class ChatBotScreen(Screen):
    """Chat interface screen"""

    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.client = AsyncClient()
        self.chat_history = ""

    def compose(self):
        container = Container(
            Header(),
            Input(id="user-input", placeholder="Type your message..."),
            Markdown(id="chat-container"),
            Footer()
        )
        container.can_focus = True
        yield container

    @on(Input.Submitted)
    async def on_input(self, event: Input.Submitted):
        # Get input text and clear field
        user_text = event.value
        input_widget = self.query_one("#user-input")
        input_widget.value = ""

        # Update chat history with user message
        self.chat_history += f"\n\n**You:** {user_text}"
        chat_widget = self.query_one("#chat-container")
        chat_widget.update(self.chat_history)

        # Send prompt to AI
        self.send_prompt(user_text)

    @work(thread=True)
    def send_prompt(self, prompt):
        worker = get_current_worker()
        chat_widget = self.query_one("#chat-container")
        
        # Update chat history with AI response header
        self.chat_history += "\n\n**ChatBot:** "
        chat_widget.update(self.chat_history)

        # Stream response from model
        response_text = ""
        for response in self.client.chat(model="smollm", stream=True, messages=[{"role": "user", "content": prompt}]):
            if worker.is_cancelled:
                break
            logger.debug(response)
            chunk = response.get("message", {}).get("content", "")
            logger.debug(chunk)
            response_text += chunk

            # Update chat history with new content
            self.chat_history = self.chat_history.rsplit("**Chatbot:** ", 1)[0] + "**Chatbot:** " + response_text
            chat_widget.update(self.chat_history)