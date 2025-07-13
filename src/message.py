
class MessageClass:
    """Lightweight container for data transferred across the network."""

    def __init__(self, data, sender, to_person, is_encrypted: bool = False):
        self.sender = sender
        self.to_person = to_person
        self.data = data
        self.is_encrypted = is_encrypted

    def __str__(self):
        return "\n".join(f"- {k} = {v}" for k, v in self.__dict__.items())
