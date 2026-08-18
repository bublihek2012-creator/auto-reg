import requests
import time

class TRAWLCaptchaSolver:
    def __init__(self, api_url: str = "http://localhost:8000", api_key: str = None):
        """
        api_url: URL, на котором запущен ваш экземпляр TRAWL.
        api_key: (Опционально) API-ключ, если он требуется для вашего экземпляра.
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        if self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})

    def solve_turnstile(self, site_key: str, page_url: str, proxy: str = None) -> str:
        """
        Решает Cloudflare Turnstile капчу.
        Возвращает токен для отправки на целевой сайт.
        """
        payload = {
            "type": "turnstile",
            "site_key": site_key,
            "page_url": page_url,
        }
        if proxy:
            payload["proxy"] = proxy

        try:
            # 1. Отправляем задачу
            response = self.session.post(f"{self.api_url}/solve", json=payload)
            response.raise_for_status()
            task_id = response.json().get("task_id")

            if not task_id:
                raise Exception("Не удалось получить task_id от TRAWL")

            print(f"[+] Задача отправлена в TRAWL. ID: {task_id}")

            # 2. Ожидаем результат
            start_time = time.time()
            timeout = 120  # Максимальное время ожидания

            while time.time() - start_time < timeout:
                status_response = self.session.get(f"{self.api_url}/status/{task_id}")
                status_response.raise_for_status()
                data = status_response.json()

                if data.get("status") == "solved":
                    token = data.get("token")
                    print(f"[✅] Капча решена. Токен получен.")
                    return token
                elif data.get("status") == "failed":
                    raise Exception(f"Ошибка решения капчи в TRAWL: {data.get('error')}")

                print(f"[⏳] Ожидание решения капчи... (статус: {data.get('status')})")
                time.sleep(3)

            raise TimeoutError("Превышено время ожидания решения капчи в TRAWL")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка связи с TRAWL: {e}")
        except Exception as e:
            raise Exception(f"Ошибка при решении капчи через TRAWL: {e}")

    def solve_recaptcha_v2(self, site_key: str, page_url: str, proxy: str = None) -> str:
        """
        Решает reCAPTCHA v2.
        """
        # Аналогично solve_turnstile, но с другим типом задачи
        payload = {
            "type": "recaptcha_v2",
            "site_key": site_key,
            "page_url": page_url,
        }
        if proxy:
            payload["proxy"] = proxy

        try:
            response = self.session.post(f"{self.api_url}/solve", json=payload)
            response.raise_for_status()
            task_id = response.json().get("task_id")

            if not task_id:
                raise Exception("Не удалось получить task_id от TRAWL")

            print(f"[+] Задача reCAPTCHA v2 отправлена в TRAWL. ID: {task_id}")

            start_time = time.time()
            timeout = 120

            while time.time() - start_time < timeout:
                status_response = self.session.get(f"{self.api_url}/status/{task_id}")
                status_response.raise_for_status()
                data = status_response.json()

                if data.get("status") == "solved":
                    token = data.get("token")
                    print(f"[✅] reCAPTCHA решена. Токен получен.")
                    return token
                elif data.get("status") == "failed":
                    raise Exception(f"Ошибка решения reCAPTCHA в TRAWL: {data.get('error')}")

                print(f"[⏳] Ожидание решения reCAPTCHA... (статус: {data.get('status')})")
                time.sleep(3)

            raise TimeoutError("Превышено время ожидания решения reCAPTCHA в TRAWL")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка связи с TRAWL: {e}")
        except Exception as e:
            raise Exception(f"Ошибка при решении reCAPTCHA через TRAWL: {e}")