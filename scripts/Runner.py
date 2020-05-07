"""
The Runner is a ultrafast fuzzy finder built for TouchDesigner.
"""

# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from _stubs import *

from typing import List, Dict

class Runner:
    builtinType = ['COMP', 'TOP', 'CHOP', 'SOP', 'MAT', 'DAT']
    usingSublist = False

    def __init__(self, ownerComp):

        # The component to which this extension is attached
        self.runner = ownerComp

        # Internal
        self.db = op('db')
        self.dummyNetwork = op('dummyNetwork')

        # UI
        self.window = op('runnerWindow')
        self.field = op('UI/field')
        self.list = op('UI/list')

        # Check Dependencies
        mod('dependenciesChecker').CheckDependencies()

        return

    def GetDB(self):
        return self.db

    def GetDummyNetwork(self) -> COMP:
        return self.dummyNetwork

    def GetInput(self) -> str:
        return self.db.GetInput()

    # Sublist
    def useDefaultIndex(self):
        if self.usingSublist:
            self.list.Clear()
        self.usingSublist = False

    def useSublist(self):
        if not self.usingSublist:
            self.clearInput()

        self.usingSublist = True

    def IsUsingSublist(self):
        return self.usingSublist

    def clearInput(self):
        run("op('UI/field').par.Value0 = ''", delayFrames=1, fromOP=me)
        self.field.op('stringField0/field').panel.fieldediting.val = ''
        self.field.op('stringField0/field').panel.field.val = ''

    def SetFocus(self):
        self.window.setForeground()
        self.field.op('stringField0/field').setKeyboardFocus(selectAll=True)
        return

    def displayRunner(self):
        # Reset runner properly
        for node in self.dummyNetwork.children:
            node.destroy()

        if self.window.isOpen:
            run('parent.runner.SetFocus()', delayFrames=2, fromOP=me)
            return

        if not self.IsUsingSublist():
            self.list.Refresh()

        # Enable the panel
        self.runner.par.enable = True

        # Open window and give focus
        self.window.par.winopen.pulse()
        self.runner.interactClear()
        self.field.setFocus()
        run('parent.runner.SetFocus()', delayFrames=2, fromOP=me)
        return

    def Open(self):
        # Default open: display the database
        self.useDefaultIndex()
        self.displayRunner()
        return

    def OpenSublist(self, entries: List[Dict]):
        self.db.InitSublist(entries)

        self.useSublist()
        self.list.DisplayResults(entries)

        self.displayRunner()
        return

    def Close(self):
        self.window.par.winclose.pulse()
        self.runner.par.enable = False

        self.field.interactClear()
        return

    def RowConditionIsValid(self, package, method):
        if package[0:6] == 'runner':
            package = package.split('.')[1]
            return getattr(mod('scripts/' + package), method)()

        # TODO: Implement plugins logic
        return

    def ComputeInline(self, package, method, userInput):
        if package[0:6] == 'runner':
            package = package.split('.')[1]
            return getattr(mod('scripts/' + package), method)(userInput)

        # TODO: Implement plugins logic
        return

    def Execute(self, data):

        if data['type'] in self.builtinType:
            self.placeNewOP(data['opType'])
        elif data['type'] == 'OP':
            self.goToOP(data['path'])
        elif data['type'] == 'TOX':
            self.placeNewFromTOX(data['path'])
        elif data['type'] == 'PALETTE':
            self.placeNewFromPalette(data['path'], data['opName'])
        elif data['type'] == 'PRESET':
            self.applyPreset(data['path'], data['opName'])
        elif data['type'] == 'COMMAND':
            self.executeCommand(data['package'], data['executeMethod'])
        else:
            ui.status = "Runner: Unrecognized type of action: " + data['type']

    def placeNewOP(self, opType):
        if ui.panes.current.type != PaneType.NETWORKEDITOR:
            # We are not in a network editor, just create the node
            ui.panes.current.create(opType)
            self.Close()
            return

        # Create the node out of sight and let the user place it
        node = self.dummyNetwork.create(opType)
        self.Close()

        ui.panes.current.placeOPs([node])
        return

    def goToOP(self, path):
        node = op(path)
        target = node.parent()

        self.Close()

        if not int(iop.settings['openopinplace', 1].val):
            # Open op in floating pane
            p = ui.panes.createFloating(
                type=PaneType.NETWORKEDITOR,
                name=target.path,
                maxWidth=1920,
                maxHeight=1080,
                monitorSpanWidth=0.7,
                monitorSpanHeight=0.7
            )
            p.owner = target
            p.showParameters = True
            node.current = True
            p.home(zoom=5, op=node)
            return

        if ui.panes.current is None:
            ui.status = "Runner could not found the current panel..."
            return

        ui.panes.current.owner = target
        ui.panes.current.home(zoom=5, op=node)
        node.current = True
        return

    def placeNewFromTOX(self, path):
        if ui.panes.current.type != PaneType.NETWORKEDITOR:
            # We are not in a network editor, just create the node
            ui.panes.current.loadTox(path, unwired=False, pattern=None)
            self.Close()
            return

        # Create the node out of sight and let the user place it
        tox = self.dummyNetwork.loadTox(path, unwired=False, pattern=None)
        self.Close()
        ui.panes.current.placeOPs([tox])
        return

    def placeNewFromPalette(self, path, name):
        # Load the tox
        tox = ui.panes.current.owner.loadTox(path, unwired=False, pattern=name)
        tox.tags.add('runner-keepout')
        self.Close()

        if ui.panes.current.type == PaneType.NETWORKEDITOR:
            tox.nodeX = ui.panes.current.x
            tox.nodeY = ui.panes.current.y

        return

    def applyPreset(self, path, nodeName):
        # Create the node from the tox out of sight
        node = self.dummyNetwork.loadTox(path, unwired=False, pattern=nodeName)
        self.Close()

        if len(ui.panes.current.owner.children) == 0 or ui.panes.current.owner.currentChild.OPType != node.OPType:
            # The user has not selected a node of the same type, we let it place the node
            ui.panes.current.placeOPs([node])
            return

        # The user has selected a node of the same type, we udpate the selected node parameters
        ui.panes.current.owner.currentChild.copyParameters(node, custom=True, builtin=True)
        # And we erase the source node
        node.destroy()
        return

    def executeCommand(self, package, method):
        if package[0:6] == 'runner':
            path = 'scripts/' + package.split('.')[1]
        else:
            # Implement plugins logic
            path = ''
            pass

        # Execute command
        shouldClose = getattr(mod(path), method)()

        # Should we close the runner ?
        if shouldClose is None or shouldClose:
            self.Close()

        return
