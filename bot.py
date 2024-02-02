import telebot
from telebot import types

bot = telebot.TeleBot('6956163861:AAHiedP7PYOWS-QHeLSqyhGtJsm5aSkFrE8')

user_data = {}


@bot.message_handler(commands=['start'])
def handle_services_worker(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Для начала, давайте заполним некоторые дополнительные данные.")
    bot.send_message(user_id, "Введите ваше И.Ф.О(имя, фамилия, отчество):")
    bot.register_next_step_handler(message, handle_worker_info)


def handle_worker_info(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Теперь введите вашу дату рождения (дд.мм.гггг):")
    bot.register_next_step_handler(message, handle_worker_birthday)


def handle_worker_birthday(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Теперь введите ваши паспортные данные:")
    bot.register_next_step_handler(message, handle_worker_passport)


def handle_worker_passport(message):
    user_id = message.from_user.id
    bot.send_message(user_id,
                     "Отлично! Теперь вы можете использовать команду /services для просмотра доступных действий.")


@bot.message_handler(func=lambda message: user_data[message.from_user.id]['role'] == 'worker', commands=['services'])
def handle_services_worker(message):
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton("Подать заявку"))
    bot.send_message(user_id, "Выберите действие:", reply_markup=markup)


# "Take Order" request
@bot.message_handler(commands=['take_order'])
def handle_apply_service(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Введите id заказа, который вы принимаете, и цену за выполнение этого заказа.")
    bot.register_next_step_handler(message, handle_worker_order_info)


def handle_worker_order_info(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Вы успешно подали заявку на выполнение заказа.")


if __name__ == "__main__":
    bot.polling(none_stop=True)
