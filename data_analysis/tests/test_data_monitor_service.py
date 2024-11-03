import time
import unittest

from data_analysis.modules.data_monitor_service import DataMonitorService


class TestDataMonitorService(unittest.TestCase):
    def setUp(self):
        self.monitor_service = DataMonitorService(keyword="example", interval=1)

    def test_start_stop_service(self):
        self.monitor_service.start()
        self.assertTrue(self.monitor_service._running, "Сервис должен быть запущен")

        # Подождем, чтобы мониторинг успел выполниться
        time.sleep(2)

        self.monitor_service.stop()
        self.assertFalse(self.monitor_service._running, "Сервис должен быть остановлен")


if __name__ == "__main__":
    unittest.main()
