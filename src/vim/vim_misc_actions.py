# -----------------------------------------------------------
# AUTHOR --------> Francisco Contreras
# OFFICE --------> Senior VFX Compositor, Software Developer
# WEBSITE -------> https://vinavfx.com
# -----------------------------------------------------------
from ...nuke_util.pyside import QTextCursor
import os
import shutil
import subprocess

from .vim_general_actions import normal


def change_case(self, cursor, _, uppercase=True):
    cursor.beginEditBlock()

    if uppercase:
        text = cursor.selectedText().upper()
    else:
        text = cursor.selectedText().lower()

    cursor.removeSelectedText()
    cursor.insertText(text)
    cursor.endEditBlock()

    self.setTextCursor(cursor)
    normal(self, cursor)


def change_case_word(_, cursor, __, uppercase=True):
    pos = cursor.position()
    cursor.beginEditBlock()
    cursor.select(QTextCursor.WordUnderCursor)

    if uppercase:
        text = cursor.selectedText().upper()
    else:
        text = cursor.selectedText().lower()

    cursor.removeSelectedText()
    cursor.insertText(text)
    cursor.endEditBlock()
    cursor.setPosition(pos)
    return cursor


def indent_line_to_left(self, cursor, _, edit_block=True):
    if edit_block:
        cursor.beginEditBlock()
    text = cursor.block().text()

    cursor.movePosition(QTextCursor.StartOfLine)

    for c in text[: self.tab_spaces]:
        if c.isspace():
            cursor.deleteChar()
        else:
            break

    text = cursor.block().text()

    if text[0].isspace() if text else "":
        cursor.movePosition(QTextCursor.NextWord)

    if edit_block:
        cursor.endEditBlock()

    return cursor


def indent_line_to_right(self, cursor, _, edit_block=True):
    if edit_block:
        cursor.beginEditBlock()

    if cursor.block().text().strip():
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.insertText(self.tab_string)

        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.NextWord)

    if edit_block:
        cursor.endEditBlock()
    return cursor


def indent_selection(self, cursor, _, right=True):
    start = cursor.selectionStart()
    end = cursor.selectionEnd()

    cursor.beginEditBlock()

    cursor.setPosition(start)
    block1 = cursor.blockNumber()
    cursor.setPosition(end)
    block2 = cursor.blockNumber()

    cursor.setPosition(start)

    for _ in range(block1, block2 + 1):
        for _ in range(self.held_number):
            if right:
                indent_line_to_right(self, cursor, _, False)
            else:
                indent_line_to_left(self, cursor, _, False)

        cursor.movePosition(QTextCursor.NextBlock)

    cursor.clearSelection()
    self.set_mode("normal")

    cursor.setPosition(start)
    cursor.movePosition(QTextCursor.StartOfLine)

    text = cursor.block().text()
    if text[0].isspace() if text else "":
        cursor.movePosition(QTextCursor.NextWord)

    cursor.endEditBlock()

    self.setTextCursor(cursor)


def format_python(self, cursor, _):
    if self.parent.get_syntax() != "python":
        print("Python formatting is only available for Python code.")
        return cursor

    executable = shutil.which("black") or shutil.which(
        os.path.expanduser("~/.local/bin/black")
    )
    if not executable:
        print("Black was not found in PATH or ~/.local/bin.")
        return cursor

    source = self.toPlainText()
    command = [executable, "--quiet", "--line-length", "79"]
    try:
        help_result = subprocess.run(
            [executable, "--help"],
            capture_output=True,
            encoding="utf-8",
            timeout=3,
            check=True,
        )
        if "--enable-unstable-feature" in help_result.stdout:
            command.extend(
                ["--preview", "--enable-unstable-feature", "string_processing"]
            )
        else:
            command.append("--experimental-string-processing")
        command.append("-")
        result = subprocess.run(
            command,
            input=source,
            capture_output=True,
            encoding="utf-8",
            timeout=5,
            check=True,
        )
    except (OSError, subprocess.SubprocessError) as error:
        details = getattr(error, "stderr", None) or str(error)
        print("Black could not format the code: {}".format(details))
        return cursor

    formatted = result.stdout
    if formatted.endswith("\n") and not source.endswith("\n"):
        formatted = formatted[:-1]
    if formatted == source:
        return cursor

    line = cursor.blockNumber()
    column = cursor.positionInBlock()
    vertical_scroll = self.verticalScrollBar().value()
    horizontal_scroll = self.horizontalScrollBar().value()

    cursor.beginEditBlock()
    cursor.select(QTextCursor.Document)
    cursor.insertText(formatted)
    block = self.document().findBlockByNumber(min(line, self.blockCount() - 1))
    cursor.setPosition(block.position() + min(column, block.length() - 1))
    cursor.endEditBlock()

    self.setTextCursor(cursor)
    self.verticalScrollBar().setValue(vertical_scroll)
    self.horizontalScrollBar().setValue(horizontal_scroll)
