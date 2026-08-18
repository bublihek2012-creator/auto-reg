import requests
import re
import time
from bs4 import BeautifulSoup

class DisposeEmailClient:
    def __init__(self, timeout=300):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.timeout = timeout
        self.email = None
        self.email_prefix = None

    def get_new_email(self) -> str:
        """
        Получает новый временный email-адрес с Dispose.lol.
        Возвращает строку с email или выбрасывает исключение.
        """
        try:
            response = self.session.get("https://dispose.lol/")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Ищем поле с email
            email_input = soup.find("input", {"id": "email-address"})
            if email_input and email_input.get("value"):
                self.email = email_input["value"]
            else:
                # Если поле не найдено, пытаемся найти email в тексте
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@gmail\.com', response.text)
                if email_match:
                    self.email = email_match.group(0)
                else:
                    raise Exception("Не удалось найти email-адрес на странице Dispose.lol")

            self.email_prefix = self.email.split('@')[0]
            print(f"[+] Получен новый email: {self.email}")
            return self.email

        except Exception as e:
            raise Exception(f"Ошибка при получении email от Dispose.lol: {e}")

    def wait_for_verification_code(self, sender_filter: str = None) -> str:
        """
        Ожидает появления письма с кодом подтверждения.
        Возвращает 6-значный код или выбрасывает исключение по таймауту.
        """
        if not self.email:
            raise Exception("Сначала получите email с помощью get_new_email()")

        inbox_url = f"https://dispose.lol/inbox/{self.email_prefix}"
        start_time = time.time()

        print(f"[⏳] Ожидание кода подтверждения на {self.email}...")

        while time.time() - start_time < self.timeout:
            try:
                response = self.session.get(inbox_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # Ищем все сообщения
                messages = soup.find_all("div", class_=re.compile(r"message|email|inbox", re.I))

                for msg in messages:
                    # Получаем текст сообщения и отправителя
                    msg_text = msg.get_text()
                    sender = msg.find("span", class_=re.compile(r"sender|from", re.I))
                    sender_text = sender.get_text() if sender else ""

                    # Если задан фильтр по отправителю, проверяем
                    if sender_filter and sender_filter not in sender_text:
                        continue

                    # Ищем 6-значный код
                    code_match = re.search(r'\b(\d{6})\b', msg_text)
                    if code_match:
                        code = code_match.group(1)
                        print(f"[✅] Получен код подтверждения: {code}")
                        return code

                    # Ищем ссылку для подтверждения
                    link_match = re.search(r'https?://[^\s]+confirm[^\s]+', msg_text)
                    if link_match:
                        print(f"[✅] Найдена ссылка для подтверждения: {link_match.group(0)}")
                        return link_match.group(0)

                time.sleep(5)  # Пауза между проверками

            except Exception as e:
                print(f"[!] Ошибка при проверке почты: {e}")
                time.sleep(5)

        raise TimeoutError(f"Не удалось получить код подтверждения за {self.timeout} секунд.")