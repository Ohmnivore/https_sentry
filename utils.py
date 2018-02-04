#!/usr/bin/env python
# -*- coding: utf-8 -*-

def open_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        contents = f.read()
    return contents
