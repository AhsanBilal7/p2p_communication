"""
~~~~~~~~~~~~~~~~~~~~~~~~
Core networking primitives for the demo P2P secure-messaging project.

Author: Ahsan Bilal, University of Oklahoma
"""

from src.logging import logger
from src.fun_introduction import introduce

class NetworkClass:
    """A deliberately insecure broadcast network.

    Every message (plaintext or key material) is sent to *all* connected users.
    Cryptographic techniques (RSA for key transport, AES for payloads) are
    therefore required to achieve confidentiality over this channel.
    """

    def __init__(self, name: str):
        """Create a new named network."""
        self.name = name
        self.people = []

    @introduce
    def join(self, person):
        """Register *person* to receive future broadcasts."""
        logger.info("[NET %s] %s joined the network.", self.name, person.name)
        self.people.append(person)

    @introduce
    def send_message(self, message):
        """Broadcast an arbitrary *message* object to all participants."""
        logger.info("[NET %s] Broadcasting payload from %s.", self.name, message.sender)
        for person in self.people:
            if person is not message.sender:
                person.receive_message(message)

    @introduce
    def send_symmetric_key(self, message):
        """Broadcast an RSA-encrypted AES key to all participants."""
        logger.info(
            "[NET %s] Broadcasting symmetric key from %s.", self.name, message.sender
        )
        for person in self.people:
            if person is not message.sender:
                person.rsa_encrypted_key(message)

    def __str__(self):
        return self.name





