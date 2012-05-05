#!/usr/bin/env python
"""
This script...

    - Asks for the new project name
    - Asks for London version (stable release or development)
    - Installs virtualenv
    - Creates a new virtualenv box
    - Downloads and install london and dependencies
    - Creates a new project, using SQLite
    - Asks to run the project public service
"""
from london_start.bootstrap import LondonStart


def install(*args, **kwargs):
    start = LondonStart(**kwargs)

    # Runs the default sequence to create directories, virtualenv, install dependencies, etc.
    start.run_default_sequence()

    # Run the public service
    start.run_project_service()

