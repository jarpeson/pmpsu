#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Turku University (2018) Department of Future Technologies
# Foresail-1 / PATE Monitor / OBC Emulator
# Configuration values from PATE Monitor's backend
#
import serial

class Config:
    class PSU:
        port          = '/dev/ttyUSB0'
        #port          = 'COM15'
        baudrate      = 9600
        parity        = serial.PARITY_NONE
        stopbits      = serial.STOPBITS_TWO
        bytesize      = serial.EIGHTBITS
        timeout       = 0.500    #seconds, timeout has to be > 300 ms
        write_timeout = None
        default_voltage = 2.5         #[V]
        default_current_limit = 0.100 #[A]
    class PATE:
        class Bus:
            port          = '/dev/ttyUSB1'
            baudrate      = 115200
            parity        = serial.PARITY_NONE
            stopbits      = serial.STOPBITS_ONE
            bytesize      = serial.EIGHTBITS
            timeout       = 0.05
            write_timeout = None
        class Interval:
            status_check    = 10    # seconds
            housekeeping    = 60
    logging_level   = 'DEBUG'
    database_file   = '/srv/nginx-root/pmapi.sqlite3'
    command_poll    = 0.1           # seconds

# EOF