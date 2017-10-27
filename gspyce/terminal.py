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


class PTY:
    """"Collect lines of text"""
    def __init__(self, n_lines=24, n_columns=80):
        """Wrap output to n_columns and keep the last n_lines lines"""
        self.n_lines = n_lines
        self.n_columns = n_columns
        self.lines = collections.deque([""], maxlen=n_lines)

    def __str__(self):
        return '\n'.join(self.lines)

    def write(self, text):
        # wrap to n_columns
        def hard_wrap(text, width):
            for line in text.split('\r\n'):
                if not line:
                    yield line
                for i in range(0, len(line), width):
                    yield line[i:i+width]
        lines = hard_wrap(text, width=self.n_columns)

        # collect lines
        self.lines[-1] += next(lines)
        for line in lines:
            self.lines.append(line)


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

    def __enter__(self):
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

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush_pipes()

        # should kill thread because of readline, but cannot do this in Python

        # restore redirections
        os.close(self.terminal_pipe)
        # we should close file descriptors 0, 1 and 2 at this point, but the
        # REPL thread might still be using them...
        os.dup2(self.real_stderr, 2)
        os.dup2(self.real_stdout, 1)
        os.dup2(self.real_stdin, 0)
        self.terminal_pipe = None

        # restore standard file descriptors attributes
        if self.terminal_attr_stdin is not None:
            termios.tcsetattr(2, termios.TCSADRAIN, self.terminal_attr_stderr)
            termios.tcsetattr(1, termios.TCSADRAIN, self.terminal_attr_stdout)
            termios.tcsetattr(0, termios.TCSADRAIN, self.terminal_attr_stdin)
        os.set_blocking(0, self.was_blocking)

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
        else:
            c = k.decode('latin1')
            if self.terminal_pipe:
                os.write(self.terminal_pipe, c.encode())
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
        self.flush_pipes()
        time.sleep(.01)

    def draw_hud(self):
        """Draw the HUD"""
        super().draw_hud()
        self.flush_pipes()
        if self.terminal_enabled:
            self.hud_print(str(self.terminal_pty))


def main():
    with TerminalGUI():
        gui.main()


if __name__ == '__main__':
    main()
