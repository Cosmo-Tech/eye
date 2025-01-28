from textual.screen import Screen
from textual.widgets import Input, Markdown, Header, Footer
from textual.containers import Container, VerticalScroll
from textual import on
from ollama import AsyncClient
import logging

logger = logging.getLogger(__name__)

class ChatBotScreen(Screen):
    """Chat interface screen"""

    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        self.client = AsyncClient()
        self.chat_messages = []

    def compose(self):
        container = Container(
            Header(),
            Input(id="user-input", placeholder="Type your message..."),
            VerticalScroll(Markdown(id="chat-container")),
            Footer()
        )
        yield container

    @on(Input.Submitted)
    async def on_input(self, event: Input.Submitted) -> None:
        if event.input.id != "user-input":
            return
            
        try:
            user_message = event.value
            event.input.value = ""
            
            self.chat_messages.append({"role": "user", "content": user_message})
            await self._update_chat()
            
            response = await self.client.chat(
                model="smollm", 
                messages=self.chat_messages
            )
            self.chat_messages.append({
                "role": "assistant", 
                "content": response["message"]["content"]
            })
            await self._update_chat()
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            self.notify("Error processing message", severity="error")

    async def _update_chat(self) -> None:
        chat_text = "\n\n".join(
            f"**{m['role']}**: {m['content']}" 
            for m in self.chat_messages
        )
        await self.query_one("#chat-container").update(chat_text) 