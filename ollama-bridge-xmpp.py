#!/usr/bin/env python3
__author__ = 'Jon Stratton'

import argparse, configparser, requests, slixmpp, pickle, os.path

# Only used if msg_history_file is set in the config
def read_history(msg_history_file):
   user_messages = {}
   if msg_history_file and os.path.exists(msg_history_file):
      file = open(msg_history_file, 'rb')
      user_messages = pickle.load(file)
      file.close()
   return user_messages

def write_history(msg_history_file, user_messages):
   if msg_history_file:
      file = open(msg_history_file, 'wb')
      pickle.dump(user_messages, file)
      file.close()
   return 0

class OllamaBridge(slixmpp.ClientXMPP):
   ollama_url = ''
   ollama_model = ''
   msg_history_file = ''
   msg_history_isolate = 1
   verbose = 0
   user_messages = {}
   def __init__(self, config):
      self.ollama_url = config['ollama_url']
      self.ollama_model = config['ollama_model']
      self.msg_history_file = config.get('msg_history_file', '')
      self.msg_history_isolate = int(config.get('msg_history_isolate', 1))
      self.verbose = int(config.get('verbose', 0))
      self.user_messages = read_history(self.msg_history_file)
      slixmpp.ClientXMPP.__init__(self, config['xmpp_username'], config['xmpp_password'])
      self.add_event_handler("session_start", self.start)
      self.add_event_handler("message", self.message)

   async def start(self, event):
      self.send_presence()
      await self.get_roster()

   def message(self, msg):
      if msg['type'] in ('chat', 'normal'):
         user = str(msg['from']).split('/')[0]

         # Isolate sessions
         session = 'all'
         if self.msg_history_isolate:
            session = user

         if not self.user_messages.get(session):
            self.user_messages[session] = []

         print("%s: %s" % (user, msg['body'])) if self.verbose else 0
         self.user_messages[session].append({"role": "user", "content": msg['body']})

         ollama_req = {'model': self.ollama_model, 'stream': False, 'messages': self.user_messages[session]}
         res = requests.post(self.ollama_url, json = ollama_req)
         if res.status_code == requests.codes.ok:
            response = res.json()['message']['content']
            msg.reply(response).send()

            print("%s: %s" % (self.ollama_model, response)) if self.verbose else 0
            self.user_messages[session].append({"role": "assistant", "content": response})
            write_history(self.msg_history_file, self.user_messages)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    xmpp = OllamaBridge(config['DEFAULT'])
    xmpp.connect()
    xmpp.process()
