import mysql.connector
import asyncio
import dotenv
import time
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from threading import Thread
from pyowm import OWM
from PIL import Image

from keyboards import *

global registration_mode, ch_name_mode, ch_age_mode, ch_city_mode, ch_photo_mode, ch_desc_mode
global profile_name, profile_age, profile_city, profile_description, profile_photo, profile_gender
global bot_main_msg_id, bot_misc_msg_id, photo_name, chat_user_platform, chat_user_platform_id
global stop_thread, new_msg_current_chat

dotenv.load_dotenv('../.env')

bot = Bot(token=os.getenv('TG_TOKEN'))
dp = Dispatcher()
owm = OWM(os.getenv('OWM_TOKEN'))
mgr = owm.weather_manager()

conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    user='root',
    passwd='',
    database='messages')
cur = conn.cursor()

menu_media = FSInputFile('../user_profile_photos/media.jpg')

registration_mode = CHAT_MODE = 0


@dp.message()
async def message_handler(message: types.Message) -> None:
    global registration_mode, bot_main_msg_id, bot_misc_msg_id, chat_user_platform, chat_user_platform_id, CHAT_MODE
    global stop_thread

    if message.text == '/start':
        registration_mode = CHAT_MODE = 0
        if 'bot_misc_msg_id' in globals() and bot_misc_msg_id is not None:
            try: await bot.delete_message(chat_id=message.from_user.id, message_id=bot_misc_msg_id)
            except Exception as err: print('/start bot_misc_msg_id existing\n', err)

        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await bot.send_photo(
            chat_id=message.from_user.id, photo=menu_media, caption='Меню',
            reply_markup=await main_menu_create(message.from_user.id))

    elif message.text == '/stop':
        stop_thread = True
        registration_mode = CHAT_MODE = 0

        await bot.send_photo(
            chat_id=message.from_user.id, photo=menu_media, caption='Вы вышли из режима переписки',
            reply_markup=await main_menu_create(message.from_user.id))
# ===========================================================================================================Регистрация
    elif registration_mode == 1:
        global ch_name_mode, ch_age_mode, ch_city_mode, ch_photo_mode, ch_desc_mode, photo_name
        global profile_name, profile_age, profile_city, profile_description, profile_photo

        profile_photo = types.InputMediaPhoto(media=FSInputFile(f'../user_profile_photos/{photo_name}.jpg'))

        if ch_name_mode == 1:
            global a
            var_name = message.text.lower()
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            for i in var_name:
                if i not in ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р',
                             'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', '-', ' ']:
                    a = 0
                    break
                else: a = 1

            if a == 1:
                profile_name = var_name.title()
                ch_name_mode = 0
            else:
                bot_misc_msg_id = await bot.send_message(
                    chat_id=message.from_user.id, text='Введите имя кириллицей без цифр и специальных символов')
                bot_misc_msg_id = bot_misc_msg_id.message_id
                await asyncio.sleep(2)
                await bot.delete_message(chat_id=message.from_user.id, message_id=bot_misc_msg_id)

        elif ch_age_mode == 1:
            var_age = message.text
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            try:
                var_age = int(var_age)
                if var_age >= 18:
                    if var_age < 125:
                        profile_age = var_age
                        ch_age_mode = 0
                    else:
                        bot_misc_msg_id = await bot.send_message(
                            chat_id=message.from_user.id, text='Напишите ваш реальный возраст')
                        bot_misc_msg_id = bot_misc_msg_id.message_id
                        await asyncio.sleep(2)
                        await bot.delete_message(chat_id=message.from_user.id, message_id=bot_misc_msg_id)
                else:
                    bot_misc_msg_id = await bot.send_message(chat_id=message.from_user.id,
                                                             text='Сервис предназанчен для лиц страше 18 лет')
                    bot_misc_msg_id = bot_misc_msg_id.message_id
                    await asyncio.sleep(4)
                    await bot.send_message(chat_id=message.from_user.id, text='%future_feature-banned%')
            except Exception as err:
                print('int age\n', err)
                bot_misc_msg_id = await bot.send_message(chat_id=message.from_user.id, text='Введите числовое значение')
                bot_misc_msg_id = bot_misc_msg_id.message_id
                await asyncio.sleep(2)
                await bot.delete_message(chat_id=message.from_user.id, message_id=bot_misc_msg_id)

        elif ch_city_mode == 1:
            var_city = message.text.lower()
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            try:
                mgr.weather_at_place(var_city)
                profile_city = var_city.title()
                ch_city_mode = 0
            except Exception as err:
                print('city existing\n', err)
                bot_misc_msg_id = await bot.send_message(
                    chat_id=message.from_user.id, text='Пожалуйста, введите существующий город')
                bot_misc_msg_id = bot_misc_msg_id.message_id
                await asyncio.sleep(2)
                await bot.delete_message(chat_id=message.from_user.id, message_id=bot_misc_msg_id)

        elif ch_desc_mode == 1:
            profile_description = message.text
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            ch_desc_mode = 0

        elif ch_photo_mode == 1:
            if message.photo:
                photo_name = f'tg{message.from_user.id}'
                file = await bot.get_file(message.photo[-1].file_id)
                file_path = file.file_path
                await bot.download_file(file_path=file_path, destination=f'../user_profile_photos/{photo_name}.jpg')

                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                await bot.edit_message_caption(
                    chat_id=message.from_user.id, message_id=bot_main_msg_id, caption='Загружаем файл')

                image = Image.open(f'../user_profile_photos/{photo_name}.jpg')
                resize_k = image.width/300
                image = image.resize((round(image.width/resize_k), round(image.height/resize_k)))
                image.save(f'../user_profile_photos/{photo_name}.jpg')

                profile_photo = types.InputMediaPhoto(media=FSInputFile(f'../user_profile_photos/{photo_name}.jpg'))
                await bot.edit_message_media(
                    chat_id=message.from_user.id, message_id=bot_main_msg_id, media=profile_photo)
                ch_photo_mode = 0
            else:
                await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                bot_misc_msg_id = await bot.send_message(
                    chat_id=message.from_user.id, text='Пожалуйста, загрузие фото')
                bot_misc_msg_id = bot_misc_msg_id.message_id
                await asyncio.sleep(2)
                await bot.delete_message(chat_id=message.from_user.id, message_id=bot_misc_msg_id)

        else:
            registration_mode = 0
            bot_misc_msg_id = await bot.send_message(
                chat_id=message.from_user.id, text='Что-бы открыть меню - нажмите /start', reply_markup=key_start)
            bot_misc_msg_id = bot_misc_msg_id.message_id

        if 1 not in [ch_name_mode, ch_age_mode, ch_city_mode, ch_photo_mode, ch_desc_mode] and registration_mode == 1:
            await bot.edit_message_caption(
                chat_id=message.from_user.id, message_id=bot_main_msg_id,
                caption=f'{profile_name}, {profile_age}\n{profile_city}\n\n{profile_description}',
                reply_markup=await profile_edit_kb())
# ======================================================================================================================
# ==================================================================================================================CHAT
    elif CHAT_MODE == 1:
        t = time.localtime()
        datetime_current = f'{t.tm_year}-{t.tm_mon}-{t.tm_mday} {t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        cur.execute(f"INSERT INTO `msgs` (`platform_1`, `platform_2`, `user1_id`, `user2_id`, `message`, `datetime`, `processed`) "
                    f'VALUES ("tg", "{chat_user_platform}", {message.from_user.id}, {chat_user_platform_id}, "{message.text}", "{datetime_current}", 0)')
        conn.commit()
# ======================================================================================================================
    else:
        bot_misc_msg_id = await bot.send_message(
            chat_id=message.from_user.id, text='Что-бы открыть меню - нажмите /start', reply_markup=key_start)
        bot_misc_msg_id = bot_misc_msg_id.message_id


@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery) -> None:
    global bot_main_msg_id, bot_misc_msg_id, chat_user_platform, chat_user_platform_id, CHAT_MODE, stop_thread
    global profile_name, profile_photo, profile_age, profile_city, profile_description, profile_gender
    global ch_name_mode, ch_age_mode, ch_city_mode, ch_photo_mode, ch_desc_mode, photo_name, registration_mode

    bot_main_msg_id = callback.message.message_id

# ===============================================================================================================Профиль
    if callback.data == 'create_profile':
        profile_name = '-----------'
        profile_age = '----'
        profile_city = '--------'
        profile_description = '--------------------------------\n------------------\n----------'
        photo_name = '0'
        profile_gender = '0'
        profile_photo = FSInputFile(f'../user_profile_photos/{photo_name}.jpg')
        profile_photo = types.InputMediaPhoto(media=profile_photo)
        await bot.edit_message_media(chat_id=callback.from_user.id, message_id=bot_main_msg_id, media=profile_photo)
        await bot.edit_message_caption(
            chat_id=callback.from_user.id, message_id=bot_main_msg_id,
            caption=f'{profile_name}, {profile_age}\n{profile_city}\n\n{profile_description}',
            reply_markup=await profile_edit_kb())
        registration_mode = 1
        ch_name_mode = ch_age_mode = ch_city_mode = ch_photo_mode = ch_desc_mode = 0

    elif callback.data == 'edit_profile':
        conn.reset_session()
        cur.execute(f"SELECT * FROM `profiles` WHERE `platform`='tg' AND `platform_id`={callback.from_user.id}")
        profile = cur.fetchone()
        profile_name, photo_name, profile_age, profile_gender, profile_description, profile_city = [profile[i] for i in (3, 4, 5, 6, 7, 8)]
        profile_photo = types.InputMediaPhoto(media=FSInputFile(f'../user_profile_photos/{photo_name}.jpg'))
        await bot.edit_message_media(chat_id=callback.from_user.id, message_id=bot_main_msg_id, media=profile_photo)
        await bot.edit_message_caption(
            chat_id=callback.from_user.id, message_id=bot_main_msg_id,
            caption=f'{profile_name}, {profile_age}\n{profile_city}\n\n{profile_description}',
            reply_markup=await profile_edit_kb())
        registration_mode = 1
        ch_name_mode = ch_age_mode = ch_city_mode = ch_photo_mode = ch_desc_mode = 0

    elif callback.data == 'cancel_profile_edit':
        registration_mode = 0
        await bot.edit_message_media(
            chat_id=callback.from_user.id, message_id=bot_main_msg_id, media=types.InputMediaPhoto(media=menu_media))
        await bot.edit_message_caption(
            chat_id=callback.from_user.id, message_id=bot_main_msg_id,
            caption='Меню', reply_markup=await main_menu_create(callback.from_user.id))

    elif callback.data in ['ch_name', 'ch_age', 'ch_city', 'ch_desc', 'ch_photo', 'profile_empty_callback']:
        global profile_kb

        if callback.data == 'profile_empty_callback':
            bot_misc_msg_id = await bot.send_message(
                chat_id=callback.from_user.id, text='Просто напишите данные в чат')
            bot_misc_msg_id = bot_misc_msg_id.message_id
            await asyncio.sleep(2.5)
            await bot.delete_message(chat_id=callback.from_user.id, message_id=bot_misc_msg_id)
        else:
            if callback.data == 'ch_name':
                ch_age_mode = ch_city_mode = ch_photo_mode = ch_desc_mode = 0
                ch_name_mode = 1
                profile_kb = await profile_edit_kb(name='Как вас зовут?', call_N='profile_empty_callback')

            elif callback.data == 'ch_age':
                ch_name_mode = ch_city_mode = ch_photo_mode = ch_desc_mode = 0
                ch_age_mode = 1
                profile_kb = await profile_edit_kb(age='Сколько вам лет?', call_A='profile_empty_callback')

            elif callback.data == 'ch_city':
                ch_name_mode = ch_age_mode = ch_photo_mode = ch_desc_mode = 0
                ch_city_mode = 1
                profile_kb = await profile_edit_kb(city='Откуда вы?', call_C='profile_empty_callback')

            elif callback.data == 'ch_desc':
                ch_name_mode = ch_age_mode = ch_city_mode = ch_photo_mode = 0
                ch_desc_mode = 1
                profile_kb = await profile_edit_kb(desc='Расскажите о себе', call_D='profile_empty_callback')

            elif callback.data == 'ch_photo':
                ch_name_mode = ch_age_mode = ch_city_mode = ch_desc_mode = 0
                ch_photo_mode = 1
                profile_kb = await profile_edit_kb(photo='Загрузите фото', call_P='profile_empty_callback')

            await bot.edit_message_caption(
                chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                caption=f'{profile_name}, {profile_age}\n{profile_city}\n\n{profile_description}',
                reply_markup=profile_kb)

    elif callback.data == 'ch_gender':
        ch_name_mode = ch_age_mode = ch_city_mode = ch_desc_mode = ch_photo_mode = 0
        await bot.edit_message_caption(
            chat_id=callback.from_user.id, message_id=bot_main_msg_id,
            caption=f'{profile_name}, {profile_age}\n{profile_city}\n\n{profile_description}',
            reply_markup=gender_choice)

    elif callback.data in ['m', 'f']:
        await bot.edit_message_caption(
            chat_id=callback.from_user.id, message_id=bot_main_msg_id,
            caption=f'{profile_name}, {profile_age}\n{profile_city}\n\n{profile_description}',
            reply_markup=await profile_edit_kb()
        )
        profile_gender = callback.data

    elif callback.data == 'save_profile':
        global db_id, profile_existing

        if profile_existing == 1:
            cur.execute(
                f"UPDATE `profiles` SET `name` = '{profile_name}', `photo` = '{photo_name}', `age` = {profile_age}, "
                f"`gender` = '{profile_gender}', `description` = '{profile_description}', `city` = '{profile_city}'"
                f"WHERE `platform` = 'tg' AND `platform_id` = {callback.from_user.id}")
            conn.commit()
        elif profile_existing == 0:
            cur.execute(
                f"INSERT INTO `profiles` (`platform`,`platform_id`,`name`,`photo`,`age`,`gender`,`description`,`city`) "
                f"VALUES ('tg',{callback.from_user.id},'{profile_name}','{photo_name}',{profile_age},'{profile_gender}','{profile_description}','{profile_city}')"
            )
            conn.commit()

        registration_mode = 0
        await bot.edit_message_media(
            chat_id=callback.from_user.id, message_id=bot_main_msg_id, media=types.InputMediaPhoto(media=menu_media))
        await bot.edit_message_caption(
            chat_id=callback.from_user.id, message_id=bot_main_msg_id,
            caption='Профиль сохранён', reply_markup=await main_menu_create(callback.from_user.id))
# ======================================================================================================================
# ==========================================================================================================Предпочтения
    elif callback.data == 'prefs':
        await bot.edit_message_media(
            chat_id=callback.from_user.id, message_id=bot_main_msg_id, media=types.InputMediaPhoto(media=menu_media))
        await bot.edit_message_caption(
            chat_id=callback.from_user.id, message_id=bot_main_msg_id,
            caption='Кого вы хотите найти?', reply_markup=pref_gender_kb)

    elif callback.data in ['pref_m', 'pref_f', 'pref_gender_no_matter', 'pref_18-25', 'pref_25-35', 'pref_35+', 'pref_age_no_matter', 'pref_city_matter', 'pref_city_no_matter']:
        global pref_column_value, pref_column_name
        if callback.data in ['pref_m', 'pref_f', 'pref_gender_no_matter']:
            pref_gender_dict = {'pref_m': '"m"', 'pref_f': '"f"', 'pref_gender_no_matter': '`gender`'}
            pref_column_value = pref_gender_dict[callback.data]
            pref_column_name = '`pref_gender`'
            await bot.edit_message_caption(
                chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                caption='Какого возраста?', reply_markup=pref_age_kb)

        elif callback.data in ['pref_18-25', 'pref_25-35', 'pref_35+', 'pref_age_no_matter']:
            pref_age_dict = {'pref_18-25': 1, 'pref_25-35': 2, 'pref_35+': 3, 'pref_age_no_matter': 0}
            pref_column_value = pref_age_dict[callback.data]
            pref_column_name = '`pref_age`'
            await bot.edit_message_caption(
                chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                caption='Откуда?', reply_markup=pref_city_kb)

        elif callback.data in ['pref_city_matter', 'pref_city_no_matter']:
            pref_city_matter_dict = {'pref_city_matter': 1, 'pref_city_no_matter': 0}
            pref_column_value = pref_city_matter_dict[callback.data]
            pref_column_name = '`pref_city_matter`'
            await bot.edit_message_caption(
                chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                caption='Ваши предпочтения сохранены', reply_markup=await main_menu_create(callback.from_user.id))
            cur.execute(f"UPDATE `profiles` SET `completed` = 1 "
                        f"WHERE `platform` = 'tg' AND `platform_id` = {callback.from_user.id}")
            conn.commit()

        cur.execute(f"UPDATE `profiles` SET {pref_column_name} = '{pref_column_value}' "
                    f"WHERE `platform` = 'tg' AND `platform_id` = {callback.from_user.id}")
        conn.commit()
        conn.reset_session()
# ======================================================================================================================
# ==================================================================================================================ROLL
    elif callback.data in ['roll_profiles', 'next_profile', 'previous_profile', 'select_profile', 'roll_chats', 'next_chat', 'previous_chat', 'select_chat', 'clear_chat']:
        global profile_offset, last_profile, pref_age, pref_gender, city_matter, city, user_fid, city_dict, age_dict
        global user_name, user_age, user_description, user_city, chat_member_id, background_check_db, user_photo

# ======================================================================================================Смотреть Профили
        if callback.data in ['roll_profiles', 'next_profile', 'previous_profile', 'select_profile']:

            if callback.data in ['roll_profiles', 'next_profile', 'previous_profile']:

                conn.reset_session()
                cur.execute(f"SELECT `pref_age`, `pref_gender`, `pref_city_matter`, `city`, `photo` FROM `profiles` "
                            f"WHERE `platform` = 'tg' AND `platform_id` = {callback.from_user.id} LIMIT 1")

                age_dict = {'0': '= `age`', '1': '> 17 AND `age` < 25', '2': '> 24 AND `age` < 35', '3': '> 35'}
                [pref_age, pref_gender, city_matter, city, user_fid] = cur.fetchone()
                city_dict = {'0': '`city`', '1': f'{city}'}

                if callback.data == 'roll_profiles':
                    profile_offset = 0
                    try:
                        cur.execute(
                            f"SELECT COUNT(`photo`) FROM `profiles` WHERE `age` {age_dict[pref_age]} "
                            f"AND `gender` = {pref_gender} AND `city` = {city_dict[city_matter]} "
                            f"AND `photo` <> '{user_fid}' LIMIT 1 OFFSET {profile_offset}")
                        last_profile = int(cur.fetchone()[0]) - 1
                    except Exception as err: print('count last profile\n', err)

                elif callback.data in ['next_profile', 'previous_profile']:
                    if callback.data == 'next_profile':
                        profile_offset = profile_offset + 1 if profile_offset < last_profile else last_profile
                    else:
                        profile_offset = profile_offset - 1 if profile_offset > 0 else 0

                try:
                    cur.execute(
                        f"SELECT `platform`, `platform_id`, `name`, `photo`, `age`, `description`, `city` "
                        f"FROM `profiles` WHERE `age` {age_dict[pref_age]} AND `gender` = {pref_gender} "
                        f"AND `city` = {city_dict[city_matter]} AND `photo` <> '{user_fid}' "
                        f"LIMIT 1 OFFSET {profile_offset}")

                    [chat_user_platform, chat_user_platform_id, user_name, user_photo, user_age, user_description, user_city] = cur.fetchone()
                    chat_member_id = [chat_user_platform, chat_user_platform_id]

                    user_profile_photo = types.FSInputFile(f'../user_profile_photos/{user_photo}.jpg')
                    await bot.edit_message_media(chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                                                 media=types.InputMediaPhoto(media=user_profile_photo))
                    await bot.edit_message_caption(chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                                                   caption=f'{user_name}, {user_age}\n{user_city}\n\n{user_description}',
                                                   reply_markup=profiles)
                except Exception as err:
                    print('roll profiles\n', err)
                    bot_misc_msg_id = await bot.send_message(chat_id=callback.from_user.id,
                                                             text='%для вас ещё не нашлись подходящие кандидаты%')
                    await asyncio.sleep(2.5)
                    await bot.delete_message(chat_id=callback.from_user.id, message_id=bot_misc_msg_id.message_id)

            elif callback.data == 'select_profile':
                CHAT_MODE = 1
                await bot.edit_message_caption(chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                                               caption=f'{user_name}, {user_age}\n{user_city}\n\n{user_description}')
                await bot.send_message(chat_id=callback.from_user.id,
                                       text='Вы вошли в режим переписки, что бы выйти нажмите /stop', reply_markup=key_stop)

                stop_thread = False
                background_check_db = Thread(await check_new_msgs_current_chat(callback.from_user.id, chat_member_id))
                background_check_db.start()

# ======================================================================================================================
# ====================================================================================================Смотреть сообщения

        elif callback.data in ['roll_chats', 'next_chat', 'previous_chat', 'select_chat', 'clear_chat']:

            if callback.data in ['roll_chats', 'next_chat', 'previous_chat']:

                conn.reset_session()
                cur.execute(f'SELECT DISTINCT `platform_1`, `user1_id` FROM `msgs` '
                            f'WHERE `platform_2` = "tg" AND `user2_id` = {callback.from_user.id};')

                chats_list = cur.fetchall()
                last_profile = len(chats_list) - 1

                if callback.data == 'roll_chats':
                    profile_offset = 0
                elif callback.data in ['next_chat', 'previous_chat']:
                    if callback.data == 'next_chat':
                        profile_offset = profile_offset + 1 if profile_offset < last_profile else last_profile
                    else:
                        profile_offset = profile_offset - 1 if profile_offset > 0 else 0

                try:
                    cur.execute(
                        f"SELECT `platform`, `platform_id`, `name`, `photo`, `age`, `description`, `city` FROM `profiles` "
                        f"WHERE `platform` = '{chats_list[profile_offset][0]}' AND `platform_id` = {chats_list[profile_offset][1]}")

                    [chat_user_platform, chat_user_platform_id, user_name, user_photo, user_age, user_description, user_city] = cur.fetchone()
                    chat_member_id = [chat_user_platform, chat_user_platform_id]

                    user_profile_photo = types.FSInputFile(f'../user_profile_photos/{user_photo}.jpg')
                    await bot.edit_message_media(chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                                                 media=types.InputMediaPhoto(media=user_profile_photo))
                    await bot.edit_message_caption(chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                                                   caption=f'{user_name}, {user_age}\n{user_city}\n\n{user_description}',
                                                   reply_markup=chats)
                except Exception as err: print('roll chats\n', err)

            elif callback.data == 'select_chat':
                CHAT_MODE = 1
                await bot.edit_message_caption(chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                                               caption=f'{user_name}, {user_age}\n{user_city}\n\n{user_description}')
                await bot.send_message(chat_id=callback.from_user.id,
                                       text='Вы вошли в режим переписки, что бы выйти нажмите /stop', reply_markup=key_stop)

                stop_thread = False
                background_check_db = Thread(await check_new_msgs_current_chat(callback.from_user.id, chat_member_id))
                background_check_db.start()

            elif callback.data == 'clear_chat':
                try:
                    cur.execute(f"UPDATE `msgs` SET `processed` = 1 "
                                f"WHERE `platform_2` = 'tg' AND `user2_id` = {callback.from_user.id} "
                                f"AND `platform_1` = '{chat_user_platform}' AND `user1_id` = {chat_user_platform_id}")
                    conn.commit()
                    await bot.edit_message_caption(
                        chat_id=callback.from_user.id, message_id=bot_main_msg_id,
                        caption='Новые сообщения этого пользователя удалены', reply_markup=chats)
                except Exception as err: print('clear chat', err)


async def main_menu_create(user_id):
    global profile_existing
    inline_main_menu = InlineKeyboardBuilder()
    conn.reset_session()
    try:
        cur.execute(
            f"SELECT `db_id` FROM `profiles` WHERE `platform` = 'tg' AND `platform_id` = {user_id} AND `completed` = 1")
        int(cur.fetchone()[0])
        profile_existing = 1
        inline_main_menu.add(InlineKeyboardButton(text='Смотреть анкеты', callback_data='roll_profiles'))
        try:
            cur.execute(
                f"SELECT COUNT(`db_id`) FROM `msgs` WHERE (`platform_1` = 'tg' AND `user1_id` = {user_id}) "
                f"OR (`platform_2` = 'tg' AND `user2_id` = {user_id})")
            cur.fetchall()

            try:
                conn.reset_session()
                cur.execute(f"SELECT COUNT(`db_id`) FROM `msgs` "
                            f"WHERE `platform_2` = 'tg' AND `user2_id` = {user_id} AND `processed` = 0")
                new_msgs_count = int(cur.fetchone()[0])
            except Exception as err: print('new msgs count\n', err); new_msgs_count = 0

            new_msgs_count = f' ({new_msgs_count})' if new_msgs_count != 0 else ''
            inline_main_menu.add(InlineKeyboardButton(text=f'Чаты{new_msgs_count}', callback_data='roll_chats'))
        except Exception as err: print('main menu chats existing\n', err)

        inline_main_menu.add(InlineKeyboardButton(text='Изменить анкету', callback_data='edit_profile'))
        inline_main_menu.add(InlineKeyboardButton(text='Предпочтения', callback_data='prefs'))
    except Exception as err:
        print('main menu profile completed\n', err)
        try:
            cur.execute(
                f"SELECT `db_id` FROM `profiles` WHERE `platform` = 'tg' AND `platform_id` = {user_id}")
            int(cur.fetchone()[0])
            inline_main_menu.add(InlineKeyboardButton(text='Изменить анкету', callback_data='edit_profile'))
            inline_main_menu.add(InlineKeyboardButton(text='Предпочтения', callback_data='prefs'))
            profile_existing = 1
        except Exception as err:
            print('main menu profile existing\n', err)
            inline_main_menu.add(InlineKeyboardButton(text='Зарегистрироваться', callback_data='create_profile'))
            profile_existing = 0

    inline_main_menu.adjust(1)
    return inline_main_menu.as_markup()


async def check_new_msgs_current_chat(user_id, chat_member) -> None:
    global new_msg_current_chat, db_id, stop_thread
    cursor = conn.cursor()
    while True:
        conn.reset_session()
        await asyncio.sleep(0.5)
        try:
            sql = (f"SELECT `message`, `db_id`  FROM `msgs` WHERE `platform_2` = 'tg' AND `user1_id` = {chat_member[1]}"
                   f" AND `platform_1` = '{chat_member[0]}' AND `user2_id` = {user_id} AND `processed` = 0 "
                   f"ORDER BY `msgs`.`datetime` ASC LIMIT 1")
            cursor.execute(sql)
            response = cursor.fetchall()[0]
            new_msg_current_chat = response[0]
            db_id = response[1]

            try:
                await bot.send_message(chat_id=user_id, text=f'{new_msg_current_chat}')
                cursor.execute(f'UPDATE `msgs` SET `processed` = 1 WHERE `db_id` = {db_id}')
                conn.commit()
            except Exception as err: print('check_new_msgs_current_chat processed\n', err)
        except IndexError: pass
        except Exception as err: print('check_new_msgs_current_chat\n', err)

        global stop_thread
        if stop_thread:
            break


async def main() -> None:
    await dp.start_polling(bot)


asyncio.run(main())
