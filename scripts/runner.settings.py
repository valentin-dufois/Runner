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


# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from _stubs import *

import copy

entries = [{
    'title': "OPOPENING",
    'type': "COMMAND",
    'package': "runner.runner",
    'executeMethod': "toggleOPOpenBehaviour"
}, {
    'title': "TOXFOLDER",
    'type': "COMMAND",
    'package': "runner.runner",
    'executeMethod': "setTOXFolder"
}, {
    'title': "PRESETSFOLDER",
    'type': "COMMAND",
    'package': "runner.runner",
    'executeMethod': "setPresetsFolder"
}, {
    'title': "SEARCHROOT",
    'type': "COMMAND",
    'package': "runner.runner",
    'executeMethod': "setSearchRoot"
}, {
    'title': "PLUGINSFOLDER",
    'type': "COMMAND",
    'package': "runner.runner",
    'executeMethod': "setPluginsFolder"
}, {
    'title': "DISPLAYHELP",
    'type': "COMMAND",
    'package': "runner.runner",
    'executeMethod': "toggleDisplayHelp"
}, {
    'title': "EXPOSERUNNER",
    'type': "COMMAND",
    'package': "runner.runner",
    'executeMethod': "toggleExposeRunner"
}]

def getEntries():
    rows = copy.deepcopy(entries)
    settings = iop.settings

    for row in rows:
        if row['title'] == 'TOXFOLDER':
            path = settings['toxfolder', 1].val
            if len(path) > 42:
                path = '...' + path[-39:]

            row['title'] = 'TOXs Folder [' + path + ']'
            row['help'] = 'Tell Runner a location on the computer containing TOXs to index.'
        elif row['title'] == 'OPOPENING':
            row['title'] = 'Open OPs in Place [' + ('Yes' if int(settings['openopinplace', 1].val) else 'No') + ']'
            row['help'] = 'Tell if Runner should open operators in the same pane or in a new one.'
        elif row['title'] == 'PRESETSFOLDER':
            path = settings['presetsfolder', 1].val
            if len(path) > 42:
                path = '...' + path[-39:]

            row['title'] = 'Presets Folder [' + path + ']'
            row['help'] = 'Tell Runner where the presets are stored on the computer.'
        elif row['title'] == 'SEARCHROOT':
            path = settings['searchroot', 1].val
            if len(path) > 42:
                path = '...' + path[-39:]

            row['title'] = 'Search root [' + path + ']'
            row['help'] = 'Tell Runner from which node to start indexing. Pressing [Enter] will update the search root to the current location.'
        elif row['title'] == 'PLUGINSFOLDER':
            path = settings['pluginsfolder', 1].val
            if len(path) > 42:
                path = '...' + path[-39:]

            row['title'] = 'Plugins folder [' + path + ']'
            row['help'] = 'Tell Runner where to look on the computer for plugins.'
        elif row['title'] == 'DISPLAYHELP':
            row['title'] = 'Display help captions [' + ('Yes' if int(settings['displayhelp', 1].val) == 1 else 'No') + ']'
            row['help'] = 'Specify if the help captions above the results should be shown.'
        elif row['title'] == 'EXPOSERUNNER':
            row['title'] = 'Hide Runner operator' if parent.runner.expose else 'Expose Runner operator'
            row['help'] = 'Hide or expose the Runner operator. This has no impact on the Runner behavior. ' \
                          'Hiding the runner helps prevent involuntarily interacting with its node while ' \
                          'working on something else.'

    return rows

def openSettings():
    parent.runner.OpenSublist(getEntries())
    return False


def setTOXFolder():
    location = ui.chooseFolder(title='Select Folder containing TOXs', start=None)

    if location is not None:
        iop.settings['toxfolder', 1] = location
        ui.status = 'Runner TOXs folder set to ' + location

    parent.runner.OpenSublist(getEntries())
    return False


def toggleOPOpenBehaviour():
    val = int(parent.runner.op('settings')['openopinplace', 1].val)
    iop.settings['openopinplace', 1] = 0 if val else 1

    parent.runner.OpenSublist(getEntries())
    return False


def setPresetsFolder():
    location = ui.chooseFolder(title='Select Folder Storing Presets', start=None)

    if location is not None:
        iop.settings['presetsfolder', 1] = location
        ui.status = 'Runner presets folder set to ' + location

    parent.runner.OpenSublist(getEntries())
    return False

def setSearchRoot():
    node = ui.panes.current.owner if ui.panes.current is not None else None

    if node is None:
        ui.status = "Runner : Could not update search root"
    else:
        iop.settings['searchroot', 1] = node.path
        ui.status = "Runner: Search root changed to " + node.path

    parent.runner.OpenSublist(getEntries())
    return False

def refreshOPsIndex():
    parent.runner.GetDB().UpdateProjectOPs(op('/'))

def setPluginsFolder():
    location = ui.chooseFolder(title='Select Folder Storing Runner Plugins', start=None)

    if location is not None:
        iop.settings['pluginsfolder', 1] = location
        ui.status = 'Runner plugins folder set to ' + location

    parent.runner.OpenSublist(getEntries())
    return False

def toggleDisplayHelp():
    iop.settings['displayhelp', 1] = 1 if int(iop.settings['displayhelp', 1].val) == 0 else 0
    parent.runner.OpenSublist(getEntries())
    return False

def toggleExposeRunner():
    parent.runner.expose = not parent.runner.expose
    parent.runner.OpenSublist(getEntries())
    return False
