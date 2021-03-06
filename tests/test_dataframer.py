import unittest
from io import BytesIO

import numpy as np
import pandas

from dataframer.dataframer import parse


class TestDataFrames(unittest.TestCase):

    def assert_equal_data_frames(self, a, b, message=''):
        self.assertEqual(a.shape, b.shape, message)
        a_np = np.array(a.values.tolist())
        b_np = np.array(b.values.tolist())
        np.testing.assert_equal(a_np, b_np, message)
        self.assertEqual(a.columns.tolist(), b.columns.tolist(), message)
        self.assertEqual(a.index.tolist(), b.index.tolist(), message)

    def assert_good_parse(self, input_bytes, df_target, label_map_target=None,
                          kwargs={}, message=None):
        stream = BytesIO(input_bytes)
        df_info = parse(stream, **kwargs)
        self.assert_equal_data_frames(df_info.data_frame, df_target, message)
        if label_map_target:
            self.assertEqual(df_info.label_map, label_map_target, message)


class TestKwargs(TestDataFrames):

    def test_col_zero_index(self):
        self.assert_good_parse(
            b'a,b,c\n1,2,3',
            pandas.DataFrame(
                [[1, 2, 3]],
                columns=['a', 'b', 'c'],
                index=[0]
            ),
            kwargs={'col_zero_index': False})

    def test_keep_strings(self):
        self.assert_good_parse(
            b',b,c,xxx\n1,2,3,X!',
            pandas.DataFrame(
                [[2, 3, 'X!']],
                columns=['b', 'c', 'xxx'],
                index=[1]
            ),
            kwargs={'keep_strings': True})

    def test_relabel(self):
        self.assert_good_parse(
            b',b,c,xxx\n1,2,3,X!',
            pandas.DataFrame(
                [[2, 3]],
                columns=['b', 'c'],
                index=[1]
            ),
            label_map_target={1: 'X! / 1'},
            kwargs={'relabel': True})

    def test_first_row_only(self):
        self.assert_good_parse(
            b',b,c\n1,2,3\n4,5,6',
            pandas.DataFrame(
                [[2, 3]],
                columns=['b', 'c'],
                index=[1]
            ),
            kwargs={'first_row_only': True})


class TestFileTypes(TestDataFrames):

    def setUp(self):
        self.target = pandas.DataFrame([
            [2, 3]],
            columns=['b', 'c'],
            index=[1]
        )

    def test_read_crazy_delimiters(self):
        for c in '~!@#$%^&*|:;':
            self.assert_good_parse(
                bytes('{0}b{0}c\n1{0}2{0}3'.format(c), 'utf-8'),
                self.target,
                message='Failed with {} as delimiter'.format(c)
            )

    # Easier just to make the data on the commandline
    # than to create it inside python:
    #   $ gzip fake.csv
    #   >>> open('fake.csv.gz', 'rb').read()

    def test_read_gzip(self):
        self.assert_good_parse(
            b'\x1f\x8b\x08\x08\xe5\xf2\x82Z\x00\x03fake.csv\x00\xd3I\xd2I\xe62\xd41\xd21\x06\x00\xfb\x9a\xc9\xa6\n\x00\x00\x00', self.target)  # noqa: E501

    def test_read_csv(self):
        self.assert_good_parse(b',b,c\n1,2,3', self.target)

    def test_read_csv_remove_strings(self):
        self.assert_good_parse(b',b,c,xxx\n1,2,3,X!', self.target)

    def test_read_csv_rn(self):
        self.assert_good_parse(b',b,c\r\n1,2,3', self.target)

    def test_read_csv_quoted(self):
        self.assert_good_parse(b',"b","c"\n"1","2","3"', self.target)

    def test_read_tsv(self):
        self.assert_good_parse(b'\tb\tc\n1\t2\t3', self.target)

    def test_read_gct(self):
        self.assert_good_parse(
            b'#1.2\n1\t1\nNames\tDescription\tb\tc\n1\tfoo\t2\t3', self.target)

    def test_read_gct_gz(self):
        self.assert_good_parse(
            b'\x1f\x8b\x08\x085\xa3c[\x00\x03fake.gct\x00S6\xd43\xe22\xe44\xe4\xf2K\xccM-\xe6tI-N.\xca,(\xc9\xcc\xcf\xe3L\xe2L\x06\xca\xa4\xe5\xe7s\x1aq\x1a\x03\x00\xe7\xcc\xe5\xe5(\x00\x00\x00', self.target)  # noqa: E501
