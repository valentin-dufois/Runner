# pyCharm trick
# noinspection PyUnreachableCode
if False:
    # noinspection PyUnresolvedReferences
    from _stubs import *

from operator import attrgetter, itemgetter

from whoosh.qparser import QueryParser

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

        self.initDB()

        self.inlines = json.loads(op('inlines').text)
        return

    def initDB(self):
        self.index = self.storage.create_index(self.schema, 'main')  # Create the index

        # Index static elements (Built-in nodes, the palette, commands)
        writer = self.index.writer()
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
        paletteDir = app.samplesFolder + '/COMP/'
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

        # Commit all document added to the index
        writer.commit()

        # List all nodes in the project
        self.UpdateProjectOPs(op('/'))
        return

    def InitSublist(self, entries):
        self.subIndex = self.storage.create_index(self.schema, 'sub')

        writer = self.subIndex.writer()

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

        writer.commit()
        return

    def UpdateTOXIndex(self, entries):
        # First, remove all tox from the index
        writer = self.index.writer()
        writer.delete_by_term('type', 'TOX')

        # Now insert all the entries in the index
        for entry in entries:
            writer.add_document(title=entry[1].val,
                                type='TOX',
                                path=entry[0].val,
                                )
        writer.commit()

    def UpdatePresetsIndex(self, entries):
        # First, remove all tox from the index
        writer = self.index.writer()
        writer.delete_by_term('type', 'PRESET')

        # Now insert all the entries in the index
        for entry in entries:
            writer.add_document(title=entry[0].val[7:],
                                type='PRESET',
                                opName=entry[0].val[7:],
                                path=entry[1].val,
                                )
        writer.commit()

    def UpdateProjectOPs(self, parentOP):
        excludedPaths = ['/local/', self.runner.path]

        if parentOP.path.startswith(tuple(excludedPaths)) or 'runner-keepout' in parentOP.tags:
            return  # Ignore

        # First, remove all child op of the parent from the index
        writer = self.index.writer()
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
        writer.commit()

    def Search(self, userInput, callback):
        run('me.parent().ext.db._search(args[0], args[1])', userInput, callback, self, endFrame=True, fromOP=me)

    def _search(self, userInput, callback):
        self.lastSearch = userInput

        if len(userInput) == 0:
            callback([])
            return

        words = []
        for word in userInput.split():
            chars = []
            for char in word:
                chars.append(re.escape(char.lower()))
            words.append(r'(?ix)(' + r'.*?'.join(chars) + ')')

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
                return items

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

    def GetInput(self):
        return self.lastSearch

    def ClearInput(self):
        self.lastSearch = ''
