# -*- coding: utf-8-*-
import os

# Aliada main directory
APP_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))

DATA_PATH = os.path.join(APP_PATH, "static")
LIB_PATH = os.path.join(APP_PATH, "client")
LOGIN_PATH = os.path.join(APP_PATH, "login")
TEMP_PATH = os.path.join(APP_PATH, "temp")
PLUGIN_PATH = os.path.join(APP_PATH, "plugins")

CONFIG_PATH = os.path.expanduser(
    os.getenv('ALIADA_CONFIG', '%s/.aliada' % APP_PATH)
)

CUSTOM_PATH = os.path.expanduser(
    os.getenv('ALIADA_CONFIG', '%s/.aliada/custom' % APP_PATH)
)


def config(*fname):
    return os.path.join(CONFIG_PATH, *fname)


def data(*fname):
    return os.path.join(DATA_PATH, *fname)
