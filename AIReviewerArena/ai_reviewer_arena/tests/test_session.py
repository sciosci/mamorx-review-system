import json
import unittest
from datetime import datetime

from ai_reviewer_arena.sessions import Session


class TestSession(unittest.TestCase):

    def setUp(self):
        self.session = Session(
            "test_session_id", ip_address="127.0.0.1", user_agent="Test User Agent"
        )

    def test_init(self):
        self.assertEqual(self.session.session_id, "test_session_id")
        self.assertEqual(self.session.ip_address, "127.0.0.1")
        self.assertEqual(self.session.user_agent, "Test User Agent")
        self.assertIsNone(self.session.end_time)
        self.assertIsInstance(self.session.start_time, datetime)

    def test_init_empty_session_id(self):
        with self.assertRaises(ValueError):
            Session("")

    def test_immutable_attributes(self):
        with self.assertRaises(AttributeError):
            self.session["session_id"] = "new_id"
        with self.assertRaises(AttributeError):
            self.session["start_time"] = datetime.now()

    def test_mutable_attributes(self):
        new_time = datetime.now()
        self.session["end_time"] = new_time
        self.assertEqual(self.session.end_time, new_time)

        self.session["ip_address"] = "192.168.1.1"
        self.assertEqual(self.session.ip_address, "192.168.1.1")

        self.session["user_agent"] = "New User Agent"
        self.assertEqual(self.session.user_agent, "New User Agent")

    def test_custom_data(self):
        self.session["custom_key"] = "custom_value"
        self.assertEqual(self.session["custom_key"], "custom_value")

    def test_get_nonexistent_key(self):
        with self.assertRaises(KeyError):
            _ = self.session["nonexistent"]

    def test_set_none_value(self):
        with self.assertRaises(ValueError):
            self.session["none_key"] = None

    def test_delete_item(self):
        self.session["temp_key"] = "temp_value"
        del self.session["temp_key"]
        self.assertNotIn("temp_key", self.session)

    def test_delete_special_attribute(self):
        with self.assertRaises(AttributeError):
            del self.session["session_id"]

    def test_contains(self):
        self.assertIn("session_id", self.session)
        self.assertIn("start_time", self.session)
        self.assertNotIn("nonexistent", self.session)

    def test_get_method(self):
        self.assertEqual(self.session.get("session_id"), "test_session_id")
        self.assertEqual(self.session.get("nonexistent", "default"), "default")

    def test_pop_method(self):
        self.session["temp_key"] = "temp_value"
        self.assertEqual(self.session.pop("temp_key"), "temp_value")
        self.assertNotIn("temp_key", self.session)

        with self.assertRaises(AttributeError):
            self.session.pop("session_id")

    def test_clear_method(self):
        self.session["temp_key"] = "temp_value"
        self.session.clear()
        self.assertNotIn("temp_key", self.session)
        self.assertIn("session_id", self.session)  # Special attributes should remain

    def test_update_method(self):
        update_dict = {"end_time": datetime.now(), "custom_key": "custom_value"}
        self.session.update(update_dict)
        self.assertIsNotNone(self.session.end_time)
        self.assertEqual(self.session["custom_key"], "custom_value")

        # Attempt to update immutable attributes
        update_dict = {"session_id": "new_id", "custom_key2": "value2"}
        self.session.update(update_dict)
        self.assertEqual(
            self.session.session_id, "test_session_id"
        )  # Should not change
        self.assertEqual(self.session["custom_key2"], "value2")  # Should be added

    def test_keys_method(self):
        self.session["custom_key"] = "custom_value"
        keys = set(self.session.keys())
        self.assertSetEqual(
            keys,
            {
                "session_id",
                "start_time",
                "end_time",
                "ip_address",
                "user_agent",
                "custom_key",
            },
        )

    def test_values_method(self):
        values = list(self.session.values())
        self.assertEqual(len(values), 5)  # 5 special attributes
        self.assertIn(self.session.session_id, values)
        self.assertIn(self.session.start_time, values)

    def test_items_method(self):
        items = dict(self.session.items())
        self.assertIn("session_id", items)
        self.assertEqual(items["session_id"], self.session.session_id)

    def test_repr_method(self):
        repr_str = repr(self.session)
        self.assertIn("test_session_id", repr_str)
        self.assertIn("127.0.0.1", repr_str)
        self.assertIn("Test User Agent", repr_str)

    def test_str_method(self):
        str_json = str(self.session)
        self.assertIn("test_session_id", str_json)
        self.assertIn("127.0.0.1", str_json)
        self.assertIn("Test User Agent", str_json)

    def test_to_json_method(self):
        self.session["custom_key"] = "custom_value"
        json_str = self.session.to_json()
        json_dict = json.loads(json_str)
        self.assertEqual(json_dict["session_id"], "test_session_id")
        self.assertEqual(json_dict["custom_key"], "custom_value")

    def test_to_json_with_exclusions(self):
        self.session["custom_key"] = "custom_value"
        json_str = self.session.to_json(exclude_keys={"ip_address", "custom_key"})
        json_dict = json.loads(json_str)
        self.assertNotIn("ip_address", json_dict)
        self.assertNotIn("custom_key", json_dict)
        self.assertIn("session_id", json_dict)

    def test_from_json_method(self):
        original_session = self.session
        original_session["custom_key"] = "custom_value"
        json_str = original_session.to_json()

        new_session = Session.from_json(json_str)
        self.assertEqual(new_session.session_id, original_session.session_id)
        self.assertEqual(new_session.ip_address, original_session.ip_address)
        self.assertEqual(new_session.user_agent, original_session.user_agent)
        self.assertEqual(new_session["custom_key"], "custom_value")

    def test_from_json_with_missing_fields(self):
        json_str = json.dumps({"session_id": "test_id"})
        session = Session.from_json(json_str)
        self.assertEqual(session.session_id, "test_id")
        self.assertIsNone(session.ip_address)
        self.assertIsNone(session.user_agent)


if __name__ == "__main__":
    unittest.main()
