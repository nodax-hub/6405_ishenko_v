# Указываем путь к конфигу логирования и файлам логов
import logging.config
from pathlib import Path

config_path = Path(__file__).parent.parent / 'configs' / 'logging.conf'
log_file_path = Path(__file__).parent / 'logs'

# Создаем директорию для логов, если она отсутствует
log_file_path.mkdir(exist_ok=True)

if not logging.getLogger().hasHandlers():
    logging.config.fileConfig(str(config_path),
                              disable_existing_loggers=False,
                              defaults={'path_to_logs': log_file_path.as_posix()})
