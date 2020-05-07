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
        elif row['title'] == 'OPOPENING':
            row['title'] = 'Open OPs in Place [' + ('Yes' if int(settings['openopinplace', 1].val) else 'No') + ']'
        elif row['title'] == 'PRESETSFOLDER':
            path = settings['presetsfolder', 1].val
            if len(path) > 42:
                path = '...' + path[-39:]

            row['title'] = 'Presets Folder [' + path + ']'

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

def refreshOPsIndex():
    parent.runner.GetDB().UpdateProjectOPs(op('/'))
