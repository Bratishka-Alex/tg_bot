import datetime
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

geolocator = Nominatim(user_agent="tg_bot")

tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))
globalVar = dict()

token = '1953842981:AAGfrD0CbWeZHlqh31IiT8pd37ECYw39ZUI'

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
    real_estate = InlineKeyboardButton("Недвижимость", callback_data="real_estate")
    counter_agent = InlineKeyboardButton("Зарегистрироваться", callback_data="counter_agent")
    notarization = InlineKeyboardButton("Нотариальная доверенность", callback_data="notarization")
    markup.add(real_estate, counter_agent, notarization)
    return markup

def menu_real_estate():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    cadastral_number = InlineKeyboardButton("По Кадастровому номеру", callback_data="cadastral_number")
    real_address = InlineKeyboardButton("По Точному адресу", callback_data="real_address")
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(cadastral_number, real_address, back_to_menu)
    return markup

def menu_statements():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    create__statement = InlineKeyboardButton("Заказать справку 📨", callback_data="create__statement__question")
    my__statements = InlineKeyboardButton("Мои справки 📬", callback_data="my__statements")
    back_to_menu_authorized = InlineKeyboardButton('Назад', callback_data='back_to_menu_authorized')
    markup.add(create__statement, my__statements, back_to_menu_authorized)
    return markup


def deleting(chat_id):
    if len(globalVar[str(chat_id)]['to_delete']) != 0:
        for message in globalVar[str(chat_id)]['to_delete']:
            bot.delete_message(chat_id, message)
    globalVar[str(chat_id)]['to_delete'] = list()


def back_to_menu_real_estate():
    markup = InlineKeyboardMarkup()
    back_to_menu_real_estate = InlineKeyboardButton('Назад', callback_data='real_estate')
    markup.add(back_to_menu_real_estate)
    return markup

def back_to_menu_real_estate_or_try_again():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    try_again = InlineKeyboardButton('Повторить ввод', callback_data='try_again')
    back_to_menu_real_estate = InlineKeyboardButton('Назад', callback_data='real_estate')
    markup.add(try_again, back_to_menu_real_estate)
    return markup

def getting_cadastral_number(message, id, bot_message_id):
    bot.edit_message_text('Введите Кадастровый номер:', id, bot_message_id)
    globalVar[str(id)]['to_delete'].append(message.message_id)
    globalVar[str(id)]['to_delete'].append(bot_message_id)
    if message.text != None:
        flag = True
        check = message.text.split(':')
        for check_id in check:
            if not check_id.isdigit():
                flag = False
                break

        if flag:
            a = bot.send_message(id, '*Проверяю...*', parse_mode="Markdown")
            driver = webdriver.Chrome(executable_path='chromedriver.exe')
            driver.get('https://rosreestr.gov.ru/wps/portal/online_request')
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "brdg1111"))
                )
                input_field = driver.find_element_by_class_name('brdg1111')
                input_field.send_keys(message.text)
                input_field.send_keys(Keys.ENTER)
                name = driver.find_element_by_class_name('td')
                bot.edit_message_text(f'Нашел информацию по вашему запросу:\n*{name.text}*', id, a.message_id,
                             reply_markup=back_to_menu_real_estate(), parse_mode="Markdown")
            except Exception:
                bot.edit_message_text('К сожалению, система не смогла ничего найти', id, a.message_id, reply_markup=back_to_menu_real_estate_or_try_again())

            driver.quit()
        else:
            a = bot.send_message(id, 'Пожалуйста, укажите кадастровый номер в соответсвующем формате без букв',
                                 reply_markup=back_to_menu_real_estate_or_try_again())
    else:
        a = bot.send_message(id, 'Пожалуйста, укажите кадастровый номер без вложений в чат', reply_markup=back_to_menu_real_estate_or_try_again())

    globalVar[str(id)]['message_id'] = a.message_id


def error_func(id,bot_message_id):
    if str(id) not in globalVar:
        globalVar[str(id)] = {}
        globalVar[str(id)]['to_delete'] = list()
        globalVar[str(id)]['topic'] = None
        globalVar[str(id)]['error_messages'] = None
        globalVar[str(id)]['message_id'] = None
        globalVar[str(id)]['logs'] = list()
    try:
        bot.delete_message(id, globalVar[str(id)]['error_messages'])
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
        globalVar[str(message.chat.id)]['error_messages'] = None
        globalVar[str(message.chat.id)]['message_id'] = None
        globalVar[str(message.chat.id)]['logs'] = list()
    globalVar[str(message.chat.id)]['logs'] = list()

    deleting(message.chat.id)
    bot.delete_message(message.chat.id, message.message_id)
    try:
        bot.delete_message(message.chat.id, globalVar[str(message.chat.id)]['message_id'])
    except Exception:
        None

    try:
        bot.delete_message(message.chat.id, globalVar[str(message.chat.id)]['error_messages'])
    except Exception:
        None

    a = bot.send_message(message.chat.id, "Здравствуйте!\n*Приветственный текст*\nВыберите тип Проверки:", reply_markup=menu())

    if globalVar[str(message.chat.id)]['topic'] != None:
        bot.delete_message(message.chat.id, globalVar[str(message.chat.id)]['topic'])
        globalVar[str(message.chat.id)]['topic'] = None
    globalVar[str(message.chat.id)]['message_id'] = a.message_id


@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'contact'])
def error(message):
    error_func(message.chat.id, message.message_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        global globalVar
        cmcd = call.message.chat.id
        cmmi = call.message.message_id
        print(cmcd, call.data)
        try:
            bot.delete_message(cmcd, globalVar[str(cmcd)]['error_messages'])
        except Exception:
            None

        if call.data == "real_estate":
            bot.delete_message(cmcd, cmmi)
            deleting(cmcd)
            bot.clear_step_handler_by_chat_id(cmcd)
            if globalVar[str(cmcd)]['topic'] == None:
                a = bot.send_message(cmcd, '*Проверка Недвижимости*', parse_mode="Markdown")
                globalVar[str(cmcd)]['topic'] = a.message_id
            b = bot.send_message(cmcd, 'Как именно вы хотите проверить?', reply_markup=menu_real_estate())
            globalVar[str(cmcd)]['message_id'] = b.message_id

        elif call.data == 'cadastral_number':
            bot.delete_message(cmcd, cmmi)
            a = bot.send_message(cmcd, 'Введите Кадастровый номер:', reply_markup=back_to_menu_real_estate())
            bot.register_next_step_handler(a, getting_cadastral_number, cmcd, a.message_id)

        elif call.data == 'try_again':
            bot.delete_message(cmcd, cmmi)
            deleting(cmcd)
            a = bot.send_message(cmcd, 'Введите Кадастровый номер:', reply_markup=back_to_menu_real_estate())
            bot.register_next_step_handler(a, getting_cadastral_number, cmcd, a.message_id)

        elif call.data == 'back_to_menu':
            bot.delete_message(cmcd, globalVar[str(cmcd)]['topic'])
            bot.delete_message(cmcd, globalVar[str(cmcd)]['message_id'])
            a = bot.send_message(cmcd, "Здравствуйте!\n*Приветственный текст*\nВыберите тип Проверки:", reply_markup=menu())
            globalVar[str(cmcd)]['message_id'] = a.message_id
            globalVar[str(cmcd)]['topic'] = None

        elif call.data == 'delete_notification':
            bot.delete_message(cmcd, cmmi)


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
