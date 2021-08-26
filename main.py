import datetime
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim
import json
import requests
from validate_email import validate_email

geolocator = Nominatim(user_agent="tg_bot")

tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))
globalVar = dict()

token = '1917275192:AAFfAT_ggb_QS8Shwp6G2aNbuid69pfSNQ4'  # bot constants Проф1
#token = '1916725688:AAH7DNy9VshGWp1FE25K38Dv9kcuDRnj6_E'  # bot constants Проф2
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
    exit = InlineKeyboardButton("Выйти из аккаунта", callback_data="exit")
    markup.add(appeals, exit)
    return markup


def menu_appeals():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    create__appeal = InlineKeyboardButton("Пожаловаться", callback_data="create__appeal")
    my__appeals = InlineKeyboardButton("Мои жалобы", callback_data="my__appeals")
    back_to_menu_authorized = InlineKeyboardButton('Назад', callback_data='back_to_menu_authorized')
    markup.add(create__appeal, my__appeals, back_to_menu_authorized)
    return markup

def choose_appeal():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2  # Ширина поля кнопок
    choose_appeal_back = InlineKeyboardButton("<--", callback_data='choose_appeal_back')
    choose_appeal_forward = InlineKeyboardButton("-->", callback_data="choose_appeal_forward")
    back_to_menu_appeals = InlineKeyboardButton('Назад', callback_data='back_to_menu_appeals')
    markup.add(choose_appeal_back, choose_appeal_forward, back_to_menu_appeals)
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


def logging_in2(message, logs, id):
    global globalVar
    logs.append(message.text)
    globalVar[str(message.chat.id)]['to_delete'].append(id)
    globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
    s = requests.Session()
    payload = {"email": logs[0].lower(), "password": logs[1], "chat_id": str(message.chat.id)}
    send_to = 'telegram/connect'
    r = s.post(f'{url}/{send_to}', json=payload)
    try:
        if json.loads(r.text)['user'] and json.loads(r.text)['user']['emailVerified']:
            bot.edit_message_text('Введите пароль:', message.chat.id, id)  # editing = 0
            a = bot.send_message(message.chat.id, 'Вы вошли в свой аккаунт!✅', reply_markup=menu_authorized())  # editing = 4
            globalVar[str(message.chat.id)]['message_id'] = str(a.message_id)
        else:
            bot.edit_message_text('Введите пароль:', message.chat.id, id)  # editing = 0
            a = bot.send_message(message.chat.id,
                                 'Вы не подтвердили почту! Перейдите по ссылке в письме и повторите авторизацию',
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


def deleting(chat_id):
    if len(globalVar[str(chat_id)]['to_delete']) != 0:
        for message in globalVar[str(chat_id)]['to_delete']:
            bot.delete_message(chat_id, message)
    globalVar[str(chat_id)]['to_delete'] = list()


def check(id):
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


def back_to_menu_appeals():
    markup = InlineKeyboardMarkup()
    back_to_menu_appeals = InlineKeyboardButton('Назад', callback_data='back_to_menu_appeals')
    markup.add(back_to_menu_appeals)
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


def create_appeal(message, bot_message_id):
    a = bot.edit_message_text('Опишите вашу проблему:', message.chat.id, bot_message_id)
    s = requests.Session()
    id = message.chat.id
    payload = {"text": message.text,"chat_id": str(id)}
    send_to = 'appeals/create'
    r = s.post(f'{url}/{send_to}', json=payload)
    globalVar[str(message.chat.id)]['to_delete'].append(bot_message_id)
    globalVar[str(message.chat.id)]['to_delete'].append(message.message_id)
    a = bot.send_message(id, 'Ваша жалоба принята💀', reply_markup=back_to_menu_appeals())
    globalVar[str(cmcd)]['message_id'] = str(a.message_id)


def my_appeals(bot_message_id, id):
    s = requests.Session()
    payload = {"chat_id": str(id)}
    send_to = 'appeals/my'
    r = s.get(f'{url}/{send_to}', json=payload)
    flag = False
    try:
        appeals = json.loads(r.text)['appeals']
        flag = True
        appeals = appeals[::-1]
        if int(globalVar[str(id)]['move']) >= len(appeals):
            globalVar[str(id)]['move'] = str(len(appeals))
            bot.edit_message_text('У вас нет более старых жалоб', id, bot_message_id,
                                 reply_markup=choose_appeal())
        elif int(globalVar[str(id)]['move']) <= -1:
            globalVar[str(id)]['move'] = str(-1)
            bot.edit_message_text('У вас нет более новых жалоб', id, bot_message_id,
                                 reply_markup=choose_appeal())
        elif json.loads(r.text)['appeals'] and len(appeals)!=0:
            appeal_id = int(globalVar[str(id)]['move'])
            t = appeals[appeal_id]
            date = str(date_update(datetime1=str(t['dateOfRequest']))).split('-')
            status = str(t['status'])
            text = str(t['text'])
            if status == 'waiting':
                status = 'Ожидание'
            elif status == 'in_work':
                status = 'В работе'
            elif status == 'done':
                status = "Выполнено"
            elif status == 'rejected':
                status = 'Отклонено'
            if len(appeals)-1 == 0:
                bot.edit_message_text(f'Дата: *{str(date[2])[:2]}.{date[1]}.{date[0]}*\nСтатус: *{status}*\n*{text}*', id,
                                          bot_message_id, reply_markup=back_to_menu_appeals(), parse_mode="Markdown")
            else:
                bot.edit_message_text(f'Дата: *{str(date[2])[:2]}.{date[1]}.{date[0]}*\nСтатус: *{status}*\n*{text}*', id,
                                          bot_message_id, reply_markup=choose_appeal(), parse_mode="Markdown")
            globalVar[str(id)]['to_delete'].append(b.message_id)
        else:
            b = bot.send_message(id, 'Вы не отправляли ни одной жалобы')
            globalVar[str(id)]['to_delete'].append(b.message_id)
    except Exception:
        if not flag:
            b = bot.send_message(id, 'Вы не отправляли ни одной жалобы')
            globalVar[str(id)]['to_delete'].append(b.message_id)
            globalVar[str(id)]['to_delete'].append(bot_message_id)
            a = bot.send_message(id, 'Выберите действие', reply_markup=back_to_menu_appeals())
            globalVar[str(cmcd)]['message_id'] = str(a.message_id)


def date_update(datetime1):
    year = int(datetime1[:4])
    month = int(datetime1[5:7])
    day = int(datetime1[8:10])
    hour = int(datetime1[11:13])
    all = datetime.datetime(year=year, month=month, day=day, hour=hour) + datetime.timedelta(hours=3)
    return all


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

    globalVar[str(message.chat.id)]['move'] = '0'
    deleting(message.chat.id)
    try:
        bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['error_messages']))
    except Exception:
        None

    if check(message.chat.id):
        s = requests.Session()
        payload = {"chat_id": message.chat.id}
        send_to = 'telegram/user'
        r = s.get(f'{url}/{send_to}', json=payload)
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
    if str(message.chat.id) not in globalVar:
        globalVar[str(message.chat.id)] = {}
        globalVar[str(message.chat.id)]['to_delete'] = list()
        globalVar[str(message.chat.id)]['topic'] = None
        globalVar[str(message.chat.id)]['error_messages'] = None
        globalVar[str(message.chat.id)]['message_id'] = str(message.message_id)
        globalVar[str(message.chat.id)]['move'] = '0'
    try:
        bot.delete_message(message.chat.id, int(globalVar[str(message.chat.id)]['error_messages']))
    except Exception:
        None
    bot.delete_message(message.chat.id, message.message_id)
    a = bot.send_message(message.chat.id, 'Воспользуйтесь предложенными кнопками. '
                                      'Если кнопки исчезли, введите команду /start')
    globalVar[str(message.chat.id)]['error_messages'] = a.message_id


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        global cmcd, cmmi, url, globalVar
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
            bot.delete_message(cmcd,cmmi)
            a = bot.send_message(cmcd, '*Жалобы*', parse_mode="Markdown")
            b = bot.send_message(cmcd, 'Выберите действие:', reply_markup=menu_appeals())
            deleting(cmcd)
            globalVar[str(cmcd)]['topic'] = str(a.message_id)
            globalVar[str(cmcd)]['message_id'] = str(b.message_id)
            print(globalVar)

        elif call.data == 'create__appeal':
            a = bot.edit_message_text('Опишите вашу проблему:', cmcd, cmmi, reply_markup=back_to_menu_appeals())
            bot.register_next_step_handler(a, create_appeal, cmmi)

        elif call.data == 'my__appeals':
            a = bot.edit_message_text('Ваши жалобы:', cmcd, cmmi)
            my_appeals(cmmi,cmcd)

        elif call.data == 'choose_appeal_back':
            globalVar[str(cmcd)]['move'] = str(int(globalVar[str(cmcd)]['move']) - 1)
            my_appeals(cmmi, cmcd)

        elif call.data == 'choose_appeal_forward':
            globalVar[str(cmcd)]['move'] = str(int(globalVar[str(cmcd)]['move']) + 1)
            my_appeals(cmmi, cmcd)

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
            globalVar[str(cmcd)]['move'] = str(0)
            bot.clear_step_handler_by_chat_id(cmcd)
            deleting(cmcd)
            bot.edit_message_text('Выберите действие:', cmcd, cmmi, reply_markup=menu_appeals())


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
