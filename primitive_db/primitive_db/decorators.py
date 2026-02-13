from collections.abc import Callable
from functools import wraps
import time

FunctionType = Callable[..., object]

def handle_db_errors(func: FunctionType) -> FunctionType:
    """Декоратор для перехвата ошибок БД и вывода понятного сообщения."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as exc:
            print(f"Ошибка: {exc}")
        except Exception as exc:  # на всякий случай
            print(f"Неожиданная ошибка: {exc}")
        return None

    return wrapper  # type: ignore[return-value]


def confirm_action(message: str = "Вы уверены? (y/n): ") -> Callable[[FunctionType], FunctionType]:
    """Декоратор, запрашивающий подтверждение перед выполнением действия."""

    def decorator(func: FunctionType) -> FunctionType:
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(message).strip().lower()
            if answer not in ("y", "yes", "д", "да"):
                print("Действие отменено.")
                return None
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def log_time(func: FunctionType) -> FunctionType:
    """Декоратор для логирования времени выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} выполнена за {duration:.4f} с")
        return result

    return wrapper  # type: ignore[return-value]
