import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import Select
import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# починить возврат к меню в контрагенет
geolocator = Nominatim(user_agent="tg_bot")

tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))
globalVar = dict()


storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot=bot, storage=storage)

class State_list(StatesGroup):
    waiting_cadastral_number = State()
    waiting_address = State()
    waiting_serial_number = State()
    waiting_FIO = State()
    waiting_bdate = State()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(getting_cadastral_number, state=State_list.waiting_cadastral_number)
    dp.register_message_handler(getting_real_address, state=State_list.waiting_address)
    dp.register_message_handler(getting_serial_number, state=State_list.waiting_serial_number)
    dp.register_message_handler(getting_FIO, state=State_list.waiting_FIO)
    dp.register_message_handler(getting_bdate, state=State_list.waiting_bdate)



def menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    real_estate = InlineKeyboardButton("Недвижимость", callback_data="real_estate")
    counter_agent = InlineKeyboardButton("Контрагент", callback_data="counter_agent")
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

def back_to_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(back_to_menu)
    return markup


async def delete_message(id, bot_message_id):
    await bot.delete_message(id, bot_message_id)


async def deleting(chat_id):
    if len(globalVar[str(chat_id)]['to_delete']) != 0:
        tasks = list()
        for message in globalVar[str(chat_id)]['to_delete']:
            tasks.append(asyncio.create_task(delete_message(chat_id, message)))
        await asyncio.gather(*tasks)
    globalVar[str(chat_id)]['to_delete'] = list()


def back_to_menu_real_estate():
    markup = InlineKeyboardMarkup()
    back_to_menu_real_estate = InlineKeyboardButton('Назад', callback_data='real_estate')
    markup.add(back_to_menu_real_estate)
    return markup


def back_to_menu_or_try_again():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    try_again = InlineKeyboardButton('Повторить ввод', callback_data='try_again_serial_number')
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(try_again, back_to_menu)
    return markup


def back_to_menu_or_try_again1():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    try_again = InlineKeyboardButton('Повторить ввод', callback_data='try_again_FIO')
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(try_again, back_to_menu)
    return markup


def back_to_menu_or_try_again2():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    try_again = InlineKeyboardButton('Повторить ввод', callback_data='try_again_bdate')
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(try_again, back_to_menu)
    return markup


def back_to_menu_real_estate_or_try_again():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    try_again = InlineKeyboardButton('Повторить ввод', callback_data='try_again')
    back_to_menu_real_estate = InlineKeyboardButton('Назад', callback_data='real_estate')
    markup.add(try_again, back_to_menu_real_estate)
    return markup


def back_to_menu_real_estate_or_try_again1():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    try_again1 = InlineKeyboardButton('Повторить ввод', callback_data='try_again1')
    back_to_menu_real_estate = InlineKeyboardButton('Назад', callback_data='real_estate')
    markup.add(try_again1, back_to_menu_real_estate)
    return markup


def check_correct():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    correct = InlineKeyboardButton('Данные верны', callback_data='correct')
    not_correct = InlineKeyboardButton('Ввести данные заново', callback_data='try_again_serial_number')
    back_to_menu = InlineKeyboardButton('Назад', callback_data='back_to_menu')
    markup.add(correct, not_correct, back_to_menu)
    return markup


@dp.message_handler(state=State_list.waiting_serial_number)
async def getting_serial_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        id = data['id']
        bot_message_id = data['bot_message_id']
    await bot.edit_message_text('Введите серию и номер паспорта:', id, bot_message_id)
    globalVar[str(id)]['to_delete'].append(bot_message_id)
    globalVar[str(id)]['to_delete'].append(message.message_id)
    if message.text is not None:
        mes = message.text.replace(' ', '')
        if mes.isdigit() and len(mes)==10:
            a = await bot.send_message(id, 'Введите ФИО:', reply_markup=back_to_menu())
            async with state.proxy() as data:
                data['id'] = id
                data['bot_message_id'] = a.message_id
            globalVar[str(id)]['logs'].append(mes)
            await State_list.waiting_FIO.set()
        else:
            a = await bot.send_message(id, 'Укажите действительные данные числом и в верном количестве', reply_markup=back_to_menu_or_try_again())

    else:
        a = await bot.send_message(id, 'Укажите действительные данные без вложений в чат', reply_markup=back_to_menu_or_try_again())
    globalVar[str(id)]['message_id'] = a.message_id


@dp.message_handler(state=State_list.waiting_FIO)
async def getting_FIO(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        id = data['id']
        bot_message_id = data['bot_message_id']
    await bot.edit_message_text('Введите ФИО:', id, bot_message_id)
    globalVar[str(id)]['to_delete'].append(bot_message_id)
    globalVar[str(id)]['to_delete'].append(message.message_id)
    if message.text is not None:
        mes = message.text.replace(' ', '')
        if mes.isalpha() and len(message.text.split()) == 3:
            a = await bot.send_message(id, 'Введите дату рождения:', reply_markup=back_to_menu())
            async with state.proxy() as data:
                data['id'] = id
                data['bot_message_id'] = a.message_id
            mes1=''
            for mes in message.text.split():
                mes1 += mes.capitalize() + ' '
            globalVar[str(id)]['logs'].append(mes1[:-1])
            await State_list.waiting_bdate.set()
        else:
            a = await bot.send_message(id, 'Укажите действительные данные буквами кириллицы', reply_markup=back_to_menu_or_try_again1())

    else:
        a = await bot.send_message(id, 'Укажите действительные данные без вложений в чат', reply_markup=back_to_menu_or_try_again1())
    globalVar[str(id)]['message_id'] = a.message_id


@dp.message_handler(state=State_list.waiting_bdate)
async def getting_bdate(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        id = data['id']
        bot_message_id = data['bot_message_id']
    await bot.edit_message_text('Введите дату рождения:', id, bot_message_id)
    globalVar[str(id)]['to_delete'].append(bot_message_id)
    globalVar[str(id)]['to_delete'].append(message.message_id)
    if message.text != None:
        flag = True
        check = message.text.split('.')
        for check_id in check:
            if not check_id.isdigit():
                flag = False
                break
        if flag and len(message.text) == 10:
            globalVar[str(id)]['logs'].append(message.text)
            a = await check_before_send(id)
        else:
            a = await bot.send_message(id, 'Укажите действительные данные в указанном формате', reply_markup=back_to_menu_or_try_again2())

    else:
        a = await bot.send_message(id, 'Укажите действительные данные без вложений в чат', reply_markup=back_to_menu_or_try_again2())
    globalVar[str(id)]['message_id'] = a.message_id


async def check_before_send(id):
    pasport = globalVar[str(id)]['logs'][0]
    FIO = globalVar[str(id)]['logs'][1]
    bdate = globalVar[str(id)]['logs'][2]
    a = await bot.send_message(id, f'Пожалуйста, проверьте верны ли указанные данные:\n\n'
                                   f'• Паспорт: {pasport}\n'
                                   f'• ФИО: {FIO}\n'
                                   f'• Дата рождения: {bdate}', reply_markup=check_correct())
    return a


async def send_to_site(id):
    a = await bot.send_message(id, '*Проверяю.*', parse_mode="Markdown")
    task_1 = asyncio.create_task(checking_message(a.chat.id, a.message_id))
    task_2 = asyncio.create_task(checking_on_server_INN(globalVar[str(id)]['logs'], a.chat.id, a.message_id))
    await task_1
    await task_2
    if task_1.done() and not task_2.done():
        task_2.cancel()
        await bot.edit_message_text(
            'На сервере произошла ошибка.\nПовторите попытку позже', id, a.message_id,
            reply_markup=back_to_menu_real_estate_or_try_again())
    globalVar[str(id)]['sleep'] = 9


async def checking_on_server_INN(logs,id, bot_meesage_id):
    driver = webdriver.Chrome(executable_path='chromedriver.exe')
    driver.get('https://service.nalog.ru/inn.do')

    pas = logs[0]
    FIO = logs[1].split()
    bdate = logs[2]

    passport = pas[:2] + ' ' + pas[2:4] + ' ' + pas[4:]
    fam = FIO[0]
    nam = FIO[1]
    otch = FIO[2]

    element = driver.find_element_by_id('personalData')
    driver.execute_script("arguments[0].click();", element)
    driver.find_element_by_css_selector("button.btn-next").click()
    await asyncio.sleep(1)
    field = driver.find_element_by_id('fam')
    driver.execute_script(f"arguments[0].value='{fam}'", field)
    field = driver.find_element_by_id('nam')
    driver.execute_script(f"arguments[0].value='{nam}'", field)
    field = driver.find_element_by_id('otch')
    driver.execute_script(f"arguments[0].value='{otch}'", field)
    field = driver.find_element_by_id('bdate')
    driver.execute_script(f"arguments[0].value='{bdate}'", field)
    field = driver.find_element_by_id('docno')
    driver.execute_script(f"arguments[0].value='{passport}'", field)
    driver.find_element_by_css_selector("button.btn-l.float-right.btn-next").click()
    await asyncio.sleep(2)

    globalVar[str(id)]['sleep'] = 0

    if 'block' == driver.find_element_by_xpath("//*[@id='result_1']").value_of_css_property("display"):
        name = driver.find_element_by_xpath('//*[@id="resultInn"]')
        a = await bot.edit_message_text(f'Нашел ИНН по вашему запросу:\n{name.text}', id, bot_meesage_id,
                                        reply_markup=back_to_menu())

    else:
        a = await bot.edit_message_text(f'К сожалению, информация по вашему запросу не найдена', id, bot_meesage_id,
                                        reply_markup=back_to_menu())

    globalVar[str(id)]['message_id'] = a.message_id

    driver.quit()


@dp.message_handler(state=State_list.waiting_cadastral_number)
async def getting_cadastral_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        id = data['id']
        bot_message_id = data['bot_message_id']
    await bot.edit_message_text('Введите Кадастровый номер:', id, bot_message_id)
    globalVar[str(id)]['to_delete'].append(message.message_id)
    globalVar[str(id)]['to_delete'].append(bot_message_id)
    if message.text is not None:
        flag = True
        check = message.text.split(':')
        for check_id in check:
            if not check_id.isdigit():
                flag = False
                break

        if flag:
            a = await bot.send_message(id, '*Проверяю.*', parse_mode="Markdown")
            task_1 = asyncio.create_task(checking_message(a.chat.id, a.message_id))
            task_2 = asyncio.create_task(checking_on_server_cadastral_number(message, a.chat.id, a.message_id))
            await task_1
            await task_2
            if task_1.done() and not task_2.done():
                task_2.cancel()
                await bot.edit_message_text(
                                           'На сервере произошла ошибка.\nПовторите попытку позже', id, a.message_id,
                                           reply_markup=back_to_menu_real_estate_or_try_again())

        else:
            a = await bot.send_message(id, 'Пожалуйста, укажите кадастровый номер в соответсвующем формате без букв',
                                 reply_markup=back_to_menu_real_estate_or_try_again())
    else:
        a = await bot.send_message(id, 'Пожалуйста, укажите кадастровый номер без вложений в чат', reply_markup=back_to_menu_real_estate_or_try_again())

    globalVar[str(id)]['message_id'] = a.message_id
    globalVar[str(id)]['sleep'] = 9


async def checking_message(id, bot_message_id):
    while globalVar[str(id)]['sleep'] > 0:
        await asyncio.sleep(0.5)
        if globalVar[str(id)]['sleep'] == 0:
            break
        await bot.edit_message_text('*Проверяю..*', id, bot_message_id, parse_mode="Markdown")
        await asyncio.sleep(0.5)
        if globalVar[str(id)]['sleep'] == 0:
            break
        await bot.edit_message_text('*Проверяю...*', id, bot_message_id, parse_mode="Markdown")
        await asyncio.sleep(0.5)
        if globalVar[str(id)]['sleep'] == 0:
            break
        await bot.edit_message_text('*Проверяю.*', id, bot_message_id, parse_mode="Markdown")
        globalVar[str(id)]['sleep'] -= 1.5

async def checking_on_server_real_address(message, id, bot_message_id):
    logs = message.text.split(', ')
    driver = webdriver.Chrome(executable_path='chromedriver.exe')
    driver.get('https://rosreestr.gov.ru/wps/portal/online_request')
    try:
        street = logs.pop(2).split()
        await asyncio.sleep(1)
        ddelement = Select(driver.find_element_by_id('subjectId'))
        ddelement.select_by_visible_text(logs[0])
        await asyncio.sleep(1)
        ddelement = Select(driver.find_element_by_id('regionId'))
        ddelement.select_by_visible_text(logs[1])
        await asyncio.sleep(1)
        ddelement = Select(driver.find_element_by_name('street_type'))
        ddelement.select_by_visible_text(street[0])
        field = driver.find_element_by_name('street')
        driver.execute_script(f"arguments[0].value='{street[1]}'", field)
        field = driver.find_element_by_name('house')
        driver.execute_script(f"arguments[0].value='{logs[2]}'", field)
        field = driver.find_element_by_name('apartment')
        driver.execute_script(f"arguments[0].value='{logs[3]}'", field)
        driver.find_element_by_css_selector("button.terminal-button-bright").click()
        name = driver.find_element_by_xpath('// *[ @ id = "js_oTr0"] / td[2] / nobr')
        globalVar[str(id)]['sleep'] = 0
        await bot.edit_message_text(f'Нашел информацию по вашему запросу:\n*{name.text}*', id, bot_message_id,
                                    reply_markup=back_to_menu_real_estate(), parse_mode="Markdown")
    except Exception:
        globalVar[str(id)]['sleep'] = 0
        await bot.edit_message_text('К сожалению, система не смогла ничего найти', id, bot_message_id,
                                    reply_markup=back_to_menu_real_estate_or_try_again1())

    driver.quit()


async def checking_on_server_cadastral_number(message, id, bot_message_id):
    driver = webdriver.Chrome(executable_path='chromedriver.exe')
    driver.get('https://rosreestr.gov.ru/wps/portal/online_request')
    try:
        input_field = driver.find_element_by_xpath(
            '//*[@id="online_request_search_form_span"]/table/tbody/tr[1]/td[1]/table/tbody/tr[3]/td/table[1]/tbody/tr[2]/td[3]/input')
        input_field.send_keys(message.text)
        input_field.send_keys(Keys.ENTER)
        name = driver.find_element_by_xpath('//*[@id="js_oTr0"]/td[1]/a')
        await asyncio.sleep(1)
        globalVar[str(id)]['sleep'] = 0
        await bot.edit_message_text(f'Нашел информацию по вашему запросу:\n*{name.text}*', id, bot_message_id,
                                    reply_markup=back_to_menu_real_estate(), parse_mode="Markdown")
    except Exception:
        await asyncio.sleep(1)
        globalVar[str(id)]['sleep'] = 0
        await bot.edit_message_text('К сожалению, система не смогла ничего найти', id, bot_message_id,
                                    reply_markup=back_to_menu_real_estate_or_try_again())

    driver.quit()

@dp.message_handler(state=State_list.waiting_address)
async def getting_real_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        id = data['id']
        bot_message_id = data['bot_message_id']
    await bot.edit_message_text('Введите адрес:', id, bot_message_id)
    globalVar[str(id)]['to_delete'].append(message.message_id)
    globalVar[str(id)]['to_delete'].append(bot_message_id)
    if message.text is not None:
        a = await bot.send_message(id, '*Проверяю.*', parse_mode="Markdown")

        task_1 = asyncio.create_task(checking_message(a.chat.id, a.message_id))
        task_2 = asyncio.create_task(checking_on_server_real_address(message, a.chat.id, a.message_id))
        await task_1
        await task_2
        if task_1.done() and not task_2.done():
            task_2.cancel()
            await bot.edit_message_text(
                'На сервере произошла ошибка.\nПовторите попытку позже', id, a.message_id,
                reply_markup=back_to_menu_real_estate_or_try_again())


    else:
        a = await bot.send_message(id, 'Пожалуйста, укажите адрес без вложений в чат',
                             reply_markup=back_to_menu_real_estate_or_try_again1())

    globalVar[str(id)]['message_id'] = a.message_id
    globalVar[str(id)]['sleep'] = 9


async def error_func(id, bot_message_id):
    print(globalVar, bot_message_id)
    if str(id) not in globalVar:
        globalVar[str(id)] = {}
        globalVar[str(id)]['to_delete'] = list()
        globalVar[str(id)]['topic'] = None
        globalVar[str(id)]['error_messages'] = None
        globalVar[str(id)]['message_id'] = None
        globalVar[str(id)]['logs'] = list()
        globalVar[str(id)]['sleep'] = 9
    try:
        await bot.delete_message(id, globalVar[str(id)]['error_messages'])
    except Exception:
        None
    await bot.delete_message(id, bot_message_id)
    a = await bot.send_message(id, 'Воспользуйтесь предложенными кнопками. '
                                      'Если кнопки исчезли, введите команду /start')
    globalVar[str(id)]['error_messages'] = a.message_id


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    global globalVar
    print(globalVar)

    if str(message.chat.id) not in globalVar:

        globalVar[str(message.chat.id)] = {}
        globalVar[str(message.chat.id)]['to_delete'] = list()
        globalVar[str(message.chat.id)]['topic'] = None
        globalVar[str(message.chat.id)]['error_messages'] = None
        globalVar[str(message.chat.id)]['message_id'] = None
        globalVar[str(message.chat.id)]['logs'] = list()
        globalVar[str(message.chat.id)]['sleep'] = 9
    globalVar[str(message.chat.id)]['sleep'] = 9
    globalVar[str(message.chat.id)]['logs'] = list()

    await deleting(message.chat.id)
    await bot.delete_message(message.chat.id, message.message_id)
    try:
        await bot.delete_message(message.chat.id, globalVar[str(message.chat.id)]['message_id'])
    except Exception:
        None

    try:
        await bot.delete_message(message.chat.id, globalVar[str(message.chat.id)]['error_messages'])
    except Exception:
        None

    a = await bot.send_message(message.chat.id, "Здравствуйте!\n*Приветственный текст*\nВыберите тип Проверки:", reply_markup=menu())

    if globalVar[str(message.chat.id)]['topic'] != None:
        await bot.delete_message(message.chat.id, globalVar[str(message.chat.id)]['topic'])
        globalVar[str(message.chat.id)]['topic'] = None
    globalVar[str(message.chat.id)]['message_id'] = a.message_id


@dp.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'contact'])
async def error(message):
    await error_func(message.chat.id, message.message_id)


@dp.callback_query_handler(lambda c: c.data, state='*') #может ошибка в этом
async def callback_query(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        global globalVar
        cmcd = callback_query.message.chat.id
        cmmi = callback_query.message.message_id
        print(cmcd, callback_query.data)
        try:
            await bot.delete_message(cmcd, globalVar[str(cmcd)]['error_messages'])
            globalVar[str(cmcd)]['error_messages'] = None
        except Exception:
            None

        if callback_query.data == "real_estate":
            await bot.delete_message(cmcd, cmmi)
            await deleting(cmcd)
            current_state = await state.get_state()
            if current_state is not None:
                await state.finish()
                await state.reset_state()
            if globalVar[str(cmcd)]['topic'] is None:
                a = await bot.send_message(cmcd, '*Проверка Недвижимости*', parse_mode="Markdown")
                globalVar[str(cmcd)]['topic'] = a.message_id
            b = await bot.send_message(cmcd, 'Как именно вы хотите проверить?', reply_markup=menu_real_estate())
            globalVar[str(cmcd)]['message_id'] = b.message_id

        elif callback_query.data == 'cadastral_number':
            await bot.delete_message(cmcd, cmmi)
            a = await bot.send_message(cmcd, 'Введите Кадастровый номер:', reply_markup=back_to_menu_real_estate())
            async with state.proxy() as data:
                data['id'] = cmcd
                data['bot_message_id'] = a.message_id
            await State_list.waiting_cadastral_number.set()

        elif callback_query.data == 'real_address':
            await bot.delete_message(cmcd, cmmi)
            a = await bot.send_message(cmcd, 'Введите адрес:', reply_markup=back_to_menu_real_estate())
            async with state.proxy() as data:
                data['id'] = cmcd
                data['bot_message_id'] = a.message_id
            await State_list.waiting_address.set()

        elif callback_query.data == 'try_again':
            await bot.delete_message(cmcd, cmmi)
            await deleting(cmcd)
            a = await bot.send_message(cmcd, 'Введите Кадастровый номер:', reply_markup=back_to_menu_real_estate())
            async with state.proxy() as data:
                data['id'] = cmcd
                data['bot_message_id'] = a.message_id
            await State_list.waiting_cadastral_number.set()


        elif callback_query.data == 'try_again1':
            await bot.delete_message(cmcd, cmmi)
            await deleting(cmcd)
            a = await bot.send_message(cmcd, 'Введите адрес:', reply_markup=back_to_menu_real_estate())
            async with state.proxy() as data:
                data['id'] = cmcd
                data['bot_message_id'] = a.message_id
            await State_list.waiting_address.set()

        elif callback_query.data == 'try_again_serial_number':
            await bot.delete_message(cmcd, cmmi)
            if len(globalVar[str(cmcd)]['to_delete']) == 6:
                await deleting(cmcd)
                globalVar[str(cmcd)]['logs'] = list()
            else:
                a = globalVar[str(cmcd)]['to_delete'].pop()
                await bot.delete_message(cmcd, a)
                a = globalVar[str(cmcd)]['to_delete'].pop()
                await bot.delete_message(cmcd, a)
            a = await bot.send_message(cmcd, 'Введите серию и номер паспорта:', reply_markup=back_to_menu_real_estate())
            async with state.proxy() as data:
                data['id'] = cmcd
                data['bot_message_id'] = a.message_id
            await State_list.waiting_serial_number.set()

        elif callback_query.data == 'try_again_FIO':
            await bot.delete_message(cmcd, cmmi)
            a = globalVar[str(cmcd)]['to_delete'].pop()
            await bot.delete_message(cmcd, a)
            a = globalVar[str(cmcd)]['to_delete'].pop()
            await bot.delete_message(cmcd, a)
            a = await bot.send_message(cmcd, 'Введите ФИО:', reply_markup=back_to_menu_real_estate())
            async with state.proxy() as data:
                data['id'] = cmcd
                data['bot_message_id'] = a.message_id
            await State_list.waiting_FIO.set()

        elif callback_query.data == 'try_again_bdate':
            await bot.delete_message(cmcd, cmmi)
            a = globalVar[str(cmcd)]['to_delete'].pop()
            await bot.delete_message(cmcd, a)
            a = globalVar[str(cmcd)]['to_delete'].pop()
            await bot.delete_message(cmcd, a)
            a = await bot.send_message(cmcd, 'Введите дату рождения:', reply_markup=back_to_menu_real_estate())
            async with state.proxy() as data:
                data['id'] = cmcd
                data['bot_message_id'] = a.message_id
            await State_list.waiting_bdate.set()


        elif callback_query.data == 'counter_agent':
            await bot.delete_message(cmcd, cmmi)
            await deleting(cmcd)
            current_state = await state.get_state()
            if current_state is not None:
                await state.finish()
                await state.reset_state()
            if globalVar[str(cmcd)]['topic'] is None:
                a = await bot.send_message(cmcd, '*Проверка Контрагента*', parse_mode="Markdown")
                globalVar[str(cmcd)]['topic'] = a.message_id
            b = await bot.send_message(cmcd, 'Введите серию и номер паспорта:', reply_markup=back_to_menu())
            globalVar[str(cmcd)]['message_id'] = b.message_id
            async with state.proxy() as data:
                data['id'] = cmcd
                data['bot_message_id'] = b.message_id
            await State_list.waiting_serial_number.set()

        elif callback_query.data == 'correct':
            await bot.delete_message(cmcd,cmmi)
            await send_to_site(cmcd)

        elif callback_query.data == 'back_to_menu':
            current_state = await state.get_state()
            if current_state is not None:
                await state.finish()
                await state.reset_state()
            await bot.delete_message(cmcd, globalVar[str(cmcd)]['topic'])
            await bot.delete_message(cmcd, globalVar[str(cmcd)]['message_id'])
            await deleting(cmcd)
            globalVar[str(cmcd)]['logs'] = list()
            a = await bot.send_message(cmcd, "Здравствуйте!\n*Приветственный текст*\nВыберите тип Проверки:", reply_markup=menu())
            globalVar[str(cmcd)]['message_id'] = a.message_id
            globalVar[str(cmcd)]['topic'] = None

        elif callback_query.data == 'delete_notification':
            await bot.delete_message(cmcd, cmmi)


        await bot.answer_callback_query(callback_query.id)


    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp)
