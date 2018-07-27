import warnings
from csv import Sniffer, excel_tab

from pandas import read_csv


def parse(file, col_zero_index=True, keep_strings=False, relabel=False):
    '''
    Given a file handle, try to determine its format and return a dataframe.

    :param file:
    :param col_zero_index:
    :param keep_strings: Preserve string values in dataframe if True
    :param relabel: Use the first string column inside the table as row labels
    :return:
    '''
    compression_type = {
        b'\x1f\x8b': 'gzip',
        b'\x50\x4b': 'zip'
    }.get(file.read(2))
    file.seek(0)
    index_col = 0 if col_zero_index else None

    if compression_type:
        # TODO: Both zip and gzip reading will be slow because
        # internally the python parser is used... but for now this
        # seems better than unzipping to sniff the first line.
        dataframe = read_csv(
            file,
            index_col=index_col,
            compression=compression_type
        )
    else:
        # We could use read_csv with separator=None...
        # but that requires the python parser, which seems to be about
        # three times as slow as the c parser.
        first_line = file.readline().decode('latin-1')
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
            warnings.simplefilter("ignore")
            dataframe = read_csv(
                file,
                index_col=index_col,
                dialect=dialect
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
        return (dataframe, label_map)
    return (dataframe.select_dtypes(['number']), label_map)
