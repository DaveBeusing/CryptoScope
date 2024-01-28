#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#

from os import remove
from os.path import isfile, dirname, abspath


class IPC:

    isRunning = 'isRunning'
    isPaused = 'isPaused'

    def get( signal ):
        #TODO make it a global config
        path = dirname( abspath( __file__ ) ) + signal + '.ipc'
        if isfile( path ):
            return True
        else:
            return False    

    def set( signal, delete=False ):
        #TODO make it a global config
        path = dirname( abspath( __file__ ) ) + signal + '.ipc'
        with open( path, 'a+' ) as fd:
            fd.close()
        if delete:
            remove( path )    