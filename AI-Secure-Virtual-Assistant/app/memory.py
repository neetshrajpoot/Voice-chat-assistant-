class ConversationMemory:
    def __init__(self, max_messages=10):
        self.messages = []
        self.max_messages = max_messages

    def add_message(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })

        # Keep only the latest messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_messages(self):
        return self.messages

    def clear(self):
        self.messages = []


memory = ConversationMemory()