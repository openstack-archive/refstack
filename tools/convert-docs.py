#!/usr/bin/env python
# Copyright (c) 2017 IBM, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Convert RST files to basic HTML. The primary use case is to provide a way
to display RefStack documentation on the RefStack website.
"""

import argparse
import glob
import os

from bs4 import BeautifulSoup
from docutils.core import publish_file


def extract_body(html):
    """Extract the content of the body tags of an HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    return ''.join(['%s' % str(a) for a in soup.body.contents])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert RST files to basic HTML template files.'
    )
    parser.add_argument('files',
                        metavar='file',
                        nargs='+',
                        help='RST file(s) to be converted to HTML templates.')
    parser.add_argument('-o', '--output_dir',
                        required=False,
                        help='The directory where template files should be '
                             'output to. Defaults to the current directory.')
    args = parser.parse_args()

    if args.output_dir:
        output_dir = args.output_dir
        # If the output directory doesn't exist, create it.
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError:
                if not os.path.isdir(output_dir):
                    raise
    else:
        output_dir = os.getcwd()

    for path in args.files:
        for file in glob.glob(path):
            base_file = os.path.splitext(os.path.basename(file))[0]

            # Calling publish_file will also print to stdout. Destination path
            # is set to /dev/null to suppress this.
            html = publish_file(source_path=file,
                                destination_path='/dev/null',
                                writer_name='html',)
            body = extract_body(html)

            output_file = os.path.join(output_dir, base_file + ".html")
            with open(output_file, "w") as template_file:
                template_file.write(body)
