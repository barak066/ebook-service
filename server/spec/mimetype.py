'''Converter file extention to MIME type.
Based on mimetypes module.

Usage:
>>> from spec.mimetype import mimetype
>>> mimetype('.pdf')
'application/pdf'''

import mimetypes

# add mimetypes file from apache
mimetypes.knownfiles.insert(0, 'spec/a_mime.types')
# add our mimetypes file
mimetypes.knownfiles.insert(0, 'spec/mime.types')

mimetypes.init()

def mimetype(ext):
    '''Convert file extention with leading '.' to MIME type'''
    return mimetypes.types_map[ext]
