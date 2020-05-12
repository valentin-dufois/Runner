# Runner

![Supported plateform](https://img.shields.io/badge/plateform-macOS%20%7C%20Windows-lightgrey?style=flat-square)
[![Latest Release](https://img.shields.io/github/v/release/Boisier/Runner?include_prereleases&style=flat-square)](https://github.com/valentin-dufois/Runner/releases)

![This is Runner](assets/this-is-runner-small.gif?raw=true "This is Runner")

Runner is a fast, efficient, fuzzy-finder for TouchDesigner on MacOS and Windows.
Runner provides a unique search field for finding anything in TD ranging from built-in operators to TOX inside a folder on the computer.
Runner support third-party-plugins to extend its capacities. 
Runner is build entirely in Python inside TouchDesigner using a unique external python module.

Runner is used with a unique keyboard shortcut working accross the entire project. By default, the shortcut is `\`` and can be changed in the Runner parameters (top left key, just below escape on US Keyboards).

**Warning**
Runner needs to download 1MB of additional data upon first use on a computer to work. 
Updating TouchDesigner may also require Runner to get its additional content again
 
## Built-in Functionnalities

Runner has a lot of built-in functionnalities provinding access to multiple types of elements

Runner is not case-sensitive and provide relevant results even if their is typos (missing letters) in your search.
 
### Built-In Operators
All built-in operators can be found in the runner both by their display name `Movie File In` and their type `moviefileinTOP`.

### Palette
All palette built-in operators are referenced in the finder and can be found by their name `Probe` or path in the palette `Tools/Probe`.

### TOXs
It is possible to specify a folder in which Runner will reference all available TOXs. You can set the folder location in `Runner Settings`. All TOXs in the specified folder and its sub-folder will be referenced.
All TOXs can be found using their name `myTOX` or their path in the folder `category1/myTOX`.

### Project OPs
Runner references all the operators in the current project. They can be found by their name `wave1`, their path in the project `/project1/wave1` or their tags.

Runner also uses tags to adjust its search behaviours:
* `runner-ignore` Tell Runner to ignore this node and its child operator (if applicable)
* `runner-keepout` Tell Runner to ignore the child operators of this node (if applicable) but not the node itself. Operators from the palette placed using Runner are automatically given this tag to hide their inner network. This is useful to prevent cluttering in the results.

### Presets
Runner integrates an efficient presets system that can be used to save-and-recall nodes with their specific parameters. For presets to work, you need to specify where to store the presets inside the `Runner Settings`.

To save a preset for a node: Select the node and search for `Save Preset`. This will save the preset in the specified location with the name of node. The preset can then be found by searching the name of the preset. If you have a Node of the same type selected, the preset parameters will directly be applied to it.

Presets are stored inside basic TOX component and can therethore be shared or used elsewhere very easily.

### Inlines
Runner provides simple utilities to facilitate everyday work. 

#### Equations
Runner can solve basic equations directly in its search field and display the result

#### Python
Runner can execute Python expressions directly in its search field and display the return result.

For runner to try to execute the given expression, it needs to be preceded by a `>`.

`> me.par.name` Will display the name of the current pane path
`> me.findChildren(type=baseCOMP)` Will list all the comp in the current network

### Commands
Runner can execute different commands:

* Layout commands: `Align Operators`, `Distribute Operators`
* Operators: `Set Smoothness` on TOPs, `Customize` on COMPs
* Dialogs: `Open Beat Window`, `Open MIDI Mapper`
* Saves: `Save as TOX` on COMPs, `Save Preset`
* Runner: `Settings`

Feel free to open an issue to request a new command.

## Plugins

Runner support integrating plugins made by third-parties. Plugin add functionnalities to the runner and are easy to use.
All you need to add a plugin is to define a plugins folder in the runner settings and place plugins TOX in it. Runner will then include them automatically.

### Creating a plugin

Plugins are very easy to make. They are shared as TOX files.

They require only the following things:

- Plugins must be contained in a Base COMP;
- Plugins must have a Table TOP named `plugin` with one row per property, with the property name in the first column, and its value in the second. Required properties are:
    * `name` Name of the plugin, should be a TD compatible name;
    * `version` The version of the plugin, eg. `1.0.0`;
    * `author` Author of the plugin, unused for now;
- Plugins must have a Text DAT names `commands` containing the list of the plugin commands in JSON in the following format:
```json
{
  "<name of the Text DAT containing the methods>": [{
	"label": "<Text displayed in the runner results>",
	"conditionalMethod": "<A method name telling the Runner if the row should be shown or none (returning True or False), or null if the row should always be shown>",
	"executeMethod": "<Name of the method to call when the user press execute this result>",
	"help": "<A help message to be shown just under the Runner field, optional>"
  }]
}
```

**Exemple of a `commands` Text DAT content**
```json
{
  "runner.nodes": [{
      "label": "Customize Operator",
      "conditionalMethod": "selectedOPIsCOMP",
      "executeMethod": "openCustomizeDialog",
      "help": "Opens the Customize Operator dialog."
    },{
      "label": "Align Operators Horizontally",
      "conditionalMethod": "selectionIsMultiple",
      "executeMethod": "alignOPsHorizontally",
      "help": "Align the selected operators on the same line."
  }]
}
```

Everytime a project opens, Runner will compare its already-loaded plugins with the ones in the defined location. 
If there is a mismatch with a plugin version, the plugin will be replaced by the one on the disk. 
If a plugin is missing on the disk, the plugin will not be removed.
If a new plugin is found, it will be loaded.

**Notice** As of now, it is not possible to remove a plugin without going inside the Runner network directly. This will be addressed soon in an update.

**Notice** A full documentation for writing plugins will be made available as soon as the specifications are stabilized.
