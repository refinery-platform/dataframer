import gzip
import warnings
from collections import namedtuple
from csv import Sniffer, excel_tab
from re import search

from pandas import DataFrame, read_csv

DataFrameInfo = namedtuple('DataFrameInfo', ['data_frame', 'label_map'])
SniffResult = namedtuple('SniffResult',
                         ['compression', 'is_gct', 'dialect',
                          'is_list', 'as_list'])


def sniff(file):
    # The pandas default behavior is to look at filename extensions,
    # but we decided we can't rely on those to be accurate.
    compression = {
        b'\x1f\x8b': 'gzip'
    }.get(file.read(2))
    file.seek(0)

    encoding = 'latin-1'
    if compression:
        peek_window = 1024  # arbitrary
        if compression == 'gzip':
            first_bytes = gzip.open(file).peek(peek_window)
        else:
            raise Exception(
                'Unsupported compression type: {}'.format(compression))
        first_characters = first_bytes.decode(encoding)
    else:
        first_characters = file.readline().decode(encoding)
    is_gct = first_characters.startswith('#1.2')
    dialect = excel_tab if is_gct else Sniffer().sniff(first_characters)

    if search(r'\W', first_characters.split('\n')[0]):
        is_list = False
        as_list = None
    else:
        # No non-word characters in first line
        file.seek(0)
        is_list = True
        as_list = DataFrame({'item': [bytes.decode(encoding) for
                                      bytes in file.read().splitlines()]})
    file.seek(0)
    return SniffResult(compression=compression, is_gct=is_gct, dialect=dialect,
                       is_list=is_list, as_list=as_list)


def parse(file, col_zero_index=True, keep_strings=False, relabel=False,
          first_row_only=False):
    '''
    Given a file handle, try to determine its format and return a DataFrame.

    :param file: Fine handle open for binary reading
    :param col_zero_index:
    :param keep_strings: Preserve string values in DataFrame if True
    :param relabel: Use the first string column inside the table as row labels
    :param encoding: Character encoding to assume
    :return: DataFrameInfo, which contains the DataFrame itself,
    and a dict of labels for the rows, if relabel is True
    '''
    sniff_result = sniff(file)
    if sniff_result.is_list:
        return DataFrameInfo(data_frame=sniff_result.as_list, label_map=None)
    with warnings.catch_warnings():
        # https://github.com/pandas-dev/pandas/issues/18845
        # pandas raises unnecessary warnings.
        warnings.simplefilter('ignore')
        dataframe = read_csv(
            file,
            index_col=0 if col_zero_index else None,
            compression=sniff_result.compression,
            dialect=sniff_result.dialect,
            skiprows=2 if sniff_result.is_gct else 0,
            nrows=1 if first_row_only else None,
            engine='c'
            # If other parameters were tweaked and it would fall back to the
            # python engine, we'll get an explicit error instead.
        )
    if sniff_result.is_gct:
        dataframe.drop(columns=['Description'], inplace=True)

    if relabel:
        label_map = {
            i: ' / '.join(
                dataframe.select_dtypes(['object']).loc[i].tolist()[:1] +
                # `select_dtypes` returns a subset of the original columns.
                # 'object' means non-number, usually string, in numpy.
                # `loc` returns a single row.
                # tolist() may be empty if there were no strings.
                [str(i)]
                # `i` is the original, cryptic, row index
            )
            for i in dataframe.index
        }
    else:
        label_map = None

    if not keep_strings:
        dataframe = dataframe.select_dtypes(['number'])

    return DataFrameInfo(data_frame=dataframe, label_map=label_map)
