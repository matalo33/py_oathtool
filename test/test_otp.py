import io
import os
import re
import sys
import unittest

import src.py_oathtool.otp as otp

class otp_tests(unittest.TestCase):
  def test_print_labels(self):
    output = self._execute(['--list-labels'])
    self.assertEqual(output, 'bar\nfoo')


  def test_shell_autocomplete(self):
    output = self._execute(['--tab-complete'])
    self.assertEqual(output, 'bar foo')


  def test_generate_code(self):
    output = self._execute(['foo'])
    self.assertRegex(output, re.compile('.*[\d]{6}\\t\([\d]{1,2}sec\)$'))


  def test_generate_code_without_time(self):
    output = self._execute(['--minimalist', 'foo'])
    self.assertRegex(output, re.compile('.*[\d]{6}$'))


  def _execute(self, args):
    # Pass a dedicated test config file to avoid using a real one
    sys.argv = ['otp.py', '--secrets-file', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_config.yml')] + args

    stdout_capture = io.StringIO()
    sys.stdout = stdout_capture

    try:
      otp.main()
    finally:
      sys.stdout = sys.__stdout__

    return stdout_capture.getvalue().strip()
