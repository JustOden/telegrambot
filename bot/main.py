from config import bot

"""
A telegram bot using the python-telegram-bot api wrapper with custom decorator logic.
This main file is simply to run the application; all bot setup and decorator logic is within the config module.
The decorators act as register functions, which simply adds the handlers to the application.
"""

if __name__ == "__main__":
    bot.run()
