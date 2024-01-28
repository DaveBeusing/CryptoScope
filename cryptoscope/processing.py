#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) Dave Beusing <david.beusing@gmail.com>
#
#

import os
import signal
import subprocess

class Processing:
    '''
    #https://stackoverflow.com/a/7224186
    #https://stackoverflow.com/a/51950538
    #https://docs.python.org/3/library/subprocess.html#module-subprocess
    '''
    def start( script, logfile=None ):
        if logfile is not None:
            with open( logfile, 'a+' ) as lf:
                proc = subprocess.Popen( [ '/usr/bin/python', script ], close_fds=True, stdout=lf, stderr=lf )
        else:
            proc = subprocess.Popen( [ '/usr/bin/python', script ], close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
        return proc.pid

    def stop( pid:int ):
        os.kill( pid, signal.SIGTERM )