import time
import collections

import gui.system
import gui.textures
from load import solar, kerbol
from gui.graphics import *


class SimulationGUI(gui.system.SystemGUI):
    def __init__(self, *args, **kwargs):
        super(SimulationGUI, self).__init__(*args, **kwargs)

        self.timewarp = 1.
        self.message_log = collections.deque(maxlen=10)

    def log(self, message):
        """Show message on HUD"""
        self.message_log.append(message)

    def draw_hud(self):
        """Draw the HUD"""

        self.hud_print("Time x%g\n" % self.timewarp)

        # display time
        self.hud_print('Date: %s\n' % self.system.format_date(self.time))

        super(SimulationGUI, self).draw_hud()

        self.hud_grid(-self.message_log.maxlen-1, 1)
        self.hud_print("Message log:\n")
        for message in self.message_log:
            self.hud_print("%s\n" % message)

    @glut_callback
    def keyboardFunc(self, k, x, y):
        """Handle key presses (GLUT callback)"""
        if k == b'\x1b':  # escape
            self.is_running = False
        elif k == b',':
            self.timewarp /= 10.
            self.update()
        elif k == b';':
            self.timewarp *= 10.
            self.update()
        else:
            super(SimulationGUI, self).keyboardFunc(k, x, y)

    def main(self):
        """Main loop"""
        last = time.time()
        while self.is_running:
            glutMainLoopEvent()

            # passage of time
            now = time.time()
            elapsed = now - last
            last = now

            self.time += elapsed * self.timewarp

            # avoid wasting cycles
            pause = 1./60 - elapsed
            if pause > 0.:
                time.sleep(pause)

            self.update()

        glutCloseFunc(None)

if __name__ == "__main__":
    SimulationGUI.from_cli_args().main()
