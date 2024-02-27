import sqlite3
import telebot
from datetime import datetime

bot = telebot.TeleBot('6956163861:AAHiedP7PYOWS-QHeLSqyhGtJsm5aSkFrE8')

user_data = {}

conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
cursor = conn.cursor()


user_info = {}


@bot.message_handler(commands=['log_into'])
def handle_services_worker(message):
    user_id = message.from_user.id
    user_info[user_id] = {}

    cursor.execute("SELECT * FROM admin_page_app_employee WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        bot.send_message(user_id, "Добро пожаловать обратно! tipa regestratsiya otboldi")
    elif message.contact.phone_number if message.contact else False:
        bot.send_message(user_id, "Для начала, давайте заполним некоторые дополнительные данные.")
        bot.send_message(user_id, "Введите ваше номер телефона:")
        bot.register_next_step_handler(message, check_handle_phone_number)
    else:
        bot.send_message(user_id, "Добро пожаловать обратно!, tipa regestratsiya otboldi")


def check_handle_phone_number(message):
    user_id = message.from_user.id
    phone_number = message.text
    # ToDo: checking if phone number written valid
    user_info[user_id]['phone_number'] = phone_number
    if phone_number:
        cursor.execute("SELECT * FROM admin_page_app_employee WHERE phone_number=?", (phone_number,))
        existing_user = cursor.fetchone()

        if existing_user:
            bot.send_message(phone_number, "Добро пожаловать обратно!")
        else:
            bot.send_message(phone_number, "Yengi useraka, keyingi stepga otamiz")
            bot.send_message(phone_number, "Введите ваше имя:")
            bot.register_next_step_handler(message, handle_name)


def handle_phone(message):
    phone_number = message.text
    user_info[phone_number] = {}
    bot.send_message(phone_number, "Thank you. Now we can proceed.")

    print(user_info[user_id]['phone_number'])
    bot.send_message(user_id, "Введите ваше имя как указано в паспорте:")
    bot.register_next_step_handler(message, handle_name)

def handle_name(message):
    user_id = message.from_user.id
    user_info[user_id]['name'] = message.text

    bot.send_message(user_id, "Введите вашу фамилию как указано в паспорте:")
    bot.register_next_step_handler(message, handle_surname)


def handle_surname(message):
    user_id = message.from_user.id
    user_info[user_id]['surname'] = message.text

    bot.register_next_step_handler(message, insert_all_user_data)


def insert_all_user_data(message):
    user_id = message.from_user.id

    date_created = datetime.now()
    cursor.execute("INSERT INTO admin_page_app_employee (user_id, name, surname, phone_number, date_created) VALUES ("
                   "?, ?, ?, ?, ?)",
                   (user_id, user_info[user_id]['name'], user_info[user_id]['surname'], user_info[user_id]['phone_number'], date_created))
    conn.commit()

    bot.send_message(user_id,
                     "Отлично! Теперь вы можете использовать команду /jobs для просмотра доступных действий.")
    
# @bot.message_handler(commands=['add_proposal'])
# def handle_add_proposal(message):
#     set_user_state(message.chat.id, "ADD_ORDER")
#     bot.send_message(message.from_user.id, "Please enter the order ID.")
#     bot.register_next_step_handler(message, handle_order)
#
# def handle_order(func=lambda message: get_user_state(message.chat.id) == "ADD_ORDER"):
#     set_user_data(message.chat.id, "order", message.text)
#     set_user_state(message.chat.id, "ADD_MESSAGE")
#     bot.send_message(message.from_user.id, "Please enter your message to the order owner.")
#     bot.register_next_step_handler(message, handle_message)
#
# @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "ADD_MESSAGE")
# def handle_message(message):
#     set_user_data(message.chat.id, "message", message.text)
#     set_user_state(message.chat.id, "ADD_PRICE")
#     bot.reply_to(message, "Please set the price.")
#
# @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "ADD_PRICE")
# def handle_price(message):
#     set_user_data(message.chat.id, "price", message.text)
#     set_user_data(message.chat.id, "owner", message.from_user.id)
#     set_user_state(message.chat.id, "DONE")
#
#     # Save to db
#     conn = sqlite3.connect('your_database.db')  # replace with your database
#     c = conn.cursor()
#     c.execute("INSERT INTO admin_page_app_proposal (owner, order, message, price) VALUES (?, ?, ?, ?)",
#               (get_user_data(message.chat.id, "owner"), get_user_data(message.chat.id, "order"),
#                get_user_data(message.chat.id, "message"), get_user_data(message.chat.id, "price")))
#     conn.commit()
#
#     bot.reply_to(message, "Proposal has been added successfully.")
#

@bot.message_handler(commands=['proposals'])
def list_job_proposals(message):
    user_id = message.chat.id
    cursor.execute("SELECT id FROM admin_page_app_employee where user_id=?", (user_id,))
    id = cursor.fetchone()
    print(id)
    cursor.execute("SELECT * FROM admin_page_app_proposal WHERE owner_id=?", (id,))
    proposals = cursor.fetchall()
    print(proposals)

    for proposal in proposals:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Edit', callback_data=f'edit_{proposal[0]}'),
                   types.InlineKeyboardButton(text='Cancel', callback_data=f'cancel_{proposal[0]}'))
        bot.send_message(chat_id, f'Proposal {proposal[0]}: {proposal[1]}', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    action, proposal_id = call.data.split('_')
    if action == 'edit':
        # Handle editing
        pass
    elif action == 'cancel':
        # Handle cancelation
        pass



if name == "__main__":
    bot.polling(none_stop=True)