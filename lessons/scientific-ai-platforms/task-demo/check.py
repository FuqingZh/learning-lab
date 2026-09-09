"""Exercise real HTTP and process recovery: python3 check.py."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import lab


def until(read, predicate, seconds=6):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = read()
        if predicate(value):
            return value
        time.sleep(.05)
    raise AssertionError('condition did not become true')


def main():
    processes = []
    with tempfile.TemporaryDirectory() as directory:
        db = Path(directory) / 'jobs.sqlite'
        lab.initialize(db)

        def start(mode, *args):
            process = subprocess.Popen([sys.executable, str(Path(lab.__file__)), mode,
                                        '--db', str(db), *args], stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL, text=True)
            processes.append(process)
            return process

        def stop(process):
            process.terminate()
            process.wait(timeout=5)

        def request(path, key=None, label='demo'):
            headers = {'Content-Type': 'application/json', 'Idempotency-Key': key} if key else {}
            data = json.dumps({'label': label}).encode() if key else None
            try:
                with urlopen(Request(base + path, data=data, headers=headers), timeout=3) as response:
                    return response.status, json.load(response)
            except HTTPError as error:
                with error:
                    return error.code, json.load(error)

        try:
            api = start('api', '--port', '0')
            base = api.stdout.readline().strip()
            code, original = request('/exports', 'K1')
            assert code == 202 and original['status'] == 'queued'
            assert request('/exports', 'K1')[1]['id'] == original['id']
            assert request('/exports', 'K1', 'changed')[0] == 409
            stop(api)
            api = start('api', '--port', '0')
            base = api.stdout.readline().strip()
            assert request('/exports', 'K1')[1]['id'] == original['id']
            print('PASS: committed task survives API restart; same key reuses task; conflict rejected')

            get = lambda: request('/exports/' + original['id'])[1]
            first = start('worker', '--duration', '20', '--lease', '.6')
            stale = until(get, lambda row: row['status'] == 'running')
            stop(first)
            replacement = start('worker', '--duration', '.3', '--lease', '.6')
            complete = until(get, lambda row: row['status'] == 'succeeded')
            assert complete['generation'] == stale['generation'] + 1
            assert not lab.advance(db, stale, 4, 'stale report')
            assert get()['result'] == complete['result']
            stop(replacement)
            print('PASS: killed Worker replaced after expiry; stale completion rejected')

            pending = lab.submit(db, 'K2', 'race')
            racers = [start('claim', '--lease', '10') for _ in range(2)]
            rows = [json.loads(process.communicate(timeout=5)[0]) for process in racers]
            assert sum(row is not None for row in rows) == 1
            assert next(row for row in rows if row)['id'] == pending['id']
            print('PASS: two processes race; only one claims the queued task')
        finally:
            for process in processes:
                if process.poll() is None:
                    stop(process)
                if process.stdout:
                    process.stdout.close()


if __name__ == '__main__':
    main()
