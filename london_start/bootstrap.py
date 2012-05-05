#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import commands
import pkg_resources


class LondonStart(object):
    LONDON_DEV_REPO = '-e git+git@github.com:mochii/london.git#egg=london'
    LONDON_BIN_DIR = os.path.dirname(os.path.abspath(__file__))

    DEFAULT_PACKAGES = ('tornado', 'pymongo==2.1.1', 'ipython')
    additional_packages = []

    def __init__(self, **kwargs):
        self.verbosity = kwargs.get('verbosity', None) or '1'
        self.project_name = kwargs.get('project_name', None) or self.input_project_name()
        self.london_version = kwargs.get('london_version', None) or self.input_london_version()
        self.no_virtualenv = kwargs.get('no_virtualenv', False)
        self.package_host = kwargs.get('package_host', None) or 'londonframework.org'
        self.project_template_dir = kwargs.get('project_template_dir', None)
        self.database_name = kwargs.get('database_name', None)
        self.project_dir = kwargs.get('project_dir', None)
        self.additional_packages = kwargs.get('additional_packages', None) or self.additional_packages

        self.update_params()

    def write_output(self, msg):
        if self.verbosity != '0':
            print(msg)

    def input_project_name(self):
        # Asks for new project name
        if self.verbosity == '0':
            raise Exception('No project name informed.')

        return raw_input('> Please inform the project name: ')

    def input_london_version(self):
        # Asks for the version of London
        london_version = ''
        if not london_version and self.verbosity != '0':
            msg = '> Which london of London you want to use? [stable]\n' +\
                  '  type the version number, "stable" for latest stable version, "dev" for development version or "local" to ignore London installation: '
            london_version = raw_input(msg).lower()
            
        return london_version or 'stable'

    def check_params(self):
        if not self.valid_london_version():
            msg = 'Invalid version "%s"' % self.london_version
            if self.verbosity != '0':
                print(msg)
                sys.exit(0)
            else:
                raise Exception(msg)

    def makedirs(self):
        if not os.path.exists(self.root_dir):
            self.write_output('. Creating root directory...')
            os.makedirs(self.root_dir)

        if not os.path.exists(self.get_project_dir()):
            self.write_output('. Creating project directory...')
            os.makedirs(self.get_project_dir())

    def update_params(self):
        self.root_dir = os.path.join(os.path.abspath(os.curdir), self.project_name)
        self.bin_dir = os.path.join(self.root_dir, 'env', 'bin')
        self.pip_bin = os.path.join(self.bin_dir, 'pip')

    def get_database_name(self):
        return self.database_name or self.project_name

    def get_project_dir(self):
        return os.path.join(self.root_dir, self.project_dir or 'project')

    def get_project_template_dir(self, name='default'):
        if self.project_template_dir:
            return self.project_template_dir

        london_path = self.get_london_dir()
        return os.path.join(london_path, 'project_templates', name)

    def get_london_dir(self):
        return commands.getoutput('%s -c "import london; print(london.__path__[0])"' % os.path.join(self.bin_dir, 'python'))

    def get_bin_dir(self, absolute=False):
        return '' if self.no_virtualenv else self.bin_dir

    def get_additional_packages(self):
        return list(self.DEFAULT_PACKAGES) + list(self.additional_packages)

    @property
    def version_os(self):
        return sys.version_info[0]

    @property
    def TEMP_DIR(self):
        if self.version_os == 'win32':
            return os.path.join(self.root_dir, 'tmp')
        return '/tmp/'

    def install_initial_dependencies(self):
        if self.verbosity != '0':
            self.write_output('. Installing dependencies...')

        os.chdir(self.TEMP_DIR)

        # pip
        try:
            import pip
        except ImportError:
            self.write_output('.. pip')
            commands.getoutput('sudo easy_install pip')

        # virtualenv
        try:
            import virtualenv
        except ImportError:
            self.write_output('.. virtualenv')
            commands.getoutput('sudo pip install virtualenv==1.6.4')

        os.chdir(self.root_dir)

    def create_virtualenv(self):
        if self.no_virtualenv or os.listdir(os.path.join(self.root_dir, 'env')):
            return

        if self.verbosity != '0':
            self.write_output('. Creating virtual environment...')

        import virtualenv
        virtualenv.create_environment('env')

    def install_optional_dependencies(self, packages=None):
        if self.verbosity != '0':
            self.write_output('. Installing optional packages...')

        packages = packages or self.get_additional_packages()

        for pkg in packages:
            try:
                simple_pkg = pkg_resources.Requirement.parse(pkg).project_name
                __import__(simple_pkg)
                self.write_output('.. %s: already installed' % pkg)
            except (ImportError, ValueError):
                status, output = commands.getstatusoutput('%s install %s --upgrade' % (self.pip_bin, pkg)) # -I ignores installed package
                self.write_output('.. %s: %s'%(pkg, 'not installed (error)' if status else 'installed'))

    def valid_london_version(self, version=None):
        version = version or self.london_version
        return bool(version.strip())

    def parse_london_package(self, version):
        if version == 'local':
            return os.path.join(self.LONDON_BIN_DIR, '..', '..')
        elif version in ('dev','stable'): # FIXME: stable will be just 'london' pypi package
            return self.LONDON_DEV_REPO
        else:
            return 'london==' + version

    def install_london(self):
        if self.london_version == 'local':
            return

        if self.verbosity != '0':
            self.write_output('. Installing London framework...')

        london_package = self.parse_london_package(self.london_version)

        if self.london_version == 'local' and os.path.exists(os.path.join(london_package, 'setup.py')):
            prev_cur_dir = os.path.abspath(os.curdir)
            os.chdir(london_package)
            commands.getoutput('%s setup.py develop' % os.path.join(self.get_bin_dir(), 'python'))
            os.chdir(prev_cur_dir)
            return

        commands.getoutput('%s install %s' % (self.pip_bin, london_package))

    def create_basic_project(self):
        if os.listdir(self.get_project_dir()):
            return

        if self.verbosity != '0':
            self.write_output('. Creating basic project...')

        project_template_dir = self.get_project_template_dir()

        macro_values = {
                'project_name': self.project_name,
                'london_version': self.london_version,
                'no_virtualenv': self.no_virtualenv,
                'package_host': self.package_host,
                'project_template_dir': project_template_dir,
                'database_name': self.get_database_name(),
                'root_dir': self.root_dir,
                'project_dir': self.get_project_dir(),
                'bin_dir': self.bin_dir,
                'pip_bin': self.pip_bin,
                }

        for folder, folders, files in os.walk(project_template_dir):
            short_folder = folder[len(project_template_dir) + 1:]

            # Creates the folder if it doesn't exist
            dest_folder = os.path.join(self.project_dir, short_folder)
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            # Copies the files into destination folder
            for filename in files:
                # Special case: settings.py
                if not short_folder and filename == 'settings.py':
                    # Reading origin file
                    fp = file(os.path.join(folder, filename))
                    content = fp.read()
                    fp.close()

                    # Saving destination file
                    fp = file(os.path.join(dest_folder, filename), 'w')
                    fp.write(content % macro_values) # Replacing macros for respective values
                    fp.close()

                # Everything else
                elif not filename.startswith('.') and not filename.endswith('.pyc'):
                    shutil.copyfile(os.path.join(folder, filename), os.path.join(dest_folder, filename))

    def run_default_sequence(self):
        # Checks the given params before to start
        self.check_params()

        # Creates new project directory
        self.makedirs()

        # Installing dependencies
        self.install_initial_dependencies()

        # Creates the new virtualenv box
        self.create_virtualenv()

        # Installs London
        self.install_london()

        # Installs optional packages
        self.install_optional_dependencies()

        # Creates basic template project
        self.create_basic_project()

        # Updates dependencies
        self.update_dependencies()

    def get_london_admin_bin(self):
        if self.london_version == 'local':
            return 'london-admin.py'
        else:
            return os.path.join(self.get_bin_dir(), 'london-admin.py')

    def run_project_service(self, service='public'):
        if self.verbosity != '0':
            self.write_output('. Now you can try on the browser:    http://localhost:8000/')
            self.write_output('')

        os.chdir(self.get_project_dir())
        os.system('%s run %s' % (self.get_london_admin_bin(), service))

    def update_dependencies(self):
        if self.verbosity != '0':
            self.write_output('. Updating needed packages')

        os.chdir(self.get_project_dir())
        os.system('%s update_dependencies' % self.get_london_admin_bin())
