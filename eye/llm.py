from typing import List, Dict
import os
import aiohttp
import logging

logger = logging.getLogger(__name__)
class ChatAPI:
    def __init__(self, api_key: str):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.chat_history: List[Dict[str, str]] = []

    async def send_message(self, message_content: str) -> str:
        # Add user message to history
        logger.info(f"Sending message {message_content}")
        self.chat_history.append({"role": "user", "content": message_content})
        
        payload = {
            "messages": self.chat_history
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url, 
                    headers=self.headers,
                    json=payload
                ) as response:
                    result = await response.json()
                    assistant_message = result['choices'][0]['message']['content']
                    
                    # Add assistant response to history
                    self.chat_history.append({"role": "assistant", "content": assistant_message})
                    return assistant_message
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")

    def get_chat_history(self) -> List[Dict[str, str]]:
        return self.chat_history

    def get_chat_history_markup(self) -> str:
        """Convert chat history to markdown formatted text."""
        markup = []
        for msg in self.chat_history:
            role = msg["role"]
            content = msg["content"]
            markup.append(f"**{role}**:\n{content}\n")
        return "\n".join(markup)

def main():
    chat = ChatAPI(os.getenv('OPEN_ROUTER_KEY'))
    response = chat.send_prompt("What is the answer to life the universe and everything?")
    print("Response:", response)
    print("\nChat history:", chat.get_chat_history())

if __name__ == "__main__":
    main()