import yaml


def load_config(path='config.yaml'):
    with open(path, 'r') as stream:
        config = yaml.safe_load(stream)
    return config
    
def get_cf_ip():
    from collections import defaultdict
    import requests

    url = "http://bot.sudoer.net/best.cf.iran"
    response = requests.get(url)
    data = response.text.strip().split('\n')
    net = defaultdict(str, {"MCI":"HamrahAval", "RTL":"Rightel", "AST":"Asiatek", "IRC":"Irancel", "SHT":"Shatel", "MKB":"Mokhaberat", "MBT":"Mobinnet", "ZTL":"Zitel"})
    data_list = []
    for i in data:
        parts = i.split()
        if parts[0] not in net.keys():
                continue
        if len(parts)>=3:
            data_dict = {'Name': parts[0], 'IP': parts[1], 'Time': parts[2],"DESC":net[parts[0]]}
        else:
            data_dict = {'Name': parts[0], 'IP': None, 'Time': None, "DESC":None}
        data_list.append(data_dict)
    return data_list

async def get_outline_key(user_id):
    config = load_config('config.yaml')
    import requests
    url = f"http://{config['outline_ip']}/get_outline_key?user_id={user_id}"
    response = requests.get(url)
    return response.status_code, str(response.content).split('"')[1]
