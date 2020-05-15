# Importing stuff
import telebot
import psycopg2
from configfile import * 
config = Config()

TOKEN  = config.TOKEN
food_bot = telebot.TeleBot(TOKEN)

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
    conn = psycopg2.connect(host=config.HOST, database=config.DATABASE, user=config.USER, password=config.PASSWORD)
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

@food_bot.message_handler(commands=['start']) 
def at_start(message):
    chatid = message.chat.id
    if message.content_type == 'text':
        text = 'Hei ' + message.from_user.first_name + '!'
        food_bot.send_message(chatid, text)


# Needed functions
def dbConnection(conn):
    # DB connection
    conn = psycopg2.connect(host=config.HOST, database=config.DATABASE, user=config.USER, password=config.PASSWORD)
    return conn


def insertNewItem(chatid, item, amount):
    sql = """INSERT INTO groceries(chatid, item, amount)
             VALUES(%s, %s, %s)"""
    conn = None
    try:
        conn = dbConnection(conn)
        cur = conn.cursor()
        cur.execute(sql, (str(chatid), item, str(amount)))

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def getShoppingList(chatid):
    sql = """SELECT 
                item, amount 
            FROM
                groceries
            WHERE
                chatid = %s
            ORDER BY item"""
    conn = None
    result = []
    try:
        conn = dbConnection(conn)
        cur = conn.cursor()
        cur.execute(sql, [str(chatid)])
        row = cur.fetchone()

        while row is not None:
            print(row)
            result.append(row)
            row = cur.fetchone()

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    
    return result

def emptyShoppingList(chatid):
    sql = """DELETE FROM
                groceries
            WHERE
                chatid = %s"""
    conn = None
    result = []
    try:
        conn = dbConnection(conn)
        cur = conn.cursor()
        cur.execute(sql, [str(chatid)])

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

# Shoud add the new item to the db, table based on the chat id
@food_bot.message_handler(commands=['add'])
def add_new(message):
    chatid = message.chat.id
    words = message.text.split()
    if len(words) == 3 or len(words) == 2:
        # Check if the third argument is the number
        amount = 1
        if len(words) == 3:
            try: 
                amount = int(words[2])
            except ValueError:
                text = "Toinen parametri pitäisi olla kokonaisluku"
                food_bot.send_message(chatid, text)
                return
        # Add item to the database
        item = words[1]
        insertNewItem(chatid, item, amount)
        # Send confirm message
        text = "Tuote " + item + " lisätty kauppalistaan"
        food_bot.send_message(chatid, text)
    else:
        text = """Ensimmäinen sana on tuote, joka lisätään kauppalistaan. Jos haluat lisätä tuotteiden määrän, voit laittaa sen toiseksi parametriksi."""
        food_bot.send_message(chatid, text)

@food_bot.message_handler(commands=['list'])
def getItems(message):
    chatid = message.chat.id
    shoppingList = getShoppingList(chatid)
    print(shoppingList)

    text = 'Kauppalista: \n'
    for item in shoppingList:
        text = text + item[0] + " x" + str(item[1]) + "\n"

    food_bot.send_message(chatid, text)

@food_bot.message_handler(commands=['clear'])
def clearList(message):
    chatid = message.chat.id
    emptyShoppingList(chatid)
    text = "Kauppalista tyhjennetty"
    food_bot.send_message(chatid, text)

# SHOULD BE END OF THE FILE BECAUSE OF THE PYTHON 
# food_bot.set_update_listener(listener) #register listener
food_bot.polling()
#Use none_stop flag let polling will not stop when get new message occur error.
food_bot.polling(none_stop=True)
# Interval setup. Sleep 3 secs between request new message.
food_bot.polling(interval=3)

while True: # Don't let the main Thread end.
    pass
