from utils import add_cloudflare_record, load_config
import schedule
import time
import logging
import datetime

from utils import get_daily_number
from traffic_manager import TrafficManager
# Summary:
# This code sets up a scheduler to run every day at midnight and 1 minute after midnight.
# It calls the add_cloudflare_record function with config from config.yaml file and today_number or tomorrow_number as arguments. 
# The scheduler runs indefinitely until stopped with run_pending and sleep statements. 
# Logging is also enabled to log information during execution.


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def next_monday():
    today = datetime.datetime.today()
    next_monday = today + datetime.timedelta((7 - today.weekday()) % 7)
    delta = next_monday - today
    return delta.total_seconds()

def update_cf(cf_config):
    add_cloudflare_record(config=cf_config, number_str=get_daily_number(delta=0))   
    add_cloudflare_record(config=cf_config, number_str=get_daily_number(delta=1))

config = load_config('config.yaml')
logger.info("Scheduler started")
today_number = get_daily_number()
tomorrow_number = get_daily_number(delta=1)
traffic_manager = TrafficManager(config)
# schedule.every().day.at("00:00").do(update_cf, cf_config=config['cloudflare'])

schedule.every(1).minutes.do(traffic_manager.run)
schedule.every().monday.at("00:00").do(traffic_manager.reset_traffic)
 
for job in schedule.jobs:
    logger.info(" - " + str(job))

traffic_manager.run()
# update_cf(config['cloudflare'])

while True:
    schedule.run_pending()
    time.sleep(1)
