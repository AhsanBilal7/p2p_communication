from src import RSA_utils
from src.cryp import CipherClass
from src.message import MessageClass
from src.network import NetworkClass
from src.logging import logger
from src.fun_introduction import introduce
class PersonClass:
    """Represents an endpoint (honest or malicious) in the network."""

    def __init__(self, name: str, is_bad_man: bool = False):
        """Generate an RSA key-pair and initialize local key cache."""
        self.name = name
        self.is_bad_man = is_bad_man
        self.__private_key, self.public_key = RSA_utils.generate_RSA_key_pairs()
        self.secure_partners = {}  # {partner_name: CipherClass}

    @introduce
    def exchange_key_with(self, other_person, sym_key: str, network: NetworkClass):
        """Securely send *sym_key* to *other_person* using RSA encryption."""
        logger.info(
            "[%s] Exchanging AES key with %s via %s.",
            self.name,
            other_person.name,
            network,
        )
        encrypted_key = RSA_utils.encrypt_text(sym_key, other_person.public_key)
        msg = MessageClass(encrypted_key, self, other_person, is_encrypted=True)
        network.send_symmetric_key(msg)
        self.secure_partners[other_person.name] = CipherClass(sym_key)

    @introduce
    def rsa_encrypted_key(self, message):
        """Handle an incoming RSA-encrypted AES key."""
        if message.to_person != self:
            logger.warning("[%s] Received a key not intended for me.", self.name)
            return

        sender_name = message.sender.name
        key = RSA_utils.decrypt_text(message.data, self.__private_key)
        self.secure_partners[sender_name] = CipherClass(key)
        logger.info(
            "[%s] Stored new AES key for secure chat with %s.", self.name, sender_name
        )

    @introduce
    def receive_message(self, message):
        """Process an incoming plaintext or AES-encrypted message."""
        if message.to_person != self:
            if not self.is_bad_man:
                logger.debug("[%s] Ignored message for another recipient.", self.name)
                return
            logger.info("[%s] Attempting to intercept foreign traffic.", self.name)

        if message.is_encrypted:
            cipher = self.secure_partners.get(message.sender.name)
            if cipher:
                plaintext = cipher.decrypt(message.data)
                logger.info(
                    "[%s] Decrypted message from %s: %s",
                    self.name,
                    message.sender.name,
                    plaintext,
                )
            else:
                logger.warning(
                    "[%s] Encrypted message from %s could not be decrypted "
                    "(missing key).",
                    self.name,
                    message.sender.name,
                )
        else:
            logger.info(
                "[%s] Plaintext message from %s: %s",
                self.name,
                message.sender.name,
                message.data,
            )

    @introduce
    def send_message(self, to_person, plain_text: str, network: NetworkClass):
        """Send *plain_text* to *to_person*, encrypting if a shared AES key exists."""
        cipher = self.secure_partners.get(to_person.name)
        data, is_encrypted = (
            (cipher.encrypt(plain_text), True) if cipher else (plain_text, False)
        )
        msg = MessageClass(data, self, to_person, is_encrypted=is_encrypted)
        logger.info("[%s] Sending message to %s via %s.", self.name, to_person, network)
        network.send_message(msg)

    def __str__(self):
        return self.name