# me - this DAT
#
# comp - the List Component that holds this panel
# row - the row number of the cell being updated
# col - the column number of the cell being updated
#
# attribs contains the following members:
#
# text				   str            cell contents
# help                 str       	  help text
#
# textColor            r g b a        font color
# textOffsetX		   n			  horizontal text offset
# textOffsetY		   n			  vertical text offset
# textJustify		   m			  m is one of:  JustifyType.TOPLEFT, JustifyType.TOPCENTER,
#													JustifyType.TOPRIGHT, JustifyType.CENTERLEFT,
#													JustifyType.CENTER, JustifyType.CENTERRIGHT,
#													JustifyType.BOTTOMLEFT, JustifyType.BOTTOMCENTER,
#													JustifyType.BOTTOMRIGHT
#
# bgColor              r g b a        background color
#
# leftBorderInColor	   r g b a		  inside left border color
# rightBorderInColor   r g b a		  inside right border color
# bottomBorderInColor  r g b a		  inside bottom border color
# topBorderInColor	   r g b a		  inside top border color
#
# leftBorderOutColor   r g b a		  outside left border color
# rightBorderOutColor  r g b a		  outside right border color
# bottomBorderOutColor r g b a		  outside bottom border color
# topBorderOutColor	   r g b a		  outside top border color
#
# colWidth             w              sets column width
# colStetch            True/False     sets column stretchiness (width is min width)
# rowHeight            h              sets row height
# rowStetch            True/False     sets row stretchiness (height is min height)
# rowIndent            w              offsets entire row by this amount
#
# editable			   int			  number of clicks to activate editing the cell.
# draggable             True/False     allows cell to be drag/dropped elsewhere
# fontBold             True/False     render font bolded
# fontItalic           True/False     render font italicized
# fontSizeX            float		  font X size in pixels
# fontSizeY            float		  font Y size in pixels, if not specified, uses X size
# fontFace             str			  font face, example 'Verdana'
# wordWrap             True/False     word wrap
#
# top                  TOP			  background TOP operator
#
# select   true when the cell/row/col is currently being selected by the mouse
# rollover true when the mouse is currently over the cell/row/col
# radio    true when the cell/row/col was last selected
# focus    true when the cell/row/col is being edited
#
# currently not implemented:
#
# type                str             cell type: 'field' or 'label'
# fieldtype           str             field type: 'float' 'string' or  'integer'
# setpos              True/False x y  set cell absolute when first argument is True
# padding             l r b t         cell padding from each edge, expressed in pixels
# margin              l r b t         cell margin from neighbouring cells, expressed in pixels
#
# fontpath            path            File location to font. Don't use with 'font'
# fontformat          str             font format: 'polygon', 'outline' or 'bitmap'
# fontantialiased     True/False      render font antialiased
# fontcharset         str             font character set
#
# textjustify         h v             left/right/center top/center/bottom
# textoffset          x y             text position offset
#

# called when Reset parameter is pulsed, or on load

def onInitCell(list, row, col, attribs):
    return


def onInitRow(comp, row, attribs):
    return


def onInitCol(comp, col, attribs):
    return


def onInitTable(comp, attribs):
    return


# called during specific events
#
# coords - a named tuple containing the following members:
#   x
#   y
#   u
#   v

def onRollover(list, row, col, coords, prevRow, prevCol, prevCoords):
    # Update selectedRow index
    list.SelectRow(row)
    return


def onSelect(list, startRow, startCol, startCoords, endRow, endCol, endCoords, start, end):
    if end:
        # We only want to catch the mouse down event
        return

    list.ExecuteSelected()
    return


def onRadio(comp, row, col, prevRow, prevCol):
    return


def onFocus(comp, row, col, prevRow, prevCol):
    return


def onEdit(comp, row, col, val):
    return


# return True if interested in this drop event, False otherwise
def onHoverGetAccept(comp, row, col, coords, prevRow, prevCol, prevCoords, dragItems):
    return False


def onDropGetAccept(comp, row, col, coords, prevRow, prevCol, prevCoords, dragItems):
    return False
