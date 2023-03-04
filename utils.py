import yaml
import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config(path='config.yaml'):
    """Load the configuration from the specified yaml file.

    Args:
        path (str, optional): The path of the configuration file. Defaults to 'config.yaml'.

    Returns:
        dict: The configuration data.
    """
    with open(path, 'r') as stream:
        config = yaml.safe_load(stream)
    return config

def get_cf_ip(url = "http://bot.sudoer.net/best.cf.iran"):
    """Get the list of nonblocked cloudflare internet service providers in Iran.

    Returns:
        list: A list of dictionaries containing provider name, IP, time and description.
    """
    from collections import defaultdict
    import requests

    data = []
    try:
        response = requests.get(url,timeout=1)
        data = response.text.strip().split('\n')
    except:
        pass
    net = defaultdict(str, {"MCI": "HamrahAval", "RTL": "Rightel", "AST": "Asiatek", "IRC": "Irancel",
                      "SHT": "Shatel", "MKB": "Mokhaberat", "MBT": "Mobinnet", "ZTL": "Zitel", "PRS": "ParsOnline"})
    data_list = []
    for i in data:
        parts = i.split()
        if parts[0] not in net.keys():
            continue
        if len(parts) >= 3:
            data_dict = {'NAME': parts[0], 'IP': parts[1],
                         'Time': parts[2], "DESC": net[parts[0]]}
        else:
            data_dict = {'NAME': parts[0],
                         'IP': None, 'Time': None, "DESC": None}
        data_list.append(data_dict)
    return data_list


async def get_outline_key(user_id):
    """
    This function retrieves the Outline key for a user.
    
    :param user_id: ID of the user.
    :type user_id: str
    :return: A tuple of HTTP status code and Outline key.
    :rtype: tuple (int, str) status code and the url
    """
    config = load_config('config.yaml')
    import requests
    url = f"http://{config['outline_ip']}/get_outline_key?user_id={user_id}"
    try:
        response = requests.get(url, timeout = 15)
    except:
        return 408, ""

    return response.status_code, str(response.content).split('"')[1]


def add_cloudflare_record(config, number_str):
    """
    This function adds a record in Cloudflare.
    
    :param config: Configuration object containing the necessary authentication information.
    :type config: dict
    :param number_str: The string representation of a number to be added to the record name.
    :type number_str: str
    :return: None
    :rtype: None
    """
    import requests
    import time

    # code for adding the record goes here
    auth_email = config['auth_email']
    auth_key = config['auth_key']
    zone_id = config['zone_id']
    record_name = config['prefix_subdomain_name'] + number_str
    record_content = config['ip']
    record_type = "A"

    headers = {
        "X-Auth-Email": auth_email,
        "X-Auth-Key": auth_key,
        "Content-Type": "application/json"
    }

    data = {
        "name": record_name,
        "type": record_type,
        "content": record_content,
        "proxied": True
    }

    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"

    response = requests.get(url, headers=headers)
    records = response.json()["result"]
    record_exists = False
    for record in records:
        if record["name"].split('.')[0] == record_name and record["type"] == record_type:
            record_exists = True
            break

    if record_exists:
        logging.info(f"Record A {record_name} already exists.")

        return

    retry = 0
    record_added = False

    while not record_added and retry < 300:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            logging.info(
                f"Record A {record_name} successfully added to Cloudflare")
            record_added = True
        else:
            logging.info(f"Failed to add record A {record_name} to Cloudflare")
            time.sleep(1)
            retry += 1


def get_daily_number(delta=0):
    import datetime
    number = datetime.datetime.now().date() + datetime.timedelta(days=delta)
    return number.strftime("%m%d")


if __name__ == "__main__":
    config = load_config('config.yaml')
    tomorrow = get_daily_number(1)
    today = get_daily_number(0)
    add_cloudflare_record(config['cloudflare'], today)
    add_cloudflare_record(config['cloudflare'], tomorrow)


def is_valid_uuid(val):
    import uuid
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False