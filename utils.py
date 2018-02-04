#!/usr/bin/env python
# -*- coding: utf-8 -*-

def open_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        contents = f.read()
    return contents

def save_file(path, filestr):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(filestr)
