import unittest

import system_details


class ApplicationVersionTests(unittest.TestCase):
    def test_parse_ui_applications_payload(self) -> None:
        payload = [
            {"Name": "chrome", "Version": "126.0.6478.127"},
            {"Name": "notepad", "Version": ""},
        ]
        self.assertEqual(
            system_details.parse_ui_applications_payload(payload),
            [("chrome", "126.0.6478.127"), ("notepad", "Unknown")],
        )


if __name__ == "__main__":
    unittest.main()
