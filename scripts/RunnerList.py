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


"""
The RunnerList handles the display of results and interactions with it
"""

# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from _stubs import *

import json
from typing import List, Dict


class RunnerList:
    selection: int = 0
    colors = json.loads(op('colors').text)
    builtinType = ['COMP', 'TOP', 'CHOP', 'SOP', 'MAT', 'DAT']

    def __init__(self, ownerComp):
        # The component to which this extension is attached
        self.list = ownerComp
        self.db = parent.runner.GetDB()
        self.results = []
        self.field = parent.runner.op('UI/field')
        self.helpTOP = parent.runner.op('UI/help/helptext')

        return

    def setListHeight(self, h):
        self.list.par.h = h

    def Clear(self):
        self.setListHeight(0)
        self.list.par.rows = 0
        self.results = []
        self.helpTOP.par.text = ''
        self.db.ClearInput()
        self.field.ext.RunnerField.setHintText('')

    def Refresh(self):
        self.OnInputUpdate(self.field.GetInput())

    def OnInputUpdate(self, userInput: str):
        if not parent.runner.IsUsingSublist() and len(userInput) < 3:
            self.Clear()
            return

        # Request results from the db and display them
        self.db.Search(userInput, self.DisplayResults)
        self.ResetSelection()

    def DisplayResults(self, results: List[Dict]):
        self.results = results

        # Adjust the number of rows in the list
        resultCount = len(self.results)
        self.list.par.rows = resultCount
        self.list.par.cols = 2

        sizeAcc = 0

        # Fill in the rows
        for i in range(resultCount):
            data = self.results[i]
            type = data['type']

            row = self.list.rowAttribs[i]
            label = self.list.cellAttribs[i, 0]
            tooltip = self.list.cellAttribs[i, 1]

            # Stylize the row
            row.rowHeight = 50
            if i != 0:
                row.topBorderOutColor = (.2, .2, .2, 1)

            label.colStretch = True
            label.fontSizeX = 22
            label.textJustify = JustifyType.CENTERLEFT
            label.textOffsetX = 10.0

            tooltip.colStretch = False
            tooltip.colWidth = 0 if parent.runner.IsUsingSublist() else 100
            tooltip.fontSizeX = 18
            tooltip.textJustify = JustifyType.CENTERRIGHT
            tooltip.textOffsetX = -10.0

            # Set the row colors
            colors = self.colors[type] if type in self.colors else self.colors['DEFAULT']
            if i == self.selection:
                row.bgColor = tuple(colors['focusbg'])
                row.textColor = tuple(colors['focusfont'])
                self.helpTOP.par.text = data.get('help')
            else:
                row.bgColor = tuple(colors['idlebg'])
                row.textColor = tuple(colors['idlefont'])

            # Format and set the labels
            label.text = data['title']
            tooltip.text = type

            # Do adjustement based on type
            if type == 'OP':
                label.text += ' [' + data['opType'] + ']'

            if (type == 'OP' or type == 'TOX' or
                type == 'PALETTE' or type == 'PRESET'):
                if len(label.text) > 49:
                    label.text = '...' + label.text[-46:]

            if type == 'COMMAND':
                tooltip.text = ''

                if len(data['package']) > 0 and not data['package'].startswith('runner'):
                    tooltip.text = parent.runner.op('plugins/' + data['package'].split('.')[0] + '/plugin')['name', 1].val.upper()

                if len(label.text) > 57:
                    label.text = label.text[:54] + '...'

            if type == 'INLINE':
                textLen = len(label.text)
                if textLen > 50:
                    tooltip.textJustify = JustifyType.CENTERLEFT
                    tooltip.textOffsetX = 15.0
                else:
                    tooltip.textOffsetX = -15.0
                row.editable = True

                tooltip.text = label.text
                tooltip.colStretch = True
                tooltip.fontSizeX = 25
                tooltip.textOffsetY = 0.0
                tooltip.wordWrap = False

                label.text = ''
                label.colStretch = False
                label.colWidth = 0

            if type in self.builtinType:
                if len(label.text) > 49:
                    label.text = label.text[:46] + '...'

            sizeAcc += row.rowHeight

        self.setListHeight(min(sizeAcc, 300))
        return

    def ResetSelection(self):
        self.SelectRow(0)

    def getNumberOfRows(self):
        return len(self.results)

    # Update the list cells based on the new selection
    def SelectRow(self, newRow):
        # Get the results list
        resultLen = len(self.results)
        if resultLen == 0:
            self.list.scroll(0, 0)
            self.helpTOP.par.text = ''
            return

        prevRowIndice = self.selection

        if prevRowIndice < resultLen:
            # Reset previously hovered row color
            prevRow = self.list.rowAttribs[prevRowIndice]
            prevType = self.results[prevRowIndice]['type']
            colors = self.colors[prevType] if prevType in self.colors else self.colors['DEFAULT']
            if prevRow is not None:
                prevRow.bgColor = tuple(colors['idlebg'])
                prevRow.textColor = tuple(colors['idlefont'])

        # Set currently hovered row color
        row = self.list.rowAttribs[newRow]
        rowType = self.results[newRow]['type']
        self.helpTOP.par.text = self.results[newRow].get('help')
        colors = self.colors[rowType] if rowType in self.colors else self.colors['DEFAULT']
        row.bgColor = tuple(colors['focusbg'])
        row.textColor = tuple(colors['focusfont'])

        if rowType != 'INLINE':
            if rowType in self.builtinType:
                hint = self.results[newRow]['opType']
            elif rowType == 'TOX' or rowType == 'PALETTE' or rowType == 'OP':
                hint = self.results[newRow]['opName']
            else:
                hint = self.results[newRow]['title']

            self.field.ext.RunnerField.setHintText(hint)

        self.selection = newRow

        if newRow == 0:
            self.list.scroll(0, 0)

        return

    def SelectNext(self):
        # Check overflow
        if self.selection < self.getNumberOfRows() - 1:
            prevRow = self.selection
            self.SelectRow(self.selection + 1)

            if self.selection >= 5 and self.selection > prevRow:
                self.list.scroll(self.selection - 5, 0)

        return

    def SelectPrev(self):
        # Check overflow
        if self.selection > 0:
            self.SelectRow(self.selection - 1)

        return

    def ExecuteSelected(self):
        try:
            parent.runner.Execute(self.results[self.selection])
        except IndexError:
            return

        return
