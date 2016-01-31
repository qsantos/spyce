import unittest

import ksp_cfg
try:  # Python 2
    from StringIO import StringIO
except ImportError:  # Python 3
    from io import StringIO


class TestCfg(unittest.TestCase):
    def test_part(self):
        cfg = StringIO("""
        PART
        {
        name = somepart
        }
        """)
        part = {"PART": {"name": "somepart"}}
        self.assertEqual(ksp_cfg.parse(cfg), part)

    def test_module(self):
        cfg = StringIO("""
        PART
        {
        MODULE
        {
        name = somemodule
        }
        }""")
        part = {"PART": {"MODULE": {"name": "somemodule"}}}
        self.assertEqual(ksp_cfg.parse(cfg), part)

    def test_groups(self):
        cfg = StringIO("""
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
        self.assertEqual(ksp_cfg.parse(cfg), part)

    def test_get_group(self):
        module = {"MODULE": [{"name": "first"}, {"name": "second"}]}
        result = ksp_cfg.dict_get_group(module, "MODULE", "first")
        expected = {"name": "first"}
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
