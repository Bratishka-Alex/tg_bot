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

token = '1970646588:AAE7sCxoXRMZ-p1PcI0anjVu7xekEyA9Kh0'
CHANNEL_ID = -1001512982778

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot=bot, storage=storage)

def take():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1  # Ширина поля кнопок
    taking = InlineKeyboardButton('Беру', callback_data='taking')
    markup.add(taking)
    return markup

@dp.callback_query_handler(lambda c: c.data, state='*') #может ошибка в этом
async def callback_query(callback_query: types.CallbackQuery, state: FSMContext):
    print(14)
    try:
        lol = list()
        cmcd = callback_query.message.chat.id
        cmmi = callback_query.message.message_id
        print(cmcd, callback_query.data, cmmi)

        if callback_query.data == "taking":
            lol.append(cmcd)
            print(lol)


        await bot.answer_callback_query(callback_query.id)


    except Exception as e:
        print(e)
        pass

async def main():
    await bot.send_message(CHANNEL_ID, 'lol', reply_markup=take())


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp)
    main()
