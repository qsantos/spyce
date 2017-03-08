import re
import sys
import code
import collections
import rlcompleter

import interact
import gui.hud
from gui.graphics import *


class Readline(object):
    """readline-like interface-agnostic text buffer"""
    def __init__(self, interpreter, completer=None):
        """"Initiate text buffer

        interpreter must implement resetbuffer() and push()
            see code.InteractiveConsole
        completer must be callable
            see rlcomplete.Complete.complete()
        """
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        self.interpreter = interpreter
        self.completer = completer
        self.input_buffer = ""
        self.more = False
        self.history = [""]
        self.history_index = 0

    def press(self, k):
        """Handle key press"""
        if " " <= k <= "~":
            self.input_buffer += k
        elif k == "\x03":  # Ctrl+C
            sys.stderr.write(self.current_line())
            sys.stderr.write("\nKeyboardInterrupt\n")
            self.interpreter.resetbuffer()
            self.input_buffer = ""
            self.more = False
        elif k == "\b":
            self.input_buffer = self.input_buffer[:-1]
        elif k == "\t":
            if not self.input_buffer or self.completer is None:
                # just indent
                self.input_buffer += k
                return
            # look for a completable string
            m = re.search(r"(.*?)([\.\w]*)$", self.input_buffer)
            if m is None:  # no completable string
                return
            rest, completable = m.groups()
            suggestion = self.completer(completable, 0)
            if suggestion is None:  # no suggestion
                return
            if self.completer(completable, 1):  # several suggestions
                return
            self.input_buffer = rest + suggestion
        elif k == "\n" or k == "\r":
            print(self.current_line())
            self.more = self.interpreter.push(self.input_buffer)
            self.history[-1] = self.input_buffer
            self.history_index = len(self.history)
            self.history.append("")
            self.input_buffer = ""

    def up(self):
        """Handle up key press"""
        self.history[self.history_index] = self.input_buffer
        self.history_index -= 1
        if self.history_index < 0:
            self.history_index = 0
        self.input_buffer = self.history[self.history_index]

    def down(self):
        """Handle down key press"""
        self.history[self.history_index] = self.input_buffer
        self.history_index += 1
        if self.history_index >= len(self.history):
            self.history_index = len(self.history) - 1
        self.input_buffer = self.history[self.history_index]

    def current_line(self):
        """Return the current buffer"""
        prompt = sys.ps2 if self.more else sys.ps1
        return prompt + self.input_buffer


class Console(object):
    """"Capture output

    >>> console = Console(n_lines=4)
    >>> with console:
    ...    for i in range(30):
    ...        print(i)
    ...
    >>> console.lines
    deque(['97', '98', '99', ''], maxlen=4)
    """
    def __init__(self, n_lines=24, n_columns=80):
        """Wrap output to n_columns and keep the last n_lines lines"""
        self.n_lines = n_lines
        self.n_columns = n_columns
        self.lines = collections.deque([""], maxlen=n_lines)

    def __enter__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self

    def __exit__(self, type, value, traceback):
        sys.stdout = self.stdout
        sys.stderr = self.stderr

    def flush(self):
        pass

    def write(self, text):
        # wrap to n_columns
        def hard_wrap(text, width):
            for line in text.split("\n"):
                if not line:
                    yield line
                for i in range(0, len(line), width):
                    yield line[i:i+width]
        lines = hard_wrap(text, width=self.n_columns)

        # collect lines
        self.lines[-1] += next(lines)
        for line in lines:
            self.lines.append(line)


class TerminalGUI(gui.hud.HUD):
    """GUI with an interactive text terminal"""
    def __init__(self, title=b"Terminal in GUI"):
        super(TerminalGUI, self).__init__(title)

        self.console = Console()
        interact.namespace["gui"] = self
        self.interpreter = code.InteractiveConsole(interact.namespace)
        self.completer = rlcompleter.Completer(interact.namespace)
        self.readline = Readline(self.interpreter, self.completer.complete)

        v = sys.version_info
        with self.console:
            # banner
            print('Spyce (running Python %s.%s.%s on %s)'
                  % (v.major, v.minor, v.micro, sys.platform))

    @glut_callback
    def keyboardFunc(self, k, x, y):
        """Handle key presses (GLUT callback)"""
        self.update()
        with self.console:
            self.readline.press(k.decode('latin1'))
        super(TerminalGUI, self).keyboardFunc(k, x, y)

    @glut_callback
    def specialFunc(self, k, x, y):
        """Handle special key presses (GLUT callback)"""
        self.update()
        if k == GLUT_KEY_UP:
            with self.console:
                self.readline.up()
        elif k == GLUT_KEY_DOWN:
            with self.console:
                self.readline.down()
        else:
            super(TerminalGUI, self).specialFunc(k, x, y)

    def draw_hud(self):
        """Draw the HUD"""
        super(TerminalGUI, self).draw_hud()
        self.hud_print('\n'.join(self.console.lines))
        self.hud_print(self.readline.current_line() + '_')


def main():
    TerminalGUI().main()


if __name__ == '__main__':
    main()
