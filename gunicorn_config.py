# gunicorn_config.py
workers = 4
bind = "127.0.0.1:5001"
timeout = 120
keepalive = 5
worker_class = "sync"
errorlog = "-"
accesslog = "-"
loglevel = "info"