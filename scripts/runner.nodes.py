# pyCharm trick
# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from _stubs import *

import math
import copy

def selectedOPIsCOMP():
    return ui.panes.current.owner.currentChild.isCOMP


def selectionIsMultiple():
    return len(ui.panes.current.owner.selectedChildren) >= 1


def openCustomizeDialog():
    ui.openCOMPEditor(ui.panes.current.owner.selectedChildren[0])
    return

def selectedOPsAreTOP():
    if ui.panes.current is None:
        return False

    if ui.panes.current.owner.currentChild.family != 'TOP':
        return False

    for node in ui.panes.current.owner.selectedChildren:
        if node.family != 'TOP':
            return False

    return True

def alignOPsHorizontally():
    ops = ui.panes.current.owner.selectedChildren

    acc = 0

    for node in ops:
        acc += node.nodeY

    posY = math.floor(acc / len(ops))

    for node in ops:
        node.nodeY = posY

    return


def alignOPsVertically():
    ops = ui.panes.current.owner.selectedChildren

    acc = 0

    for node in ops:
        acc += node.nodeX

    posX = math.floor(acc / len(ops))

    for node in ops:
        node.nodeX = posX

    return


def getNodePosX(node):
    return node.nodeX

def getNodePosY(node):
    return node.nodeY

def distributeOPsHorizontally():
    ops = ui.panes.current.owner.selectedChildren
    ops.append(ui.panes.current.owner.currentChild)

    ops.sort(key=getNodePosX)

    minX = ops[0].nodeX
    maxX = ops[-1].nodeX

    step = (maxX - minX) / (len(ops) - 1)

    # Adjust node positions, keep first and last in place
    for i in range(1, len(ops) - 1):
        ops[i].nodeX = minX + step * i;

    return


def distributeOPsVertically():
    ops = ui.panes.current.owner.selectedChildren
    ops.append(ui.panes.current.owner.currentChild)

    ops.sort(key=getNodePosY)

    minY = ops[0].nodeY
    maxY = ops[-1].nodeY

    step = (maxY - minY) / (len(ops) - 1)

    # Adjust node positions, keep first and last in place
    for i in range(1, len(ops) - 1):
        ops[i].nodeY = minY + step * i

    return


saveAsTOXEntries = [{
    'title': "TOXFOLDER",
    'type': "COMMAND",
    'package': "runner.nodes",
    'executeMethod': "saveTOXInDefaultFolder"
}, {
    'title': "Alongside Project",
    'type': "COMMAND",
    'package': "runner.nodes",
    'executeMethod': "saveTOXAlongsideProject"
}, {
    'title': "Other Location",
    'type': "COMMAND",
    'package': "runner.nodes",
    'executeMethod': "saveTOXInCustomLocation"
}]

def getSaveAsTOXEntries():
    rows = copy.deepcopy(saveAsTOXEntries)
    settings = iop.settings

    for row in rows:
        if row['title'] == 'TOXFOLDER':
            path = settings['toxfolder', 1].val
            if len(path) >= 56:
                path = '...' + path[-52:] + '/'

            row['title'] = path

    return rows

def openSaveAsTOXOptions():
    parent.runner.OpenSublist(getSaveAsTOXEntries())
    return False


def saveTOXInDefaultFolder():
    node = ui.panes.current.owner.currentChild
    node.save(iop.settings['toxfolder', 1].val + '/' + node.name + '.tox')


def saveTOXAlongsideProject():
    ui.panes.current.owner.currentChild.save()


def saveTOXInCustomLocation():
    node = ui.panes.current.owner.currentChild
    location = ui.chooseFile(load=False, start=node.name + '.tox', fileTypes=['tox'],
                             title='Save ' + node.name + ' as TOX', asExpression=False)

    if location is None:
        # user cancelled
        return

    # Append extension if missing
    if location[-4:].lower() != '.tox':
        location += '.tox'

    node.save(location)


def savePreset():
    # Get the selected node in a base in the dummy network
    dummyNetwork = parent.runner.GetDummyNetwork()
    base = dummyNetwork.create(baseCOMP, 'preset')
    node = base.copy(ui.panes.current.owner.currentChild)
    base.name = node.name

    filepath = iop.settings['presetsfolder', 1].val

    if len(filepath) == 0:
        ui.messageBox("Runner could not execute command", "Please define a preset folder.", buttons=['Ok'])
        return

    # Save the preset
    filename = 'preset_' + base.name + '.tox'
    base.save(filepath + '/' + filename)


def setTOPSmoothnessToNearest():
    ui.panes.current.owner.currentChild.par.inputfiltertype.val = 0
    ui.panes.current.owner.currentChild.par.filtertype.val = 0

    for node in ui.panes.current.owner.selectedChildren:
        node.par.inputfiltertype.val = 0
        node.par.filtertype.val = 0

def setTOPSmoothnessToInterpolate():
    ui.panes.current.owner.currentChild.par.inputfiltertype.val = 1
    ui.panes.current.owner.currentChild.par.filtertype.val = 1

    for node in ui.panes.current.owner.selectedChildren:
        node.par.inputfiltertype.val = 1
        node.par.filtertype.val = 1
