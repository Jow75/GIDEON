import unittest
from skills.desktop import LaunchApplicationSkill

class TestAutomationFramework(unittest.TestCase):
    def test_launch_app_schema(self):
        skill = LaunchApplicationSkill()
        self.assertEqual(skill.name, "launch_application")
        self.assertIn("app_name", skill.parameters["required"])

    def test_launch_app_validation(self):
        import asyncio
        skill = LaunchApplicationSkill()
        res = asyncio.run(skill.execute())
        self.assertEqual(res, "Error: app_name is required.")

if __name__ == '__main__':
    unittest.main()
