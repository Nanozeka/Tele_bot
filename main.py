
import sqlite3
import threading
import telebot
from telebot import types
import time


# Подключение к базе данных SQLite
conn = sqlite3.connect('C:/GeekBrains/Diplom/Clean_car/myapp/data_base.sqlite3', check_same_thread=False)
c = conn.cursor()


# Функция для получения списка всех клиентов из базы данных
def get_all_clients():
    c.execute("SELECT * FROM main_servicerecord")
    rows = c.fetchall()
    return rows


# Функция для получения новых данных из базы данных
def get_new_data_from_database():
    c.execute("SELECT * FROM main_servicerecord")
    rows = c.fetchall()
    return rows


# Создание экземпляра телеграм бота
bot = telebot.TeleBot('6491672056:AAEhekG23BQ9pZh2ysJCRVcqLzPpXPKsqCo')


chat_id = '1456342409'
# Обработчик отправки сообщения "Новые клиенты"
@bot.message_handler(func=lambda message: message.text == "Список клиентов")
def handle_new_clients(message):
    global chat_id
    chat_id = message.chat.id
    # Получение всех клиентов из базы данных
    clients = get_all_clients()

    # Формирование ответного сообщения
    response = "Список клиентов: \n"
    for client in clients:
        response += f"ID: {client[0]}, Имя: {client[1]}, Дата: {client[2]}, Телефон: {client[3]}, Комментарий: {client[4]}, Услуга: {client[5]}\n"

    # Создание клавиатуры для вывода списка клиентов
    keyboard = types.InlineKeyboardMarkup()
    kb_button = types.InlineKeyboardButton(text="Список клиентов", callback_data="show_clients")
    keyboard.add(kb_button)

    # Отправка ответного сообщения
    bot.reply_to(message, "Все клиенты", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "show_clients")
def callback_show_clients(call):
    # Получение всех клиентов из базы данных
    clients = get_all_clients()

    # Формирование ответного сообщения
    response = "Список клиентов: \n"
    for client in clients:
        # response += f"ID: {client[0]}, Имя: {client[1]}, Фамилия: {client[2]}\n"
        response += f"ID: {client[0]}, Имя: {client[1]}, Дата: {client[2]}, Телефон: {client[3]}, Комментарий: {client[4]}, Услуга: {client[5]}\n"

    # Отправка списка клиентов в чат
    bot.send_message(call.message.chat.id, response)

    # Вывод информации о новых клиентах
def check_new_data_from_database(chat_id):
    while True:
        old_data = get_new_data_from_database()

        time.sleep(10)  # Подождать некоторое время

        new_data = get_new_data_from_database()

        changes = []  # Список для хранения измененных данных

        for data in new_data:
            if data not in old_data:
                changes.append(data)

        if changes:
            # Отправить уведомление о наличии измененных данных
            response = "Вы получили новые данные:"
            for data in changes:
                response += f"ID: {data[0]}, Имя: {data[1]}, Дата: {data[2]}, Телефон: {data[3]}, Комментарий: {data[4]}, Услуга: {data[5]}\n"


            bot.send_message(chat_id, response)

        old_data = new_data

    # Удаление клиентов
def delete_client_from_database(client_id):
    c.execute("DELETE FROM main_servicerecord WHERE id=?", (client_id,))
    conn.commit()

@bot.message_handler(func=lambda message: message.text.startswith("/delete_client"))
def handle_delete_client(message):
    # Разбиваем команду на аргументы, чтобы получить id клиента
    command_parts = message.text.split()
    if len(command_parts) == 2:
        client_id = command_parts[1]
        delete_client_from_database(client_id)
        bot.reply_to(message, f"Клиент с id {client_id} успешно удален")
    else:
        bot.reply_to(message, "Некорректная команда на удаление клиента")




# Запуск проверки новых данных в отдельном потоке
check_data_thread = threading.Thread(target=check_new_data_from_database, args=(chat_id,))

check_data_thread.start()

# Запуск бота
bot.polling(none_stop=True)
