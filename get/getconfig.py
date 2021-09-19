# -*- coding: utf-8 -*-
import logging
import sys
import os
import random
import cookielib
"""
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='Log.log', filemode='a+', format=FORMAT)
"""
def checkFile(filepath):
    if os.path.isfile(filepath):
        logging.info(filepath+" is exist")
    else:
        logging.error(filepath +" file not found")
        sys.exit()

class Config:
    def __init__(self,configfile = "config.txt"):
        file = open(configfile, 'r')
        txt = file.readlines()
        file.close()
        self.KeyFile = txt[0].split("#")[0].replace('KeyFile"', "").replace('\n', "").replace('\r', "").replace('"', "")
        self.KeyName = txt[1].split("#")[0].replace('KeyName"', "").replace('\n', "").replace('\r', "").replace('"', "")
        self.InstanceType = txt[2].split("#")[0].replace('InstanceType"', "").replace('\n', "").replace('\r', "").replace('"', "")
        self.SecurityGroupIds = txt[3].split("#")[0].replace('SecurityGroupIds"', "").replace('\n', "").replace('\r', "").replace('"', "")



if __name__ == '__main__':
    config = Config()
    print config.KeyFile
    print config.KeyName
    print config.InstanceType
    print config.SecurityGroupIds
