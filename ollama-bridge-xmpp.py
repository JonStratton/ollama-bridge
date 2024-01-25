#!/usr/bin/env python3
__author__ = 'Jon Stratton'

import argparse, configparser, requests, slixmpp

class OllamaBridge(slixmpp.ClientXMPP):
   ollama_url = ''
   ollama_model = ''
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
         ollama_req = {'model': self.ollama_model, 'prompt': msg['body'], 'stream': False}
         res = requests.post(self.ollama_url, json = ollama_req)
         if res.status_code == requests.codes.ok:
            msg.reply(res.json()['response']).send()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    xmpp = OllamaBridge(config['DEFAULT'])
    xmpp.connect()
    xmpp.process()
