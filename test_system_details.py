import unittest

import system_details


class NetworkHelpersTests(unittest.TestCase):
    def test_parse_isp_payload(self) -> None:
        payload = {
            "ip": "203.0.113.9",
            "org": "Example ISP LLC",
            "city": "Bengaluru",
            "region": "Karnataka",
            "country": "IN",
        }

        self.assertEqual(
            system_details.parse_isp_payload(payload),
            ("Example ISP LLC (203.0.113.9)", "Bengaluru, Karnataka, IN"),
        )

    def test_parse_speed_payload(self) -> None:
        raw = {"Download": 7.5, "Upload": 2.25}
        self.assertEqual(system_details.format_network_speed(raw), ("7.50 MB/s", "2.25 MB/s"))


if __name__ == "__main__":
    unittest.main()
