#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#
#import os

class Credentials:
    """ Load key and secret from file.
    Expected file format is key and secret on separate lines.
    :param path: path to keyfile
    :type path: str
    :returns: None
    """
    def __init__(self, path):
        self.key = ''
        self.secret = ''
        self.path = path #os.path.dirname( os.path.abspath(__file__) ) + '/' + path

        with open(self.path, 'r') as fd:
            self.key = fd.readline().strip()
            self.secret = fd.readline().strip()