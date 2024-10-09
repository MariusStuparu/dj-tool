"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""
import sys
from setuptools import setup

mainscript = 'App/main.py'
packages = ['pathlib', 'queue', 'threading', 'ttkbootstrap', 'tkinter']

if sys.platform == 'darwin':
    extra_options = dict(
        setup_requires=['py2app'],
        app=[mainscript],
        # Cross-platform applications generally expect sys.argv to
        # be used for opening files.
        # Don't use this with GUI toolkits, the argv
        # emulator causes problems and toolkits generally have
        # hooks for responding to file-open events.
        options=dict(py2app=dict(argv_emulation=False)),
        includes=packages,
        iconfile='App/Assets/icon.icns',
    )
elif sys.platform == 'win32':
    extra_options = dict(
        setup_requires=['py2exe'],
        app=[mainscript],
        includes=packages,
        iconfile='App/Assets/icon.ico',
    )
else:
    extra_options = dict(
        # Normally unix-like platforms will use "setup.py install"
        # and install the main script as such
        scripts=[mainscript],
        includes=packages,
        iconfile='App/Assets/icon.ico',
    )

setup(
    name="DJ Regulatory Track Checker",
    **extra_options
)
