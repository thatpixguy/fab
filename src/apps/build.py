#!/usr/bin/env python
"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup
import shutil
import os
import stat

# Trick to make this run properly
import sys
sys.argv += ['py2app']

# This is the pythons script that we're bundling into an application.
shutil.copy('../guis/cad_ui','cad_ui.py')

APP = ['cad_ui.py']
DATA_FILES = ['../py/cad_shapes.py',
              '../py/cad_text.py',
              '../py/math_string.py',
              '../../bin/cad_math',
              '../../bin/math_png',
              '../../bin/math_stl',
              '../../bin/math_svg',
              '../../bin/math_dot',
              'cba_icon.png']
OPTIONS = {'argv_emulation': True,
           'iconfile':'cba.icns'}

# Run py2app to bundle everything.
setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

shutil.rmtree('build')
os.remove('cad_ui.py')

# Copy the boost threads library.
shutil.copy('/usr/local/lib/libboost_thread-mt.dylib', 
            'dist/cad_ui.app/Contents/Frameworks/libboost_thread-mt.dylib')

# Change math_png linking so that it links against the local copy of
# boost threads
os.system('install_name_tool -change ' +
          '"/usr/local/lib/libboost_thread-mt.dylib" ' +
          '"@executable_path/../Frameworks/libboost_thread-mt.dylib" ' +
          'dist/cad_ui.app/Contents/Resources/math_png')
os.system('install_name_tool -change ' +
          '"/usr/local/lib/libboost_thread-mt.dylib" ' +
          '"@executable_path/../Frameworks/libboost_thread-mt.dylib" ' +
          'dist/cad_ui.app/Contents/Resources/math_stl')
os.system('install_name_tool -change ' +
          '"/usr/local/lib/libboost_thread-mt.dylib" ' +
          '"@executable_path/../Frameworks/libboost_thread-mt.dylib" ' +
          'dist/cad_ui.app/Contents/Resources/math_svg')

# Make math_png executable
executable = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | \
             stat.S_IRUSR | stat.S_IWUSR
os.chmod('dist/cad_ui.app/Contents/Resources/math_png', executable)
os.chmod('dist/cad_ui.app/Contents/Resources/math_svg', executable)
os.chmod('dist/cad_ui.app/Contents/Resources/math_stl', executable)
os.chmod('dist/cad_ui.app/Contents/Resources/math_dot', executable)

# Copy the readme folder into the distribution directory
shutil.copy('README','dist')

os.system('cd dist; zip -r cad_ui.zip cad_ui.app README')