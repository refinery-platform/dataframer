# dataframer
Tries to load any file into a pandas DataFrame,
with a minimum of configuration,
and a focus on bioinformatics

## Example

```
>>> filename = '/tmp/test.csv'
>>> with open(filename, 'w') as f:
...   f.write('a,b,c\n1,2,3\n4,5,6')
17
>>> from dataframer import dataframer
>>> pair = dataframer.parse(open(filename, 'rb'))
>>> pair[0]
   b  c
a      
1  2  3
4  5  6

```

## Release process

In your branch update `VERSION.txt`, using semantic versioning: When the PR
is merged, the successful Docker build will push a new version to pypi.
