# python 3.11
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import random
import time
from icecream import ic
from paho.mqtt import client as mqtt_client
from paho.mqtt.client import MQTTv5
from paho.mqtt.subscribeoptions import SubscribeOptions
import os
import requests

from logging.handlers import TimedRotatingFileHandler
# Function to create a TimedRotatingFileHandler with custom filename format
def create_timed_rotating_log_handler():
    log_filename = datetime.now().strftime("logs/log.mess.krx.%Y.%m.%d.txt")
    handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=7)
    handler.suffix = "%Y.%m.%d"
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    return handler

# Create a handler that rotates log files every day
handler = create_timed_rotating_log_handler()
handler.suffix = "%Y-%m-%d"  # Adds the date to the log file name

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Get the root logger and add the handler to it
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


class Config:
    """
    Application Configuration Class
    """
    BROKER = os.getenv('KRX_BROKER_URL', 'datafeed-lts-krx.dnse.com.vn')
    PORT = 443
    TOPICS = tuple(os.getenv('KRX_TOPICS', '').split(';'))
    CLIENT_ID = ''
    USERNAME = ''

    FIRST_RECONNECT_DELAY = 1
    RECONNECT_RATE = 2
    MAX_RECONNECT_COUNT = 12
    MAX_RECONNECT_DELAY = 60

    @staticmethod
    def get_auth_url():
        return os.getenv('KRX_AUTH_URL', 'https://api.dnse.com.vn/auth-service/login')

    @staticmethod
    def get_user_info_url():
        return os.getenv('KRX_USER_INFO_URL', 'https://api.dnse.com.vn/user-service/api/me')


class MQTTClient:
    """
    Class encapsulating MQTT Client related functionalities
    """

    def __init__(self):
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,Config.CLIENT_ID,
                                         protocol=MQTTv5,
                                         transport='websockets')

        self.client.username_pw_set(Config.USERNAME, self.login())
        self.client.tls_set_context()
        self.client.ws_set_options(path="/wss")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.retry_required = False
        self.FLAG_EXIT = False

    def login(self):

        url = Config.get_auth_url()

        payload = json.dumps({
            "username": os.getenv('KRX_USERNAME'),
            "password": os.getenv('KRX_PASSWORD')
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        token = json.loads(response.text)['token']
        self.token = token  # Store token for later use
        return token

    def get_user_info(self):
        """
        Get user information from user-service API
        Returns:
            str: investorId from user info
        """
        url = Config.get_user_info_url()
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        user_info = json.loads(response.text)
        return user_info['investorId']

    def connect_mqtt(self):
        # Get user info and set username
        Config.USERNAME = self.get_user_info()
        Config.CLIENT_ID = f'dnse-price-json-mqtt-ws-sub-{Config.USERNAME}-{random.randint(0, 1000)}'
        self.client.username_pw_set(Config.USERNAME, self.login())
        self.client.ws_set_options(path="/wss")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.connect(Config.BROKER, Config.PORT, keepalive=120, clean_start=True)
        return self.client
    
    def retry_failed_subscriptions(self):
        while True:
            time.sleep(3)  # Delay giữa các lần thử
            if self.denied_topics:
                self.client.username_pw_set(Config.USERNAME, self.login())
                self.client.ws_set_options(path="/wss")
                self.client.on_connect = self.on_connect
                self.client.on_message = self.on_message
                self.client.on_disconnect = self.on_disconnect
                self.client.on_subscribe = self.on_subscribe
            else:
                break
            
    def on_subscribe(self,client,mosq, obj, mid, granted_qos):
        print("granted_qos",mosq, obj, mid,granted_qos)
        has_denied = False
        for i, rc in enumerate(mid):
            topic = list(Config.TOPICS)[i]
            reason = str(rc)
            if reason == "Not authorized":
                logging.warning(f"Subscription to '{topic}' failed: Not authorized")
                has_denied = True
            else:
                logging.info(f"Subscribed to '{topic}' with {reason}")
        #granted_qos None 1 [ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized'), ReasonCode(Suback, 'Not authorized')] []
        #granted_qos None 1 [ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0'), ReasonCode(Suback, 'Granted QoS 0')] []
        # if granted_qos[0] == 128:
        #     print("❌ Subscription rejected by broker.")
        # else:
        #     print("✅ Subscription successful.")
        
        
        if has_denied:
            self.retry_required = True
            logging.info("At least one topic denied. Disconnecting to retry...")
            client.disconnect()
            
    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0 and client.is_connected():
            logging.info("Connected to MQTT Broker!")
            # time.sleep(3)
            topic_tuple = [(topic, SubscribeOptions(qos=0)) for topic in Config.TOPICS]
            ic(topic_tuple)
            self.client.subscribe(topic_tuple)
        else:
            logging.error(f'Failed to connect, return code {rc}')

    def on_disconnect(self, client, userdata, rc, properties=None):
        logging.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, Config.FIRST_RECONNECT_DELAY
        while reconnect_count < Config.MAX_RECONNECT_COUNT:
            logging.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                logging.info("Reconnected successfully!")
                return
            except Exception as err:
                logging.error("%s. Reconnect failed. Retrying...", err)
                reconnect_count += 1
                reconnect_delay = min(reconnect_delay * Config.RECONNECT_RATE, Config.MAX_RECONNECT_DELAY)

        # If we reach here, we've exceeded max reconnect attempts
        logging.error("Reached maximum reconnect attempts. Waiting for 1 hour before retrying...")
        time.sleep(3600)  # Wait for 1 hour
        self.on_disconnect(client, userdata, rc, properties)  # Try again

    def on_message(self, client, userdata, msg):
        payload = json.JSONDecoder().decode(msg.payload.decode())
        res = f'Topic: {msg.topic}, msg: {msg.payload}'
        logging.debug(res)
        print(res)


def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    my_mqtt_client = MQTTClient()
    client = my_mqtt_client.connect_mqtt()
    client.loop_forever()


if __name__ == '__main__':
    run()
