from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

key_stop = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/stop')]], resize_keyboard=True)
key_start = ReplyKeyboardRemove(keyboard=[[KeyboardButton(text='/start')]], resize_keyboard=True)

gender_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Мужской', callback_data='m'),
            InlineKeyboardButton(text='Женский', callback_data='f')
        ]
    ])

pref_gender_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Мужчину', callback_data='pref_m')
        ],
        [
            InlineKeyboardButton(text='Женщину', callback_data='pref_f')
        ],
        [
            InlineKeyboardButton(text='Не важно', callback_data='pref_gender_no_matter')
        ]
    ]
)

pref_age_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='18-25', callback_data='pref_18-25')
        ],
        [
            InlineKeyboardButton(text='25-35', callback_data='pref_25-35')
        ],
        [
            InlineKeyboardButton(text='35+', callback_data='pref_35+')
        ],
        [
            InlineKeyboardButton(text='Не важно', callback_data='pref_age_no_matter')
        ]
    ]
)

pref_city_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='В моём городе', callback_data='pref_city_matter')
        ],
        [
            InlineKeyboardButton(text='Не важно', callback_data='pref_city_no_matter')
        ]
    ]
)


async def profile_edit_kb(name='Имя', age='Возраст', city='Город', desc='Описание', photo='Фото',
                          call_N='ch_name', call_A='ch_age', call_C='ch_city', call_D='ch_desc', call_P='ch_photo'):
    profile_kb = InlineKeyboardBuilder()
    profile_kb.row(
        InlineKeyboardButton(text=name, callback_data=call_N),
        InlineKeyboardButton(text=age, callback_data=call_A)
    )
    profile_kb.row(
        InlineKeyboardButton(text=city, callback_data=call_C),
        InlineKeyboardButton(text=desc, callback_data=call_D)
    )
    profile_kb.row(
        InlineKeyboardButton(text='Пол', callback_data='ch_gender'),
        InlineKeyboardButton(text=photo, callback_data=call_P)
    )
    profile_kb.row(
        InlineKeyboardButton(text='Сохранить', callback_data='save_profile'),
        InlineKeyboardButton(text='Отмена', callback_data='cancel_profile_edit')
    )
    profile_kb.adjust(2, 2, 2, 2)
    return profile_kb.as_markup()


profiles = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='<-', callback_data='previous_profile'),
            InlineKeyboardButton(text='->', callback_data='next_profile')
        ],
        [
            InlineKeyboardButton(text='Выбрать', callback_data='select_profile')
        ]
    ])

chats = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='<-', callback_data='previous_chat'),
            InlineKeyboardButton(text='🚫', callback_data='clear_chat'),
            InlineKeyboardButton(text='->', callback_data='next_chat')
        ],
        [
            InlineKeyboardButton(text='Выбрать', callback_data='select_chat')
        ]
    ])
