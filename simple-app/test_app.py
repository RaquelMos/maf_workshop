import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode
from urllib.request import urlopen

import app
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
        app.next_task_id = 1

    def post(self, path, fields):
        data = urlencode(fields).encode()
        with urlopen(f"{self.base_url}{path}", data=data) as response:
            self.assertEqual(response.status, 200)

    def submit(self, task):
        self.post("/tasks", {"task": task})

    def test_empty_and_whitespace_submissions_are_ignored(self):
        self.submit("")
        self.submit(" \t\n ")

        self.assertEqual(tasks, [])

    def test_nonempty_submission_is_trimmed_and_added(self):
        self.submit("  finish the report  ")

        self.assertEqual([task.description for task in tasks], ["finish the report"])
        self.assertFalse(tasks[0].completed)

    def test_tasks_can_be_completed_and_reopened(self):
        self.submit("finish the report")

        self.post("/tasks/complete", {"task_id": tasks[0].id})
        self.assertTrue(tasks[0].completed)

        with urlopen(self.base_url) as response:
            page = response.read().decode()
        self.assertIn('class="completed">finish the report</span>', page)
        self.assertIn(">Reopen</button>", page)

        self.post("/tasks/complete", {"task_id": tasks[0].id})
        self.assertFalse(tasks[0].completed)


if __name__ == "__main__":
    unittest.main()
