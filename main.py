import datetime
import time
import telebot
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim
import json
import requests
from validate_email import validate_email

geolocator = Nominatim(user_agent="tg_bot")

tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))
globalVar = dict()


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


def menu_authorized():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    appeals = InlineKeyboardButton("Жалобы", callback_data="appeals")
    meter = InlineKeyboardButton("Счётчики", callback_data="meter")
    exit = InlineKeyboardButton("Выйти из аккаунта", callback_data="exit")
    markup.add(appeals, meter, exit)
    return markup


def menu_appeals():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    create__appeal = InlineKeyboardButton("Пожаловаться", callback_data="create__appeal")
    my__appeals = InlineKeyboardButton("Мои жалобы", callback_data="my__appeals")
    back_to_menu_authorized = InlineKeyboardButton('Назад', callback_data='back_to_menu_authorized')
    markup.add(create__appeal, my__appeals, back_to_menu_authorized)
    return markup


def menu_meter():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    update_meter = InlineKeyboardButton("Обновить показания", callback_data="update_meter")
    back_to_menu_authorized = InlineKeyboardButton('Назад', callback_data='back_to_menu_authorized')
    markup.add(update_meter, back_to_menu_authorized)
    return markup


def send_meter():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    send_meter = InlineKeyboardButton("Да", callback_data="send_meter")
    back_to_menu_choose_meter = InlineKeyboardButton('Назад', callback_data='back_to_menu_choose_meter')
    markup.add(send_meter, back_to_menu_choose_meter)
    return markup


def choose_appeal():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2  # Ширина поля кнопок
    choose_appeal_back = InlineKeyboardButton("<--", callback_data='choose_appeal_back')
    choose_appeal_forward = InlineKeyboardButton("-->", callback_data="choose_appeal_forward")
    reload_my_appeal = InlineKeyboardButton('Обновить', callback_data='reload_my_appeal')
    back_to_menu_appeal = InlineKeyboardButton('Назад', callback_data='back_to_menu_appeals')
    markup.add(choose_appeal_back, choose_appeal_forward)
    markup.row_width = 1  # Ширина поля кнопок
    markup.add(reload_my_appeal, back_to_menu_appeal)
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
            print(globalVar)
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
    reload_my_appeal = InlineKeyboardButton('Обновить', callback_data='reload_my_appeal')
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
    update_meter = InlineKeyboardButton("Повторить ввод", callback_data="update_meter")
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
    log_in = InlineKeyboardButton('Повторить ввод', callback_data='log_in')
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(back_to_menu, log_in)
    return markup


def upload_my_appeal0():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    send_text = InlineKeyboardButton('Да', callback_data='send_text')
    back_to_menu_appeals = InlineKeyboardButton('Назад в меню', callback_data='back_to_menu_appeals')
    markup.add(send_text, back_to_menu_appeals)
    return markup


def upload_my_appeal():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    send_appeal = InlineKeyboardButton('Отправить жалобу без фото', callback_data='send_appeal')
    back_to_menu_appeals = InlineKeyboardButton('Назад в меню', callback_data='back_to_menu_appeals')
    send_photo = InlineKeyboardButton('Да', callback_data='send_photo')
    markup.add(send_photo, send_appeal, back_to_menu_appeals)
    return markup

def upload_my_appeal1():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    send_appeal = InlineKeyboardButton('Да', callback_data='send_appeal')
    back_to_menu_appeals = InlineKeyboardButton('Назад в меню', callback_data='back_to_menu_appeals')
    markup.add(send_appeal, back_to_menu_appeals)
    return markup

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
    except Exception:
        if message.text.lower() == '/start':
            error_func(message.chat.id, message.message_id)
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
    bot.edit_message_text('Ваша жалоба принята💀', id, bot_message_id, reply_markup=back_to_menu_appeals())
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
    print(f'{url}/{send_to}')
    r = s.post(f'{url}/{send_to}', json=payload)
    print(r.text)
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
        if int(globalVar[str(id)]['move']) >= len(appeals):
            globalVar[str(id)]['move'] = str(len(appeals))
            try:
                bot.delete_message(id, int(globalVar[str(id)]['message_id']))
                a = bot.send_message(id, 'У вас нет более старых жалоб',
                                    reply_markup=choose_appeal())
            except Exception:
                None
        elif int(globalVar[str(id)]['move']) <= -1:
            globalVar[str(id)]['move'] = str(-1)
            try:
                bot.delete_message(id, int(globalVar[str(id)]['message_id']))
                a = bot.send_message(id, 'У вас нет более новых жалоб',
                                reply_markup=choose_appeal())
            except Exception:
                None
        elif json.loads(r.text)['appeals'] and len(appeals) != 0:
            appeal_id = int(globalVar[str(id)]['move'])
            t = appeals[appeal_id]
            date = str(t['dateOfRequest'])
            status = str(t['status'])
            text = str(t['text'])
            img = t['image']
            rejectReason = ''
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
                                                        chat_id=id, reply_markup=choose_appeal())
                    else:
                        bot.delete_message(id, int(globalVar[str(id)]['message_id']))
                        a = bot.send_message(id, f'{appeal_id + 1}/{len(appeals)}\n'
                                                    f'Дата: *{date}*\n'
                                                    f'Статус: *{status}*{rejectReason}\n\nТекст обращения:\n*{text}*',
                                                    reply_markup=choose_appeal(), parse_mode="Markdown")
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


def error_func(id,bot_message_id):
    if str(id) not in globalVar:
        globalVar[str(id)] = {}
        globalVar[str(id)]['to_delete'] = list()
        globalVar[str(id)]['topic'] = None
        globalVar[str(id)]['error_messages'] = None
        globalVar[str(id)]['message_id'] = str(id)
        globalVar[str(id)]['move'] = '0'
        globalVar[str(id)]['appeal_text'] = ''
        globalVar[str(id)]['photo_url'] = ''
        globalVar[str(id)]['meter'] = list()
    try:
        bot.delete_message(id, int(globalVar[str(id)]['error_messages']))
    except Exception:
        None
    bot.delete_message(id, bot_message_id)
    a = bot.send_message(id, 'Воспользуйтесь предложенными кнопками. '
                                      'Если кнопки исчезли, введите команду /start')
    globalVar[str(id)]['error_messages'] = a.message_id


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global globalVar
    print(globalVar)

    if str(message.chat.id) not in globalVar:

        globalVar[str(message.chat.id)] = {}
        globalVar[str(message.chat.id)]['to_delete'] = list()
        globalVar[str(message.chat.id)]['topic'] = None
        globalVar[str(message.chat.id)]['error_messages'] = list()
        globalVar[str(message.chat.id)]['message_id'] = str(message.message_id)
        globalVar[str(message.chat.id)]['move'] = '0'
        globalVar[str(message.chat.id)]['appeal_text'] = ''
        globalVar[str(message.chat.id)]['photo_url'] = ''
        globalVar[str(message.chat.id)]['meter'] = list()

    globalVar[str(message.chat.id)]['move'] = '0'
    globalVar[str(message.chat.id)]['appeal_text'] = ''
    globalVar[str(message.chat.id)]['meter'] = list()
    deleting(message.chat.id)
    if globalVar[str(message.chat.id)]['photo_url'] != '' and globalVar[str(message.chat.id)]['photo_url'] != 'error':
        os.remove(globalVar[str(message.chat.id)]['photo_url'])
    try:
        bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['error_messages']))
    except Exception:
        None

    if check(message.chat.id):
        s = requests.Session()
        send_to = f'telegram/user/{str(message.chat.id)}'
        r = s.get(f'{url}/{send_to}')
        firstname = json.loads(r.text)['user']['fullname'].split()[1].capitalize()
        bot.delete_message(message.chat.id, message.message_id)
        a = bot.send_message(message.chat.id, f"С возвращением, *{firstname}*!\nВыберите действие:",
                             reply_markup=menu_authorized(), parse_mode="Markdown")
        if int(globalVar[str(message.chat.id)]['message_id']) != message.message_id:
            bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['message_id']))
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id + 1)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        a = bot.send_message(message.chat.id, "Здравствуйте!\nВыберите действие:", reply_markup=menu())
        if int(globalVar[str(message.chat.id)]['message_id']) != message.message_id:
            bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['message_id']))
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id + 1)

    if globalVar[str(message.chat.id)]['topic'] != None:
        bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['topic']))
        globalVar[str(message.chat.id)]['topic'] = None
    globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)


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
            a = bot.send_message(cmcd, f'Регистрация проходит на сайте:\n {url}', reply_markup=back3())
            globalVar[str(cmcd)]['message_id'] = str(a.message_id)

        elif call.data == 'appeals':
            bot.delete_message(cmcd, cmmi)
            a = bot.send_message(cmcd, '*Жалобы*', parse_mode="Markdown")
            b = bot.send_message(cmcd, 'Выберите действие:', reply_markup=menu_appeals())
            deleting(cmcd)
            globalVar[str(cmcd)]['topic'] = str(a.message_id)
            globalVar[str(cmcd)]['message_id'] = str(b.message_id)
            print(globalVar)

        elif call.data == 'meter':
            bot.delete_message(cmcd, cmmi)
            a = bot.send_message(cmcd, '*Счётчики*', parse_mode="Markdown")
            s = requests.Session()
            send_to = f'telegram/user/{cmcd}'
            r = s.get(f'{url}/{send_to}')
            print(json.loads(r.text)['user'])
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
                                     reply_markup=back2())
                elif today < 20:
                    b = bot.send_message(cmcd,
                                         'У вас отстутсвуют данные счетчиков.'
                                         ' Вы сможете их указать только в период с 20 по 25 числа месяца',
                                         reply_markup=menu_meter())
                else:
                    b = bot.send_message(cmcd, 'У вас отстутсвуют данные счетчиков.'
                                               ' Вы сможете их указать только в следующем месяце',
                                         reply_markup=back2())
            globalVar[str(cmcd)]['topic'] = str(a.message_id)
            globalVar[str(cmcd)]['message_id'] = str(b.message_id)
            print(globalVar)

        elif call.data == 'create__appeal':
            a = bot.edit_message_text('Опишите возникшую проблему:', cmcd, cmmi, reply_markup=back_to_menu_appeals())
            bot.register_next_step_handler(a, create_appeal, cmmi)

        elif call.data == 'send_text':
            text = 'Опишите возникшую проблему:'
            print(globalVar)
            a = bot.edit_message_text(text, cmcd, cmmi, reply_markup=back_to_menu_appeals())
            b = globalVar[str(cmcd)]['to_delete'].pop()
            c = globalVar[str(cmcd)]['to_delete'].pop()
            print(globalVar)
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
            with open('uploads/file_for_meter.jpg','rb') as f:
                img = f.read()
            a = bot.send_photo(photo=img, caption='Введите показания счетчика *ГВС*\n(Только черные цифры до запятой):',
                               parse_mode="Markdown",
                               chat_id=cmcd, reply_markup=back_to_menu_choose_meter())
            globalVar[str(cmcd)]['message_id'] = str(a.message_id)
            bot.register_next_step_handler(a, hot_water_update, a.message_id, img)


        elif call.data == 'send_meter':
            send_meter1(cmcd)

        elif call.data == 'exit':
            exit(call.message.chat.id)
            deleting(cmcd)
            bot.edit_message_text('Вы вышли из аккаунта❗', cmcd, cmmi, reply_markup=menu())

        elif call.data == 'back_to_menu':
            bot.clear_step_handler_by_chat_id(cmcd)  # Может это вызывает ошибку при входе с двух устройств одновременно
            deleting(cmcd)
            bot.edit_message_text('Выберите действие:', cmcd, cmmi, reply_markup=menu())

        elif call.data == 'back_to_menu_authorized':
            bot.delete_message(cmcd, int(globalVar[str(cmcd)]['topic']))
            globalVar[str(cmcd)]['topic'] = None
            bot.clear_step_handler_by_chat_id(cmcd)
            deleting(cmcd)
            bot.edit_message_text('Выберите действие:', cmcd, cmmi, reply_markup=menu_authorized())

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
