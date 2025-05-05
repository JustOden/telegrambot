from telegram import InlineKeyboardMarkup, InlineKeyboardButton


class Button:
    def new(format: tuple[dict]) -> InlineKeyboardMarkup:
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton(key, callback_data=value) for key, value in i.items()] for i in format]
        )

        return button