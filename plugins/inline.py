from urllib.parse import quote
from pyrogram import Client, filters, emoji
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument
from utils import get_search_results
from info import MAX_RESULTS, CACHE_TIME, SHARE_BUTTON_TEXT


@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for given inline query"""

    results = []
    string = query.query
    reply_markup = get_reply_markup(bot.username)
    files = await get_search_results(string, max_results=MAX_RESULTS)

    for file in files:
        results.append(
            InlineQueryResultCachedDocument(
                title=file.file_name,
                file_id=file.file_id,
                caption=file.caption,
                description=f'Size: {get_size(file.file_size)}\nType: {file.file_type}',
                reply_markup=reply_markup,
            )
        )

    if results:
        count = len(results)
        switch_pm_text = f"{emoji.FILE_FOLDER} {count} Result{'s' if count > 1 else ''}"
        if string:
            switch_pm_text += f" for {string}"

        await query.answer(results=results,
                           cache_time=CACHE_TIME,
                           switch_pm_text=switch_pm_text,
                           switch_pm_parameter="start")
    else:

        switch_pm_text = f'{emoji.CROSS_MARK} No results'
        if string:
            switch_pm_text += f' for "{string}"'

        await query.answer(
            results=[],
            cache_time=CACHE_TIME,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter="okay")


def get_reply_markup(username):
    buttons = [[
        InlineKeyboardButton('Search again', switch_inline_query_current_chat=''),
        InlineKeyboardButton(
            text='Share bot',
            url='tg://msg?text='+ quote(SHARE_BUTTON_TEXT.format(username=username))),
    ]]
    return InlineKeyboardMarkup(buttons)


def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])