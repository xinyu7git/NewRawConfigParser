#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
#xinyu7@staff.sina.com.cn
#2013-06-08

import os
import sys

os.chdir(sys.path[0])
sys.path.append("./")

from NewRawConfigParser import *

config = NewRawConfigParser(allow_no_value=True,new_option_len=33)

config.read("a.cnf")

print config.get("mysqld","user")
config.set("mysqld","user","xinyu7")

with open("a.cnf",'wb') as configfile:
    config.write(configfile)