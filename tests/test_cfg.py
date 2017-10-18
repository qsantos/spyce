import unittest
import io

import spyce.ksp_cfg


class TestCfg(unittest.TestCase):
    def test_part(self):
        cfg = io.StringIO("""
        PART
        {
        name = somepart
        }
        """)
        part = {"PART": {"name": "somepart"}}
        self.assertEqual(spyce.ksp_cfg.parse(cfg), part)

    def test_module(self):
        cfg = io.StringIO("""
        PART
        {
        MODULE
        {
        name = somemodule
        }
        }""")
        part = {"PART": {"MODULE": {"name": "somemodule"}}}
        self.assertEqual(spyce.ksp_cfg.parse(cfg), part)

    def test_groups(self):
        cfg = io.StringIO("""
        PART
        {
        MODULE
        {
        name = first
        }
        MODULE
        {
        name = second
        }
        }
        """)
        part = {"PART": {"MODULE": [{"name": "first"}, {"name": "second"}]}}
        self.assertEqual(spyce.ksp_cfg.parse(cfg), part)

    def test_get_group(self):
        module = {"MODULE": [{"name": "first"}, {"name": "second"}]}
        result = spyce.ksp_cfg.dict_get_group(module, "MODULE", "first")
        expected = {"name": "first"}
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
