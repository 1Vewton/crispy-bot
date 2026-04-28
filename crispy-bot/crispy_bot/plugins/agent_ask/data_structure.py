# Streaming message data model
class StreamingMessage():
    def __init__(self, step: str, done: bool, content: str):
        self.step: str = step
        self.done: bool = done
        self.content: str = content
