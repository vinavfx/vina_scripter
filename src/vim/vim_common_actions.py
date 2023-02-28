# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
from PySide2.QtGui import QTextCursor


def fill_selection_blocks(cursor):
    start = cursor.selectionStart()
    end = cursor.selectionEnd()

    anchor = QTextCursor.KeepAnchor

    if start == cursor.position():
        cursor.setPosition(end)
        cursor.movePosition(QTextCursor.EndOfLine)
        cursor.setPosition(start, anchor)
        cursor.movePosition(QTextCursor.StartOfLine, anchor)
    else:
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.setPosition(end, anchor)
        cursor.movePosition(QTextCursor.EndOfLine, anchor)

    return cursor
