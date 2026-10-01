from dataclasses import dataclass
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


@dataclass
class Task:
    id: int
    description: str
    completed: bool = False


tasks = []
next_task_id = 1


HTML = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Simple Tasks</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 3rem auto; max-width: 38rem; padding: 0 1rem; }}
    form {{ display: flex; gap: .5rem; margin: 1.5rem 0; }}
    input {{ flex: 1; padding: .6rem; }}
    button {{ padding: .6rem .9rem; }}
    li {{ margin: .5rem 0; }}
    .completed {{ color: #666; text-decoration: line-through; }}
    .task-form {{ display: inline; margin: 0; }}
  </style>
</head>
<body>
  <h1>Simple Tasks</h1>
  <form method="post" action="/tasks">
    <input name="task" placeholder="What needs doing?" aria-label="New task">
    <button type="submit">Add task</button>
  </form>
  <ul>
    {items}
  </ul>
</body>
</html>
"""


class TaskHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if urlparse(self.path).path != "/":
            self.send_error(404)
            return

        items = "".join(
            f'<li><span class="{"completed" if task.completed else ""}">'
            f"{escape(task.description)}</span> "
            f'<form class="task-form" method="post" action="/tasks/complete">'
            f'<input type="hidden" name="task_id" value="{task.id}">'
            f'<button type="submit">{"Reopen" if task.completed else "Mark complete"}</button>'
            f"</form></li>"
            for task in tasks
        )
        body = HTML.format(items=items).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/tasks", "/tasks/complete"):
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode())
        if path == "/tasks":
            global next_task_id
            description = form.get("task", [""])[0].strip()
            if description:
                tasks.append(Task(id=next_task_id, description=description))
        else:
            try:
                task_id = int(form.get("task_id", [""])[0])
            except ValueError:
                self.send_error(400, "A valid task_id is required")
                return

            task = next((task for task in tasks if task.id == task_id), None)
            if task is None:
                self.send_error(404, "Task not found")
                return
            task.completed = not task.completed

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


if __name__ == "__main__":
    print("Open http://localhost:8000")
    ThreadingHTTPServer(("localhost", 8000), TaskHandler).serve_forever()
