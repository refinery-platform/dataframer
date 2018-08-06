# dataframer

[![PyPI version](https://badge.fury.io/py/dataframer.svg)](https://pypi.org/project/dataframer/)

Tries to load any file into a pandas DataFrame,
with a minimum of configuration,
and a focus on bioinformatics

## Example

```
>>> from io import BytesIO
>>> from dataframer import dataframer

>>> bytes = b'a,b,c,z\n1,2,3,foo\n4,5,6,bar'
>>> stream = BytesIO(bytes)

>>> df_info = dataframer.parse(stream)
>>> df_info.data_frame
   b  c
a      
1  2  3
4  5  6
>>> df_info.label_map


```

## Release process

In your branch update `VERSION.txt`, using semantic versioning: When the PR
is merged, the successful Docker build will push a new version to pypi.
