# Author: Francisco Jose Contreras Cuevas
# Office: VFX Artist - Senior Compositor
# Website: vinavfx.com
from time import time

from PySide2.QtCore import Qt
from PySide2.QtGui import QTextCursor
from .keys_normal_mode import key_press_event as key_press_event_normal

from .vim_misc_actions import *
from .vim_general_actions import *
from .vim_extract_actions import *
from .vim_nav_actions import *
from .vim_search_actions import *
from .vim_surround_actions import *
from .vim_commenter_actions import *


def init(self):
    self.held_number = 0
    self.copied = ''
    self.key_words = ['def', 'class', 'if', 'elif', 'else',
                      'while', 'with', 'try', 'except', 'for']

    self.first_held_key = None
    self.second_held_key = None
    self.third_held_key = None
    self.fourth_held_key = None

    self.undo_cursor_position = -1
    self.redo_cursor_position = -1

    self.leader = False
    self.leader_activation = 0

    self.normal_hotkeys = {
        'a': insert_next_char,
        'b': go_back_word_start,

        'c0': delete_towards_and_insert,
        'c_': delete_towards_and_insert,
        'c$': delete_towards_and_insert,
        'cb': delete_towards_and_insert,
        'cc': delete_towards_and_insert,
        'ce': delete_towards_and_insert,
        'cf?': delete_towards_and_insert,
        'cF?': delete_towards_and_insert,
        'cj': delete_towards_and_insert,
        'ck': delete_towards_and_insert,
        'ch': delete_towards_and_insert,
        'cl': delete_towards_and_insert,
        'cs??': replace_enclosed_word,
        'cw': delete_towards_and_insert,

        'd0': delete_towards,
        'd_': delete_towards,
        'd$': delete_towards,
        'db': delete_towards,
        'dd': delete_towards,
        'de': delete_towards,
        'df?': delete_towards,
        'dF?': delete_towards,
        'dh': delete_towards,
        'dk': delete_towards,
        'dj': delete_towards,
        'dl': delete_towards,
        'ds?': remove_enclosed_word,
        'dw': delete_towards,

        'e': goto_end_of_word,
        'f?': goto_char,
        'gg': goto_start,
        'gt': lambda: self.parent.parent.next_script_page(),
        'gT': lambda: self.parent.parent.previous_script_page(),
        'gUaw': change_case_word,
        'guaw': (change_case_word, False),
        'h': goto_left,
        'i': insert,
        'j': goto_down,
        'k': goto_up,
        'l': goto_right,
        'm': None,
        'n': next_found_word,
        'o': insert_under,
        'p': paste,
        'q': None,
        'r?': replace_char,
        's': insert_and_delete_char,
        't': None,
        'u': undo,
        'v': visual,
        'w': goto_next_word_start,
        'x': delete_char,

        'y0': copy,
        'y_': copy,
        'y$': copy,
        'yw': copy,
        'ye': copy,
        'yb': copy,
        'yk': copy,
        'yj': copy,
        'yl': copy,
        'yh': copy,
        'yf?': copy,
        'yF?': copy,
        'yy': copy,

        'ysiw?': enclose_word,
        'zz': center_cursor,

        'A': insert_to_end,
        'C': delete_towards_and_insert,
        'D': delete_towards,
        'G': goto_end,
        'I': insert_to_start,
        'J': raise_bottom_line,
        'N': previous_found_word,
        'V': visual_line,
        'F?': (goto_char, True),

        '0': goto_start_of_line,
        '$': goto_end_of_line,
        '^': goto_first_char,
        '_': goto_first_char,
        ':': write_command,
        '/': search,
        '*': find_words_over_cursor,
        '<<': indent_line_to_left,
        '>>': indent_line_to_right,

        'ctrl+d': jump_down,
        'ctrl+e': scroll_down,
        'ctrl+h': goto_left,
        'ctrl+k': goto_up,
        'ctrl+j': goto_down,
        'ctrl+l': goto_right,
        'ctrl+r': redo,
        'ctrl+u': jump_up,
        'ctrl+y': scroll_up,
        'ctrl+[': escape,
        'ctrl+]': goto_function,
        'ctrl+o': undo_cursor,
        'ctrl+i': redo_cursor,
        'ctrl+-': (zoom, False),
        'ctrl++': zoom
    }

    self.visual_hotkeys = {
        'b': go_back_word_start,
        'c': delete_selection,
        'd': delete_selection,
        'e': (goto_end_of_word, True),
        'f?': (goto_char, False, True),
        'gg': goto_start,
        'h': goto_left,
        'j': goto_down,
        'k': goto_up,
        'l': goto_right,
        'u': (change_case, False),
        'v': normal,
        'w': goto_next_word_start,
        'y': copy_selection,

        'F?': (goto_char, True),

        '$': (goto_end_of_line, True),
        '_': goto_first_char,
        ':': write_command,
        '/': search,
        '<': (indent_selection, False),
        '>': (indent_selection, True),

        'G': goto_end,
        'U': change_case,

        'ctrl+d': jump_down,
        'ctrl+u': jump_up,
        'ctrl+[': normal,
        'ctrl+-': (zoom, False),
        'ctrl++': zoom
    }

    self.leader_normal_hotkeys = {
        'ci': comment_current_line,
        'cA': comment_end_line,
        'c$': comment_to_end,
        'cc': (comment_current_line, False, True),
        'cu': (comment_current_line, False, False),
    }

    self.leader_visual_hotkeys = {
        'ci': comment_selected_text,
        'cc': (comment_selected_text, False, True),
        'cu': (comment_selected_text, False, False),
    }

    self.abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
           'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
           's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


    self.keys = {
        '0': Qt.Key_0,
        '1': Qt.Key_1,
        '2': Qt.Key_2,
        '3': Qt.Key_3,
        '4': Qt.Key_4,
        '5': Qt.Key_5,
        '6': Qt.Key_6,
        '7': Qt.Key_7,
        '8': Qt.Key_8,
        '9': Qt.Key_9,

        'a': Qt.Key_A,
        'b': Qt.Key_B,
        'c': Qt.Key_C,
        'd': Qt.Key_D,
        'e': Qt.Key_E,
        'f': Qt.Key_F,
        'g': Qt.Key_G,
        'h': Qt.Key_H,
        'i': Qt.Key_I,
        'j': Qt.Key_J,
        'k': Qt.Key_K,
        'l': Qt.Key_L,
        'm': Qt.Key_M,
        'n': Qt.Key_N,
        'o': Qt.Key_O,
        'p': Qt.Key_P,
        'q': Qt.Key_Q,
        'r': Qt.Key_R,
        's': Qt.Key_S,
        't': Qt.Key_T,
        'u': Qt.Key_U,
        'v': Qt.Key_V,
        'w': Qt.Key_W,
        'x': Qt.Key_X,
        'y': Qt.Key_Y,
        'z': Qt.Key_Z,

        ':': Qt.Key_Colon,
        '$': Qt.Key_Dollar,
        '_': Qt.Key_Underscore,
        '[': Qt.Key_BracketLeft,
        ']': Qt.Key_BracketRight,
        '\\': Qt.Key_Backslash,
        ';': Qt.Key_Semicolon,
        '\'': Qt.Key_Apostrophe,
        ',': Qt.Key_Comma,
        '.': Qt.Key_Period,
        '/': Qt.Key_Slash,
        '=': Qt.Key_Equal,
        '-': Qt.Key_Minus,
        '`': Qt.Key_QuoteLeft,
        '{': Qt.Key_BraceLeft,
        '}': Qt.Key_BraceRight,
        '|': Qt.Key_Bar,
        '!': Qt.Key_Exclam,
        '@': Qt.Key_At,
        '#': Qt.Key_NumberSign,
        '%': Qt.Key_Percent,
        '^': Qt.Key_AsciiCircum,
        '&': Qt.Key_Ampersand,
        '*': Qt.Key_Asterisk,
        '(': Qt.Key_ParenLeft,
        ')': Qt.Key_ParenRight,
        '+': Qt.Key_Plus,
        '<': Qt.Key_Less,
        '>': Qt.Key_Greater,
        '?': Qt.Key_Question,
        ' ': Qt.Key_Space
    }

def key_press_event(self, event):
    key = event.key()
    ret = 0

    if (time() - self.leader_activation) > 1:
        self.leader = False

    if key == Qt.Key_Escape:
        if self.mode == 'normal':
            self.parent.parent.exit_node()

        elif self.mode in ['visual', 'visual_line', 'insert']:
            self.set_mode('normal')

    elif self.leader and not self.mode == 'insert':
        if self.mode == 'visual' :
            ret = press(self, event, True, False, True)

        elif self.mode == 'visual_line':
            ret = press(self, event, True, True, True)

        else:
            ret = press(self, event, False, False, True)

    elif ( key == Qt.Key_Comma and not self.mode == 'insert'):
        self.leader = True
        self.leader_activation = time()

    elif self.mode == 'visual':
        ret = press(self, event, True)

    elif self.mode == 'visual_line':
        ret = press(self, event, True, True)

    elif self.mode == 'insert':
        ret = insert_mode(self, event)

    else:
        ret = press(self, event)

    return ret


def key_match(self, event, char):
    if not char:
        return

    lower_char = char.lower()
    if not lower_char in self.keys:
        return False

    shift = event.modifiers() == Qt.ShiftModifier

    if event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
        shift = True

    key = event.key()

    upper_match = True

    if lower_char in self.abc:
        upper_match = shift == char.isupper()

    if self.keys[lower_char] == key and upper_match:
        return True

    return False


def validate_hotkey(self, event, _hotkey):

    modifiers, hotkey = _hotkey.split(
        '+', 1) if '+' in _hotkey else [False, _hotkey]

    shift = event.modifiers() == Qt.ShiftModifier
    ctrl = event.modifiers() == Qt.ControlModifier

    if event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
        shift = True
        ctrl = True

    shift_match = shift == (modifiers == 'shift')
    ctrl_match = ctrl == (modifiers == 'ctrl')

    first_key = hotkey[0]
    second_key = hotkey[1] if len(hotkey) > 1 else ''
    third_key = hotkey[2] if len(hotkey) > 2 else ''
    fourth_key = hotkey[3] if len(hotkey) > 3 else ''
    fifth_key = hotkey[4] if len(hotkey) > 4 else ''

    first_match = key_match(self, event, first_key)
    second_match = key_match(self, event, second_key)
    third_match = key_match(self, event, third_key)
    fourth_match = key_match(self, event, fourth_key)
    fifth_match = key_match(self, event, fifth_key)

    if first_key in self.abc:
        upper_match = shift == first_key.isupper()
        if not upper_match and not shift_match:
            first_match = False

    if second_key.lower() in self.abc:
        upper_match = shift == second_key.isupper()
        if not upper_match and not shift_match:
            second_match = False

    if third_key in self.abc:
        upper_match = shift == third_key.isupper()
        if not upper_match and not shift_match:
            third_match = False

    if fourth_key in self.abc:
        upper_match = shift == fourth_key.isupper()
        if not upper_match and not shift_match:
            fourth_match = False

    if fifth_key in self.abc:
        upper_match = shift == fifth_key.isupper()
        if not upper_match and not shift_match:
            fifth_match = False

    first_match = first_match if ctrl_match else False
    second_match = second_match if ctrl_match else False
    third_match = third_match if ctrl_match else False
    fourth_match = fourth_match if ctrl_match else False
    fifth_match = fifth_match if ctrl_match else False

    return {
        'first_key': first_key,
        'second_key': second_key,
        'third_key': third_key,
        'fourth_key': fourth_key,
        'fifth_key': fifth_key,

        'first_match': first_match,
        'second_match': second_match,
        'third_match': third_match,
        'fourth_match': fourth_match,
        'fifth_match': fifth_match,
    }


def get_action(self, event, hotkeys, resend_if_not_match=True):
    run = None

    key_char = char(event.key())
    if not key_char:
        return run

    def get_current_char():
        shift = event.modifiers() == Qt.ShiftModifier

        if key_char.lower() in self.abc and not shift:
            return key_char.lower()

        return key_char

    def reset():
        if not resend_if_not_match:
            return

        self.first_held_key = None
        self.second_held_key = None
        self.third_held_key = None
        self.fourth_held_key = None

        key_press_event(self, event)

    if self.fourth_held_key:
        for hotkey, action in hotkeys.items():
            val = validate_hotkey(self, event, hotkey)

            if not val['fifth_match'] and not val['fifth_key'] == '?':
                continue

            if not val['first_key'] == self.first_held_key[0]:
                continue

            if not val['second_key'] == self.second_held_key[0]:
                continue

            if not val['third_key'] == self.third_held_key[0]:
                continue

            if not val['fourth_key'] == self.fourth_held_key[0]:
                continue

            run = action, val, val['fifth_key']
            break

        if not run:
            reset()

    elif self.third_held_key:
        for hotkey, action in hotkeys.items():
            val = validate_hotkey(self, event, hotkey)

            if not val['fourth_match'] and not val['fourth_key'] == '?':
                continue

            if not val['first_key'] == self.first_held_key[0]:
                continue

            if not val['second_key'] == self.second_held_key[0]:
                continue

            if not val['third_key'] == self.third_held_key[0]:
                continue

            if val['fifth_key']:
                self.fourth_held_key = val['fourth_key'], get_current_char()
                return

            run = action, val, val['fourth_key']
            break

        if not run:
            reset()

    elif self.second_held_key:
        for hotkey, action in hotkeys.items():
            val = validate_hotkey(self, event, hotkey)

            if not val['third_match'] and not val['third_key'] == '?':
                continue

            if not val['first_key'] == self.first_held_key[0]:
                continue

            if not val['second_key'] == self.second_held_key[0]:
                continue

            if val['fourth_key']:
                self.third_held_key = val['third_key'], get_current_char()
                return

            run = action, val, val['third_key']
            break

        if not run:
            reset()

    elif self.first_held_key:
        for hotkey, action in hotkeys.items():
            val = validate_hotkey(self, event, hotkey)

            if not val['second_match'] and not val['second_key'] == '?':
                continue

            if not val['first_key'] == self.first_held_key[0]:
                continue

            if val['third_key']:
                self.second_held_key = val['second_key'], get_current_char()
                return

            run = action, val, val['second_key']
            break

        if not run:
            reset()

    else:
        for hotkey, action in hotkeys.items():
            val = validate_hotkey(self, event, hotkey)

            if val['first_match']:
                if val['second_key']:
                    self.first_held_key = val['first_key'], get_current_char()
                    return

                run = action, val, val['first_key']
                break

    return run


def char(key):
    try:
        return chr(key)
    except:
        return ''

def press(self, event, visual = False, visual_line = False, leader = False):
    _char = char(event.key())

    if visual:
        hotkeys = self.leader_visual_hotkeys if leader else self.visual_hotkeys
        anchor = QTextCursor.KeepAnchor
    else:
        hotkeys = self.leader_normal_hotkeys if leader else self.normal_hotkeys
        anchor = QTextCursor.MoveAnchor

    cursor = self.textCursor()

    run = None
    if not _char.isdigit():
        run = get_action(self, event, hotkeys)
    else:
        digit_action = get_action(self, event, hotkeys, False)
        if digit_action:
            key = digit_action[2]

            if key == '?':
                run = digit_action
            elif key == '0' and not self.held_number:
                run = digit_action

    func, hotkey, key = run if run else [None, None, None]

    if func:
        self.held_number = self.held_number if self.held_number else 1

        params = {
            'anchor': anchor,
            'event': event,
            'key': key,
            'hotkey': hotkey
        }

        if type(func) == tuple:
            args = func[1:]
            func = func[0]
            cursor = func(self, cursor, params, *args)

        else:
            if func.__name__ == '<lambda>':
                func()
            else:
                cursor = func(self, cursor, params)

        self.first_held_key = None
        self.second_held_key = None
        self.third_held_key = None
        self.fourth_held_key = None
        self.leader = None
        self.held_number = 0

    if _char.isdigit():
        if not self.held_number > 100:
            self.held_number = int(str(self.held_number) + _char)

    if not cursor:
        return

    cursor = fill_selection_blocks(cursor) if visual_line else cursor
    self.setTextCursor(cursor)




def insert_mode(self, event):
    ctrl = event.modifiers() == Qt.ControlModifier
    key = event.key()
    cursor = self.textCursor()

    ret = False
    if ctrl:
        if key == Qt.Key_BracketLeft:
            normal(self, cursor)

        elif key == Qt.Key_K:
            self.moveCursor(QTextCursor.Up)

        elif key == Qt.Key_J:
            self.moveCursor(QTextCursor.Down)

        elif key == Qt.Key_H:
            if cursor.positionInBlock() > 0:
                self.moveCursor(QTextCursor.Left)

        elif key == Qt.Key_L:
            if cursor.positionInBlock() < cursor.block().length() - 1:
                self.moveCursor(QTextCursor.Right)
        else:
            ret = True
    else:
        if key == Qt.Key_Escape:
            normal(self, cursor)

        elif key == Qt.Key_Backspace:
            text = cursor.block().text()
            pos = cursor.positionInBlock()

            current_char = text[pos] if len(text) > pos else ''
            prev_char = text[pos - 1] if pos > 0 else ''

            if ( prev_char == '(' and current_char == ')'
                or prev_char == '{' and current_char == '}'
                or prev_char == '[' and current_char == ']'
                or prev_char == "'" and current_char == "'"
                or prev_char == '"' and current_char == '"'
                ):
                cursor.movePosition(QTextCursor.Left)
                cursor.deleteChar()
                cursor.deleteChar()
            else:
                ret = True

        else:
            ret = True

    if ret:
        return key_press_event_normal(self, event)


