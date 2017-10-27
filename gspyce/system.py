import sys
import math

import spyce.human
from spyce.vector import Mat4
import gspyce.textures
import gspyce.skybox
import gspyce.picking
import gspyce.terminal
import gspyce.mesh
from gspyce.graphics import *


def ancestors_descendants(body, max_depth=1):
    """Return the ancestors of a body and their descendants

    Return two lists: ancestors and descendants.
    ancestors are `body` itself, its primary, its primary's primary and so on
    descendants are the children of each ancestors, their children and so on

    `max_depth` limits the level of recursion when search for descendants.

    With max_depth=-1, it will return all the bodies, except that the ancestors
    will be in a separate list.
    """
    ancestors = []
    descendants = []

    def down(body, skip, max_depth):
        """Explore down the tree and collect other nodes"""
        if not max_depth:
            return
        for satellite in body.satellites:
            if satellite is skip:
                continue
            descendants.append(satellite)
            down(satellite, skip, max_depth-1)

    def up(body, skip=None):
        """Climb up the tree and collect ancestors"""
        ancestors.append(body)
        down(body, skip, max_depth)
        if body.orbit is not None:
            up(body.orbit.primary, body)

    up(body)
    return ancestors, descendants


class SystemGUI(gspyce.picking.PickingGUI, gspyce.terminal.TerminalGUI):
    """GUI for showing a planetary system"""
    def __init__(self, focus):
        title = b'Sp' + b'a'*42 + b'ce'
        super().__init__(title)

        self.time = 0
        self.zoom = 1e-7

        # detect current system
        self.focus = focus
        self.system = self.focus
        while self.system.orbit is not None:
            self.system = self.system.orbit.primary

        if self.system.name == 'Sun':
            self.time = spyce.human.seconds_since_J2000()

        self.shader_position_marker = main_program("circle_point")

        # lighting shader
        self.shader_lighting = main_program("lighting")
        self.lighting_source = \
            glGetUniformLocation(self.shader_lighting, b'lighting_source')

        # skybox shader
        self.shader_skybox = main_program('cubemap')
        # cubemap_texture = GL_TEXTURE0
        variable = glGetUniformLocation(self.shader_skybox, b"cubemap_texture")
        glUseProgram(self.shader_skybox)
        glUniform1i(variable, 0)

        # sphere VBO for drawing bodies
        self.sphere = gspyce.mesh.Sphere(1, 64, 64)

        # meshes for drawing orbits
        self.circle_through_origin = gspyce.mesh.CircleThroughOrigin(1, 256)

        # collect list of all bodies
        self.bodies = []

        def collect_bodies(body):
            self.bodies.append(body)
            for satellite in body.satellites:
                collect_bodies(satellite)
        collect_bodies(self.system)

        # orbit meshes
        for body in self.bodies:
            if body.orbit is None:
                continue
            body.orbit.mesh = gspyce.mesh.OrbitMesh(body.orbit)
            body.orbit.apses_mesh = gspyce.mesh.ApsesMesh(body.orbit)

        # textures
        gspyce.textures.init()
        texture_directory = self.system._texture_directory
        for body in self.bodies:
            filename = "%s.jpg" % body.name
            body.texture = gspyce.textures.load(texture_directory, filename)

        # skybox
        self.skybox = gspyce.skybox.Skybox("skybox", "GalaxyTex_%s.jpg")

    @classmethod
    def from_cli_args(cls):
        """Load the system given in command-line arguments"""
        import spyce.load

        try:
            name = sys.argv[1]
        except IndexError:
            name = 'Kerbin'

        try:
            body = spyce.load.from_name(name)
        except KeyError:
            print("Unknwon body '%s'" % name, file=sys.stderr)
            sys.exit(1)

        return cls(body)

    def draw_body(self, body):
        """Draw a CelestialBody"""

        transform = (
            self.modelview_matrix @
            Mat4.translate(*body._relative_position)
        )
        self.add_pick_object(body)

        # axial tilt
        if body.north_pole is not None:
            z_angle = body.north_pole.ecliptic_longitude - math.pi/2
            transform @= Mat4.rotate(z_angle, 0, 0, 1)
            x_angle = body.north_pole.ecliptic_latitude - math.pi/2
            transform @= Mat4.rotate(x_angle, 1, 0, 0)

        # OpenGL use single precision while Python has double precision
        # reducing modulo 2 PI in Python reduces loss of significance
        turn_fraction, _ = math.modf(self.time / body.rotational_period)
        transform @= Mat4.rotate(2 * math.pi * turn_fraction, 0, 0, 1)

        # radius
        transform @= Mat4.scale(body.radius, body.radius, body.radius)

        # textured quadric (representation from close by)
        # sphere with radius proportional to that of the body
        if body.texture:
            glBindTexture(GL_TEXTURE_2D, body.texture)
        else:
            original_color = self.color
            self.set_color(.5, .5, 1., 1.)

        original_modelview_matrix = self.modelview_matrix
        self.set_modelview_matrix(transform)
        self.sphere.draw()
        self.set_modelview_matrix(original_modelview_matrix)

        if body.texture:
            glBindTexture(GL_TEXTURE_2D, 0)
        else:
            self.set_color(*original_color)

        glDepthMask(True)

    def draw(self):
        """Draw the scene"""
        # ancestors_descendants() can just be assumed to return all celestial
        # bodies, except that ancestors are in a separate list
        ancestors, descendants = ancestors_descendants(self.focus)
        bodies = ancestors + descendants

        # cache position of celestial bodies relative to the scene origin
        scene_origin = self.focus.global_position_at_time(self.time)
        for body in bodies:
            body_position = body.global_position_at_time(self.time)
            body._relative_position = body_position - scene_origin

        # draw celestial bodies
        self.sphere.bind()
        # draw system star individually (without lighting)
        self.draw_body(self.system)
        # enable lighting and place light source
        self.shader_set(self.shader_lighting)
        x, y, z, _ = self.modelview_matrix @ self.system._relative_position
        glUniform3f(self.lighting_source, x, y, z)
        # draw planets and moons (with lighting)
        for body in bodies:
            if body is self.system:
                continue
            self.draw_body(body)
        # clean
        self.shader_set()
        self.sphere.unbind()

        # draw circles around celestial bodies when from far away
        glPointSize(20)
        glDepthMask(False)
        self.shader_set(self.shader_position_marker)
        self.set_color(1, 0, 0, 0.5)
        glBegin(GL_POINTS)
        for body in bodies:
            self.add_pick_object(body, GL_POINTS)
            glVertex3f(*body._relative_position)
        glEnd()
        # clean
        self.shader_set()
        glDepthMask(True)

        # draw orbits
        glPointSize(5)
        self.set_color(1.0, 1.0, 0.0, 0.2)
        original_modelview_matrix = self.modelview_matrix
        for body in descendants:  # skip ancestors (see below)
            self.set_modelview_matrix(
                original_modelview_matrix @
                Mat4.translate(*body.orbit.primary._relative_position)
            )
            self.add_pick_object(body)
            if not hasattr(body.orbit, "mesh"):
                body.orbit.mesh = gspyce.mesh.OrbitMesh(body.orbit)
                body.orbit.apses_mesh = gspyce.mesh.ApsesMesh(body.orbit)
            body.orbit.mesh.draw()
            body.orbit.apses_mesh.draw()
        self.set_modelview_matrix(original_modelview_matrix)

        # separately draw orbits of ancestors
        # since the focused celestial body  and its ancestors are relatively
        # close to the camera, it is best to draw them with the origin the
        # orbit, rather than at the primary
        self.set_color(1.0, 1.0, 0.0, 1.0)
        for body in ancestors:
            if body.orbit is None:
                continue
            original_modelview_matrix = self.modelview_matrix
            self.set_modelview_matrix(
                self.modelview_matrix @
                Mat4.translate(*body._relative_position)
            )
            self.add_pick_object(body)
            gspyce.mesh.FocusedOrbitMesh(body.orbit, self.time).draw()
            gspyce.mesh.FocusedApsesMesh(body.orbit, self.time).draw()
            self.set_modelview_matrix(original_modelview_matrix)

    def set_and_draw(self):
        """Setup the camera and draw"""

        # reset everything
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.pick_reset()
        self.shader_set()

        # skybox
        self.shader_set(self.shader_skybox)
        self.set_modelview_matrix(
            Mat4.rotate(math.radians(self.phi),   1, 0, 0) @
            Mat4.rotate(math.radians(self.theta), 0, 0, 1)
        )
        glDisable(GL_DEPTH_TEST)
        self.skybox.draw()
        glEnable(GL_DEPTH_TEST)
        self.shader_set()

        # set up camera
        self.set_modelview_matrix(
            Mat4.translate(0, 0, -1/self.zoom) @
            Mat4.rotate(math.radians(self.phi),   1, 0, 0) @
            Mat4.rotate(math.radians(self.theta), 0, 0, 1)
        )

        self.draw()
        self.clear_pick_object()

    def draw_hud(self):
        """Draw the HUD"""
        self.hud_print("Focus: %s\n" % self.focus)
        super().draw_hud()

    @glut_callback
    def mouseFunc(self, button, state, x, y):
        """Handle mouse clicks (GLUT callback)"""
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # body selection
            self.focus = self.pick(x, y, self.focus)
            self.update()
        else:
            super().mouseFunc(button, state, x, y)


def main():
    with SystemGUI.from_cli_args() as gui:
        gui.main()


if __name__ == '__main__':
    main()
