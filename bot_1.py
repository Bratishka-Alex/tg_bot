import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# починить возврат к меню в контрагенет
geolocator = Nominatim(user_agent="tg_bot")

tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x))
globalVar = dict()

token = '1953842981:AAEHA3tIuypmcUW3u5cFMmbrvWJgGE6ShMA'
PAYMENTS_PROVIDER_TOKEN = '381764678:TEST:29208'
PRICE = types.LabeledPrice(label='тачила', amount=42000)

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
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row_width = 1  # Ширина поля кнопок
    real_estate = KeyboardButton('Избавиться от боли в спине и укрепить тело в формате “Умного фитнеса"')
    counter_agent = KeyboardButton("Похудеть и научиться питаться без голода, получая фигуру мечты")
    notarization = KeyboardButton("Помочь своим стопам быть здоровыми")
    markup.add(real_estate, counter_agent, notarization)
    return markup


def guide():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    real_estate = InlineKeyboardButton("Упражнения для спины", "https://vk.com/surikovaleks")
    counter_agent = InlineKeyboardButton("Топ 3 ошибки в питании и как худеть без силы воли", callback_data="https://vk.com/surikovaleks")
    notarization = InlineKeyboardButton("Нотариальная доверенность", callback_data="notarization")
    markup.add(real_estate, counter_agent, notarization)
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


@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message, state: FSMContext):
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

    if globalVar[str(message.chat.id)]['topic'] is not None:
        await bot.delete_message(message.chat.id, globalVar[str(message.chat.id)]['topic'])
        globalVar[str(message.chat.id)]['topic'] = None

    await bot.send_message(message.chat.id, f"Привет, *{message.from_user.first_name}*!\n"
                                                f"Ниже в сообщении для тебя гайды по интересующим тебя темам,"
                                                f" а пока мы с тобой познакомимся…\n\n", parse_mode="Markdown")

    await bot.send_message(message.chat.id, f"Гайды:", reply_markup=guide())

    a = await bot.send_message(message.chat.id, 'Расскажи, что для тебя сейчас самое главное?\n'
                                                'И я расскажу тебе, как я могу помочь!', reply_markup=menu())



@dp.message_handler(commands=['buy'], state='*')
async def buy(message: types.Message, state: FSMContext):
    if PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, 'Вы покупаете тачилу за 2324214 рублей')
        await bot.send_invoice(
            message.chat.id,
            title='Тачила',
            description='супер быстрая',
            provider_token=PAYMENTS_PROVIDER_TOKEN,
            currency='rub',
            is_flexible=False,  # True если конечная цена зависит от способа доставки
            prices=[PRICE],
            start_parameter='car-example',
            payload='some-invoice-payload-for-our-internal-use'
        )


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    print('successful_payment:')
    pmnt = message.successful_payment.to_python()
    for key, val in pmnt.items():
        print(f'{key} = {val}')

    await bot.send_message(
        message.chat.id,
        ('УДАЧНАЯ ПОКУПКА ЮХУУУУУУУУУУУ').format(
            total_amount=message.successful_payment.total_amount // 100,
            currency=message.successful_payment.currency
        )
    )



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
