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

class RunnerField:
    def __init__(self, ownerComp):
        # The component to which this extension is attached
        self.field = ownerComp
        self.innerField = op('stringField0/field')
        self.text = self.innerField.op('text')

        self.hint = self.innerField.op('hint')

        self.inputText = ''

        self.list = parent.runner.op('UI/list')

    def Focus(self):
        self.field.setFocus()
        if len(self.GetInput()) > 0:
            self.innerField.setKeyboardFocus(selectAll=True)
        else:
            self.innerField.setKeyboardFocus(selectAll=False)

        self.field.click(.5, .5)

    def Blur(self):
        self.innerField.interactClear()

    def onInputUpdate(self, input):
        self.inputText = input

        self.field.par.Value0 = input
        self.setHintText('')
        self.refreshHintOffset()

    def refreshHintOffset(self):
        self.hint.par.position1 = self.text.textWidth

    def setHintText(self, content):
        self.hint.par.text = content

    def GetInput(self):
        return self.innerField.panel.fieldediting.val

    def Clear(self):
        self.field.par.Value0 = ''
        self.innerField.panel.fieldediting.val = ''
        self.innerField.panel.field.val = ''

        self.innerField.cook(force=True)
        self.field.cook(force=True)
