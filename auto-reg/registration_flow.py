import time
from email_client import DisposeEmailClient
from captcha_solver import TRAWLCaptchaSolver

class RegistrationFlow:
    def __init__(self, email_client: DisposeEmailClient, captcha_solver: TRAWLCaptchaSolver):
        self.email_client = email_client
        self.captcha_solver = captcha_solver

    def register(self, target_site_url: str, signup_api_endpoint: str, site_key: str = None):
        """
        Выполняет полный цикл регистрации.
        """
        print("=== НАЧАЛО ПРОЦЕССА РЕГИСТРАЦИИ ===")

        # 1. Получаем email
        email = self.email_client.get_new_email()
        print(f"[1/4] Используем email: {email}")

        # 2. Получаем капчу (в реальном сценарии site_key и page_url будут динамическими)
        # site_key обычно получается при загрузке страницы регистрации.
        print("[2/4] Ожидание решения капчи...")
        if site_key:
            token = self.captcha_solver.solve_turnstile(
                site_key=site_key,
                page_url=target_site_url
            )
            print(f"[2/4] Капча решена, токен получен.")
        else:
            print("[2/4] site_key не указан, пропускаем решение капчи.")
            token = None

        # 3. Отправляем данные на регистрацию
        # Это пример. В реальном проекте вам нужно будет заменить на вызов API целевого сайта.
        print("[3/4] Отправка данных регистрации...")
        registration_data = {
            "email": email,
            "captcha_token": token,
            # ... другие поля, например, пароль
        }
        # response = requests.post(f"{target_site_url}{signup_api_endpoint}", json=registration_data)

        # Имитация успешного ответа
        print(f"[3/4] Данные отправлены. Ответ: Успешно.")

        # 4. Проверяем почту на наличие кода подтверждения
        print("[4/4] Проверка почты на наличие кода подтверждения...")
        try:
            verification_code = self.email_client.wait_for_verification_code()
            print(f"[4/4] Получен код подтверждения: {verification_code}")
            # Здесь вы бы отправили этот код на сайт для завершения регистрации
            print("=== РЕГИСТРАЦИЯ УСПЕШНО ЗАВЕРШЕНА! ===")
            return True
        except TimeoutError as e:
            print(f"[!] Ошибка: {e}")
            return False