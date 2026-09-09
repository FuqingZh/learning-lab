#!/usr/bin/env python3
"""Local task experiment: run `python lab.py api` and `python lab.py worker`.

Uses one SQLite file across independent processes. No authentication or real
scientific analysis: bind to loopback only; this is not a production server.
"""

import argparse
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import time
from urllib.parse import urlparse
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB = ROOT / ".build/task-demo/jobs.sqlite"


def connect(path):
    """Open a local store, e.g. `with closing(connect(path)) as db:`.

    Explicit transactions below cover acceptance and ownership transitions.
    Each caller must close its connection; workers never hold a write lock
    during simulated computation.
    """
    db = sqlite3.connect(path, timeout=5, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA synchronous=FULL")
    return db


def initialize(path):
    """Create the demo store once: `initialize(DEFAULT_DB)` is idempotent."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect(path)) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY, operation_key TEXT NOT NULL UNIQUE,
            label TEXT NOT NULL, status TEXT NOT NULL,
            generation INTEGER NOT NULL DEFAULT 0,
            lease_until REAL, result TEXT)""")


def submit(path, key, label):
    """Return the same task for the same key/payload: `submit(path, 'K1', 'demo')`.

    Conflicting payloads raise ValueError. BEGIN IMMEDIATE serializes SQLite
    writers; this is not a PostgreSQL isolation experiment.
    """
    with closing(connect(path)) as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT * FROM jobs WHERE operation_key=?", (key,)).fetchone()
        if row is not None:
            db.rollback()
            if row["label"] != label:
                raise ValueError("同一个操作编号不能用于不同内容")
            return dict(row)
        identifier = str(uuid4())
        db.execute("INSERT INTO jobs(id,operation_key,label,status) VALUES (?,?,?,'queued')",
                   (identifier, key, label))
        db.commit()
        return dict(db.execute("SELECT * FROM jobs WHERE id=?", (identifier,)).fetchone())


def claim(path, lease):
    """Acquire one waiting/expired job: `claim(path, 4)` returns a row or None.

    The demo uses one host clock. Renewal and takeover share SQLite write
    serialization; distributed clock uncertainty is outside this experiment.
    """
    with closing(connect(path)) as db:
        db.execute("BEGIN IMMEDIATE")
        now = time.time()
        row = db.execute("""SELECT id FROM jobs WHERE status='queued'
            OR (status='running' AND lease_until<=?) ORDER BY rowid LIMIT 1""", (now,)).fetchone()
        if row is None:
            db.rollback()
            return None
        row = db.execute("""UPDATE jobs SET status='running', generation=generation+1,
            lease_until=? WHERE id=? RETURNING *""", (now + lease, row["id"])).fetchone()
        db.commit()
        return dict(row)


def advance(path, job, lease, result=None):
    """Renew or finish the current lease: `advance(path, job, 4, 'report')`.

    Returns False for expired/replaced executions. Completion stores the small
    report in the same database update: no external file transaction is claimed.
    """
    with closing(connect(path)) as db:
        db.execute("BEGIN IMMEDIATE")
        now = time.time()
        cursor = db.execute("""UPDATE jobs SET lease_until=?, status=?, result=?
            WHERE id=? AND generation=? AND status='running' AND lease_until>?""",
            (now + lease, "succeeded" if result is not None else "running", result,
             job["id"], job["generation"], now))
        accepted = cursor.rowcount == 1
        db.commit()
        return accepted


def worker(path, duration, lease):
    """Process jobs until interrupted: `worker(path, duration=8, lease=4)`.

    Sleep stands in for calculation. Restarting repeats an expired attempt from
    the beginning, not from a saved computational checkpoint.
    """
    while True:
        job = claim(path, lease)
        if job is None:
            time.sleep(0.2)
            continue
        print(f"claimed {job['id']} generation={job['generation']}", flush=True)
        deadline = time.monotonic() + duration
        owned = True
        while time.monotonic() < deadline:
            time.sleep(min(lease / 3, max(0, deadline - time.monotonic())))
            if not advance(path, job, lease):
                owned = False
                break
        if owned:
            report = f"教学报告：{job['label']}\n任务：{job['id']}\n执行代次：{job['generation']}\n不含真实科研分析。\n"
            accepted = advance(path, job, lease, report)
            print(f"completion accepted={accepted}", flush=True)


def serve(path, port):
    """Serve the local page/API: `serve(DEFAULT_DB, 8765)` blocks until stopped."""
    class Handler(BaseHTTPRequestHandler):
        def send(self, status, value, content_type="application/json; charset=utf-8"):
            body = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass  # A disconnected caller does not undo the committed job.

        def do_GET(self):
            route = urlparse(self.path).path
            if route == "/":
                self.send(200, Path(__file__).with_name("index.html").read_bytes(), "text/html; charset=utf-8")
                return
            if not route.startswith("/exports/"):
                self.send(404, {"error": "not found"})
                return
            with closing(connect(path)) as db:
                row = db.execute("SELECT * FROM jobs WHERE id=?", (route.removeprefix("/exports/"),)).fetchone()
            self.send(200, dict(row)) if row else self.send(404, {"error": "task not found"})

        def do_POST(self):
            if self.path != "/exports":
                self.send(404, {"error": "not found"})
                return
            # The browser sends JSON, not a cross-origin HTML form.
            if self.headers.get("Content-Type") != "application/json":
                self.send(415, {"error": "JSON required"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 2048:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(length))
                key = self.headers.get("Idempotency-Key", "")
                label = payload.get("label") if isinstance(payload, dict) else None
                if not 1 <= len(key) <= 100 or not isinstance(label, str) or not 1 <= len(label) <= 120:
                    raise ValueError("invalid key or label")
            except (ValueError, UnicodeError):
                self.send(400, {"error": "invalid request"})
                return
            try:
                row = submit(path, key, label)
            except ValueError as error:
                self.send(409, {"error": str(error)})
                return
            self.send(202, row)

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["api", "worker", "claim"])
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--duration", type=float, default=8)
    parser.add_argument("--lease", type=float, default=4)
    args = parser.parse_args()
    if args.lease <= 0 or args.duration < 0:
        parser.error("lease must be positive and duration nonnegative")
    initialize(args.db)
    try:
        if args.mode == "api":
            serve(args.db, args.port)
        elif args.mode == "worker":
            worker(args.db, args.duration, args.lease)
        else:
            print(json.dumps(claim(args.db, args.lease)))
    except KeyboardInterrupt:
        pass
