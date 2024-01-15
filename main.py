#!/usr/bin/env python

"""
Bot for playing tic tac toe game with multiple CallbackQueryHandlers.
"""
from copy import deepcopy
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
from typing import List, Any, Coroutine, Union
import os
import random

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - '
           '%(levelname)s - %(message)s', level=logging.INFO
)
# set higher logging level for httpx to avoid all
# GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# get token using BotFather
TOKEN = os.getenv('TG_TOKEN')

CONTINUE_GAME, FINISH_GAME = range(2)

FREE_SPACE = '.'
CROSS = 'X'
ZERO = 'O'

DEFAULT_STATE = [[FREE_SPACE for _ in range(3)] for _ in range(3)]


def get_default_state():
    """Helper function to get default state of the game"""
    return deepcopy(DEFAULT_STATE)


def generate_keyboard(state: List[List[str]]) \
        -> List[List[InlineKeyboardButton]]:
    """Generate tic tac toe keyboard 3x3 (telegram buttons)"""
    return [
        [
            InlineKeyboardButton(state[r][c], callback_data=f'{r}{c}')
            for r in range(3)
        ]
        for c in range(3)
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    context.user_data['keyboard_state'] = get_default_state()
    keyboard = generate_keyboard(context.user_data['keyboard_state'])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('X (your) turn! Please, '
                                    'put X to the free place',
                                    reply_markup=reply_markup)
    return CONTINUE_GAME


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) \
        -> Union[Coroutine[Any, Any, int], Any]:
    """Main processing of the game"""
    query = update.callback_query
    user_move = query.data
    row, col = map(int, user_move)

    keyboard_state = context.user_data['keyboard_state']

    if keyboard_state[row][col] == FREE_SPACE:
        keyboard_state[row][col] = CROSS

        if won(keyboard_state):
            await query.message.reply_text("Congratulations! "
                                           "You won!")
            return end(context)

        if all(all(cell != FREE_SPACE for cell in row)
               for row in keyboard_state):
            await query.message.reply_text("It's a draw!")
            return end(context)

        opponent_move(context)

        if won(keyboard_state):
            await query.message.reply_text("Oops! You lost. Try again!")
            return end(context)

        if all(all(cell != FREE_SPACE for cell in row)
               for row in keyboard_state):
            await query.message.reply_text("It's a draw!")
            return end(context)

        keyboard = generate_keyboard(keyboard_state)
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Your move (X)!"
                                      "\nPlace X to a free spot.",
                                      reply_markup=reply_markup)

    return CONTINUE_GAME


def opponent_move(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Make a move for the opponent in the Tic Tac Toe game.

    This function is responsible for determining the opponent's move
    and updating the game state accordingly. The opponent's move
    involves placing 'O' in a random empty cell on the Tic Tac Toe board.

    Parameters:
    - context (telegram.ext.ContextTypes.DEFAULT_TYPE):
    The context object for the current conversation.

    Returns:
    None
    """
    keyboard_state = context.user_data['keyboard_state']

    empty_cells = [(r, c) for r in range(3) for c in range(3)
                   if keyboard_state[r][c] == FREE_SPACE]

    if empty_cells:
        row, col = random.choice(empty_cells)
        keyboard_state[row][col] = ZERO


def won(fields: List[str]) -> bool:
    """Check if crosses or zeros have won the game"""
    for i in range(3):
        if fields[i][0] == fields[i][1] == fields[i][2] != FREE_SPACE or \
                fields[0][i] == fields[1][i] == fields[2][i] != FREE_SPACE:
            return True

    if fields[0][0] == fields[1][1] == fields[2][2] != FREE_SPACE or \
            fields[0][2] == fields[1][1] == fields[2][0] != FREE_SPACE:
        return True

    return False


async def end(context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    # reset state to default so you can play again with /start
    context.user_data['keyboard_state'] = get_default_state()
    return ConversationHandler.END


def main() -> None:
    """Run the bot"""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Setup conversation handler with the states CONTINUE_GAME and FINISH_GAME
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONTINUE_GAME: [
                CallbackQueryHandler(game, pattern='^' + f'{r}{c}' + '$')
                for r in range(3)
                for c in range(3)
            ],
            FINISH_GAME: [
                CallbackQueryHandler(end, pattern='^' + f'{r}{c}' + '$')
                for r in range(3)
                for c in range(3)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add ConversationHandler to application
    # that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
