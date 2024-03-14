import unittest
from unittest.mock import MagicMock
from telegram import InlineKeyboardButton, Update
from main import (
    DEFAULT_STATE,
    FREE_SPACE,
    CROSS,
    ZERO,
    generate_keyboard,
    won
)


class TestTicTacToeBot(unittest.TestCase):
    def setUp(self):

        self.mock_update = MagicMock(spec=Update)
        self.mock_update.message.reply_text.return_value = MagicMock()

        self.context = MagicMock()
        self.context.user_data = {'keyboard_state': DEFAULT_STATE}

    def test_generate_keyboard(self):

        keyboard = generate_keyboard(DEFAULT_STATE)
        self.assertEqual(len(keyboard), 3)
        self.assertEqual(len(keyboard[0]), 3)
        self.assertTrue(all(isinstance(btn, InlineKeyboardButton)
                            for row in keyboard for btn in row))

    def test_won(self):
        self.context.user_data['keyboard_state'] = [
            [CROSS, CROSS, CROSS],
            [FREE_SPACE, ZERO, FREE_SPACE],
            [ZERO, ZERO, FREE_SPACE],
        ]
        self.assertTrue(won(self.context.user_data['keyboard_state']))

        self.context.user_data['keyboard_state'] = [
            [CROSS, FREE_SPACE, ZERO],
            [CROSS, ZERO, FREE_SPACE],
            [CROSS, FREE_SPACE, ZERO],
        ]
        self.assertTrue(won(self.context.user_data['keyboard_state']))

        self.context.user_data['keyboard_state'] = [
            [CROSS, ZERO, CROSS],
            [ZERO, ZERO, FREE_SPACE],
            [CROSS, FREE_SPACE, FREE_SPACE],
        ]
        self.assertFalse(won(self.context.user_data['keyboard_state']))


if __name__ == '__main__':
    unittest.main()
