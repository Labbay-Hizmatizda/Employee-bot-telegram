import sqlite3
import telebot

bot = telebot.TeleBot('6956163861:AAHiedP7PYOWS-QHeLSqyhGtJsm5aSkFrE8')

user_data = {}

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

@bot.message_handler(commands=['start'])
def handle_services_worker(message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM workers WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        bot.send_message(user_id, "Добро пожаловать обратно!")
    else:
        bot.send_message(user_id, "Для начала, давайте заполним некоторые дополнительные данные.")
        bot.send_message(user_id, "Введите ваше И.Ф.О (имя, фамилия, отчество):")
        bot.register_next_step_handler(message, handle_worker_info)

def handle_worker_info(message):
    user_id = message.from_user.id
    user_name = message.text

    # Save user information to the database
    cursor.execute("INSERT INTO workers (user_id, user_name) VALUES (?, ?)", (user_id, user_name))
    conn.commit()

    bot.send_message(user_id, "Теперь введите вашу дату рождения (дд.мм.гггг):")
    bot.register_next_step_handler(message, handle_worker_birthday)

def handle_worker_birthday(message):
    user_id = message.from_user.id
    user_birthday = message.text

    # Save user birthday to the database
    cursor.execute("UPDATE workers SET birthday=? WHERE user_id=?", (user_birthday, user_id))
    conn.commit()

    bot.send_message(user_id, "Теперь введите ваши паспортные данные:")
    bot.register_next_step_handler(message, handle_worker_passport)

def handle_worker_passport(message):
    user_id = message.from_user.id
    user_passport = message.text

    cursor.execute("UPDATE workers SET passport=? WHERE user_id=?", (user_passport, user_id))
    conn.commit()

    bot.send_message(user_id, "Отлично! Теперь вы можете использовать команду /services для просмотра доступных действий.")


@bot.message_handler(commands=['services'])
def handle_services(message):
    pass


if __name__ == "__main__":
    bot.polling(none_stop=True)