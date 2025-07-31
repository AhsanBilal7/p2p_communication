
import argparse
import json
import os
import base64
from datetime import datetime
from src.network import NetworkClass
from src.person import PersonClass

PLAIN_FILE = "messages_plain.json"
ENC_FILE = "messages_enc.json"

"""
key mapping json object
so that we can store the messages in a separaet encrypted
we take the frozen object of the python to predefined the set of sender and recipent
"""
keys_map = {}

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def encrypt(key, text):
    b = text.encode("utf-8")
    k = key.encode("utf-8")
    cipher = bytearray()
    for i, byte in enumerate(b):
        cipher.append(byte ^ k[i % len(k)])
    return base64.b64encode(bytes(cipher)).decode("ascii")


def decrypt(key, ciphertext):
    data = base64.b64decode(ciphertext)
    k = key.encode("utf-8")
    plain = bytearray()
    for i, byte in enumerate(data):
        plain.append(byte ^ k[i % len(k)])
    return plain.decode("utf-8")


def append_message(sender, recipient, text):
    conv = frozenset({sender, recipient})
    ts = datetime.utcnow().isoformat() + "Z"
    if conv in keys_map:
        # encrypted message
        cipher = encrypt(keys_map[conv], text)
        entry = {
            "timestamp": ts,
            "sender": sender,
            "recipient": recipient,
            "ciphertext": cipher
        }
        msgs = load_json(ENC_FILE)
        msgs.append(entry)
        save_json(ENC_FILE, msgs)
    else:
        # plaintext message
        entry = {
            "timestamp": ts,
            "sender": sender,
            "recipient": recipient,
            "message": text
        }
        msgs = load_json(PLAIN_FILE)
        msgs.append(entry)
        save_json(PLAIN_FILE, msgs)


def display_menu(is_eve, role):
    if is_eve:
        print("""
🕵️  EAVESDROPPER'S MONITORING SYSTEM 🕵️
Commands:
  join <name>                            Add a target to monitor
  intercept <sender> <recipient> <text>  Intercept and modify a message
  listen                                 Show plaintext traffic
  targets                                List monitored targets
  help                                   Show this menu
  quit / exit                            Exit surveillance
""")
    else:
        print(f"""
{'='*50}
   {role}'s SECURE MESSAGING SYSTEM
{'='*50}
Commands:
  join <name>                     Add a participant to your network
  send <recipient> <text>         Send a message (plaintext or encrypted if key exists)
  exchange <recipient> <key>      Exchange a symmetric key for encryption
  list                            List network participants
  messages                        View your received messages
  help                            Show this menu
  quit / exit                     Exit the system
""")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Secure Messaging Interface")
    parser.add_argument("role", help="Your name (Alice, Bob, or Eavesdropper)")
    args = parser.parse_args()
    role = args.role
    is_eve = role.lower() in ("eavesdropper", "eve", "attacker")
    me = PersonClass(name=role, is_bad_man=is_eve)
    net = NetworkClass(name="Internet")
    net.join(me)

    contacts = {}
    print(f"Welcome, {role}! You are now on the network.\n")
    display_menu(is_eve, role)

    while True:
        try:
            line = input(f"{role}> ").strip()
            if not line:
                continue
            parts = line.split(" ", 3 if is_eve else 2)
            cmd = parts[0].lower()

            if cmd in ("quit", "exit"):
                print(f"Goodbye, {role}!")
                break

            if cmd == "help":
                display_menu(is_eve, role)
                continue

            if cmd == "join":
                if len(parts) < 2:
                    print("Usage: join <name>")
                    continue
                name = parts[1]
                if name in contacts:
                    print(f"✗ {name} already joined.")
                else:
                    bad = (not is_eve) and name.lower() in ("eavesdropper","eve","attacker")
                    p = PersonClass(name=name, is_bad_man=bad)
                    net.join(p)
                    contacts[name] = p
                    status = " (⚠️  Eavesdropper)" if bad else ""
                    print(f"✓ {name} joined{status}")
                continue

            # Normal user
            if not is_eve:
                if cmd == "exchange":
                    if len(parts) < 3:
                        print("Usage: exchange <recipient> <key>")
                        continue
                    to, key = parts[1], parts[2]
                    if to not in contacts:
                        print(f"✗ {to} not joined; use 'join {to}' first.")
                        continue
                    me.exchange_key_with(contacts[to], key, net)
                    conv = frozenset({role, to})
                    keys_map[conv] = key
                    print(f"✓ Key exchanged with {to}")
                    continue

                if cmd == "send":
                    if len(parts) < 3:
                        print("Usage: send <recipient> <message>")
                        continue
                    to, msg = parts[1], parts[2]
                    if to not in contacts:
                        print(f"✗ {to} not joined; use 'join {to}' first.")
                        continue
                    me.send_message(contacts[to], msg, net)
                    append_message(role, to, msg)
                    status = "(encrypted)" if frozenset({role,to}) in keys_map else "(plaintext)"
                    print(f"✓ Sent {status} to {to}")
                    continue

                if cmd == "list":
                    print("\nParticipants in network:")
                    print(f"- {role} (You)")
                    for n,p in contacts.items():
                        flag = " (⚠️  Eavesdropper)" if getattr(p,"is_bad_man",False) else ""
                        print(f"- {n}{flag}")
                    continue

                if cmd == "messages":
                    plain = load_json(PLAIN_FILE)
                    inbox_plain = [m for m in plain if m["recipient"]==role]
                    enc = load_json(ENC_FILE)
                    inbox_enc = [m for m in enc if m["recipient"]==role]
                    print("\nYour messages:")
                    items = []
                    for m in inbox_plain:
                        items.append((m["timestamp"], f"{m['sender']}: {m['message']}"))
                    for m in inbox_enc:
                        conv = frozenset({m['sender'],role})
                        key = keys_map.get(conv)
                        text = decrypt(key,m['ciphertext']) if key else "<cannot decrypt>"
                        items.append((m["timestamp"], f"{m['sender']} (encrypted): {text}"))
                    if not items:
                        print("No messages.")
                    else:
                        for ts, line in sorted(items):
                            print(f"[{ts}] {line}")
                    continue

            else:
                if cmd == "intercept":
                    if len(parts) < 4:
                        print("Usage: intercept <sender> <recipient> <message>")
                        continue
                    s, r, text = parts[1], parts[2], parts[3]
                    if s not in contacts or r not in contacts:
                        print("Join both sender and recipient first.")
                        continue
                    print(f"📡 {s}→{r}: {text}")
                    if input("Modify? (y/n):").strip().lower() == "y":
                        text = input("New message: ").strip()
                        print(f"✏️ Modified: {text}")
                    me.send_message(contacts[r], text, net)
                    append_message(s, r, text)
                    print(f"📤 Relayed to {r}")
                    continue

                if cmd == "listen":
                    plain = load_json(PLAIN_FILE)
                    print("\nPlaintext traffic:")
                    if not plain:
                        print("No messages.")
                    else:
                        for m in plain:
                            print(f"[{m['timestamp']}] {m['sender']}→{m['recipient']}: {m['message']}")
                    continue

                if cmd == "targets":
                    print("\nMonitored targets:")
                    print(f"- {role} (You)")
                    for n in contacts:
                        print(f"- {n}")
                    continue

            print(f"Unknown command: {cmd}. Type 'help' for options.")

        except (KeyboardInterrupt, EOFError):
            print(f"\nGoodbye, {role}!")
            break
        except Exception as e:
            print(f"Error: {e}")
