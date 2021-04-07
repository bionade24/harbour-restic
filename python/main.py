#! /usr/bin/env python3

import pyotherside
import sfsecret
from restic.init import ResticInitThread


config = {
        "backup_destination": "",
        "ssh_key": "",
        "exclude_rules": "",
        "env_vars": "",
        "backup_include_paths": [],
        "password": ""
        }


def main():
    pyotherside.send('info', "Initialized")


def set_config(key, value):
    config[key] = value


def init_repo():
    params = config
    params["password"] = sfsecret.get_secret("restic", "password")
    params = ResticInitThread.prepare(params)
    if params["ok"]:
        ResticInitThread(params["cmd"], params).run()

