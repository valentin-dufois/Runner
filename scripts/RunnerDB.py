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


# pyCharm trick
# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from _stubs import *

from operator import attrgetter, itemgetter

import os.path
import json
import glob

from whoosh.filedb.filestore import RamStorage
from whoosh.fields import *
from whoosh.analysis import NgramAnalyzer, LowercaseFilter, StandardAnalyzer, LanguageAnalyzer, SimpleAnalyzer
from whoosh import query, sorting


class RunnerDB:
    storage = RamStorage()

    schema = Schema(
        title=TEXT(stored=True, field_boost=10.0),  # Full letter label
        type=ID(stored=True),  # Type of entry
        opType=ID(stored=True, field_boost=5.0),  # Type of the op referenced
        opName=ID(stored=True),  # Name of the op/tox referenced
        opPars=KEYWORD(commas=True),  # Parameters of the op referenced (for built-ins)
        opTags=KEYWORD(commas=True),  # Parameters of the op referenced (for built-ins)
        help=TEXT(stored=True, analyzer=SimpleAnalyzer()),  # Help caption to display on the runner
        path=ID(stored=True),  # Path to an OP or a file
        package=STORED,  #
        conditionalMethod=STORED,  # Name of a method telling if the entry should be shown or not
        executeMethod=STORED  # Method execute when user press enter or click on it
    )

    index = None
    subIndex = None

    lastSearch: str = ''

    def __init__(self, indexBase):
        self.runner = indexBase.parent.runner

        self.inlines = json.loads(op('inlines').text)
        self.plugins = op('../plugins')

        self.initDB()
        return

    def initDB(self):
        self.index = self.storage.create_index(self.schema, 'main')  # Create the index

        # Index static elements (Built-in nodes, the palette, commands)
        with self.index.writer() as writer:
            parametersRef = json.loads(op('/ui/dialogs/parGrabber/offlineHelp').text)['help']
            # Built-in nodes (& custom)
            for family in ['COMP', 'TOP', 'CHOP', 'SOP', 'MAT', 'DAT']:
                for node in families[family]:
                    opPars = []
                    opHelp = None

                    # Check if the node is present in the reference
                    if node.OPType in parametersRef[family + 's']:
                        opHelp = parametersRef[family + 's'][node.OPType].get('summary')
                        for par, val in parametersRef[family + 's'][node.OPType]['parameters'].items():
                            if val['label'] is not None:
                                opPars.append(val['label'].lower())

                    # Add the node to the index
                    writer.add_document(title=node.label,
                                        type=family,
                                        opType=node.OPType,
                                        opPars=opPars,
                                        help=opHelp,
                                        )

            # Palette nodes
            paletteDir = app.samplesFolder + '/Palette/'
            palette = glob.glob(paletteDir + '**/*.tox', recursive=True)
            for node in palette:
                writer.add_document(title=node[len(paletteDir):-4],
                                    type='PALETTE',
                                    opName=os.path.basename(node)[0:-4],
                                    path=node,
                                    )

            # Register commands
            commands = json.loads(op('commands').text)
            for packageName in commands:
                package = commands[packageName]
                for command in package:
                    writer.add_document(title=command['label'],
                                        type='COMMAND',
                                        help=command.get('help'),
                                        package=packageName,
                                        conditionalMethod=command['conditionalMethod'],
                                        executeMethod=command['executeMethod']
                                        )

        # List all nodes in the project
        self.UpdateProjectOPs(op(iop.settings['searchroot', 1].val))
        self.UpdatePlugins(op('pluginsFolder').rows()[1:])
        self.UpdateUserPaletteIndex(op('userPaletteFolder').rows()[1:])
        self.UpdateTOXIndex(op('toxFolder').rows()[1:])
        self.UpdatePresetsIndex(op('presetsFolder').rows()[1:])
        return

    def InitSublist(self, entries):
        self.subIndex = self.storage.create_index(self.schema, 'sub')

        with self.subIndex.writer() as writer:
            for entry in entries:
                writer.add_document(
                    title=entry.get("title"),
                    type=entry.get("type"),
                    opType=entry.get("opType"),
                    opName=entry.get("opName"),
                    opPars=entry.get("opPars"),
                    opTags=entry.get("opTags"),
                    help=entry.get("help"),
                    path=entry.get("path"),
                    package=entry.get("package"),
                    conditionalMethod=entry.get("conditionalMethod"),
                    executeMethod=entry.get("executeMethod"),
                )

    def UpdateUserPaletteIndex(self, entries):
        # First, remove all tox from the index
        with self.index.writer() as writer:
            delQuery = query.And([query.Term("type", "PALETTE"),
                                  query.Regex("path", app.userPaletteFolder + '/*')])
            writer.delete_by_query(delQuery)

            # Now insert all the entries in the index
            prefixLen = len(app.userPaletteFolder)
            for entry in entries:
                writer.add_document(title='My Components/' + entry[2].val[prefixLen:],
                                    type='PALETTE',
                                    opName=entry[0].val,
                                    path=entry[1].val,
                                    )

    def UpdateTOXIndex(self, entries):
        # First, remove all tox from the index
        with self.index.writer() as writer:
            writer.delete_by_term('type', 'TOX')

            # Now insert all the entries in the index
            for entry in entries:
                writer.add_document(title=entry[1].val,
                                    type='TOX',
                                    opName=entry[1].val,
                                    path=entry[0].val,
                                    )

    def UpdatePresetsIndex(self, entries):
        # First, remove all tox from the index
        with self.index.writer() as writer:
            writer.delete_by_term('type', 'PRESET')

            # Now insert all the entries in the index
            for entry in entries:
                writer.add_document(title=entry[0].val[7:],
                                    type='PRESET',
                                    opName=entry[0].val[7:],
                                    path=entry[1].val,
                                    )

    def UpdatePlugins(self, entries):
        # First, Import new plugins and remove old ones
        installedNames = [p.op('plugin')['name', 1].val for p in self.plugins.children]

        for pluginPath in entries:
            plugin = self.runner.GetDummyNetwork().loadTox(pluginPath[0].val, unwired=False, pattern=None)

            if plugin.op('plugin') is None:
                # This is not a valid plugin, ignore it
                plugin.destroy()
                continue

            pluginName = plugin.op('plugin')['name', 1].val
            pluginVersion = plugin.op('plugin')['version', 1].val

            # Is the plugin already installed
            if pluginName in installedNames:
                # Check if just-loaded plugin has a greater version than the currently installde
                plugin.destroy()
                installedNames.remove(pluginName)
                continue

            # This is a new plugin, install it
            self.plugins.copy(plugin, name=pluginName)

            # Clean up
            plugin.destroy()

        # Remaining plugins in the list can be removed
        # for pluginInfos in pluginsInfos:
        #     print(pluginInfos[0] + '_' + pluginInfos[1].replace('.', '_'))
        #     self.runner.GetDummyNetwork().op(pluginInfos[0] + '_' + pluginInfos[1].replace('.', '_')).destroy()

        # Finally, update the index
        self.UpdatePluginsIndex()

    def UpdatePluginsIndex(self):
        with self.index.writer() as writer:
            writer.delete_by_query(query.And([query.Term("type", "COMMAND"), query.Not(query.Wildcard('package', 'runner.*'))]))
            pluginsNodes = op('../plugins').findChildren(type=COMP)

            for plugin in pluginsNodes:
                pluginName = plugin.name
                commands = json.loads(plugin.op('commands').text)
                for packageName in commands:
                    package = commands[packageName]
                    for command in package:
                        writer.add_document(title=command['label'],
                                            type='COMMAND',
                                            help=command.get('help'),
                                            package=pluginName + '.' + packageName,
                                            conditionalMethod=command['conditionalMethod'],
                                            executeMethod=command['executeMethod']
                                            )

    def UpdateProjectOPs(self, parentOP):
        if parentOP is None:
            return

        excludedPaths = ['/local/', self.runner.path]

        if parentOP.path.startswith(tuple(excludedPaths)) or 'runner-keepout' in parentOP.tags:
            return  # Ignore

        # First, remove all child op of the parent from the index
        with self.index.writer() as writer:
            path = re.escape(parentOP.path) + '.+'

            delQuery = query.And([query.Term("type", "OP"),
                                  query.Regex("path", path)
                                  ])
            writer.delete_by_query(delQuery)

            # Now get all the current child of the op
            nodes = parentOP.findChildren()
            for node in nodes:
                if node.path.startswith(tuple(excludedPaths)):
                    continue

                if 'runner-ignore' in node.tags:
                    excludedPaths.append(node.path)
                    continue

                if 'runner-keepout' in node.tags:
                    excludedPaths.append(node.path)

                writer.add_document(title=node.path,
                                    type='OP',
                                    opType=node.OPType,
                                    opName=node.name,
                                    opTags=list(node.tags),
                                    path=node.path,
                                    help=node.comment,
                                    )

    def Search(self, userInput, callback):
        run('me.parent().ext.db._search(args[0], args[1])', userInput, callback, self, endFrame=True, fromOP=me)

    def _search(self, userInput, callback):
        self.lastSearch = userInput

        if len(userInput) == 0 and not self.runner.IsUsingSublist():
            callback([])
            return

        words = []
        for word in userInput.split():
            chars = []
            for char in word:
                chars.append(re.escape(char.lower()))
            words.append(r'(?ix)(' + r'.*?'.join(chars) + ')')

        if len(userInput) == 0 and self.runner.IsUsingSublist():
            q = query.Every('title')
        else:
            q = query.Or([query.And([query.Regex("title", w) for w in words]),
                          query.Regex("opType", words[0]),
                          query.Regex("opName", words[0]),
                          query.Regex("opPars", r"\ ".join(words)),
                          query.And([query.Regex("opTags", w) for w in words]),
                          query.And([query.Regex("help", w) for w in words])
                          ])

        # get the correct index
        index = self.subIndex if self.runner.IsUsingSublist() else self.index
        with index.searcher() as crawler:
            results = crawler.search(q, limit=12, terms=True)
            items = []

            compregex = re.compile(r'<b.*?>(.*?)</b>', re.S)

            for rawHit in results:
                hit = dict(rawHit.items())

                # Check if command should be shown
                if hit["type"] == "COMMAND" and "conditionalMethod" in hit:
                    check = self.runner.RowConditionIsValid(hit['package'], hit['conditionalMethod'])

                    if check is not True:
                        continue  # Do not show command

                if "opType" in rawHit.keys():
                    match = compregex.match(rawHit.highlights("opType"))
                    hit['opTypeHitLen'] = len(match.groups()[0].strip()) if match else 99999
                else:
                    hit['opTypeHitLen'] = 99999

                match = compregex.match(rawHit.highlights("title"))
                hit['titleHitLen'] = len(match.groups()[0].strip()) if match else 99999

                items.append(hit)

            # Sort items
            items = sorted(items, key=itemgetter('opTypeHitLen'))
            items = sorted(items, key=itemgetter('titleHitLen'))

            # Stop here if we are in the sublist
            if self.runner.IsUsingSublist():
                callback(items)
                return

            # Check inlines
            for package in self.inlines:
                for inline in self.inlines[package]:
                    res = self.runner.ComputeInline(package, inline["method"], userInput)
                    if res is not False:
                        items.insert(0, {
                            "title": res,
                            "type": "INLINE",
                        })

        callback(items)

    def GetLastInput(self):
        return self.lastSearch

    def ClearInput(self):
        self.lastSearch = ''
