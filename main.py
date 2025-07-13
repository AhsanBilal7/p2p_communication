
from src.network import NetworkClass
from src.person import PersonClass


def main():
    """Run the secure messaging demonstration."""
    # Create participants
    ahsan = PersonClass(name='Ahsan')
    joe = PersonClass(name='Joe')
    eavesdropper = PersonClass(name='Eavesdropper', is_bad_man=True)

    # Set up an insecure broadcast network
    internet = NetworkClass(name="Internet")
    internet.join(ahsan)
    internet.join(eavesdropper)  # Man-in-the-middle
    internet.join(joe)

    # Simple plaintext message (unencrypted)
    ahsan.send_message(
        joe,
        'Hi Joe, I want to tell you our meeting place and time',
        internet
    )

    # Exchange a symmetric key for encrypted communication
    ahsan.exchange_key_with(joe, 'CS2025', internet)

    # Send an encrypted message
    ahsan.send_message(
        joe,
        'I will meet you at the Memorial Union at 12PM.',
        internet
    )

    # Reply from Joe (also encrypted)
    joe.send_message(
        ahsan,
        "Okay Ahsan, I got you. I can't wait to see you again!",
        internet
    )


if __name__ == '__main__':
    main()
