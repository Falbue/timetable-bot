# bot_api = ""
bot_api = '' # бот для тестов
folder = 'data'
# folder = '/data'


import os
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import telebot
import re
from datetime import datetime
import pytz
from flask import Flask
import sys
sys.path.append(folder)
import threading

from timetable_html import *
from anekdots import *

if not os.path.exists(f"{folder}"):
    os.makedirs(f"{folder}")
    print("Папка библиотеки создана")
# Путь к папке с базой данных
folder_path = f"{folder}"
# Название файла базы данных
db_name = "database.db"

# Проверяем существует ли файл базы данных
db_path = os.path.join(folder_path, db_name)
if os.path.exists(db_path):
    print("База данных существует")
else:
    # Подключение к базе данных
    conn = sqlite3.connect(f"{folder}/database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER,
            course INTEGER,
            groupe INTEGER,
            time_registration INTEGER,
            id_message INTEGER);
        ''')
    # Закрытие соединения с базой данных
    conn.close()

bot = telebot.TeleBot(bot_api)

user_data = {}

hello_text = "Привет"
text_groups = "Выберите группу"
text_days = "Выберите день"
text_return = '< Назад'
# Клавиатуры
btn_return_group = InlineKeyboardButton(text = text_return, callback_data = 'return_course')
btn_return_weeks = InlineKeyboardButton(text = text_return, callback_data = 'return_weeks')
btn_return_days = InlineKeyboardButton(text = text_return, callback_data = 'return_days')
btn_return_timetable = InlineKeyboardButton(text = text_return, callback_data = 'return_timetable')
btn_return_profile = InlineKeyboardButton(text = text_return, callback_data = 'return_profile')
btn_return_keyboard_notification = InlineKeyboardButton(text = text_return, callback_data = 'notification')

btn_add_group = InlineKeyboardButton(text = '+ добавить группу', callback_data = 'new_group')
btn_profile = InlineKeyboardButton(text = '👤 Профиль', callback_data ='profile')

keyboard_groups = InlineKeyboardMarkup(row_width=2)
keyboard_notification = InlineKeyboardMarkup(row_width=3)
groups = {}
groups_notification = {}

conn = sqlite3.connect(f'{folder}/database.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
num_buttons = 0
row_buttons = []
row_buttons_notification = []

for table in tables:
    if table[0] == 'users':
        continue  # Пропуск таблицы с пользователями
    button_text = table[0].replace('_', '-')  # Текст кнопки
    button_notification_callback_data = f'{table[0]}_notification'
    button_callback_data = table[0]
    groups[table[0]] = table[0]
    groups_notification[table[0] + '_notification'] = f'{table[0]}_notification'
    button = InlineKeyboardButton(text=f'{button_text}', callback_data=button_callback_data)
    button_notification = InlineKeyboardButton(text=f'{button_text}', callback_data=button_notification_callback_data)
    row_buttons.append(button)
    row_buttons_notification.append(button_notification)
    num_buttons += 1
    if num_buttons == 2:
        keyboard_groups.add(*row_buttons)
        keyboard_notification.add(*row_buttons_notification)
        row_buttons = []
        row_buttons_notification = []
        num_buttons = 0

if num_buttons > 0:
    keyboard_groups.add(*row_buttons)
    keyboard_notification.add(*row_buttons_notification)
        
conn.close()

keyboard_groups.add(btn_add_group, btn_profile)
btn_delete_notification = InlineKeyboardButton(text = '× Отписаться', callback_data='unsubscribe')
keyboard_notification.add(btn_return_profile, btn_delete_notification)

btn_week_even = InlineKeyboardButton(text = 'Чётная', callback_data = 'week_even')
btn_week_odd = InlineKeyboardButton(text = 'Нечётная', callback_data = 'week_odd')
keyboard_weeks = InlineKeyboardMarkup(row_width = 2)
keyboard_weeks.add(btn_week_even, btn_week_odd, btn_return_weeks)

btn_day1 = InlineKeyboardButton(text = 'Понедельник', callback_data = 'day1')
btn_day2 = InlineKeyboardButton(text = 'Вторник', callback_data = 'day2')
btn_day3 = InlineKeyboardButton(text = 'Среда', callback_data = 'day3')
btn_day4 = InlineKeyboardButton(text = 'Четверг', callback_data = 'day4')
btn_day5 = InlineKeyboardButton(text = 'Пятница', callback_data = 'day5')
btn_day6 = InlineKeyboardButton(text = 'Суббота', callback_data = 'day6')
btn_week = InlineKeyboardButton(text = 'Неделя', callback_data = 'week')
keyboard_days = InlineKeyboardMarkup(row_width = 2)
keyboard_days.add(btn_day1, btn_day2, btn_day3, btn_day4, btn_day5, btn_day6, btn_week)
keyboard_days.add(btn_return_days)

keyboard_profile = InlineKeyboardMarkup(row_width = 1)
btn_notification = InlineKeyboardButton(text = 'Уведомления', callback_data = 'notification')
btn_schedule_call = InlineKeyboardButton(text = 'Расписание звонков', callback_data = 'schedule_call')
keyboard_profile.add(btn_notification, btn_schedule_call, btn_return_weeks)

keyboard_timetable = InlineKeyboardMarkup(row_width=2)
keyboard_timetable.add(btn_return_timetable)

keyboard_start_message = InlineKeyboardMarkup()
keyboard_start_message.add(InlineKeyboardButton(text = 'Прочитано', callback_data = 'del_message'))

keyboard_return_group = InlineKeyboardMarkup()
keyboard_return_group.add(btn_return_weeks)

keyboard_return_profile = InlineKeyboardMarkup()
keyboard_return_profile.add(btn_return_profile)

keyboard_return_notification = InlineKeyboardMarkup()
keyboard_return_notification.add(btn_return_keyboard_notification)



def now_time():
    now = datetime.now()
    tz = pytz.timezone('Europe/Moscow')
    now_moscow = now.astimezone(tz)
    current_time = now_moscow.strftime("%H:%M")
    current_date = now_moscow.strftime("%m.%d.%Y")
    date = f"{current_date} {current_time}"
    return date

def get_weekday():
    import datetime
    weekday = datetime.datetime.today().weekday()
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    return days[weekday]

def current_week():
    import datetime
    today = datetime.date.today()
    week_number = today.isocalendar()[1]
    if week_number % 2 == 0: x = 'чётная неделя'
    else: x = 'нечётная неделя'
    return x

def notification():
    conn = sqlite3.connect(f'{folder}/database.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users"
    cursor.execute(query)
    result = cursor.fetchall()
    message = ""
    for row in result:
        user = row[0]
        id_message = row[4]
        group = row[2]
        if str(group) != '0':
            try:
                x = current_week()
                if x == 'чётная неделя': week = 'Четная'
                else: week = 'Нечетная'
                
                day = get_weekday()
                # Подключение к базе данных
                table_name = group
                query = f"SELECT * FROM {table_name} WHERE week = '{week}' AND day = '{day}'"
                cursor.execute(query)
                result = cursor.fetchall()
                # Создание строки с несколькими строками
                message = ""
                prev_pair = ""
                for row in result:
                    if row[2] != prev_pair:
                        time = row[8].replace('-', '\-')
                        message += f"\n*{row[2]} пара* • _{time}_\n"
                    if row[7] == 0:
                        group_text = ''
                    else:
                        group_text = f'__Группа: *{row[7]}*__\n'
                    aud = row[6].replace('-', '\-')
                    aud = aud.replace('.','')
                    aud = aud.replace('+', 'отсутствует')
                    lesson = row[3].replace('-', '\-')
                    lesson = lesson.replace('(', '"')
                    lesson = lesson.replace(')', '"')
                    message += f"{group_text}*{lesson}* • _{row[5]}_\n*{row[4]}* • {aud}\n"
                    prev_pair = row[2]
            
                # Отправка сообщения
                if message == '':
                    message = "Расписания на сегодня нет"
                group = group.replace("_", "\-")
                bot.send_message(chat_id=user, text=f'Сегодня __*{day.upper()}*__ • {group}\n{message}', reply_markup = keyboard_start_message, parse_mode = 'MarkdownV2')
            except Exception as e:
                print(f'Ошибка в уведомлении: {e}')
                print(f"Пользователь {user} заблокировал бота")
    conn.close()

    try:
        x = anek()
        bot.send_message(chat_id=1000533946, text=f"{x}", reply_markup = keyboard_start_message)
    except Exception as e:
        print(f"Ошибка в анекдоте: {e}")
        bot.send_message(chat_id=1000533946, text='Я где то проебался, но здесь должен был быть анекдот', reply_markup = keyboard_start_message, parse_mode = 'MarkdownV2')
        bot.send_message(chat_id=1210146115, text=f"Ошибка в анекдоте: {e}", reply_markup = keyboard_start_message)


def timetable_day(call, day):
    group = user_data[call.message.chat.id]['group']
    week = user_data[call.message.chat.id]['week']
    # Подключение к базе данных
    conn = sqlite3.connect(f'{folder}/database.db')
    cursor = conn.cursor()
    table_name = group
    query = f"SELECT * FROM {table_name} WHERE week = '{week}' AND day = '{day}'"
    cursor.execute(query)
    result = cursor.fetchall()
    # Создание строки с несколькими строками
    message = ""
    prev_pair = ""
    for row in result:
        if row[2] != prev_pair:
            time = row[8].replace('-', '\-')
            message += f"\n*{row[2]} пара* • _{time}_\n"
        if row[7] == 0:
            group_text = ''
        else:
            group_text = f'__Группа: *{row[7]}*__\n'
        aud = row[6].replace('-', '\-')
        aud = aud.replace('.','')
        aud = aud.replace('+', 'отсутствует')
        lesson = row[3].replace('-', '\-')
        lesson = lesson.replace('(', '"')
        lesson = lesson.replace(')', '"')
        message += f"{group_text}*{lesson}* • _{row[5]}_\n*{row[4]}* • {aud}\n"
        prev_pair = row[2]

    # Отправка сообщения
    if message == '':
        message = "Расписания на этот день нет"
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message, reply_markup = keyboard_timetable, parse_mode = 'MarkdownV2')
    # Закрытие соединения с базой данных
    conn.close()

def new_group(message):
    x = message.text
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print('Ошибка при удалении сообщения')
    successfully = new_timetable(x)
    print(successfully)

    conn = sqlite3.connect(f'{folder}/database.db')
    cursor = conn.cursor()
    if successfully == False:
        query = f"SELECT * FROM users WHERE user_id = '{message.chat.id}'"
        cursor.execute(query)
        result = cursor.fetchall()
        message = ""
        user = result[0][0]
        id_message = result[0][4]
        bot.edit_message_text(chat_id=user, message_id=id_message, text="Группа не найдена", reply_markup = keyboard_return_group)
    if successfully == True:
        query = f"SELECT * FROM users"
        cursor.execute(query)
        result = cursor.fetchall()
        message = ""
        for row in result:
            user = row[0]
            id_message = row[4]
            bot.edit_message_text(chat_id=user, message_id=id_message, text="Добавление группы. Ожидайте...", reply_markup = '')
        dasd

@bot.message_handler(commands=['start'])
def start(message):
    message_id = message.id+1
    print(message_id)
    conn = sqlite3.connect(f'{folder}/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (message.chat.id,))
    result = c.fetchone()
    if result is None:
        date_registration = now_time()
        c.execute("INSERT INTO users (user_id, course, groupe, time_registration, id_message) VALUES (?, ?, ?, ?, ?)",
                  (message.chat.id, 0, 0, date_registration, message_id))
        conn.commit()
        conn.close()
        print('Зарегистрирован новый пользователь', message.chat.id)
    else:
        c.execute(f"UPDATE users SET id_message = {(message_id)} WHERE user_id = {message.chat.id}")
        print('Пользователь' ,message.chat.id,'уже существует в базе')
        conn.commit()
        pass
    conn.close()
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.send_message(message.chat.id, text_groups, reply_markup = keyboard_groups)

@bot.message_handler(commands=['info_users'])
def info_users(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    conn = sqlite3.connect(f'{folder}/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    result = c.fetchall()
    message = ''
    for row in result:
        message += f'{row}\n'
    bot.send_message(chat_id=1210146115, text=message, reply_markup = keyboard_start_message)
    conn.close()

@bot.message_handler(commands=['anekdot'])
def info_users(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    x = anek()
    bot.send_message(message.chat.id, x, reply_markup = keyboard_start_message)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data in groups:
        if call.message.chat.id not in user_data:
            user_data[call.message.chat.id] = {}
        print(call.data)
        group = groups[call.data]
        user_data[call.message.chat.id]['group'] = group
        text_weeks = f'Выберите неделю\nСейчас __*{current_week()}*__'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_weeks, reply_markup=keyboard_weeks, parse_mode = 'MarkdownV2')

    weeks = {'week_even': 'Четная', 'week_odd': "Нечетная"}
    if call.data in weeks.keys():
        week = weeks[call.data]
        user_data[call.message.chat.id]['week'] = week
        week_day = get_weekday()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{text_days}\nСейчас __*{week_day}*__', reply_markup=keyboard_days, parse_mode = 'MarkdownV2')

    days = {'day1': 'Понедельник', 'day2': 'Вторник', 'day3': 'Среда', 'day4': "Четверг", 'day5': "Пятница", 'day6': "Суббота"}
    if call.data in days.keys():
        day = days[call.data]
        timetable_day(call, day)

    if call.data == 'week':
        group = user_data[call.message.chat.id]['group']
        week = user_data[call.message.chat.id]['week']
        # Подключение к базе данных
        conn = sqlite3.connect(f'{folder}/database.db')
        cursor = conn.cursor()
        # SQL-запрос для получения данных за первый день
        table_name = group
        query = f"SELECT * FROM {table_name} WHERE week = '{week}'"
        # Выполнение запроса и получение результатов
        cursor.execute(query)
        result = cursor.fetchall()
        # Создание строки с несколькими строками
        message = ""
        day_pair = ''

        for row in result:
            prev_pair = ''
            if row[1] != day_pair:
                message += f"\n*__{row[1].upper()}__*\n"
                day_pair = row[1]
            if row[2] != prev_pair:
                time = row[8].replace('-', '\-')
                message += f"\n*{row[2]} пара* • _{time}_\n"
                prev_pair = row[2]

            if row[7] == 0:
                group_text = ''
            else:
                group_text = f'__Группа: *{row[7]}*__\n'
            aud = row[6].replace('-', '\-')
            aud = aud.replace('.','')
            aud = aud.replace('+', 'отсутствует')
            lesson = row[3].replace('-', '\-')
            lesson = lesson.replace('(', '"')
            lesson = lesson.replace(')', '"')
            message += f"{group_text}*{lesson}* • _{row[5]}_\n*{row[4]}* • {aud}\n"
        
        # Отправка сообщения
        if message == '':
            message = "Расписание на неделю отсутствует"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=message, reply_markup=keyboard_timetable, parse_mode = 'MarkdownV2')
        # Закрытие соединения с базой данных
        conn.close()

    if call.data == 'new_group':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите свою группу", reply_markup=keyboard_return_group)
        bot.register_next_step_handler(call.message, new_group)

    if call.data == 'profile':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ваш профиль", reply_markup=keyboard_profile)

    if call.data == 'schedule_call':
        with open(f'{folder}/call.txt', 'r+', encoding='utf-8') as f:
            shedule_call_text = f.read()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=shedule_call_text, reply_markup=keyboard_return_profile)

    if call.data == 'notification':
        conn = sqlite3.connect(f'{folder}/database.db')
        cursor = conn.cursor()
        query = f"SELECT groupe FROM users WHERE user_id = '{call.message.chat.id}'"
        cursor.execute(query)
        result = cursor.fetchall()
        if str(result[0][0]) == '0':
            text = 'Выберите группу, что бы подписаться на уведомления'
        else:
            result = result[0][0].replace("_", '-')
            text = f"Вы подписаны на группу: {result}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard_notification)

    if call.data in groups_notification:
        group_notification = str(groups_notification[call.data])
        group_notification = group_notification.replace('_notification', "")
        conn = sqlite3.connect(f'{folder}/database.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET groupe = '{group_notification}' WHERE user_id = {call.message.chat.id}")
        conn.commit()
        conn.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Вы подписались на уведомление, которое будет приходить Вам в 7:30 и присылать расписание на сегодня', reply_markup=keyboard_return_notification)

    if call.data == 'unsubscribe':
        conn = sqlite3.connect(f'{folder}/database.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET groupe = 0 WHERE user_id = {call.message.chat.id}")
        conn.commit()
        conn.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Вы отписались от уведомлений', reply_markup=keyboard_return_notification)



    if call.data == 'return_main':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=hello_text, reply_markup = keyboard_main)
        course = 0
    if call.data == 'return_course':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_course, reply_markup = keyboard_courses)
        group = 0
    if call.data == 'return_weeks':
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        week = 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_groups, reply_markup = keyboard_groups)
    if call.data == 'return_days':
        day_edit = 0
        text_weeks = f'Выберите неделю\nСейчас __*{current_week()}*__'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_weeks, reply_markup=keyboard_weeks, parse_mode = 'MarkdownV2')
    if call.data == 'return_timetable':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text_days, reply_markup = keyboard_days)
    if call.data == 'return_profile':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ваш профиль", reply_markup=keyboard_profile)



    if call.data == 'del_message':
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception as e:
            print("Сообщение не удалено")



def send_start_message():
    conn = sqlite3.connect(f'{folder}/database.db')
    cursor = conn.cursor()
    # SQL-запрос для получения данных за первый день
    query = f"SELECT * FROM users"
    # Выполнение запроса и получение результатов
    cursor.execute(query)
    result = cursor.fetchall()
    # Создание строки с несколькими строками
    time = now_time()
    message = ""
    for row in result:
        user = row[0]
        id_message = row[4]
        print(id_message)
        # Получаем идентификатор чата, из которого необходимо удалить сообщения
        chat_id = user
        try:
            bot.edit_message_text(chat_id=user, message_id=id_message, text="Обновление...", reply_markup = '')
            bot.edit_message_text(chat_id=user, message_id=id_message, text=text_groups, reply_markup = keyboard_groups)
        except Exception as e:
            print(f'Ошибка в старте: {e}')
            print(f"Пользователь {user} заблокировал бота")
    # Закрытие соединения с базой данных
    try:
        with open(f'{folder}/log.txt', 'r+', encoding='utf-8') as f:
            text_error = f.read()
    except Exception as e:
        text_error = "Нет файла с логом"
        print(f'Ошибка в поиске лога: {e}')
    with open(f'{folder}/log.txt', 'w+', encoding='utf-8') as f:
        print("Файл с логом, очищен")
    bot.send_message(chat_id=1210146115, text=f"Бот перезапущен\n{time}\nОшибка: {text_error}", reply_markup = keyboard_start_message)
    x = anek()
    bot.send_message(chat_id=1210146115, text=f"{x}", reply_markup = keyboard_start_message)
    conn.close()

def notification_thread():
    import datetime
    import time
    while True:
        now = datetime.datetime.now()
        tz = pytz.timezone('Europe/Moscow')
        now = now.astimezone(tz)
        weekday = get_weekday()
        if weekday != 'Воскресенье':
            if now.hour == 5 and now.minute == 30:
                notification()
        time.sleep(60)


# bot.polling()
try:
    thread = threading.Thread(target=notification_thread)
    thread.start()
    send_start_message()
    time = now_time()
    bot.polling()
    print(f'Бот запущен...n{time}')
except Exception as e:
    print(f"Ошибка: {e}")
    with open(f'{folder}/log.txt', 'w+', encoding='utf-8') as f:
        f.write(str(e))
    send_start_message()
    time = now_time()
    print(f'Бот запущен...n{time}')
    thread = threading.Thread(target=notification_thread)
    thread.start()
    bot.polling()