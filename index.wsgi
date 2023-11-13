#! /usr/bin/python3
import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/html/fishapiv4')

from fishapiv4 import create_app
application = create_app()
