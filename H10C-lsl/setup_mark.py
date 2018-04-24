import os
import sys

if sys.platform == 'linux2':  # LINUX

    os.system('sudo apt-get install psychopy')
    os.system('sudo pip install --user scikit-learn')

elif sys.platform == 'win32':  # WINDOWS

    os.system('python -m pip install pypiwin32')
    os.system('python -m pip install --user psychopy scikit-learn')

elif sys.platform == 'darwin':  # MAC OSX

    os.system('pip install pyobjc-core pyobjc-framework-Quartz')
    os.system('sudo pip install psychopy scikit-learn')