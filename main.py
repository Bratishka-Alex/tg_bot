import datetime
import time
import telebot
import os
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from geopy.geocoders import Nominatim
import json
import requests
from validate_email import validate_email


geolocator = Nominatim(user_agent="tg_bot")

tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))
globalVar = dict()



bot = telebot.TeleBot(token)
url = 'https://api-prof.ru'


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
    log_in = InlineKeyboardButton("Войти в систему 🔐", callback_data="log_in")
    registration = InlineKeyboardButton("Зарегистрироваться 📝", callback_data="registration")
    markup.add(log_in, registration)
    return markup


def menu_authorized():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    appeals = InlineKeyboardButton("Жалобы ☹", callback_data="appeals")
    meter = InlineKeyboardButton("Счётчики 👨‍🔧", callback_data="meter")
    statements = InlineKeyboardButton("Справки 📄", callback_data="statements")
    exit = InlineKeyboardButton("Выйти из аккаунта 🚪", callback_data="exit")
    markup.add(appeals, meter, statements, exit)
    return markup

def exit_confirm():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    exit_confirmed = InlineKeyboardButton("Да", callback_data="exit_confirmed")
    back_to_menu_authorized = InlineKeyboardButton('Нет', callback_data='back_to_menu_authorized')
    markup.add(exit_confirmed, back_to_menu_authorized)
    return markup

def menu_appeals():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    create__appeal = InlineKeyboardButton("Пожаловаться 😣", callback_data="create__appeal")
    my__appeals = InlineKeyboardButton("Мои жалобы 📬", callback_data="my__appeals")
    back_to_menu_authorized = InlineKeyboardButton('Назад', callback_data='back_to_menu_authorized')
    markup.add(create__appeal, my__appeals, back_to_menu_authorized)
    return markup

def menu_statements():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    create__statement = InlineKeyboardButton("Заказать справку 📨", callback_data="create__statement__question")
    my__statements = InlineKeyboardButton("Мои справки 📬", callback_data="my__statements")
    back_to_menu_authorized = InlineKeyboardButton('Назад', callback_data='back_to_menu_authorized')
    markup.add(create__statement, my__statements, back_to_menu_authorized)
    return markup

def menu_meter():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    update_meter = InlineKeyboardButton("Обновить показания 🔄", callback_data="update_meter")
    back_to_menu_authorized = InlineKeyboardButton('Назад', callback_data='back_to_menu_authorized')
    markup.add(update_meter, back_to_menu_authorized)
    return markup


def send_meter():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    send_meter = InlineKeyboardButton("Да ✅", callback_data="send_meter")
    back_to_menu_choose_meter = InlineKeyboardButton('Назад', callback_data='back_to_menu_choose_meter')
    markup.add(send_meter, back_to_menu_choose_meter)
    return markup


def choose_appeal(last, first):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2  # Ширина поля кнопок
    if first:
        choose_appeal_back = InlineKeyboardButton("🚫", callback_data='None')
    else:
        choose_appeal_back = InlineKeyboardButton("<--", callback_data='choose_appeal_back')
    if last:
        choose_appeal_forward = InlineKeyboardButton("🚫", callback_data="None")
    else:
        choose_appeal_forward = InlineKeyboardButton("-->", callback_data="choose_appeal_forward")
    reload_my_appeal = InlineKeyboardButton('Обновить 🔄', callback_data='reload_my_appeal')
    back_to_menu_appeal = InlineKeyboardButton('Назад', callback_data='back_to_menu_appeals')
    markup.add(choose_appeal_back, choose_appeal_forward)
    markup.row_width = 1  # Ширина поля кнопок
    markup.add(reload_my_appeal, back_to_menu_appeal)
    return markup


def choose_statement(last, first):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2  # Ширина поля кнопок
    if first:
        choose_statement_back = InlineKeyboardButton("🚫", callback_data='None')
    else:
        choose_statement_back = InlineKeyboardButton("<--", callback_data='choose_statement_back')
    if last:
        choose_statement_forward = InlineKeyboardButton("🚫", callback_data="None")
    else:
        choose_statement_forward = InlineKeyboardButton("-->", callback_data="choose_statement_forward")
    reload_my_statement = InlineKeyboardButton('Обновить 🔄', callback_data='reload_my_statement')
    back_to_menu_statements = InlineKeyboardButton('Назад', callback_data='statements')
    markup.add(choose_statement_back, choose_statement_forward)
    markup.row_width = 1  # Ширина поля кнопок
    markup.add(reload_my_statement, back_to_menu_statements)
    return markup


def choose_statement_to_create(statement_id, last, first):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    button = InlineKeyboardButton(text='Заказать справку ⬆📨', callback_data='order_' + str(statement_id))
    markup.add(button)
    markup.row_width = 2  # Ширина поля кнопок
    if first:
        choose_statement_to_create_back = InlineKeyboardButton("🚫", callback_data='None')
    else:
        choose_statement_to_create_back = InlineKeyboardButton("<--", callback_data='choose_statement_to_create_back')
    if last:
        choose_statement_to_create_forward = InlineKeyboardButton("🚫",
                                                                  callback_data="None")
    else:
        choose_statement_to_create_forward = InlineKeyboardButton("-->",
                                                                  callback_data="choose_statement_to_create_forward")

    back_to_menu_statements = InlineKeyboardButton('Назад', callback_data='statements')
    markup.add(choose_statement_to_create_back, choose_statement_to_create_forward)
    markup.row_width = 1  # Ширина поля кнопок
    markup.add(back_to_menu_statements)
    return markup


def create__statement__confirm():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    next_step = InlineKeyboardButton('Данные верны', callback_data='create__statement__confirmed')
    back_to_menu_statement = InlineKeyboardButton('Назад', callback_data='statements')
    markup.add(next_step, back_to_menu_statement)
    return markup


def my_statements(statement_id, flag):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    button = InlineKeyboardButton(text='Заказать справку ⬆📨', callback_data='order_' + str(statement_id))
    markup.add(button)
    if flag:
        back_to_menu_statements = InlineKeyboardButton('Назад', callback_data='statements')
        markup.add(back_to_menu_statements)
    return markup


def order_statement(value):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    send_statement = InlineKeyboardButton('Да ✅', callback_data='send_statement_' + value)
    back_to_choose_statement = InlineKeyboardButton('Нет', callback_data='create__statement__confirmed')
    markup.add(send_statement, back_to_choose_statement)
    return markup


def back_to_menu_statements():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    back_to_menu_statements = InlineKeyboardButton('Назад', callback_data='statements')
    markup.add(back_to_menu_statements)
    return markup


def back_to_choose_statement():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    back_to_choose_statement = InlineKeyboardButton('Назад', callback_data='create__statement__confirmed')
    markup.add(back_to_choose_statement)
    return markup



def logging_in(message, id):
    global globalVar
    logs = list()
    logs.append(message.text)
    if message.text != None:
        if message.text.lower() == '/start':
            error_func(message.chat.id, message.message_id)
        else:
            globalVar[str(message.chat.id)]['to_delete'].append(id)
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
            if validate_email(logs[0]):
                bot.edit_message_text('Введите адрес электронной почты для авторизации:', message.chat.id, id)
                a = bot.send_message(message.chat.id, 'Введите пароль:', reply_markup=back3())  # editing = 2
                globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
                bot.register_next_step_handler(a, logging_in2, logs, a.message_id)

            else:
                bot.edit_message_text('Введите адрес электронной почты для авторизации:', message.chat.id, id)
                d = bot.send_message(message.chat.id, 'Недействительный адрес электронной почты\nВыберите действие:',
                                reply_markup=back())  # editing = 2
                globalVar[str(message.chat.id)]['message_id'] = str(d.message_id)
    else:
        globalVar[str(message.chat.id)]['to_delete'].append(id)
        globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
        bot.edit_message_text('Введите адрес электронной почты для авторизации:', message.chat.id, id)  # editing = 0
        d = bot.send_message(message.chat.id, 'Пожалуйста, укажите действительный адрес электронной почты без вложений'
                                              ' в чат\nВыберите действие:',
                             reply_markup=back())  # editing = 2
        globalVar[str(message.chat.id)]['message_id'] = str(d.message_id)

def logging_in2(message, logs, id):
    global globalVar
    logs.append(message.text)

    if message.text != None:
        if message.text.lower() == '/start':
            error_func(message.chat.id, message.message_id)
        else:
            globalVar[str(message.chat.id)]['to_delete'].append(id)
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
            if len(message.text) > 7:
                s = requests.Session()
                payload = {"email": logs[0].lower(), "password": logs[1]}
                send_to = f'telegram/connect/{str(message.chat.id)}'
                r = s.post(f'{url}/{send_to}', json=payload)
                try:
                    if json.loads(r.text)['user'] and json.loads(r.text)['user']['emailVerified']:
                        bot.edit_message_text('Введите пароль:', message.chat.id, id)  # editing = 0
                        a = bot.send_message(message.chat.id, 'Вы вошли в свой аккаунт!✅',
                                             reply_markup=menu_authorized())
                        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
                    else:
                        bot.edit_message_text('Введите пароль:', message.chat.id, id)  # editing = 0
                        a = bot.send_message(message.chat.id,
                                            'Вы не подтвердили почту! На ваш электронный адрес отправлено новое письмо'
                                            ' для подтверждения. Перейдите по ссылке в письме и повторите авторизацию.',
                                            reply_markup=menu())  # editing = 4
                        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
                        exit(message.chat.id)
                except Exception:
                        bot.edit_message_text('Введите пароль:', message.chat.id, id)  # editing = 0
                        mes = json.loads(r.text)['message']
                        a = bot.send_message(message.chat.id, f'{mes}\nВыберите действие:',
                                            reply_markup=menu())
                        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
                deleting(message.chat.id)
            else:
                bot.edit_message_text('Введите пароль:', message.chat.id, id)  # editing = 0
                d = bot.send_message(message.chat.id, 'Вы отправили слишком короткий пароль.\nМинимальная длина пароля'
                                                      ' - 8\nВыберите действие:',
                                     reply_markup=back())  # editing = 2
                globalVar[str(message.chat.id)]['message_id'] = str(d.message_id)
    else:
        globalVar[str(message.chat.id)]['to_delete'].append(id)
        globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
        bot.edit_message_text('Введите пароль:', message.chat.id, id)  # editing = 0
        d = bot.send_message(message.chat.id, 'Пожалуйста, укажите действительный пароль без вложений'
                                              ' в чат\nВыберите действие:',
                             reply_markup=back())  # editing = 2
        globalVar[str(message.chat.id)]['message_id'] = str(d.message_id)


def deleting(chat_id):
    if len(globalVar[str(chat_id)]['to_delete']) != 0:
        for message in globalVar[str(chat_id)]['to_delete']:
            bot.delete_message(chat_id, message)
    globalVar[str(chat_id)]['to_delete'] = list()


def check(id):
    s = requests.Session()
    send_to = f'telegram/user/{str(id)}'
    r = s.get(f'{url}/{send_to}')
    try:
        if json.loads(r.text)['user']:
            return True
    except Exception:
        return False


def understand():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    understand = InlineKeyboardButton('Хорошо, спасибо!', callback_data='delete_notification')
    markup.add(understand)
    return markup

def understand1():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    understand = InlineKeyboardButton('Хорошо, спасибо!', callback_data='delete_notification1')
    markup.add(understand)
    return markup


def exit(id):
    s = requests.Session()
    send_to = f'telegram/disconnect/{str(id)}'
    s.post(f'{url}/{send_to}')


def back_to_menu_appeals2():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    upload_my_appeal = InlineKeyboardButton('Назад', callback_data='upload_my_appeal')
    markup.add(upload_my_appeal)
    return markup


def back_to_menu_appeals1():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    back_to_menu_appeal = InlineKeyboardButton('Назад', callback_data='back_to_menu_appeals')
    reload_my_appeal = InlineKeyboardButton('Обновить 🔄', callback_data='reload_my_appeal')
    markup.add(reload_my_appeal, back_to_menu_appeal)
    return markup


def back_to_menu_appeals():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    back_to_menu_appeal = InlineKeyboardButton('Назад', callback_data='back_to_menu_appeals')
    markup.add(back_to_menu_appeal)
    return markup

def back_to_menu_choose_meter():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    back_to_menu_choose_meter = InlineKeyboardButton('Назад', callback_data='back_to_menu_choose_meter')
    markup.add(back_to_menu_choose_meter)
    return markup

def back_to_menu_choose_meter1():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    back_to_menu_choose_meter = InlineKeyboardButton('Назад', callback_data='back_to_menu_choose_meter')
    update_meter = InlineKeyboardButton("Повторить ввод 🔁", callback_data="update_meter")
    markup.add(update_meter, back_to_menu_choose_meter)
    return markup


def back3():
    markup = InlineKeyboardMarkup()
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(back_to_menu)
    return markup


def back2():
    markup = InlineKeyboardMarkup()
    back_to_menu_authorized = InlineKeyboardButton('Назад', callback_data='back_to_menu_authorized')
    markup.add(back_to_menu_authorized)
    return markup


def back():
    markup = InlineKeyboardMarkup()
    log_in = InlineKeyboardButton('Повторить ввод 🔁', callback_data='log_in')
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(back_to_menu, log_in)
    return markup


def upload_my_appeal_again():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    create_appeal = InlineKeyboardButton('Да', callback_data='create__appeal')
    back_to_menu_appeals = InlineKeyboardButton('Нет', callback_data='back_to_menu_appeals')
    markup.add(create_appeal, back_to_menu_appeals)
    return markup



def upload_my_appeal0():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    send_text = InlineKeyboardButton('Да', callback_data='send_text')
    back_to_menu_appeals = InlineKeyboardButton('Нет', callback_data='back_to_menu_appeals')
    markup.add(send_text, back_to_menu_appeals)
    return markup


def upload_my_appeal():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    send_appeal = InlineKeyboardButton('Отправить жалобу без фото', callback_data='send_appeal')
    back_to_menu_appeals = InlineKeyboardButton('Назад в меню', callback_data='back_to_menu_appeals')
    send_photo = InlineKeyboardButton('Да 📸', callback_data='send_photo')
    markup.add(send_photo, send_appeal, back_to_menu_appeals)
    return markup

def upload_my_appeal1():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    send_appeal = InlineKeyboardButton('Да ✅', callback_data='send_appeal')
    back_to_menu_appeals = InlineKeyboardButton('Назад в меню', callback_data='back_to_menu_appeals')
    markup.add(send_appeal, back_to_menu_appeals)
    return markup

def create_statement_now(id, bot_message_id):
    bot.delete_message(id, bot_message_id)
    deleting(id)

    s = requests.Session()
    send_to = f'houses-from-tg/{id}/statements'
    r = s.get(f'{url}/{send_to}')
    statements = json.loads(r.text)['statements']
    a = None
    if len(statements) != 0:
        start = int(globalVar[str(id)]['move'])
        print(globalVar)
        for statement_id in range(start, start + 3):
            if len(statements) <= 3 and statement_id == len(statements) - 1:
                a = bot.send_message(id,
                                        f'{statement_id + 1}/{len(statements)}\n{statements[statement_id]["name"]}',
                                        reply_markup=my_statements(statement_id, True))
                break
            elif statement_id == start + 2 or statement_id == len(statements) - 1:
                if statement_id in [0,1,2]:
                    a = bot.send_message(id,
                                            f'{statement_id + 1}/{len(statements)}\n{statements[statement_id]["name"]}',
                                            reply_markup=choose_statement_to_create(statement_id, False, True))
                elif statement_id in [3*(len(statements)//3), 3*(len(statements)//3) + 1, 3*(len(statements)//3) + 2]:
                    a = bot.send_message(id, f'{statement_id + 1}/{len(statements)}\n{statements[statement_id]["name"]}',
                                        reply_markup=choose_statement_to_create(statement_id, True, False))
                else:
                    a = bot.send_message(id,
                                            f'{statement_id + 1}/{len(statements)}\n{statements[statement_id]["name"]}',
                                            reply_markup=choose_statement_to_create(statement_id, False, False))
                break
            else:
                a = bot.send_message(id,
                                        f'{statement_id + 1}/{len(statements)}\n{statements[statement_id]["name"]}',
                                        reply_markup=my_statements(statement_id, False))
                globalVar[str(id)]['to_delete'].append(a.message_id)

    else:
        a = bot.send_message(id, 'К сожалению, вы не можете заказать справки в данный момент',
                             reply_markup=back_to_menu_statements())
    globalVar[str(id)]['message_id'] = str(a.message_id)


def create_appeal(message, bot_message_id):
    if message.text != None:
        if message.text.lower() == '/start':
            error_func(message.chat.id, message.message_id)
        else:
            bot.edit_message_text('Опишите возникшую проблему:', message.chat.id, bot_message_id)
            globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
            globalVar[str(message.chat.id)]['appeal_text'] = message.text
            a = bot.send_message(message.chat.id, 'Хотите отправить фотографию по проблеме?',
                                reply_markup=upload_my_appeal())
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)

    elif message.photo != None and message.caption == None:
        bot.edit_message_text('Опишите возникшую проблему:', message.chat.id, bot_message_id)
        globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
        globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)

        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'uploads/' + file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        globalVar[str(message.chat.id)]['photo_url'] = src
        text = 'Вы прислали фото.\nТеперь опишите возникшую проблему:'
        a = bot.send_message(message.chat.id, text, reply_markup=back_to_menu_appeals())
        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
        bot.register_next_step_handler(a, send_text, a.message_id, text)

    elif message.photo != None and message.caption != None:
        bot.edit_message_text('Опишите возникшую проблему:', message.chat.id, bot_message_id)
        globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
        globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
        globalVar[str(message.chat.id)]['appeal_text'] = message.caption

        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = 'uploads/' + file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        globalVar[str(message.chat.id)]['photo_url'] = src

        a = bot.send_message(message.chat.id, 'Жалоба готова! Отправить?', reply_markup=upload_my_appeal1())
        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)

    else:
        bot.edit_message_text('Опишите возникшую проблему:', message.chat.id, bot_message_id)
        globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
        globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
        a = bot.send_message(message.chat.id, 'Вы отправили не текст!\nХотите повторить ввод?',
                             reply_markup=upload_my_appeal_again())
        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)


def send_text(message,bot_id_message, text):
    if message.text != None:
        if message.text.lower() == '/start':
            error_func(message.chat.id, message.message_id)
        else:
            bot.edit_message_text(text, message.chat.id, bot_id_message)
            globalVar[str(message.chat.id)]['appeal_text'] = message.text
            a = bot.send_message(message.chat.id, 'Жалоба готова! Отправить?', reply_markup=upload_my_appeal1())
            globalVar[str(message.chat.id)]['to_delete'].append(bot_id_message)
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
    else:
        bot.edit_message_text(text, message.chat.id, bot_id_message)
        a = bot.send_message(message.chat.id, 'Вы отправили не текст! Хотите повторить ввод текста?',
                             reply_markup=upload_my_appeal0())
        globalVar[str(message.chat.id)]['to_delete'].append(bot_id_message)
        globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)


def send_photo(message, bot_id_message):
    bot.edit_message_text('Пришлите фотографию возникшей проблемы:', message.chat.id, bot_id_message)
    try:
        if message.caption == None:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            src = 'uploads/' + file_info.file_path
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            globalVar[str(message.chat.id)]['photo_url'] = src
            a = bot.send_message(message.chat.id, 'Жалоба готова! Отправить?', reply_markup=upload_my_appeal1())
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
            globalVar[str(message.chat.id)]['to_delete'].append(bot_id_message)
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
        else:
            a = bot.send_message(message.chat.id, 'Вы отправили два разных текста!',
                                 reply_markup=back_to_menu_appeals())
            globalVar[str(message.chat.id)]['photo_url'] = 'error'
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
            globalVar[str(message.chat.id)]['to_delete'].append(bot_id_message)
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
    except Exception:
        if message.text != None:
            if message.text.lower() == '/start':
                error_func(message.chat.id, message.message_id)
            else:
                a = bot.send_message(message.chat.id, 'Вы отправили не фото! Хотите отправить фотографию по проблеме?',
                                     reply_markup=upload_my_appeal())
                globalVar[str(message.chat.id)]['photo_url'] = 'error'
                globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
                globalVar[str(message.chat.id)]['to_delete'].append(bot_id_message)
                globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
        else:
            a = bot.send_message(message.chat.id, 'Вы отправили не фото! Хотите отправить фотографию по проблеме?',
                            reply_markup=upload_my_appeal())
            globalVar[str(message.chat.id)]['photo_url'] = 'error'
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
            globalVar[str(message.chat.id)]['to_delete'].append(bot_id_message)
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)


def send_appeal(id, bot_message_id):
    s = requests.Session()
    payload = {"text": globalVar[str(id)]['appeal_text']}
    send_to = f'appeals-from-tg/{str(id)}/create-complaint'
    if globalVar[str(id)]['photo_url'] != '' and globalVar[str(id)]['photo_url'] != 'error':
        files = {'image': (globalVar[str(id)]['photo_url'],
                        open(globalVar[str(id)]['photo_url'], 'rb'))}
        s.post(f'{url}/{send_to}', data=payload, files=files)
    else:
        s.post(f'{url}/{send_to}', json=payload)
    bot.edit_message_text('Ваша жалоба принята', id, bot_message_id, reply_markup=back_to_menu_appeals())
    globalVar[str(id)]['appeal_text'] = ''


def hot_water_update(message, bot_message_id, img):
    if message.text != None:
        if message.text.lower() == '/start':
            error_func(message.chat.id, message.message_id)
        elif message.text.isdigit():
            bot.edit_message_media(chat_id=message.chat.id, message_id=bot_message_id,
                                   media=telebot.types.InputMediaPhoto(media=img,
                                                                       caption='Введите показания счетчика *ГВС*:',
                                                                       parse_mode="Markdown"))
            logs = list()
            logs.append(str(int(message.text)))
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
            globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
            a = bot.send_message(message.chat.id, 'Введите показания счетчика *ХВС*:', parse_mode="Markdown",
                                 reply_markup=back_to_menu_choose_meter())
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
            bot.register_next_step_handler(a,cold_water_update, a.message_id, logs)
        else:
            bot.edit_message_media(chat_id=message.chat.id, message_id=bot_message_id,
                                   media=telebot.types.InputMediaPhoto(media=img,
                                                                       caption='Введите показания счетчика *ГВС*:',
                                                                       parse_mode="Markdown"))
            a = bot.send_message(message.chat.id,
                                 'Пожалуйста, укажите показания счётчиков целым числом',
                                 reply_markup=back_to_menu_choose_meter1())
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
            globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)

    else:
        bot.edit_message_media(chat_id=message.chat.id, message_id=bot_message_id,
                               media=telebot.types.InputMediaPhoto(media=img,
                                                                   caption='Введите показания счетчика *ГВС*:',
                                                                   parse_mode="Markdown"))
        a = bot.send_message(message.chat.id,
                             'Пожалуйста, укажите показания счётчиков текстовым сообщением без вложений',
                         reply_markup=back_to_menu_choose_meter1())
        globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
        globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)


def cold_water_update(message, bot_message_id, logs):
    if message.text != None:
        if message.text.lower() == '/start':
            error_func(message.chat.id, message.message_id)
        elif message.text.isdigit():
            bot.edit_message_text('Введите показания счетчика *ХВС*:', message.chat.id, bot_message_id,
                                  parse_mode="Markdown")
            logs.append(str(int(message.text)))
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
            globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
            a = bot.send_message(message.chat.id, 'Показания готовы. Отправить?', parse_mode="Markdown",
                                 reply_markup=send_meter())
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
            globalVar[str(message.chat.id)]['meter'] = logs
        else:
            bot.edit_message_text('Введите показания счетчика *ХВС*:', message.chat.id, bot_message_id,
                                  parse_mode="Markdown")
            a = bot.send_message(message.chat.id,
                                 'Пожалуйста, укажите показания счётчиков целым числом',
                                 reply_markup=back_to_menu_choose_meter1())
            globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
            globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
    else:
        bot.edit_message_text('Введите показания счетчика *ХВС*', message.chat.id, bot_message_id,
                              parse_mode="Markdown")
        a = bot.send_message(message.chat.id,
                             'Пожалуйста, укажите показания счётчиков текстовым сообщением без вложений',
                         reply_markup=back_to_menu_choose_meter1())
        globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
        globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
        globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)


def send_meter1(id):
    s = requests.Session()
    payload = {"hotWater": globalVar[str(id)]['meter'][0],"coldWater": globalVar[str(id)]['meter'][1]}
    url = 'http://renat-hamatov.ru'
    send_to = f'telegram/user/meter-update/{id}'
    r = s.post(f'{url}/{send_to}', json=payload)
    try:
        if json.loads(r.text)['user']:
            bot.delete_message(id, globalVar[str(id)]['message_id'])
            a = bot.send_message(id, 'Показания успешно обновлены!',
                             reply_markup=back_to_menu_choose_meter())
            globalVar[str(id)]['message_id'] = str(a.message_id)
    except Exception:
        text = json.loads(r.text)['message']
        bot.delete_message(id, globalVar[str(id)]['message_id'])
        a = bot.send_message(id, f'{text}', reply_markup=back_to_menu_choose_meter1())
        globalVar[str(id)]['message_id'] = str(a.message_id)

def my_appeals(id):
    s = requests.Session()
    send_to = f'appeals-from-tg/{str(id)}/my'
    r = s.get(f'{url}/{send_to}')
    appeals = json.loads(r.text)['appeals']
    appeals = appeals[::-1]
    a = None

    def filter_set(appeals):
        def iterator_func(x):
            if "complaint" == x.get("type"):
                return True
            else:
                return False

        return filter(iterator_func, appeals)

    appeals = list(filter_set(appeals))
    if len(appeals) != 0:
        appeal_id = int(globalVar[str(id)]['move'])
        t = appeals[appeal_id]
        date = str(t['dateOfRequest'])
        status = str(t['status'])
        text = str(t['text'])
        img = t['image']
        rejectReason = ''
        last, first = False, False
        if appeal_id == len(appeals) - 1:
            last = True
        elif appeal_id == 0:
            first = True

        if status == 'waiting':
            status = 'Ожидание ⏳'
        elif status == 'in_work':
            status = 'В работе ⚒'
        elif status == 'done':
            status = "Выполнено ✅ "
        elif status == 'rejected':
            status = 'Отклонено ❌'
            rejectReason = t['rejectReason']
            rejectReason = f'\n\nПричина отклонения:\n*{rejectReason}*'
        try:
            if len(appeals)-1 == 0:
                if img != 'not image':
                    img = f'{url}{img}'
                    bot.delete_message(id, int(globalVar[str(id)]['message_id']))
                    a = bot.send_photo(photo=img, caption=f'{appeal_id + 1}/{len(appeals)}\n'
                                        f'Дата: *{date}*\n'
                                        f'Статус: *{status}*{rejectReason}\n\nТекст обращения:\n*{text}*',
                                        parse_mode="Markdown",
                                        chat_id=id, reply_markup=back_to_menu_appeals1())
                else:
                    bot.delete_message(id, int(globalVar[str(id)]['message_id']))
                    a = bot.send_message(id, f'{appeal_id + 1}/{len(appeals)}\n'
                                                f'Дата: *{date}*\n'
                                                f'Статус: *{status}*{rejectReason}\n\nТекст обращения:\n*{text}*',
                                            reply_markup=back_to_menu_appeals1(), parse_mode="Markdown")
            else:
                if img != 'not image':
                    img = f'{url}{img}'
                    bot.delete_message(id, int(globalVar[str(id)]['message_id']))
                    a = bot.send_photo(photo=img, caption=f'{appeal_id + 1}/{len(appeals)}\n'
                                                    f'Дата: *{date}*\n'
                                                    f'Статус: *{status}*{rejectReason}\n'
                                                    f'\nТекст обращения:\n*{text}*',
                                                    parse_mode="Markdown",
                                                    chat_id=id, reply_markup=choose_appeal(last, first))
                else:
                    bot.delete_message(id, int(globalVar[str(id)]['message_id']))
                    a = bot.send_message(id, f'{appeal_id + 1}/{len(appeals)}\n'
                                                f'Дата: *{date}*\n'
                                                f'Статус: *{status}*{rejectReason}\n\nТекст обращения:\n*{text}*',
                                                reply_markup=choose_appeal(last, first), parse_mode="Markdown")
            #Если в предыдущем есть фото, то пусть edit_message_media, иначе edit_message_text"""

        except Exception:
            None
    else:
        deleting(id)
        bot.delete_message(id, int(globalVar[str(id)]['message_id']))
        b = bot.send_message(id, 'Вы не отправляли ни одной жалобы')
        a = bot.send_message(id, 'Выберите действие', reply_markup=back_to_menu_appeals1())
        globalVar[str(id)]['to_delete'].append(b.message_id)
    if a!= None:
        globalVar[str(id)]['message_id'] = str(a.message_id)


def my_statement(id):
    s = requests.Session()
    send_to = f'appeals-from-tg/{str(id)}/my'
    r = s.get(f'{url}/{send_to}')
    appeals = json.loads(r.text)['appeals']
    appeals = appeals[::-1]
    a = None

    def filter_set(appeals):
        def iterator_func(x):
            if "statement" == x.get("type"):
                return True
            else:
                return False

        return filter(iterator_func, appeals)

    appeals = list(filter_set(appeals))
    if len(appeals) != 0:
        appeal_id = int(globalVar[str(id)]['move'])
        t = appeals[appeal_id]
        date = str(t['dateOfRequest'])
        status = str(t['status'])
        text = str(t['text'])[16:-1]
        rejectReason = ''
        last, first = False, False
        if appeal_id == len(appeals) - 1:
            last = True
        elif appeal_id == 0:
            first = True

        if status == 'waiting':
            status = 'Ожидание ⏳'
        elif status == 'in_work':
            status = 'В работе ⚒'
        elif status == 'done':
            status = "Доставлено до почтового ящика ✅ "
        elif status == 'rejected':
            status = 'Отклонено ❌'
            rejectReason = t['rejectReason']
            rejectReason = f'\n\nПричина отклонения:\n*{rejectReason}*'
        if len(appeals)-1 == 0:
            bot.delete_message(id, int(globalVar[str(id)]['message_id']))
            a = bot.send_message(text=f'{appeal_id + 1}/{len(appeals)}\n'
                                                        f'Дата: *{date}*\n'
                                                        f'Статус: *{status}*{rejectReason}\n\nСправка:\n*{text}*',
                                    parse_mode="Markdown",
                                    chat_id=id, reply_markup=back_to_menu_statements())
        else:
            bot.delete_message(id, int(globalVar[str(id)]['message_id']))
            a = bot.send_message(id, f'{appeal_id + 1}/{len(appeals)}\n'
                                            f'Дата: *{date}*\n'
                                            f'Статус: *{status}*{rejectReason}\n\nСправка:\n*{text}*',
                                        reply_markup=choose_statement(last,first), parse_mode="Markdown")

        #Если в предыдущем есть фото, то пусть edit_message_media, иначе edit_message_text"""

    else:
        deleting(id)
        bot.delete_message(id, int(globalVar[str(id)]['message_id']))
        b = bot.send_message(id, 'Вы не заказывали ни одной справки')
        a = bot.send_message(id, 'Выберите действие', reply_markup=back_to_menu_statements())
        globalVar[str(id)]['to_delete'].append(b.message_id)
    if a!= None:
        globalVar[str(id)]['message_id'] = str(a.message_id)


def error_func(id,bot_message_id):
    if str(id) not in globalVar:
        globalVar[str(id)] = {}
        globalVar[str(id)]['to_delete'] = list()
        globalVar[str(id)]['topic'] = None
        globalVar[str(id)]['error_messages'] = None
        globalVar[str(id)]['message_id'] = ''
        globalVar[str(id)]['move'] = '0'
        globalVar[str(id)]['appeal_text'] = ''
        globalVar[str(id)]['photo_url'] = ''
        globalVar[str(id)]['meter'] = list()
        globalVar[str(id)]['help_message'] = list()
    try:
        bot.delete_message(id, int(globalVar[str(id)]['error_messages']))
    except Exception:
        None
    bot.delete_message(id, bot_message_id)
    a = bot.send_message(id, 'Воспользуйтесь предложенными кнопками. \n'
                                      'Если кнопки исчезли, введите команду /start\n'
                             'Если у вас трудности с ботом, введите команду /help')
    globalVar[str(id)]['error_messages'] = a.message_id


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global globalVar
    print(globalVar)

    if str(message.chat.id) not in globalVar:

        globalVar[str(message.chat.id)] = {}
        globalVar[str(message.chat.id)]['to_delete'] = list()
        globalVar[str(message.chat.id)]['topic'] = None
        globalVar[str(message.chat.id)]['error_messages'] = None
        globalVar[str(message.chat.id)]['message_id'] = ''
        globalVar[str(message.chat.id)]['move'] = '0'
        globalVar[str(message.chat.id)]['appeal_text'] = ''
        globalVar[str(message.chat.id)]['photo_url'] = ''
        globalVar[str(message.chat.id)]['meter'] = list()
        globalVar[str(message.chat.id)]['help_message'] = list()
    if globalVar[str(message.chat.id)]['message_id'] == '':
        bot.send_message(message.chat.id, 'Привет!\nЭтот бот сделан специально для жильцов домов УК Профессионал!\n\n'
                             'С его помощью вы можете оставить жалобу, поменять показания счётчиков'
                             ' или заказать справку. \nЕсли вы в чем-то запутались или хотите узнать подробней'
                             ' о боте напишите /help\n\nС уважением, создатели проекта.', reply_markup=understand())
    globalVar[str(message.chat.id)]['move'] = '0'
    globalVar[str(message.chat.id)]['appeal_text'] = ''
    globalVar[str(message.chat.id)]['meter'] = list()
    deleting(message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)
    try:
        bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['message_id']))
    except Exception:
        None

    try:
        bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['error_messages']))
    except Exception:
        None

    if globalVar[str(message.chat.id)]['photo_url'] != '' and globalVar[str(message.chat.id)]['photo_url'] != 'error':
        os.remove(globalVar[str(message.chat.id)]['photo_url'])

    if check(message.chat.id):
        s = requests.Session()
        send_to = f'telegram/user/{str(message.chat.id)}'
        r = s.get(f'{url}/{send_to}')
        firstname = json.loads(r.text)['user']['fullname'].split()[1].capitalize()
        a = bot.send_message(message.chat.id, f"С возвращением, *{firstname}*!\nВыберите действие:",
                             reply_markup=menu_authorized(), parse_mode="Markdown")
    else:
        a = bot.send_message(message.chat.id, "Здравствуйте!\nВыберите действие:", reply_markup=menu())

    if globalVar[str(message.chat.id)]['topic'] != None:
        bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['topic']))
        globalVar[str(message.chat.id)]['topic'] = None
    globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.delete_message(message.chat.id, message.message_id)
    try:
        bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['error_messages']))
    except Exception:
        None
    if len(globalVar[str(message.chat.id)]['help_message']) != 0:
        for id in globalVar[str(message.chat.id)]['help_message']:
            bot.delete_message(message.chat.id, id)
    globalVar[str(message.chat.id)]['help_message'] = list()
    a = bot.send_media_group(message.chat.id, media=[(InputMediaPhoto(media='https://github.com/NoName2201/tg_bot/blob/master/photos_help/0.jpg?raw=true', caption='Стартовое меню.\n'
                                                                                                                                                               'Чтобы открыть доступ к панеле пользователя вам необходимо авторизоваться.')),
                                                 (InputMediaPhoto(media='https://github.com/NoName2201/tg_bot/blob/master/photos_help/1.jpg?raw=true', caption='Вход в аккаунт.\n'
                                                                                                                                                               'Вам необходимо указать в два сообщения вашу почту и пароль')),
                                                 (InputMediaPhoto(media='https://github.com/NoName2201/tg_bot/blob/master/photos_help/2.jpg?raw=true', caption='Авторизованное меню\n'
                                                                                                                                                               'Вы прошли авторизацию и вам доступны на выбор\n'
                                                                                                                                                               '• Жалобы (предусматривают подачу и просмотр жалоб)\n'
                                                                                                                                                               '• Счётчики (позволяют изменить показания счётчиков в период с 20 по 25 числа месяца\n'
                                                                                                                                                               '• Справки (открывают заказ и просмотр справок')),
                                                 (InputMediaPhoto(media='https://github.com/NoName2201/tg_bot/blob/master/photos_help/3.jpg?raw=true', caption='Подача жалобы\n'
                                                                                                                                                               'Укажите возникшую проблему в любом удобном вам формате\n'
                                                                                                                                                               '(текст и фото по отдельности; фото и текст одним сообщением)')),
                                                 (InputMediaPhoto(media='https://github.com/NoName2201/tg_bot/blob/master/photos_help/4.jpg?raw=true', caption='Пример подачи жалобы с фото')),
                                                 (InputMediaPhoto(media='https://github.com/NoName2201/tg_bot/blob/master/photos_help/5.jpg?raw=true', caption='Меню ваших жалоб\n'
                                                                                                                                                               'Вы можете просмотреть поданные жалобы и определить, какие из них ожидают просмотра, находятся в работе, выполнены или отклонены')),
                                                 (InputMediaPhoto(media='https://github.com/NoName2201/tg_bot/blob/master/photos_help/6.jpg?raw=true', caption='Заказ справки\n'
                                                                                                                                                               'Система проверяет ваши данные в системе и просит у вас подтверждения\n'
                                                                                                                                                               'В случае ошибки, незамедлительно обратитесь к нам через раздел "Пожаловаться"')),
                                                 (InputMediaPhoto(media='https://github.com/NoName2201/tg_bot/blob/master/photos_help/7.jpg?raw=true', caption='Подача счётчиков\n'
                                                                                                                                                               'Данная процедура доступна только в период с 20 по 25 числа каждого месяца\n'
                                                                                                                                                               'Если вы допустили ошибку в даннх - не переживайте, так как через месяц сможете подать верные показания')),
                                                 (InputMediaPhoto(media='https://github.com/NoName2201/tg_bot/blob/master/photos_help/8.jpg?raw=true', caption='Подача счётчиков'))
                                                 ])

    for id in a:
        globalVar[str(message.chat.id)]['help_message'].append(id.message_id)
    a = bot.send_message(message.chat.id, 'Если у вас остались вопросы в работе бота, напишите нам через раздел "Пожаловаться"', reply_markup=understand1())
    globalVar[str(message.chat.id)]['help_message'].append(a.message_id)


@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'contact'])
def error(message):
    error_func(message.chat.id, message.message_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        global url, globalVar
        cmcd = call.message.chat.id
        cmmi = call.message.message_id
        print(cmcd, call.data)
        try:
            bot.delete_message(cmcd, int(globalVar[str(cmcd)]['error_messages']))
        except Exception:
            None

        if call.data == "log_in":
            a = bot.edit_message_text("Введите адрес электронной почты для авторизации:",
                                  cmcd, cmmi, reply_markup=back3())
            deleting(cmcd)
            bot.register_next_step_handler(a, logging_in, cmmi)

        elif call.data == 'registration':
            bot.delete_message(cmcd, cmmi)
            a = bot.send_message(cmcd, f'Регистрация проходит на сайте:\nhttps://prof-uk.ru/signup', reply_markup=back3())
            globalVar[str(cmcd)]['message_id'] = str(a.message_id)

        elif call.data == 'appeals':
            bot.delete_message(cmcd, cmmi)
            a = bot.send_message(cmcd, '*Жалобы*', parse_mode="Markdown")
            b = bot.send_message(cmcd, 'Выберите действие:', reply_markup=menu_appeals())
            deleting(cmcd)
            globalVar[str(cmcd)]['topic'] = str(a.message_id)
            globalVar[str(cmcd)]['message_id'] = str(b.message_id)

        elif call.data == 'meter':
            bot.delete_message(cmcd, cmmi)
            a = bot.send_message(cmcd, '*Счётчики*', parse_mode="Markdown")
            s = requests.Session()
            send_to = f'telegram/user/{cmcd}'
            r = s.get(f'{url}/{send_to}')
            deleting(cmcd)
            if json.loads(r.text)['user']['meterReadings']:
                hotWaterSupply = json.loads(r.text)['user']['meterReadings'][-1]['hotWaterSupply']
                coldWaterSupply = json.loads(r.text)['user']['meterReadings'][-1]['coldWaterSupply']

                date = (json.loads(r.text)['user']['meterReadings'][-1]['time'])
                today = int(str(datetime.date.today()).split('-')[2])
                month = int(str(datetime.date.today()).split('-')[1])
                if today > 19 and today < 26\
                        and int(json.loads(r.text)['user']['meterReadings'][-1]['time'].split('.')[1]) != month:
                    b = bot.send_message(cmcd,f'Ваши последние показания счётчиков:\n'
                                              f'\nДата обновления: *{date}*\n'
                                              f'\nХолодная вода: *{coldWaterSupply}*'
                                              f'\nГорячая вода: *{hotWaterSupply}*',
                                         parse_mode='Markdown', reply_markup=menu_meter())
                elif today < 20:
                    b = bot.send_message(cmcd, f'Ваши последние показания счётчиков:\n'
                                               f'\nДата обновления: *{date}*\n'
                                               f'\nХолодная вода: *{coldWaterSupply}*'
                                               f'\nГорячая вода: *{hotWaterSupply}*'
                                               f'\n\nВы сможете обновить показания только,'
                                               f' в период с 20 по 25 числа месяца',
                                         parse_mode='Markdown')
                    globalVar[str(cmcd)]['to_delete'].append(b.message_id)
                    b = bot.send_message(cmcd, 'Если вы допустили ошибку при отправке данных,'
                                               ' напишите нам в разделе *"Жалобы"*', parse_mode='Markdown',
                                         reply_markup=back2())
                else:
                    b = bot.send_message(cmcd, f'Ваши последние показания счётчиков:\n'
                                               f'\nДата обновления: *{date}*\n'
                                               f'\nХолодная вода: *{coldWaterSupply}*'
                                               f'\nГорячая вода: *{hotWaterSupply}*'
                                               f'\n\nВы сможете обновить показания только в следующем месяце,'
                                               f' в период с 20 по 25 числа месяца',
                                         parse_mode='Markdown')
                    globalVar[str(cmcd)]['to_delete'].append(b.message_id)
                    b = bot.send_message(cmcd, 'Если вы допустили ошибку при отправке данных,'
                                               ' напишите нам в разделе *"Жалобы"*', parse_mode='Markdown',
                                         reply_markup=back2())
            else:
                today = int(str(datetime.date.today()).split('-')[2])
                if today > 19 and today < 26:
                    b = bot.send_message(cmcd, 'У вас отстутсвуют данные счетчиков. Хотите указать?',
                                     reply_markup=menu_meter())
                elif today < 20:
                    b = bot.send_message(cmcd,
                                         'У вас отстутсвуют данные счетчиков.'
                                         ' Вы сможете их указать только в период с 20 по 25 числа месяца',
                                         reply_markup=back2())
                else:
                    b = bot.send_message(cmcd, 'У вас отстутсвуют данные счетчиков.'
                                               ' Вы сможете их указать только в следующем месяце',
                                         reply_markup=back2())
            globalVar[str(cmcd)]['topic'] = str(a.message_id)
            globalVar[str(cmcd)]['message_id'] = str(b.message_id)

        elif call.data == 'create__appeal':
            deleting(cmcd)
            a = bot.edit_message_text('Опишите возникшую проблему:', cmcd, cmmi, reply_markup=back_to_menu_appeals())
            bot.register_next_step_handler(a, create_appeal, cmmi)

        elif call.data == 'send_text':
            text = 'Опишите возникшую проблему:'
            a = bot.edit_message_text(text, cmcd, cmmi, reply_markup=back_to_menu_appeals())
            b = globalVar[str(cmcd)]['to_delete'].pop()
            c = globalVar[str(cmcd)]['to_delete'].pop()
            bot.delete_message(cmcd, b)
            bot.delete_message(cmcd, c)
            bot.register_next_step_handler(a, send_text, cmmi, text)

        elif call.data == 'send_photo':
            a = bot.edit_message_text('Пришлите фотографию возникшей проблемы:', cmcd, cmmi,
                                  reply_markup=back_to_menu_appeals2())
            if globalVar[str(cmcd)]['photo_url'] == 'error':
                b = globalVar[str(cmcd)]['to_delete'].pop()
                c = globalVar[str(cmcd)]['to_delete'].pop()
                bot.delete_message(cmcd, b)
                bot.delete_message(cmcd, c)
            bot.register_next_step_handler(a, send_photo, cmmi)

        elif call.data == 'upload_my_appeal':
            a = bot.edit_message_text('Хотите отправить фотографию по проблеме?', cmcd, cmmi,
                                      reply_markup=upload_my_appeal())

        elif call.data == 'send_appeal':
            send_appeal(cmcd, cmmi)

        elif call.data == 'my__appeals':
            bot.edit_message_text('Ваши жалобы:', cmcd, cmmi)
            my_appeals(cmcd)

        elif call.data == 'reload_my_appeal':
            my_appeals(cmcd)

        elif call.data == 'choose_appeal_back':
            globalVar[str(cmcd)]['move'] = str(int(globalVar[str(cmcd)]['move']) - 1)
            my_appeals(cmcd)

        elif call.data == 'choose_appeal_forward':
            globalVar[str(cmcd)]['move'] = str(int(globalVar[str(cmcd)]['move']) + 1)
            my_appeals(cmcd)

        elif call.data == 'update_meter':
            deleting(cmcd)
            bot.delete_message(cmcd, int(globalVar[str(cmcd)]['message_id']))
            with open('uploads/file_for_meter.jpg', 'rb') as f:
                img = f.read()
            a = bot.send_photo(photo=img, caption='Введите показания счетчика *ГВС*\n(Только черные цифры до запятой):',
                               parse_mode="Markdown",
                               chat_id=cmcd, reply_markup=back_to_menu_choose_meter())
            globalVar[str(cmcd)]['message_id'] = str(a.message_id)
            bot.register_next_step_handler(a, hot_water_update, a.message_id, img)

        elif call.data == 'send_meter':
            send_meter1(cmcd)

        elif call.data == 'statements':
            bot.delete_message(cmcd, cmmi)
            globalVar[str(cmcd)]['move'] = str(0)
            deleting(cmcd)
            if globalVar[str(cmcd)]['topic'] == None:
                a = bot.send_message(cmcd, '*Справки*', parse_mode="Markdown")
                globalVar[str(cmcd)]['topic'] = str(a.message_id)
            b = bot.send_message(cmcd, 'Выберите действие:', reply_markup=menu_statements())
            globalVar[str(cmcd)]['message_id'] = str(b.message_id)

        elif call.data == 'create__statement__question':
            bot.delete_message(cmcd, cmmi)

            s = requests.Session()
            send_to = f'telegram/user/{cmcd}'
            r = s.get(f'{url}/{send_to}')
            r = json.loads(r.text)
            FNP = r['user']['fullname'].split()
            if FNP[2] != 'Отсутствует':
                fullname = f'{FNP[0]} {FNP[1][0]}. {FNP[2][0]}.'
            else:
                fullname = f'{FNP[0]} {FNP[1][0]}.'
            phone = r['user']['phone']
            house = r['user']['house']
            city = house['city']
            address = house['address']
            flat = r['user']['flat']
            if phone[:2] != '+7' and phone[:2] != '8 ':
                pat = "(.*)(\d{4})$"
                mask_part, public_part = re.match(pat, phone).groups()
                phone = re.sub("\d", "#", mask_part) + '-' + public_part
            else:
                pat = "(.*)(-\d{2}-\d{2})$"
                mask_part, public_part = re.match(pat, phone).groups()
                public_part = public_part.split('-')
                phone = re.sub("\d", "#", mask_part) + '-' + public_part[1] + public_part[2]

            a = bot.send_message(cmcd, f'Обращаем ваше внимание, что все документы формируются на основе данных,'
                                       f' указанных при регистрации.\nВо избежание ошибок, проверьте ваши данные.\n\n'
                                       f'Заказчик: *{fullname}*\n'
                                       f'Телефон: *{phone}*\n'
                                       f'Адрес: *{city}, {address}, кв. {flat}*\n\n'
                                       f'Если в данных допущена ошибка, пожалуйста,'
                                       f' обратитесь к нам через раздел "Жалобы"',
                                 reply_markup=create__statement__confirm(), parse_mode="Markdown")
            globalVar[str(cmcd)]['message_id'] = str(a.message_id)

        elif call.data == 'create__statement__confirmed':
            create_statement_now(cmcd, cmmi)

        elif call.data == 'choose_statement_to_create_forward':
            globalVar[str(cmcd)]['move'] = str(int(globalVar[str(cmcd)]['move']) + 3)
            create_statement_now(cmcd, cmmi)

        elif call.data == 'choose_statement_to_create_back':
            globalVar[str(cmcd)]['move'] = str(int(globalVar[str(cmcd)]['move']) - 3)
            create_statement_now(cmcd, cmmi)

        elif call.data == 'my__statements':
            bot.edit_message_text('Ваши справки:', cmcd, cmmi)
            my_statement(cmcd)

        elif call.data == 'reload_my_statement':
            my_statement(cmcd)

        elif call.data == 'choose_statement_back':
            globalVar[str(cmcd)]['move'] = str(int(globalVar[str(cmcd)]['move']) - 1)
            my_statement(cmcd)

        elif call.data == 'choose_statement_forward':
            globalVar[str(cmcd)]['move'] = str(int(globalVar[str(cmcd)]['move']) + 1)
            my_statement(cmcd)


        elif call.data[:6] == 'order_':
            statement_id = int(call.data[6:])
            if cmmi in globalVar[str(cmcd)]['to_delete']:
                globalVar[str(cmcd)]['to_delete'].remove(cmmi)
                bot.delete_message(cmcd, int(globalVar[str(cmcd)]['message_id']))
                globalVar[str(cmcd)]['message_id'] = str(cmmi)
            deleting(cmcd)
            globalVar[str(cmcd)]['to_delete'].append(int(globalVar[str(cmcd)]['message_id']))
            s = requests.Session()
            send_to = f'houses-from-tg/{cmcd}/statements'
            r = s.get(f'{url}/{send_to}')
            statements = json.loads(r.text)['statements']
            statement = statements[statement_id]['name']
            value = statements[statement_id]['value']
            bot.edit_message_text(f'{statement_id + 1}/{len(statements)}\n{statements[statement_id]["name"]}', cmcd, cmmi)
            a = bot.send_message(cmcd, 'Вы хотите заказать эту справку?', reply_markup=order_statement(value))
            globalVar[str(cmcd)]['message_id'] = str(a.message_id)

        elif call.data[:15] == 'send_statement_':
            s = requests.Session()
            payload = {'value': str(call.data[15:])}
            send_to = f'appeals-from-tg/{cmcd}/order-statement'
            r = s.post(f'{url}/{send_to}', json=payload)
            bot.edit_message_text('Справка успешно заказана!', cmcd, cmmi, reply_markup=back_to_menu_statements())


        elif call.data == 'exit':
            bot.edit_message_text('Вы уверены, что хотите выйти из аккаунта❓', cmcd, cmmi, reply_markup=exit_confirm())

        elif call.data == 'exit_confirmed':
            exit(call.message.chat.id)
            deleting(cmcd)
            bot.edit_message_text('Вы вышли из аккаунта❗', cmcd, cmmi, reply_markup=menu())

        elif call.data == 'back_to_menu':
            bot.clear_step_handler_by_chat_id(cmcd)  # Может это вызывает ошибку при входе с двух устройств одновременно
            deleting(cmcd)
            bot.edit_message_text('Выберите действие:', cmcd, cmmi, reply_markup=menu())

        elif call.data == 'back_to_menu_authorized':
            try:
                bot.delete_message(cmcd, int(globalVar[str(cmcd)]['topic']))
            except Exception:
                None
            globalVar[str(cmcd)]['topic'] = None
            bot.clear_step_handler_by_chat_id(cmcd)
            deleting(cmcd)
            bot.delete_message(cmcd, cmmi)
            s = requests.Session()
            send_to = f'telegram/user/{str(cmcd)}'
            r = s.get(f'{url}/{send_to}')
            firstname = json.loads(r.text)['user']['fullname'].split()[1].capitalize()
            a = bot.send_message(cmcd, f"Приветствуем, *{firstname}*!\nВыберите действие:",
                                     reply_markup=menu_authorized(), parse_mode="Markdown")
            globalVar[str(cmcd)]['message_id'] = str(a.message_id)


        elif call.data == 'back_to_menu_appeals':
            if globalVar[str(cmcd)]['photo_url'] != '' and globalVar[str(cmcd)]['photo_url'] != 'error':
                os.remove(globalVar[str(cmcd)]['photo_url'])
            globalVar[str(cmcd)]['appeal_text'] = ''
            globalVar[str(cmcd)]['photo_url'] = ''
            globalVar[str(cmcd)]['move'] = str(0)
            bot.clear_step_handler_by_chat_id(cmcd)
            deleting(cmcd)
            bot.delete_message(cmcd, globalVar[str(cmcd)]['message_id'])
            a = bot.send_message(cmcd, 'Выберите действие:', reply_markup=menu_appeals())
            (globalVar[str(cmcd)]['message_id']) = str(a.message_id)

        elif call.data == 'back_to_menu_choose_meter':
            bot.clear_step_handler_by_chat_id(cmcd)
            deleting(cmcd)
            bot.delete_message(cmcd, globalVar[str(cmcd)]['message_id'])
            s = requests.Session()
            send_to = f'telegram/user/{cmcd}'
            r = s.get(f'{url}/{send_to}')
            deleting(cmcd)
            if json.loads(r.text)['user']['meterReadings']:
                hotWaterSupply = json.loads(r.text)['user']['meterReadings'][-1]['hotWaterSupply']
                coldWaterSupply = json.loads(r.text)['user']['meterReadings'][-1]['coldWaterSupply']

                today = int(str(datetime.date.today()).split('-')[2])
                month = int(str(datetime.date.today()).split('-')[1])
                date = (json.loads(r.text)['user']['meterReadings'][-1]['time'])
                if today > 19 and today < 26\
                        and int(json.loads(r.text)['user']['meterReadings'][-1]['time'].split('.')[1]) != month:
                    a = bot.send_message(cmcd, f'Ваши последние показания счётчиков:\n'
                                            f'\nДата обновления: *{date}*\n'
                                            f'\nХолодная вода: *{coldWaterSupply}*'
                                            f'\nГорячая вода: *{hotWaterSupply}*',
                                        parse_mode='Markdown', reply_markup=menu_meter())
                else:
                    a = bot.send_message(cmcd, f'Ваши последние показания счётчиков:\n'
                                               f'\nДата обновления: *{date}*\n'
                                               f'\nХолодная вода: *{coldWaterSupply}*'
                                               f'\nГорячая вода: *{hotWaterSupply}*'
                                               f'\n\nВы сможете обновить показания только в следующем месяце,'
                                               f' в период с 20 по 25 числа месяца',
                                         parse_mode='Markdown')
                    globalVar[str(cmcd)]['to_delete'].append(a.message_id)
                    a = bot.send_message(cmcd,
                                         'Если вы допустили ошибку при отправке данных,'
                                         ' напишите нам в разделе *"Жалобы"*',
                                         parse_mode='Markdown', reply_markup=back2())
            else:
                a = bot.send_message(cmcd, 'У вас отстутсвуют данные счетчиков. Хотите указать?',
                                     reply_markup=menu_meter())
            (globalVar[str(cmcd)]['message_id']) = str(a.message_id)
            globalVar[str(cmcd)]['meter'] = list()

        elif call.data == 'delete_notification':
            bot.delete_message(cmcd, cmmi)

        elif call.data == 'delete_notification1':
            for id in globalVar[str(cmcd)]['help_message']:
                bot.delete_message(cmcd, id)
            globalVar[str(cmcd)]['help_message'] = list()


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
