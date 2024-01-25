#!/usr/bin/env python3
__author__ = 'Jon Stratton'

import argparse, configparser, requests, slixmpp

class OllamaBridge(slixmpp.ClientXMPP):
   ollama_url = ''
   ollama_model = ''
   user_messages = {}
   def __init__(self, config):
      self.ollama_url = config['ollama_url'];
      self.ollama_model = config['ollama_model'];
      slixmpp.ClientXMPP.__init__(self, config['xmpp_username'], config['xmpp_password'])
      self.add_event_handler("session_start", self.start)
      self.add_event_handler("message", self.message)

   async def start(self, event):
      self.send_presence()
      await self.get_roster()

   def message(self, msg):
      if msg['type'] in ('chat', 'normal'):
         user = msg['from']
         if not self.user_messages.get(user):
            self.user_messages[user] = []

         self.user_messages[user].append({"role": "user", "content": msg['body']})
         ollama_req = {'model': self.ollama_model, 'stream': False, 'messages': self.user_messages[user]}
         res = requests.post(self.ollama_url, json = ollama_req)
         if res.status_code == requests.codes.ok:
            response = res.json()['message']['content']
            msg.reply(response).send()
            self.user_messages[user].append({"role": "assistant", "content": response})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    xmpp = OllamaBridge(config['DEFAULT'])
    xmpp.connect()
    xmpp.process()
