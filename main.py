import datetime
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim
import json
import requests
from validate_email import validate_email

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
tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))
globalVar = dict()

token = '1917275192:AAFfAT_ggb_QS8Shwp6G2aNbuid69pfSNQ4'  # bot constants
bot = telebot.TeleBot(token)
url = 'http://renat-hamatov.ru'


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
                    f'{m.chat.first_name}[{m.chat.id}][{datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")}]: '
                    f'{m.text}\n')


bot.set_update_listener(listener)


def menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    log_in = InlineKeyboardButton("Войти в систему", callback_data="log_in")
    registration = InlineKeyboardButton("Зарегистрироваться", callback_data="registration")
    markup.add(log_in, registration)
    return markup


def menu2():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    fuck_u = InlineKeyboardButton("Жалобы (в работе)", callback_data="appeals")
    exit = InlineKeyboardButton("Выйти из аккаунта", callback_data="exit")
    markup.add(fuck_u, exit)
    return markup


def logging_in(message, id):
    global globalVar
    logs = list()
    logs.append(message.text)
    globalVar[str(message.chat.id)]['to_delete'].append(id)
    globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
    print(globalVar)
    if validate_email(logs[0]):
        bot.edit_message_text('Введите адрес электронной почты для авторизации:', message.chat.id, id)  # editing = 0
        a = bot.send_message(message.chat.id, 'Введите пароль:', reply_markup=back3())  # editing = 2
        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
        bot.register_next_step_handler(a, logging_in2, logs, a.message_id)

    else:
        bot.edit_message_text('Введите адрес электронной почты для авторизации:', message.chat.id, id)  # editing = 0
        d = bot.send_message(message.chat.id, 'Недействительный адрес электронной почты\nВыберите действие:',
                         reply_markup=back())  # editing = 2
        globalVar[str(message.chat.id)]['message_id'] = str(d.message_id)


# Надо чтобы искал самое старое сообщение в списке
def logging_in2(message, logs, id):
    global globalVar
    logs.append(message.text)
    globalVar[str(message.chat.id)]['to_delete'].append(id)
    globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
    s = requests.Session()
    payload = {"email": logs[0], "password": logs[1]}
    send_to = 'signin'
    r = s.post(f'{url}/{send_to}', json=payload)
    try:
        if json.loads(r.text)['token']:
            s = requests.Session()
            payload = {"email": logs[0], "password": logs[1], "chat_id": str(message.chat.id)}
            send_to = 'telegram/connect'
            r = s.post(f'{url}/{send_to}', json=payload)
            try:
                if json.loads(r.text)['user']:
                    bot.edit_message_text('Введите пароль:', message.chat.id, id)  # editing = 0
                    a = bot.send_message(message.chat.id, 'Вы вошли в свой аккаунт!✅', reply_markup=menu2())  # editing = 4
                    globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
            except Exception:
                bot.edit_message_text('Введите пароль:', message.chat.id, id)  # editing = 0
                a = bot.send_message(message.chat.id, 'Ошибка! Ваш профиль уже привязан к телеграмму\nВыберите действие:',
                                 reply_markup=menu())
                globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
        else:
            bot.edit_message_text('Введите пароль:', message.chat.id, id)
            a = bot.send_message(message.chat.id, 'Ошибка! Введенные данные неверны\nВыберите действие:',
                             reply_markup=menu())
            # editing = 4
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
    except Exception:
        bot.edit_message_text('Введите пароль:', message.chat.id, id)
        a = bot.send_message(message.chat.id, 'К сожалению, такого пользователя нет в базе данных', reply_markup=back())
        # editing = 4
        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)

    deleting(globalVar, message.chat.id)


def deleting(to_delete, chat_id):
    if len(globalVar[str(chat_id)]['to_delete']) != 0:
        for message in globalVar[str(chat_id)]['to_delete']:
            bot.delete_message(chat_id, message)
    globalVar[str(chat_id)]['to_delete'] = list()


def check2(id):
    s = requests.Session()
    payload = {"chat_id": str(id)}
    send_to = 'telegram/user'
    r = s.get(f'{url}/{send_to}', json=payload)
    try:
        if json.loads(r.text)['user']:
            return True
    except Exception:
        return False


def exit(id):
    s = requests.Session()
    payload = {"chat_id": str(id)}
    send_to = 'telegram/disconnect'
    s.post(f'{url}/{send_to}', json=payload)


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


def look_for_the_newest(globalvar):
    max1 = 0
    for key in globalvar:
        key = str(key)
        if int(globalvar[key]['message_id']) > max1:
            max1 = int(globalvar[key]['message_id'])
    return max1


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global globalVar
    print(globalVar)


    if str(message.chat.id) not in globalVar:

        globalVar[str(message.chat.id)] = {}
        globalVar[str(message.chat.id)]['to_delete'] = list()
        globalVar[str(message.chat.id)]['message_id'] = str(message.message_id)

    deleting(globalVar, message.chat.id)

    if check2(message.chat.id):
        if int(globalVar[str(message.chat.id)]['message_id']) != message.message_id:
            bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['message_id']))
            globalVar[str(message.chat.id)]['message_id'] = str(message.message_id + 1)
        s = requests.Session()
        payload = {"chat_id": message.chat.id}
        send_to = 'telegram/user'
        r = s.get(f'{url}/{send_to}', json=payload)
        bot.delete_message(message.chat.id, message.message_id)
        a = bot.send_message(message.chat.id, f"С возвращением, *{json.loads(r.text)['user']['firstname'].capitalize()}"
                                          f"*!\nВыберите действие:", reply_markup=menu2(), parse_mode="Markdown")
    else:
        if int(globalVar[str(message.chat.id)]['message_id']) != message.message_id:
            bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['message_id']))
            globalVar[str(message.chat.id)]['message_id'] = str(look_for_the_newest(globalVar) + 1)

        bot.delete_message(message.chat.id, message.message_id)
        a = bot.send_message(message.chat.id, "Здравствуйте!\nВыберите действие:", reply_markup=menu())


    globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)


@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'contact'])
def error(message):
    try:
        deleting(globalVar, message.chat.id)
        bot.delete_message(message.chat.id, message.message_id)
    except Exception:
        pass
    a = bot.send_message(message.chat.id, 'Воспользуйтесь предложенными кнопками. '
                                      'Если кнопки исчезли, введите команду /start')
    globalVar[str(message.chat.id)]['to_delete'].append(a.message_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        global cmcd, cmmi, url, globalVar
        cmcd = call.message.chat.id
        cmmi = call.message.message_id
        print(cmcd, call.data)

        if call.data == "log_in":
            b = bot.edit_message_text("Введите адрес электронной почты для авторизации:",
                                  cmcd, cmmi, reply_markup=back3())
            deleting(globalVar, cmcd)
            bot.register_next_step_handler(b, logging_in, cmmi)
        elif call.data == 'registration':
            bot.delete_message(cmcd, cmmi)
            a = bot.send_message(cmcd, f'Регистрация проходит на сайте:\n {url}', reply_markup=back3())
            globalVar[str(cmcd)]['message_id'] = str(a.message_id)

        elif call.data == 'appeals':
            bot.edit_message_text('Жалобы', cmcd, cmmi, reply_markup=menu2())

        elif call.data == 'exit':
            exit(call.message.chat.id)
            bot.edit_message_text('Вы вышли из аккаунта❗', cmcd, cmmi, reply_markup=menu())

        elif call.data == 'back_to_menu':
            bot.clear_step_handler_by_chat_id(cmcd)  # Может это вызывает ошибку при входе с двух устройств одновременно
            deleting(globalVar, cmcd)
            bot.edit_message_text('Выберите действие:', cmcd, cmmi, reply_markup=menu())

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
