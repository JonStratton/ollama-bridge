# ollama-bridge

./ollama-bridge-xmpp.py -c ./xmpp.cfg

## Config Options
verbose - Turns on chat logging to standard out.
ollama_url – The URL for the ollama chat API. Probably http://localhost:11434/api/chat.
ollama_model – The model to use.  
xmpp_username – The XMPP/Jabber username (with domain). So something like user@jabber.example.com.
xmpp_password – The XMPP/Jabber password.
msg_history_isolate – Defaults to 1 (true). If set to 0 (false), all messages will be treated like one large chat with the same user. So if multiple people are talking to the model, it will appear to be the same user to the model.
msg_history_file – The local file + path of the chat history. This allows persistence across process restarts.
