from main import session_manager, database, bot


async def process_getting_file(main_image_path: str, chat_id: int):
    resp_image = await session_manager.get(main_image_path, user_id=chat_id)
    filename = main_image_path.split('/')[-1]
    image_data = await database.get_file(filename)
    if image_data:
        await bot.send_photo(chat_id, image_data)
    else:
        msg = await bot.send_photo(chat_id,
                                   photo=resp_image.get('file'))
        file_id = msg.photo[-1].file_id
        await database.save_file_to_db(filename, file_id)
