#!/usr/bin/env python
"""
Syntax:

    london-start PACKAGE_NAME

A london start package includes a installation script and a project template. It can be path for file system, a package name or
a URL. If the package is a name, it will be searched in london start repository. If a URL, it downloads from that URL (being a
.egg file) and decompress it for its usage. If a path it will search for it as a directory or .egg file.
"""

import os
import sys
import urllib
import re
import zipfile
import tempfile
from optparse import OptionParser, make_option

EXP_PACKAGE_URL = re.compile('^https?://.+$')
EXP_PACKAGE_NAME = re.compile('[\w\-\_]+')
TEMP_DIR = tempfile.gettempdir() #'/tmp/'
REPOSITORY_URL = 'http://localhost:8000/static/%s.egg' # FIXME
__version__ = '0.1'

option_list = [
    make_option('--package', action='store', dest='package', default='basic',
        help='Inform the package name or URL to generate by.'),
    make_option('--project-name', action='store', dest='project_name', default=None,
        help='Inform the project name to create.'),
    make_option('--london-version', action='store', dest='london_version', default='stable',
        help='Inform the London version. Can be "stable" (for latest stable version), "dev", "local" or the version number.'),
    make_option('--no-virtualenv', action='store_true', dest='no_virtualenv', default=False,
        help='If set, ignores virtualenv creation and use current Python environment.'),
    ]

class BasicOptionParser(OptionParser):
    #def error(self, msg):
    #    pass
    pass

def get_option_parser(option_list, cls=OptionParser):
    parser = cls(
            usage='%prog [options] [args]',
            version=__version__,
            option_list=option_list,
            )
    return parser.parse_args(sys.argv) # options, args

def get_package(package_uri):
    """
    Treats the package given and returns a directory path.
    
    The package_uri can be path for file system, a package name or a URL. If it is a name, it will be searched in london start
    repository. If a URL, it downloads from that URL (being a .egg file) and decompress it for its usage. If a path it will
    search for it as a directory or .egg file.
    """

    root_path = ''

    # is a file system path
    if os.path.exists(package_uri):
        root_path = package_uri

    # is a URL or a package name
    elif EXP_PACKAGE_URL.match(package_uri) or EXP_PACKAGE_NAME.match(package_uri):
        if EXP_PACKAGE_URL.match(package_uri):
            root_path = os.path.join(TEMP_DIR, os.path.split(package_uri)[1])
            url = package_uri
        else:
            url = REPOSITORY_URL % package_uri
            root_path = os.path.join(TEMP_DIR, package_uri + '.egg')

        # Downloads URL's content
        url_fp = urllib.urlopen(url)
        content = url_fp.read()
        url_fp.close()

        # Saves it in temporary path
        fp = file(root_path, 'wb')
        fp.write(content)
        fp.close()

    if root_path:
        sys.path.insert(0, package_uri)

        # That is a valid package only if there was a root_path, a module "london_start_package" inside it, and another
        # module "install" inside "london_start_package".
        try:
            import london_start_package
            from london_start_package import install

            # Gets the project template directory
            if zipfile.is_zipfile(root_path):
                # Extracts template directory from zip file
                extract = zipfile.PyZipFile(root_path)
                tpl_path = os.join(TEMP_DIR, 'project_template')
                os.path.makedirs(tpl_path)
                extract.extractall(tpl_path) # FIXME: doesn't extract directories
            else:
                tpl_dir = os.path.join(root_path, 'london_project_template')

            return london_start_package, tpl_dir
        except ImportError:
            pass

    # invalid package
    print('Invalid package "%s"'%package_uri)

def main():
    # Arguments parser
    options, args = get_option_parser(option_list, cls=BasicOptionParser)
    kwargs = dict([(opt.dest,getattr(options, opt.dest, None)) for opt in option_list])

    # Get the package
    mod, tpl_dir = get_package(options.package)
    kwargs['tpl_dir'] = tpl_dir

    # Run package's install function
    mod.install(*args, **kwargs)

if __name__ == '__main__':
    main()

