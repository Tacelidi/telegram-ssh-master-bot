import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv


class PasswordManager:
    def __init__(self):
        load_dotenv()
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            print("Сгенерируй ключ и добавь в .env: ENCRYPTION_KEY=key")
            raise ValueError("Нет ключа шифрования!")
        self.cipher = Fernet(key.encode())

    def encrypt(self, password: str) -> str:
        return self.cipher.encrypt(password.encode()).decode()

    def decrypt(self, password: str) -> str:
        return self.cipher.decrypt(password.encode()).decode()


pm = PasswordManager()
