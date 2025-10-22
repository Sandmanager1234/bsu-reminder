from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bsu.dtos import NotificationDTO


menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать группу", callback_data="insert_group")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")]
    ]
)

back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='back')]
    ]
)

periods_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='За 5 минут', callback_data='5min')],
        [InlineKeyboardButton(text='За 10 минут', callback_data='10min')],
        [InlineKeyboardButton(text='За 15 минут', callback_data='15min')],
        [InlineKeyboardButton(text='За Начало пары', callback_data='start')],
        [InlineKeyboardButton(text='Назад', callback_data='back')]
    ]
)

def get_times_kb(settings: NotificationDTO):
    options = {
        'min5': 'За 5 минут',
        'min10': 'За 10 минут',
        'min15': 'За 15 минут',
        'start': 'В момент начала'
    }
    buttons = []
    for key, label in options:
        text = f'✅ {label}' if getattr(settings, key, False) else label
        buttons.append([InlineKeyboardButton(text=text, callback_data=f'notify:{key}')])
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='back')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
            