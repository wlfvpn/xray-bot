#!/usr/bin/env python

import logging
import os

from sqlitedb import SQLiteDB
from utils import get_cf_ip, get_daily_number
from xtlsapi import XrayClient, utils, exceptions

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

class TrafficManager:
    def __init__(self, config):
        self.logger = logging.getLogger("TrafficManager")

        self.db = SQLiteDB(config['db_path'])
        self.config = config
        self.xray_client = XrayClient('127.0.0.1', 62789)
        self.removed = []
    
    def update_traffic(self):
        from collections import defaultdict
        usage = defaultdict(int)
        uuids = self.db.get_all_uuid()
        for uuid in uuids:
            uuid = uuid[0]
            dl = self.xray_client.get_client_download_traffic(uuid,reset=True)
            if dl is None:
                dl = 0
            upload = self.xray_client.get_client_upload_traffic(uuid,reset=True)
            if upload is None:
                upload = 0
            usage  = dl + upload
            self.db.add_usage(uuid, usage)  
        self.logger.info("Updated traffic.")
    
    def remove_users_higher(self):
        inbounds = ["Vless-XTLS-reality"]
        for inbound in inbounds:
            emails = self.db.get_uuid_by_usage(self.config['traffic_limit'])
            for email in emails:
                if email[0] in self.removed:
                    continue
                try:
                    self.removed.append(email[0])
                    self.xray_client.remove_client(inbound,email=email[0])
                except Exception as e:
                            self.logger.error(e)
        self.logger.info(f"{len(emails)} users used all traffic. {str([self.db.get_username(x)[1] for x in self.removed])}")
            
    def reset_traffic(self):
        try:
            self.db.reset_usage()
            self.xray_client.restart_logger()
            self.removed = []
            os.system('docker restart xray-bot')
            self.logger.info("Traffic was reset.")
            

        except Exception as e:
            self.logger.error(e)
            
    def run(self):
        self.update_traffic()
        self.remove_users_higher()