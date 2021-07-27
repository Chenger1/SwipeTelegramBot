from main import session_manager, database, bot


async def process_getting_file(file_path: str, chat_id: int):
    resp_file = await session_manager.get(file_path, user_id=chat_id)
    filename = file_path.split('/')[-1]
    file_data = await database.get_file(filename)
    if resp_file.get('file_type') in ('image/png', 'image/jpeg', 'image/jpg'):
        method = bot.send_photo
        file_attr = 'photo'
    else:
        method = bot.send_document
        file_attr = 'document'
    if file_data:
        await method(chat_id, file_data)
    else:
        msg = await method(chat_id, resp_file.get('file'))
        if file_attr == 'photo':
            file_id = msg.photo[-1].file_id
        else:
            file_id = getattr(msg, file_attr).file_id
        await database.save_file_to_db(filename, file_id)
