import gzip
import warnings
import zipfile
from collections import namedtuple
from csv import Sniffer, excel_tab

from pandas import read_csv

DataFrameInfo = namedtuple('DataFrameInfo', ['data_frame', 'label_map'])


def parse(file, col_zero_index=True, keep_strings=False, relabel=False,
          peek_window=1024, encoding='latin-1'):
    '''
    Given a file handle, try to determine its format and return a DataFrame.

    :param file: Fine handle open for binary reading
    :param col_zero_index:
    :param keep_strings: Preserve string values in DataFrame if True
    :param relabel: Use the first string column inside the table as row labels
    :param peek_window: If zipped, how many bytes to read to guess dialect
    :param encoding: Character encoding to assume
    :return: DataFrameInfo, which contains the DataFrame itself,
    and a dict of labels for the rows, if relabel is True
    '''

    # The pandas default behavior is to look at filename extensions,
    # but we decided we can't rely on those to be accurate.
    compression_type = {
        b'\x1f\x8b': 'gzip',
        b'\x50\x4b': 'zip'
    }.get(file.read(2))
    file.seek(0)
    index_col = 0 if col_zero_index else None

    if compression_type:
        if compression_type == 'gzip':
            first_bytes = gzip.open(file).peek(peek_window)
        elif compression_type == 'zip':
            zf = zipfile.ZipFile(file)
            files = zf.namelist()
            assert len(files) == 1
            first_bytes = zf.open(files[0]).peek(peek_window)
        else:
            raise Exception(
                'Unsupported compression type: {}'.format(compression_type))
        first_characters = first_bytes.decode(encoding)
        is_gct = first_characters.startswith('#1.2')
        dialect = excel_tab if is_gct else Sniffer().sniff(first_characters)
        file.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            dataframe = read_csv(
                file,
                index_col=index_col,
                compression=compression_type,
                dialect=dialect,
                skiprows=2 if is_gct else 0,
                engine='c'
            )
    else:
        # We could use read_csv with separator=None...
        # but that requires the python parser, which seems to be about
        # three times as slow as the c parser.
        first_line = file.readline().decode(encoding)
        is_gct = first_line.startswith('#1.2')
        if is_gct:
            # GCT: throw away the second header line
            file.readline()
            dialect = excel_tab
        else:
            dialect = Sniffer().sniff(first_line)
            # print('"{}" -> "{}"'.format(first_line, dialect.delimiter))
            file.seek(0)
        with warnings.catch_warnings():
            # https://github.com/pandas-dev/pandas/issues/18845
            # pandas raises unnecessary warnings.
            warnings.simplefilter('ignore')
            dataframe = read_csv(
                file,
                index_col=index_col,
                dialect=dialect,
                engine='c'
            )
    if is_gct:
        dataframe.drop(columns=['Description'], inplace=True)
        # TODO: Combine the first two columns?

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

    if keep_strings:
        return DataFrameInfo(data_frame=dataframe, label_map=label_map)
    return DataFrameInfo(
        data_frame=dataframe.select_dtypes(['number']),
        label_map=label_map)
