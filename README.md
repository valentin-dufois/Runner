# Runner

![Supported plateform](https://img.shields.io/badge/plateform-macOS%20%7C%20Windows-lightgrey?style=flat-square)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/boisier/runner?include_prereleases&label=release&style=flat-square)



Runner is a fast, efficient, fuzzy-finder for TouchDesigner on MacOS and Windows.
Runner provides a unique search field for finding anything in TD ranging from built-in operators to TOX inside a folder on the computer.

Runner is build entirely in Python inside TouchDesigner using a unique python module.

*Warning* Runner needs to download 1MB of additional data upon first use on a computer to work. 
Updating TouchDesigner may also require Runner to get its additional content again
 
## Functionnalities
 
Runner provides access to multiple types of elements

Runner is not case-sensitive and provide relevant results even if their is typos (missing letters) in your search.
 
### Built-In Operators
All built-in operators can be found in the runner both by their display name `Movie File In` and their type `moviefileinTOP`.

### Palette
All palette built-in operators are referenced in the finder and can be found by their name `Probe` or path in the palette `Tools/Probe`.

### TOXs
It is possible to specify a folder in which Runner will reference all available TOXs. You can set the folder location in `Runner Settings`

### Project OPs
Runner references all the operators in the current project. They can be found by their name `wave1` or their path in the project `/project1/wave1`.
Runner uses tags to adjust the search behaviours:
* `runner-ignore` Tell Runner to ignore this node and its child operator (if applicable)
* `runner-keepout` Tell Runner to ignore the child operators of this node (if applicable) but not the node itself. Operators from the palette placed using Runner are automatically given this tag to hide their inner network. This is useful to prevent cluttering in the results.

### Presets
Runner integrate an efficient presets system that can be used to save-and-recall nodes with their specific parameters. For presets to work, you need to specify where to store the presets inside the `Runner Settings`.

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

