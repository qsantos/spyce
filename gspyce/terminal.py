import os  # file descriptor manipulation
import sys  # version_info, platform
import tty  # setraw
import pty  # openpty
import code  # interact
import time  # sleep
import termios  # save and restore attributes
import threading  # Thread
import collections  # deque
import rlcompleter  # Completer

import gspyce.hud
from gspyce.graphics import *


def printable(c):
    d = ord(c)
    if c == '\x7f':
        return '^?'
    elif c != '\r' and c != '\n' and d < 32:
        return '^' + r'@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_'[d]
    else:
        return c


def parse_control_sequence(sequence):
    sequence = iter(sequence)
    if next(sequence) != '\x1b':  # escape
        return 0, None, []
    if next(sequence) != '[':
        return 0, None, []
    length = 2
    args = []
    current_arg = []
    while True:
        c = next(sequence)
        length += 1
        if c in '0123456789':
            current_arg.append(c)
        elif c == ';':
            args.append(int(''.join(current_arg) or 0))
            current_arg.clear()
        elif c in '@CKPm':
            args.append(int(''.join(current_arg) or 0))
            return length, c, args
        else:
            return 0, None, []


class VTERow:
    def __init__(self):
        self.cells = []

    def __str__(self):
        return ''.join(printable(c) for c in self.cells)

    def insert(self, column, c):
        if column >= len(self.cells):
            self.cells += [' ' for _ in range(column+1 - len(self.cells))]
        self.cells[column] = c


class PTY:
    """"Collect lines of text"""
    def __init__(self, n_rows=24, n_columns=80):
        """Wrap output to n_columns and keep the last n_rows lines"""
        self.n_rows = n_rows
        self.n_columns = n_columns
        self.rows = [VTERow() for _ in range(n_rows)]
        self.cur_row = 0
        self.cur_col = 0
        self.input_buffer = ''

    def __str__(self):
        return '\n'.join(str(row) for row in self.rows)

    def next_col(self, amount=1):
        self.cur_col += amount
        if self.cur_col >= self.n_columns:
            self.cur_col = 0
            self.next_row()

    def next_row(self, amount=1):
        self.cur_row += amount
        if self.cur_row >= self.n_rows:
            self.rows = self.rows[1:] + [VTERow()]
            self.cur_row -= 1

    def insertchar(self, c):
        self.rows[self.cur_row].insert(self.cur_col, c)
        self.next_col()

    def write(self, text):
        buf = self.input_buffer + text
        i = 0
        while i < len(buf):
            try:
                length, command, args = parse_control_sequence(buf[i:])
            except StopIteration:
                self.input_buffer = buf[i:]
                break
            else:
                if command is not None:
                    if command == '@':  # insert character
                        arg = args[0] or 1
                        row = self.rows[self.cur_row]
                        if self.cur_col < len(row.cells):
                            row.cells[self.cur_col:self.cur_col] = [
                                ' ' for _ in range(arg)
                            ]
                    elif command == 'C':  # cursor right
                        arg = args[0] or 1
                        self.cur_col = min(self.cur_col + arg, self.n_columns)
                    elif command == 'K':  # erase in line
                        arg = args[0]
                        row = self.rows[self.cur_row]
                        if arg == 0:  # from cursor to end
                            if self.cur_col < len(row.cells):
                                row.cells[self.cur_col:] = []
                        elif arg == 1:  # from beginning to cursor
                            for i in range(0, self.cur_col):
                                row.insert(i, ' ')
                        elif arg == 2:  # all line
                            row.cells[:] = []
                    elif command == 'P':  # delete character
                        arg = args[0] or 1
                        row = self.rows[self.cur_row]
                        row.cells[self.cur_col:self.cur_col+arg] = []
                    elif command == 'm':  # select graphic rendition
                        pass  # TODO: implement
                    i += length
                    continue

            c = buf[i]
            if c == '\a':  # bell
                pass
            elif c == '\b':  # backspace
                self.cur_col = max(self.cur_col - 1, 0)
            elif c == '\r':  # caret return
                self.cur_col = 0
            elif c == '\n':  # new line
                self.next_row()
                self.cur_col = 0
            else:
                self.insertchar(c)
            i += 1


def repl(gui):
    import spyce.interact
    spyce.interact.namespace["gui"] = gui
    try:
        import spyce.__main__
    except SystemExit:
        pass
    gui.quit()


class TerminalGUI(gspyce.hud.HUD):
    """GUI with an interactive text terminal"""
    def __init__(self, title=b"Terminal in GUI"):
        super().__init__(title)
        glutIdleFunc(self.idleFunc)

        # terminal controls
        self.terminal_enabled = False
        self.terminal_pipe = None  # all I/O of the terminal go through this
        self.terminal_pty = PTY()  # save I/O for graphical display

    def start_redirection(self):
        if self.terminal_pipe:
            return

        # prepare standard file descriptors for raw manipulation
        self.was_blocking = os.get_blocking(0)
        os.set_blocking(0, False)
        try:
            self.terminal_attr_stdin = termios.tcgetattr(0)
            self.terminal_attr_stdout = termios.tcgetattr(1)
            self.terminal_attr_stderr = termios.tcgetattr(2)
            tty.setraw(0)
            tty.setraw(1)
            tty.setraw(2)
        except termios.error:  # probably redirected
            self.terminal_attr_stdin = None

        # redirect standard file descriptors to new PTY
        master, slave = pty.openpty()
        os.set_blocking(master, False)
        self.real_stdin = os.dup(0)
        self.real_stdout = os.dup(1)
        self.real_stderr = os.dup(2)
        os.close(0)
        os.close(1)
        os.close(2)
        os.dup2(slave, 0)
        os.dup2(slave, 1)
        os.dup2(slave, 2)
        os.close(slave)
        self.terminal_pipe = master

        # start REPL in separate thread
        threading.Thread(target=repl, args=(self,), daemon=True).start()

    def stop_redirection(self):
        if not self.terminal_pipe:
            return

        # should kill thread because of readline, but cannot do this in Python

        # restore redirections
        os.close(self.terminal_pipe)
        # we should close file descriptors 0, 1 and 2 at this point, but the
        # REPL thread might still be using them...
        os.dup2(self.real_stderr, 2)
        os.dup2(self.real_stdout, 1)
        os.dup2(self.real_stdin, 0)
        os.close(self.real_stderr)
        os.close(self.real_stdout)
        os.close(self.real_stdin)
        self.terminal_pipe = None

        # restore standard file descriptors attributes
        if self.terminal_attr_stdin is not None:
            termios.tcsetattr(2, termios.TCSADRAIN, self.terminal_attr_stderr)
            termios.tcsetattr(1, termios.TCSADRAIN, self.terminal_attr_stdout)
            termios.tcsetattr(0, termios.TCSADRAIN, self.terminal_attr_stdin)
        os.set_blocking(0, self.was_blocking)

    def __enter__(self):
        self.start_redirection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush_pipes()
        self.stop_redirection()

    def toggle_terminal(self, enable=None):
        """Toggle terminal

        If argument is set, enable or disable it instead
        """
        if enable is None:
            enable = not self.terminal_enabled
        if enable:
            self.terminal_restore_keyboardFunc = self.keyboardFunc
            self.terminal_restore_specialFunc = self.specialFunc
            glutKeyboardFunc(self.terminal_keyboardFunc)
            glutSpecialFunc(self.terminal_specialFunc)
            self.terminal_enabled = True
        else:
            glutKeyboardFunc(self.keyboardFunc)
            glutSpecialFunc(self.specialFunc)
            self.terminal_enabled = False
        self.update()

    def flush_pipes(self):
        if not self.terminal_pipe:
            return

        # feed REPL stdin
        data = b''
        while True:
            try:
                data = os.read(self.real_stdin, 4096)
            except OSError:
                break
        os.write(self.terminal_pipe, data)

        # handle REPL stdout
        data = b''
        while True:
            try:
                data = os.read(self.terminal_pipe, 4096)
            except OSError:
                break
        self.terminal_pty.write(data.decode())
        if self.terminal_enabled and data:
            self.update()
        os.write(self.real_stdout, data)

    @glut_callback
    def specialFunc(self, k, x, y):
        """Handle special key presses (GLUT callback)"""
        if k == GLUT_KEY_HOME:
            self.toggle_terminal(True)
        else:
            super().specialFunc(k, x, y)

    @glut_callback
    def terminal_keyboardFunc(self, k, x, y):
        """Handle key presses (terminal) (GLUT callback)"""
        if k == b'\x1b':  # escape
            self.toggle_terminal(False)
        elif self.terminal_pipe:
            c = k.decode('latin1').encode()

            # pass Alt+X shortcuts to e.g. readline
            # e.g. Alt+b = back one word, Alt+u = capitalize word
            modifiers = glutGetModifiers()
            if modifiers & GLUT_ACTIVE_ALT:
                c = b'\x1b' + c

            os.write(self.terminal_pipe, c)
            self.update()

    @glut_callback
    def terminal_specialFunc(self, k, x, y):
        """Handle special key presses (terminal) (GLUT callback)"""
        if k == GLUT_KEY_HOME:
            self.toggle_terminal(False)
        elif k == GLUT_KEY_UP:
            if self.terminal_pipe:
                os.write(self.terminal_pipe, b'\x1b[A')
        elif k == GLUT_KEY_DOWN:
            if self.terminal_pipe:
                os.write(self.terminal_pipe, b'\x1b[B')
        elif k == GLUT_KEY_LEFT:
            if self.terminal_pipe:
                os.write(self.terminal_pipe, b'\x1b[D')
        elif k == GLUT_KEY_RIGHT:
            if self.terminal_pipe:
                os.write(self.terminal_pipe, b'\x1b[C')
        else:
            self.terminal_restore_specialFunc(k, x, y)

    @glut_callback
    def idleFunc(self):
        try:
            self.flush_pipes()
        except:
            # any exception in flush_pipes() is an error
            self.stop_redirection()
            raise

        time.sleep(.01)

    def draw_hud(self):
        """Draw the HUD"""
        super().draw_hud()
        self.flush_pipes()
        if self.terminal_enabled:
            self.hud_print(str(self.terminal_pty))


def main():
    with TerminalGUI() as gui:
        gui.main()


if __name__ == '__main__':
    main()
