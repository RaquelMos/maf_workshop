import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode
from urllib.request import urlopen

from app import TaskHandler, tasks


class TaskHandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), TaskHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join()

    def setUp(self):
        tasks.clear()

    def submit(self, task):
        data = urlencode({"task": task}).encode()
        with urlopen(f"{self.base_url}/tasks", data=data) as response:
            self.assertEqual(response.status, 200)

    def test_empty_and_whitespace_submissions_are_ignored(self):
        self.submit("")
        self.submit(" \t\n ")

        self.assertEqual(tasks, [])

    def test_nonempty_submission_is_trimmed_and_added(self):
        self.submit("  finish the report  ")

        self.assertEqual(tasks, ["finish the report"])


if __name__ == "__main__":
    unittest.main()
