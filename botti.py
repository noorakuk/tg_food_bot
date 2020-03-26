import telebot

import configfile as config

TOKEN  = config.TOKEN
food_bot = telebot.TeleBot(token=TOKEN)

@food_bot.message_handler(commands=['start']) 
def at_start(message):
    chatid = message.chat.id
    if message.content_type == 'text':
        text = 'Hei ' + message.from_user.first_name + '!'
        food_bot.send_message(chatid, text)


# food_bot.set_update_listener(listener) #register listener
food_bot.polling()
#Use none_stop flag let polling will not stop when get new message occur error.
food_bot.polling(none_stop=True)
# Interval setup. Sleep 3 secs between request new message.
food_bot.polling(interval=3)

while True: # Don't let the main Thread end.
    pass