# -*- coding: utf-8 -*-

import os
from flask import current_app

def get_full_path(path):
    return os.path.join(current_app.config.get('BASE_DIR'), path)

def create_folders(path, relative=False):
    if relative:
        path = get_full_path(path)
    if not os.path.exists(path):
        os.makedirs(path)

def check_file_exists(path, relative=False):
    if relative:
        path = get_full_path(path)
    return os.path.exists(path)

def delete_file_by_path(path, relative=False):
    if path:
        if relative:
            path = get_full_path(path)
        try:
            os.remove(path)
        except OSError as e:
            pass