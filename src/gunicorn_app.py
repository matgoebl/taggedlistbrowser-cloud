#!/usr/bin/env python3
"""
Wrapper script to run Gunicorn for WSGI app.
Using this wrapper executes the app initialization once and before forking.
"""

import gunicorn.app.base
import os
import app


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    options = {
        'bind': '0.0.0.0:%i' % app.port,
        'workers': int(os.environ.get('WORKERS','1')),
        'accesslog': '-',
    }

    StandaloneApplication(app.app, options).run()
