# handlers/__init__.py
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger.info("📦 Пакет handlers инициализирован")

# Здесь можно добавлять общие утилиты, переменные или настройки для всех обработчиков

# Пример: глобальная переменная
HANDLER_VERSION = "1.0.0"

