import unittest
from skills.system import TimeSkill

class TestSkills(unittest.TestCase):
    def test_time_skill(self):
        skill = TimeSkill()
        res = skill.execute()
        self.assertIn("Current date and time", res)
        self.assertEqual(skill.name, "get_current_time")

if __name__ == '__main__':
    unittest.main()
