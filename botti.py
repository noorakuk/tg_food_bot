# Importing stuff
import telebot
import psycopg2
import configfile as config

TOKEN  = config.TOKEN
food_bot = telebot.TeleBot(token=TOKEN)

# Needed functions
def dbConnection(conn):
    # DB connection
    conn = psycopg2.connect(host=config.HOST, database=config.DATABASE, user=config.USER, password=config.PASSWORD)
    return conn


@food_bot.message_handler(commands=['start']) 
def at_start(message):
    chatid = message.chat.id
    if message.content_type == 'text':
        text = 'Hei ' + message.from_user.first_name + '!'
        food_bot.send_message(chatid, text)

# Shoud add the new item to the db, table based on the chat id
@food_bot.message_handler(commands=['newItem'])
def add_new(message):
    chatid = message.chat.id
    print(message.content )
    


# Create new table IF the chat is not in the db
def createTableIfNotExcist():
    creationQuery = """
        CREATE TABLE IF NOT EXISTS groceries (
            chatid NUMERIC NOT NULL,
            item VARCHAR(20)  NOT NULL,
            amount INTEGER
            );
        """
    conn = None
    try:
        # Create connection
        conn = dbConnection(conn)
        cur = conn.cursor()
        # create table 
        cur.execute(creationQuery)
        # closes communication with the database server
        cur.close()
        # commit changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

createTableIfNotExcist()
# food_bot.set_update_listener(listener) #register listener
food_bot.polling()
#Use none_stop flag let polling will not stop when get new message occur error.
food_bot.polling(none_stop=True)
# Interval setup. Sleep 3 secs between request new message.
food_bot.polling(interval=3)

while True: # Don't let the main Thread end.
    pass


def insertNewItem(chatid, item, amount):
    sql = """INSERT INTO groceries(chatid, item, amount)
             VALUES(%s) RETURNING vendor_id;"""