import unittest
from primitive_db.parser import parse_command


class TestParseCommand(unittest.TestCase):
    def test_select_with_where(self) -> None:
        cmd = parse_command("select users where age=30")
        self.assertEqual(cmd.cmd_type, "select")
        self.assertEqual(cmd.table, "users")
        self.assertEqual(cmd.where, {"age": "30"})

    def test_alias_q_exit(self) -> None:
        cmd = parse_command("q")
        self.assertEqual(cmd.cmd_type, "exit")

    def test_bad_select_where_raises(self) -> None:
        # нет условия после where
        with self.assertRaises(ValueError):
            parse_command("select users where")

    def test_bad_update_set_raises(self) -> None:
        # нет полей после set
        with self.assertRaises(ValueError):
            parse_command("update users set where id=1")


if __name__ == "__main__":
    unittest.main()
