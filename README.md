# Xray-Bot

## Getting Started

These instructions will guide you through the setup process of Xray-Bot.

### Prerequisites

- Get your certificates and put it in the `db/cert/{site_name}` folder.
- Update `main.py` to point to your subscription domain certificate.
- Update `scripts/base.json` with your VPN certificates in `db/cert/{site_name}`. A wildcard certificate is needed. path should be in the container path.
 `db/cert/` is mounted to `/root/cert` in the container.  
- Install Python3 pip by running `apt install python3-pip`
- Install the required packages by running `pip install -r requirements.txt`
- To-Do: Make everything in the docker-compose as different services.

### Step 0: Preparations

1. Generate 1000 UUIDs by running the following command:
    `cd scripts & python3 generate_urls.py`
2. Modify `scripts/nginx.conf` as needed and put it into `/etc/nginx/conf.d/`.
3. Restart nginx by running: `rm /dev/shm/h* && service nginx restart`
### Step 1: Configuration

1. Copy `config.sample.yaml` to `config.yaml` and change it with your own parameters.

### Step 2: Xray-core
1. Run the Xray-Bot container using docker-compose:`docker-compose up --build -d`

### Step 3: Run the Telegram Bot and Subscription Server

1. Run the Xray-Bot by running:`./main.py`

Note: Make sure your firewall is set up properly and yopur ports for subscription server and xray-core is open.