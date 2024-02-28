import sqlite3
import telebot
from telebot import types
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

    else:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        reg_button = types.KeyboardButton(text="Nomeringizni taqdim eting", request_contact=True)
        keyboard.add(reg_button)
        response = bot.send_message(message.chat.id,
                                    "You should share your phone number",
                                    reply_markup=keyboard)
        bot.register_next_step_handler(message, check_handle_phone_number)


def check_handle_phone_number(message):
    user_id = message.from_user.id
    print(message.contact.phone_number)
    phone_number = message.contact.phone_number
    user_info[user_id]['phone_number'] = phone_number
    if phone_number:
        cursor.execute("SELECT * FROM admin_page_app_employee WHERE phone_number=?", (phone_number,))
        existing_user = cursor.fetchone()

        if existing_user:
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            yes_button = types.KeyboardButton(text="Xa 🟢")
            no_button = types.KeyboardButton(text="Yoq 🔴, boshqa nomer teraman")
            keyboard.add(yes_button, no_button)
            bot.send_message(user_id, "Bu nomerga akk bor, ikta akkni ulashi xolisizmi", reply_markup=keyboard)
            bot.register_next_step_handler(message, handle_user_id_relations)
        else:
            bot.send_message(user_id, "Yengi useraka, keyingi stepga otamiz")
            bot.send_message(user_id, "Введите ваше имя:")
            bot.register_next_step_handler(message, handle_name)


def handle_user_id_relations(message):
    if message.text == "Xa":
        # ToDo: add user_id to accounts_reletion table
        ...
    elif message.text == "Yoq, boshqa nomer teraman":
        bot.send_message(user_id, "nomer tering! masalan: 901231212")
        bot.register_next_step_handler(message, handle_phone)
    else:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)
        yes_button = types.KeyboardButton(text="Xa")
        no_button = types.KeyboardButton(text="Yoq, boshqa nomer teraman")
        keyboard.add(yes_button, no_button)
        bot.send_message(user_id, "Soobsheniyezi chunmadin, pasdigi knopkaladan bittasini ishlatin:", reply_markup=keyboard)
        bot.register_next_step_handler(message, handle_user_id_relations)

def handle_phone(message):
    phone_number = message.text
    user_info[phone_number] = {}
    bot.send_message(user_id, "Thank you. Now we can proceed.")

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


proposals = {}
@bot.message_handler(commands=['add_proposal'])
def handle_add_proposal(message):
    proposals[message.from_user.id] = {}
    bot.send_message(message.from_user.id, "Please enter the order ID.")
    bot.register_next_step_handler(message, handle_order)


def handle_order(message):
    user_id = message.from_user.id
    order_id = message.text
    proposals[user_id]['order_id'] = order_id
    bot.send_message(user_id, "Please enter your message to the order owner.")
    bot.register_next_step_handler(message, handle_message)


def handle_message(message):
    user_id = message.from_user.id
    message_text = message.text
    proposals[user_id]['message'] = message_text
    bot.send_message(message, "Please set the price.")
    bot.register_next_step_handler(message, handle_price)


def handle_price(message):
    user_id = message.from_user.id
    price = message.text
    proposals[user_id]['price'] = price

    for user_id, proposal_data in proposals.items():
        cursor.execute("INSERT INTO admin_page_app_proposal (message, price, order_id, owner_id) VALUES (?, ?, ?, ?)",
                      (proposal_data['message'], proposal_data['price'], proposal_data['order_id'], user_id))

    conn.commit()

    bot.send_message(message, "Отлично! Теперь вы можете использовать команду /proposals для просмотра доступных proposallar.")


@bot.message_handler(commands=['proposals'])
def list_job_proposals(message):
    user_id = message.chat.id
    # cursor.execute("SELECT owner_id FROM admin_page_app_employee where user_id=?", (user_id,))
    # id = cursor.fetchone()
    # print(id)
    cursor.execute("SELECT * FROM admin_page_app_proposal WHERE owner_id=?", (user_id,))
    proposals = cursor.fetchall()
    print(proposals)

    for proposal in proposals:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Edit', callback_data=f'edit_{proposal[0]}'),
                   types.InlineKeyboardButton(text='Cancel', callback_data=f'cancel_{proposal[0]}'))
        bot.send_message(user_id, f'Proposal {proposal[0]}: {proposal[1]}', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    action, proposal_id = call.data.split('_')
    if action == 'edit':
        # Handle editing
        pass
    elif action == 'cancel':
        # Handle cancelation
        pass



if __name__ == "__main__":
    bot.polling(none_stop=True)