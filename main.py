import datetime
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot_calendar import LSTEP, WYearTelegramCalendar
from geopy.geocoders import Nominatim
import json
import requests
import os
from validate_email import validate_email
import atexit
import random
from PIL import Image

geolocator = Nominatim(user_agent="tg_bot")
url = 'https://tools.emailmatrix.ru/event-generator/'
myobj = {
    "apikey": "AAFfAT_ggb_QS8Shwp6G2aNbuid69pfSNQ4",
    "start": "2021-09-28 00:00",
    "end": "2021-09-28 01:00",
    "timezone": "Europe/Moscow",
    "title": "Событие",
    "url": "http://emailmatrix.ru",
    "location": "г. Рязань, 390010, ул. Октябрьская, д. 65, H264",
    "description": "Описание события",
    "remind": "2",
    "remind_unit": "h"
}
url_keys = {"sport": "Спорт",
            "education": "Образование",
            "roflxdlmao": "Развлечение",
            "public_govno": "Общественная деаятельность",
            "Спорт": "sport",
            "Образование": "education",
            "Развлечение": "roflxdlmao",
            "Общественная деаятельность": "public_govno"}

x = (requests.post(url, json=myobj)).json()
#ics, google = x['ics'], x['google']
tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))
editing=0

token = '1917275192:AAFfAT_ggb_QS8Shwp6G2aNbuid69pfSNQ4'  # bot constants
bot = telebot.TeleBot(token)
users = {}  # constants for db
url = 'http://renat-hamatov.ru'
with open('users.txt', "r") as json_file:
    users = json.load(json_file)
    # print(users.keys())


def save_users(users):
    with open('users.txt', 'w') as outfile:
        json.dump(users, outfile)


def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            print("––––––––––––––––––––––––––––––––––––––––––––––––––––––")
            print(f'{m.chat.first_name}[{m.chat.id}][{datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")}]: {m.text}')
            with open('logs.txt', 'a', encoding='utf-8') as logs_file:
                logs_file.write("––––––––––––––––––––––––––––––––––––––––––––––––––––––\n")
                logs_file.write(
                    f'{m.chat.first_name}[{m.chat.id}][{datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")}]: {m.text}\n')


bot.set_update_listener(listener)


def menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1 #Ширина поля кнопок
    log_in = InlineKeyboardButton("Войти в систему", callback_data="log_in")
    registration = InlineKeyboardButton("Зарегистрироваться", callback_data="registration")
    markup.add(log_in, registration)
    return markup

def menu2():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1 #Ширина поля кнопок
    fuck_u = InlineKeyboardButton("Послать мишу нахуй", callback_data="fuck_u")
    exit = InlineKeyboardButton("Выйти из аккаунта", callback_data="exit")
    markup.add(fuck_u, exit)
    return markup


def logging_in(message):
    global editing
    logs=[]
    logs.append(message.text)
    if validate_email(logs[0]):
        a = bot.edit_message_text('Введите адрес электронной почты для авторизации:', cmcd, cmmi) #editing = 0
        a = bot.send_message(message.chat.id, 'Введите пароль:',reply_markup=back3()) #editing = 2
        editing += 2
        bot.register_next_step_handler(a,logging_in2,logs)

    else:
        a = bot.edit_message_text('Введите адрес электронной почты для авторизации:', cmcd, cmmi) #editing = 0
        a = bot.send_message(message.chat.id, 'Недействительный адрес электронной почты\nВыберите действие:', reply_markup=back()) #editing = 2
        editing +=2

def logging_in2(message,logs):
    global editing
    logs.append(message.text)
    print(logs)
    print(tconv(message.date))

    s = requests.Session()
    payload = {"email": logs[0], "password": logs[1]}
    send_to = 'signin'
    r = s.post(f'{url}/{send_to}', json=payload)
    print(json.loads(r.text))
    try:
        if json.loads(r.text)['token']:
            a = bot.edit_message_text('Введите пароль:', cmcd, cmmi+2)  # editing = 0
            bot.delete_message(message.chat.id, message.message_id)
            a = bot.send_message(message.chat.id, 'Вы вошли в свой аккаунт!✅', reply_markup=menu2()) #editing = 4
            editing +=2
        else:
            a = bot.edit_message_text('Введите пароль:', cmcd, cmmi + 2)
            bot.delete_message(message.chat.id, message.message_id)
            a = bot.send_message(message.chat.id,'Ошибка! Введенные данные неверны\nВыберите действие:',reply_markup=menu()) #editing = 4
            editing +=2
        """else:
            bot.delete_message(message.chat.id, message.message_id)
            a = bot.send_message(message.chat.id,'Ошибка! Ваш профиль уже привязан к телеграмму\nВыберите действие:', reply_markup=menu())"""
    except Exception:
        a = bot.edit_message_text('Введите пароль:', cmcd, cmmi + 2)
        bot.delete_message(message.chat.id, message.message_id)
        a = bot.send_message(message.chat.id,'К сожалению, такого пользователя нет в базе данных',reply_markup=back()) #editing = 4
        editing +=2



def check2(id):
    k = os.listdir(path="users")
    for i in range (len(k)):
        with open(f'users/{k[i]}','r') as f:
            s=f.readlines()
        if len(s)==2:
            if int(s[1]) == int(id):
                return True
    return False

def exit(id):

    k = os.listdir(path="users")
    for i in range(len(k)):
        with open(f'users/{k[i]}', 'r') as f:
            s=f.readlines()
        if len(s)==2:
            if int(s[1])==int(id):
                with open (f'users/{k[i]}', 'w') as f:
                    f.write(s[0])
                break


    return False

def back3():
    markup = InlineKeyboardMarkup()
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(back_to_menu)
    return markup


def back():
    markup = InlineKeyboardMarkup()
    log_in = InlineKeyboardButton('Повторить ввод', callback_data='log_in')
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(back_to_menu, log_in)
    return markup



@bot.message_handler(commands=['start'])
def send_welcome(message):
    global editing
    if check2(message.chat.id):
        bot.delete_message(message.chat.id, editing)
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, f"С возвращением, *{message.from_user.first_name}*!😢\nВыберите действие:", reply_markup=menu2(),parse_mode="Markdown")
    else:

        if message.message_id != 1 and editing!=0:
            bot.delete_message(message.chat.id, editing)
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "Здравствуйте!😂\nВыберите действие:", reply_markup=menu())
    if str(message.chat.id) not in users:
        users[str(message.chat.id)] = [[], [], False]
        save_users(users)
    editing = message.message_id + 1


@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'contact'])
def error(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        pass
    bot.send_message(message.chat.id, 'Воспользуйтесь предложенными кнопками. '
                                      'Если кнопки исчезли, введите команду /start')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        global cmcd, cmmi,url,editing
        cmcd = call.message.chat.id
        cmmi = call.message.message_id
        print(call.message.chat.id, call.data)
        with open(f"users.txt") as json_file:
            users = json.load(json_file)

        if call.data == "log_in":
            count=0
            a = bot.edit_message_text("Введите адрес электронной почты для авторизации:",
                                  cmcd, cmmi,reply_markup=back3())
            bot.register_next_step_handler(a, logging_in)
        elif call.data.startswith("_"):
            print(1)
            users[str(call.message.chat.id)][0].append(call.data[1:])
            bot.edit_message_text("Вы успешно записались!!", cmcd, cmmi, reply_markup=menu())
            save_users(users)
        elif call.data == 'registration':
            a = bot.delete_message(cmcd, cmmi)
            a = bot.send_message(cmcd,f'Регистрация проходит на сайте:\n {url}')
            a = bot.send_message(cmcd, 'Выберите действие🤬:',reply_markup=menu())
            editing = cmmi+2

        elif call.data == 'fuck_u':
            bot.edit_message_text('пашел нахуй', cmcd,cmmi,reply_markup=menu2())

        elif call.data == 'exit':
            exit(call.message.chat.id)
            bot.edit_message_text('Вы вышли из аккаунта❗', cmcd,cmmi,reply_markup=menu())

        elif call.data == 'back_to_menu':
            bot.clear_step_handler_by_chat_id(cmcd)
            bot.edit_message_text( 'Выберите действие😉:',cmcd, cmmi, reply_markup=menu())


        bot.answer_callback_query(call.id)
    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f'где-то херня   {e}')
            time.sleep(5)