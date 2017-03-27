from flask import Flask, request, Response
from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage
from random import choice

#This bot uses flask and kik api to send messages of random quotes to people
#it takes the messages from quotes.txt, where you just put one quote per line
#if you're using a local server for the bot use ngrok(https://ngrok.com/download)

def get_quotes():
    quotefile = open('quotes.txt')
    quotes = []
    for line in quotefile:
        quotes += [line.strip()]
    quotefile.close()
    return quotes

def random_quote():
    return choice(get_quotes())

BOT_USERNAME = ""
BOT_API_KEY = ""
WEBHOOK = "" #set this to the url ngrok gives you with the format of https://[ngrok url here]/incoming
print("Starting Flask App")
app = Flask(__name__)
kik = KikApi(BOT_USERNAME, BOT_API_KEY)

kik.set_configuration(Configuration(webhook=WEBHOOK))

@app.route('/incoming', methods=['POST'])
def incoming():
    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return Response(status=403)
    print("Checking for messages...")
    messages = messages_from_json(request.json['messages'])
    print(str(messages))
    for message in messages:
        if isinstance(message, TextMessage):
            print("Message '{}' recieved from '{}'".format(message.body, message.from_user))
            message_to_send = str(random_quote())
            print("Sending message: {}".format(message_to_send))
            kik.send_messages([
                TextMessage(
                    to=message.from_user,
                    chat_id=message.chat_id,
                    body=message_to_send
                )
            ])
    return Response(status=200)


if __name__ == "__main__":
    app.run(port=8080, debug=True)
