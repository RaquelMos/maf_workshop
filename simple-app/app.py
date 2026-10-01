from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


tasks = []


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

        items = "".join(f"<li>{escape(task)}</li>" for task in tasks)
        body = HTML.format(items=items).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if urlparse(self.path).path != "/tasks":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode())
        task = form.get("task", [""])[0].strip()
        if task:
            tasks.append(task)

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


if __name__ == "__main__":
    print("Open http://localhost:8000")
    ThreadingHTTPServer(("localhost", 8000), TaskHandler).serve_forever()
