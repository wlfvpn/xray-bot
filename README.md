# Xray-Bot

## Getting Started

These instructions will guide you through the setup process of Xray-Bot.

### Prerequisites

### Steps
0. Install docker by:
 `curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh`

1. Generate 3000 UUIDs by running the following command:
    `cd scripts & python3 generate_urls.py`
2. customize your `config.yaml` file.
3. Run the Xray-Bot container using docker-compose:
    `docker-compose up --build -d`

Note: Make sure your firewall is set up properly and your port (default 443) is open.