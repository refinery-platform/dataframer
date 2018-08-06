# dataframer

[![PyPI version](https://badge.fury.io/py/dataframer.svg)](https://pypi.org/project/dataframer/)

Tries to load any file into a pandas DataFrame,
with a minimum of configuration,
and a focus on bioinformatics

## Examples

Typically, you’ll read a file from disk (`open('my-file.txt', 'rb')`),
but a byte stream is simpler here.

```
>>> from io import BytesIO
>>> from dataframer import dataframer
>>> from pandas import set_option

>>> set_option('display.max_columns', None)

>>> bytes = b'a,b,c,z\n1,2,3,foo\n4,5,6,bar'
>>> stream = BytesIO(bytes)

```

Default behavior is to strip non-numeric values after the first column.
```
>>> df_info = dataframer.parse(stream)
>>> df_info.data_frame
   b  c
a      
1  2  3
4  5  6
>>> df_info.label_map is None
True

```

Alternatively, they can be preserved in place...
```
>>> df_info = dataframer.parse(stream, keep_strings=True)
>>> df_info.data_frame
   b  c    z
a           
1  2  3  foo
4  5  6  bar
>>> df_info.label_map is None
True

```

... or they can be used to compose more meaningful row labels.
```
>>> df_info = dataframer.parse(stream, relabel=True)
>>> df_info.data_frame
   b  c
a      
1  2  3
4  5  6
>>> df_info.label_map
{1: 'foo / 1', 4: 'bar / 4'}

```

Finally, the first column can also be treated as data.
```
>>> df_info = dataframer.parse(stream, col_zero_index=False)
>>> df_info.data_frame
   a  b  c
0  1  2  3
1  4  5  6
>>> df_info.label_map is None
True

```

## Release process

In your branch update `VERSION.txt`, using semantic versioning: When the PR
is merged, the successful Docker build will push a new version to pypi.
