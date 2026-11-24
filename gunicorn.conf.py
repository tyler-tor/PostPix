"""Gunicorn settings for Postpix. `gunicorn wsgi:app` reads this file by itself
when it is run from the project folder.

Sized for a small server (1-2 GB RAM, 1-2 CPUs, e.g. an EC2 t4g.micro/small):
a few worker processes, each with several threads, because most requests spend
their time waiting for the database or S3, not computing. Every value can be
overridden with an environment variable, so nothing needs editing on a bigger
machine.

  WEB_CONCURRENCY   worker processes   (default 2)
  GUNICORN_THREADS  threads per worker (default 4)
  GUNICORN_TIMEOUT  seconds before a stuck worker is restarted (default 30)
  PORT              port to listen on, on all interfaces (0.0.0.0:$PORT).
                    The Docker image sets PORT=8000.
  BIND              full address:port, wins over PORT (e.g. 127.0.0.1:9000)
  With neither set: 127.0.0.1:8000 (local only, same port as `flask run`).
"""
import os

workers = int(os.environ.get("WEB_CONCURRENCY", 2))
threads = int(os.environ.get("GUNICORN_THREADS", 4))
# gthread = threads inside each worker process (the default "sync" worker
# handles one request at a time per process).
worker_class = "gthread"
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 30))

if os.environ.get("BIND"):
    bind = os.environ["BIND"]
elif os.environ.get("PORT"):
    # Inside a container the server must listen on all interfaces, or the
    # published port and the reverse proxy cannot reach it.
    bind = f"0.0.0.0:{os.environ['PORT']}"
else:
    bind = "127.0.0.1:8000"

# Load the app once in the master process, then fork the workers: they share
# the imported code in memory (less RAM) and start faster.
preload_app = True

# Restart each worker after about 1000 requests (with some randomness so they
# do not all restart together). Cheap insurance against slow memory growth.
max_requests = 1000
max_requests_jitter = 100

# Logs go to stdout/stderr, where Docker and CloudWatch collect them.
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(L)ss'

# Put worker heartbeat files in memory instead of on disk (recommended in containers).
worker_tmp_dir = "/dev/shm" if os.path.isdir("/dev/shm") else None

# Gunicorn 25+ opens a "control socket" for its gunicornc tool under
# $HOME/.gunicorn. The container user has no writable home, which logged a
# "Permission denied" error on every start, and nothing here uses gunicornc.
control_socket_disable = True
