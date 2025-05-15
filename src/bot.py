import logging
import re
from telegram import Update, ForceReply, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from . import config
from . import api_client

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Command Handlers
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"Привет, {user.mention_markdown_v2()}\!\n\n"
        f"Я помогу тебе проверить ОСАГО и штрафы\.
"
        f"Используй /help, чтобы увидеть список доступных команд\."
    )
    update.message.reply_markdown_v2(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "*Доступные команды:*
"
        "/start \- Начало работы с ботом\n"
        "/help \- Показать это сообщение\n"
        "/check\_osago\_vin `VIN` \- Проверить ОСАГО по VIN номеру\.\n"
        "    Пример: `/check_osago_vin XXXXXXXXXXXXXXXXX`
"
        "/check\_osago\_reg `ГОСНОМЕР` \- Проверить ОСАГО по гос\-номеру\.\n"
        "    Пример: `/check_osago_reg A123BC77`
"
        "/check\_fines `ГОСНОМЕР` `НОМЕР_СТС` \- Проверить штрафы по гос\-номеру и номеру СТС\.\n"
        "    Пример: `/check_fines A123BC77 1234567890`
    )
    update.message.reply_markdown_v2(help_text)

def format_osago_policies(policies):
    if not policies:
        return "Полисы ОСАГО не найдены\."
    
    response_text = "*Найденные полисы ОСАГО:*
\n"
    for policy in policies:
        response_text += f"*Компания:* {policy.get('companyName', 'Н/Д')}\n"
        response_text += f"*Серия:* {policy.get('policySerial', 'Н/Д')}\n"
        response_text += f"*Номер:* {policy.get('policyNumber', 'Н/Д')}\n"
        response_text += f"*VIN:* {policy.get('vin_mask', policy.get('vin', 'Н/Д'))}\n"
        response_text += f"*Гос\-номер:* {policy.get('regNumber_mask', policy.get('regNumber', 'Н/Д'))}\n"
        response_text += f"*Марка/Модель:* {policy.get('mark', 'Н/Д')} {policy.get('model', 'Н/Д')}\n"
        response_text += f"*Начало действия:* {policy.get('startDate', 'Н/Д')}\n"
        response_text += f"*Окончание действия:* {policy.get('endDate', 'Н/Д')}\n"
        response_text += f"*Статус:* {policy.get('status', 'Н/Д')}\n\n"
    return response_text

def check_osago_vin_command(update: Update, context: CallbackContext) -> None:
    """Checks OSAGO by VIN."""
    if not context.args or len(context.args) != 1:
        update.message.reply_text("Пожалуйста, укажите VIN номер после команды\. Пример: /check\_osago\_vin XXXXXXXXXXXXXXXXX")
        return

    vin = context.args[0].upper()
    # Basic VIN validation (length and characters)
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
        update.message.reply_text("Неверный формат VIN номера\. VIN должен состоять из 17 латинских букв (кроме I, O, Q) и цифр\.")
        return

    update.message.reply_text(f"Проверяю ОСАГО для VIN: {vin}\.\.\.")
    result = api_client.check_osago_vin(vin)

    if result["status"] == "success":
        response_text = format_osago_policies(result["data"])
    else:
        response_text = f"Ошибка при проверке ОСАГО: {result['message']}"
    
    update.message.reply_markdown_v2(response_text.replace('.', '\\.').replace('-', '\\-').replace('!', '\\!'))

def check_osago_reg_command(update: Update, context: CallbackContext) -> None:
    """Checks OSAGO by registration number."""
    if not context.args or len(context.args) != 1:
        update.message.reply_text("Пожалуйста, укажите гос\-номер после команды\. Пример: /check\_osago\_reg A123BC77")
        return

    reg_number = context.args[0].upper()
    # Basic validation for Russian reg number (can be improved)
    if not re.match(r'^[АВЕКМНОРСТУХABEKMHOPCTYX]{1}\d{3}[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{2,3}$', reg_number, re.IGNORECASE):
         update.message.reply_text("Неверный формат гос\-номера\. Пример: А123ВС45 или А123ВС456\.")
         return

    update.message.reply_text(f"Проверяю ОСАГО для гос\-номера: {reg_number}\.\.\.")
    result = api_client.check_osago_reg_number(reg_number)

    if result["status"] == "success":
        response_text = format_osago_policies(result["data"])
    else:
        response_text = f"Ошибка при проверке ОСАГО: {result['message']}"
    
    update.message.reply_markdown_v2(response_text.replace('.', '\\.').replace('-', '\\-').replace('!', '\\!'))

def format_fines(fines_data, api_message):
    if api_message and not fines_data:
        return api_message.replace('.', '\\.').replace('-', '\\-').replace('!', '\\!') # Escape for MarkdownV2
    if not fines_data:
        return "Штрафы не найдены\."

    response_text = "*Найденные штрафы:*
\n"
    for fine in fines_data:
        response_text += f"*Номер постановления:* {fine.get('num_post', 'Н/Д')}\n"
        response_text += f"*Дата нарушения:* {fine.get('date_decision', 'Н/Д')}\n"
        response_text += f"*Статья КоАП:* {fine.get('koap_code', 'Н/Д')} \- {fine.get('koap_text', 'Н/Д')}\n"
        response_text += f"*Сумма:* {fine.get('sum', 'Н/Д')} руб\.
"
        if fine.get('enable_discount'):
            response_text += f"*Скидка до:* {fine.get('date_discount', 'Н/Д')}\n"
        response_text += f"*Подразделение:* {fine.get('division_name', 'Н/Д')}\n"
        # Add more fields if needed, e.g., photo availability
        if fine.get('photo_available') and fine.get('photo_token'):
            response_text += f"_Фото доступно \(для получения фото используйте соответствующие команды, если они реализованы\)_\n"
        response_text += "\n"
    return response_text

def check_fines_command(update: Update, context: CallbackContext) -> None:
    """Checks fines by registration number and STS."""
    if not context.args or len(context.args) != 2:
        update.message.reply_text("Пожалуйста, укажите гос\-номер и номер СТС после команды\. Пример: /check\_fines A123BC77 1234567890")
        return

    reg_number = context.args[0].upper()
    sts_number = context.args[1]

    # Basic validation (can be improved)
    if not re.match(r'^[АВЕКМНОРСТУХABEKMHOPCTYX]{1}\d{3}[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{2,3}$', reg_number, re.IGNORECASE):
         update.message.reply_text("Неверный формат гос\-номера\. Пример: А123ВС45 или А123ВС456\.")
         return
    if not re.match(r'^\d{10}$', sts_number):
        update.message.reply_text("Неверный формат номера СТС\. Должен состоять из 10 цифр\.")
        return

    update.message.reply_text(f"Проверяю штрафы для гос\-номера: {reg_number} и СТС: {sts_number}\.\.\.")
    result = api_client.check_fines(reg_number, sts_number)

    if result["status"] == "success":
        response_text = format_fines(result["data"], result.get("message"))
    else:
        response_text = f"Ошибка при проверке штрафов: {result['message']}"
    
    update.message.reply_markdown_v2(response_text.replace('.', '\\.').replace('-', '\\-').replace('!', '\\!'))

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("check_osago_vin", check_osago_vin_command))
    dispatcher.add_handler(CommandHandler("check_osago_reg", check_osago_reg_command))
    dispatcher.add_handler(CommandHandler("check_fines", check_fines_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()

