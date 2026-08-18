import time
from email_client import DisposeEmailClient
from captcha_solver import TRAWLCaptchaSolver
from registration_flow import RegistrationFlow

def main():
    # 1. Инициализация клиентов
    email_client = DisposeEmailClient(timeout=120)  # Таймаут ожидания кода
    captcha_solver = TRAWLCaptchaSolver(
        api_url="http://localhost:8000",  # URL вашего TRAWL
        # api_key="YOUR_API_KEY" # Если требуется
    )

    # 2. Создание основного объекта регистрации
    register = RegistrationFlow(email_client, captcha_solver)

    # 3. Запуск регистрации для примера
    # В реальном сценарии site_key получается динамически.
    # target_site_url - адрес сайта, на котором вы регистрируетесь.
    target_url = "https://example.com/signup"  # Замените на целевой сайт
    site_key = "0x4AAAAAAA..."  # Замените на реальный site_key для Turnstile

    register.register(
        target_site_url=target_url,
        signup_api_endpoint="/api/signup",  # Замените на реальный эндпоинт
        site_key=site_key
    )

if __name__ == "__main__":
    main()