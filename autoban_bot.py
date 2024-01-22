import os

import telegram.error
from telegram import Update, Message, ChatMember
from telegram.constants import ChatType, ChatMemberStatus
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler, MessageHandler, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ALLOWED_GROUPS = [int(x) for x in os.environ.get("ALLOWED_GROUPS").split(",")]

START_MESSAGE = ("Задолбало админить Telegram-группу только ради рабочих "
                 "комментов в канале? Хочешь просто рабочие комментарии, "
                 "без группы как таковой? Это бот для тебя! Правда конкретно "
                 "этот откажется работать в незнакомой ему беседе, но ты можешь"
                 "взять исходники и поднять свою его копию.")
INFO_MESSAGE = ("В эту группу нельзя вступить, она существует только для работы комментариев. "
                "Если у вас есть вопросы, напишите их в комментариях под любым сообщением, "
                "в личные сообщения админу, либо на почту support@mmk.pw.")

sent_info_messages = {}             # type: dict[int, Message]


async def on_start_command(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command
    """
    print(update.effective_chat)
    if update.effective_chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if update.effective_chat.id not in ALLOWED_GROUPS:
            await update.effective_message.reply_text(f"I don't want to work in this chat, ID={update.effective_chat.id}")
        else:
            await update.effective_message.reply_text("Let's go. Don't forgot to ban everyone except admins.")
        return
    await update.effective_message.reply_text(START_MESSAGE)


async def on_member_change(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """
    Kick user when they join a chat.
    """
    if update.effective_chat.id not in ALLOWED_GROUPS:
        await update.effective_message.reply_text(f"I don't want to work in this chat, ID={update.effective_chat.id}")
        return

    # Filter requests
    status = update.chat_member.difference().get("status")
    is_bot = update.effective_user.is_bot
    if is_bot or status is None or status[0] != ChatMemberStatus.LEFT or status[1] != ChatMember.MEMBER:
        return

    # Info message drop
    chat_id = update.effective_chat.id
    if chat_id in sent_info_messages:
        try:
            await sent_info_messages[chat_id].delete()
        except telegram.error.BadRequest:
            pass
    sent_info_messages[chat_id] = await update.effective_chat.send_message(INFO_MESSAGE, disable_notification=True)

    # Ban
    print("Ban", update.effective_user.id, "from", update.effective_chat.id)
    await update.effective_chat.unban_member(update.effective_user.id)


async def on_message(update: Update, _):
    """
    Delete join/left messages
    """
    if len(update.effective_message.new_chat_members) > 0 or update.effective_message.left_chat_member:
        await update.effective_message.delete()


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", on_start_command))
    app.add_handler(MessageHandler(filters=filters.ALL, callback=on_message))
    app.add_handler(ChatMemberHandler(on_member_change, ChatMemberHandler.CHAT_MEMBER))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
