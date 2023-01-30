#!/usr/bin/env python

import logging
import requests
import json
import base64

from sqlitedb import SQLiteDB
from utils import get_cf_ip, get_daily_number

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkManager:
    def __init__(self, config):
        self.db = SQLiteDB(config['db_path'])
        self.config = config
        self.subdomain_preffix = config['cloudflare']['prefix_subdomain_name']
        self.domain = config['cloudflare']['domain']
        
    def register_id(self,telegram_id,telegram_username):
        if self.db.get_uuid(telegram_id):
            return True
        else:
            if int(self.db.count_users_with_telegram_id())> self.config['max_users']:
                return False

            self.db.register_telegram_id(telegram_id=telegram_id,telegram_username=telegram_username,traffic_limit=self.config['traffic_limit'])
            return True

    def get_link_trojan(self, telegram_id,telegram_username):
        if not self.register_id(telegram_id,telegram_username):
            return False, ["Server is full."]

        user_uuid = self.db.get_uuid(telegram_id)
        if user_uuid is None:
            return False, ["Error connetion to server database."]

        # sni_id = telegram_id
        sni_id = get_daily_number()

        urls ={}
        urls['Trojan-WS'] = self.trojan_ws_cdn(user_uuid, sni_id)
        urls['Trojan-gRPC'] = self.trojan_grpc_cdn(user_uuid, sni_id)
        return True, urls

    def get_link_vless(self, telegram_id,telegram_username):
        if not self.register_id(telegram_id,telegram_username):
            return False, ["Server is full."]

        user_uuid = self.db.get_uuid(telegram_id)
        if user_uuid is None:
             return False, ["Error connetion to server database."]

        # sni_id = telegram_id
        sni_id = get_daily_number()

        urls ={}
        urls['VLESS-WS'] = self.vless_ws_cdn(user_uuid, sni_id)
        urls['VLESS-gRPC'] = self.vless_grpc_cdn(user_uuid, sni_id)
        return True, urls

    def get_link_vmess(self, telegram_id,telegram_username):
        if not self.register_id(telegram_id,telegram_username):
            return False, ["Server is full."]

        user_uuid = self.db.get_uuid(telegram_id)
        if user_uuid is None:
             return False, ["Error connetion to server database."]

        # sni_id = telegram_id
        sni_id = get_daily_number()

        urls ={}
        urls['VMess-WS'] = self.vmess_ws_cdn(user_uuid, sni_id)
        urls['VMess-gRPC'] = self.vmess_grpc_cdn(user_uuid, sni_id)
        return True, urls


    def trojan_grpc_cdn(self, uuid, sni_id):
        url = f"trojan://{uuid}@{self.subdomain_preffix}{sni_id}.{self.domain}:443?security=tls&type=grpc&serviceName=/trgrpc&mode=gun&alpn=h2&sni={self.subdomain_preffix}{sni_id}.{self.domain}#@WomanLifeFreedom-TgRPC"
        urls = LinkManager.alternate_vless_trojan(url)
        return urls
    
    def trojan_ws_cdn(self, uuid, sni_id):
        url = f"trojan://{uuid}@{self.subdomain_preffix}{sni_id}.{self.domain}:443?security=tls&alpn=http%2F1.1&type=ws&path=%2Ftrojanws%3Fed%3D2048#@WomanLifeFreedom-Tws"
        urls = LinkManager.alternate_vless_trojan(url)
        return urls

    def vless_grpc_cdn(self, uuid, sni_id):
        url = f"vless://{uuid}@{self.subdomain_preffix}{sni_id}.{self.domain}:443?encryption=none&security=tls&type=grpc&alpn=h2&sni={self.subdomain_preffix}{sni_id}.{self.domain}&serviceName=vlgrpc&mode=gun#@WomanLifeFreedom-VLESSgRPC"
        urls = LinkManager.alternate_vless_trojan(url)
        return urls
    
    def vless_ws_cdn(self, uuid, sni_id):
        url = f"vless://{uuid}@{self.subdomain_preffix}{sni_id}.{self.domain}:443?encryption=none&security=tls&type=ws&path=%2Fvlws#@WomanLifeFreedom-VLESSws"
        urls = LinkManager.alternate_vless_trojan(url)
        return urls
    
    def vmess_ws_cdn(self, uuid, sni_id):
        data = {"v": "2", "ps": "@WomanLifeFreedom-VMessws", "add": f"{self.subdomain_preffix}{sni_id}.{self.domain}", "port": "443", "id": uuid, "aid": "0", "scy": "none",
        "net": "ws", "type": "none", "host": "", "path": "/vmws", "tls": "tls", "sni": "", "alpn": "http/1.1" }

        json_string = json.dumps(data)
        base64_encoded_string = base64.b64encode(json_string.encode()).decode()
        url = f"vmess://{base64_encoded_string}"
        urls = LinkManager.alternate_vmess(url)
        return urls
    
    def vmess_grpc_cdn(self, uuid, sni_id):
        data = {"v": "2", "ps": "@WomanLifeFreedom-VMessgRPC", "add": f"{self.subdomain_preffix}{sni_id}.{self.domain}", "port": "443", "id": uuid, "aid": "0", "scy": "none",
        "net": "grpc", "type": "http", "host": "", "path": "vmgrpc", "tls": "tls", "sni": f"{self.subdomain_preffix}{sni_id}.{self.domain}", "alpn": "h2" }
        json_string = json.dumps(data)
        base64_encoded_string = base64.b64encode(json_string.encode()).decode()
        url = f"vmess://{base64_encoded_string}"
        urls = LinkManager.alternate_vmess(url)
        return urls

    @staticmethod
    def alternate_vless_trojan(url):
        import re

        ### get address
        addr_match = re.search(r'@([^:]+):', url)
        if addr_match:
            address = addr_match.group(1)
        else:
            return
        ### get host and add it
        host = None
        match_host = re.search(r'host=([^&#]+)', url)
        if match_host:
            host = match_host.group(1)
        else:
            host = address
            url_parts = url.split("#")
            url = url_parts[0] + f"&host={host}#" + url_parts[1]

        ### get sni and add it
        match_sni = re.search(r'sni=([^&#]+)', url)
        if not match_sni:
            url_parts = url.split("#")
            url = url_parts[0] + f"&sni={host}#" + url_parts[1] 

        cf_good_ips = get_cf_ip()
        cf_ips=[{"NAME":"iranserver.com","IP":"iranserver.com","TIME":None,"DESC":"2"}]
        cf_ips+=cf_good_ips
        urls = [url]
        for cf_ip in cf_ips:
            if cf_ip["IP"]:
                new_url = url.replace(address, cf_ip["IP"],1)
                url_parts = new_url.split("#")
                new_url +=  f'-{cf_ip["DESC"]}'
                urls.append(new_url)
        return urls

    @staticmethod
    def alternate_vmess(url):    
        cf_good_ips = get_cf_ip()
        cf_ips = []
        # cf_ips=[{"NAME":"iranserver.com","IP":"iranserver.com","TIME":None,"DESC":"2"}]
        cf_ips+=cf_good_ips
        urls = [url]
        url = url[8:]
        json_string = base64.b64decode(url).decode()
        data = json.loads(json_string)
        for cf_ip in cf_ips:
            if cf_ip["Name"] not in ["MCI","IRC"]:
                continue
            
            data_new = dict(data)
            data_new['sni'] = data['add']
            data_new['host'] = data['add']

            if cf_ip["IP"]:
                data_new['add'] = cf_ip["IP"]
                data_new['ps'] +=  f'-{cf_ip["DESC"]}'
                json_string = json.dumps(data_new)
                base64_encoded_string = base64.b64encode(json_string.encode()).decode()
                new_url = f'vmess://{base64_encoded_string}'
                urls.append(new_url)
        return urls

    def get_sub(self,telegram_id):
        user_uuid = self.db.get_uuid(telegram_id)
        url = f"https://wlfvip.au1.store:8443/subscriptions?token={user_uuid}"
        return url
    