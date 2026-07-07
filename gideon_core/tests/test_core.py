import unittest
from memory.history import ConversationHistory

class TestConversationHistory(unittest.TestCase):
    def test_add_message(self):
        history = ConversationHistory(max_messages=2)
        history.add_user_message("Hello")
        self.assertEqual(len(history.messages), 1)
        self.assertEqual(history.messages[0].role, "user")
        self.assertEqual(history.messages[0].content, "Hello")

    def test_trim(self):
        history = ConversationHistory(max_messages=2)
        history.add_user_message("1")
        history.add_assistant_message("2")
        history.add_user_message("3")
        self.assertEqual(len(history.messages), 2)
        self.assertEqual(history.messages[0].content, "2")
        self.assertEqual(history.messages[1].content, "3")

if __name__ == '__main__':
    unittest.main()
