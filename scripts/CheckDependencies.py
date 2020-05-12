#    Copyright 2020 Valentin Dufois
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import glob
import os
import sys
from pathlib import Path

# pyCharm trick
# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from _stubs import *


def download_url(url, save_path):
    import urllib.request
    import ssl
    with urllib.request.urlopen(url, context=ssl.SSLContext()) as dl_file:
        with open(save_path, 'wb') as out_file:
            out_file.write(dl_file.read())


pythonFolder = app.configFolder + '/Python'
whooshFolder = pythonFolder + '/whoosh'
tmpFolder = pythonFolder + '/dl'


def CheckDependencies():
    try:
        from whoosh.index import Index
        return
    except:
        ui.status = "Installing required python package for Runner"

    # Make sure our python folder is in the path
    if pythonFolder not in sys.path:
        sys.path.append(pythonFolder)

    # Check if we have already installed Whoosh
    if os.path.isdir(whooshFolder):
        # Whoosh fooder already exist, nothing to do
        return

    # We need to install Whoosh
    import zipfile
    import shutil

    # Create temporary folder
    Path(tmpFolder).mkdir(parents=True, exist_ok=True)

    # Download Whoosh repo
    download_url('https://bitbucket.org/mchaput/whoosh/get/default.zip', tmpFolder + '/whoosh.zip')

    # Extract Whoosh source files
    archive = zipfile.ZipFile(tmpFolder + '/whoosh.zip')
    for file in archive.namelist():
        if file[file.index('/'):].startswith('/src/'):
            archive.extract(file, tmpFolder)

    shutil.move(glob.glob(tmpFolder + '/*/src/whoosh')[0], pythonFolder)

    # Clean temp files
    shutil.rmtree(tmpFolder)

    ui.status = "Runner is ready to be used!"
    return
