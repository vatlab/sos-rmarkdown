#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import os
import shutil
import subprocess
import unittest

from sos_notebook.converter import notebook_to_script, script_to_notebook


class TestConvert(unittest.TestCase):

    def testConvertHTML(self):
        for filename in ('example.ipynb', 'executed.ipynb', 'example.html',
                         'executed.html', 'example1.html'):
            if os.path.isfile(filename):
                os.remove(filename)

        self.assertEqual(
            subprocess.call(
                'sos convert example.Rmd example.ipynb', shell=True), 0)
        self.assertTrue(os.path.isfile('example.ipynb'))

        self.assertEqual(
            subprocess.call(
                'sos convert example.Rmd executed.ipynb --execute', shell=True),
            0)
        self.assertTrue(os.path.isfile('example.ipynb'))

        self.assertEqual(
            subprocess.call('sos convert example.Rmd example.html', shell=True),
            0)
        self.assertTrue(os.path.isfile('example.html'))

        self.assertEqual(
            subprocess.call(
                'sos convert example.Rmd example.html --execute', shell=True),
            0)
        self.assertTrue(os.path.isfile('example.html'))


        self.assertEqual(
            subprocess.call(
                'sos convert example.Rmd example1.html --execute --template sos-report-toc-v2', shell=True),
            0)
        self.assertTrue(os.path.isfile('example1.html'))

if __name__ == '__main__':
    unittest.main()
