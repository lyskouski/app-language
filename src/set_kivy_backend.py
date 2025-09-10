## For GitHub CI/CD fatal error is taken:
# [CRITICAL] [GL] Minimum required OpenGL version (2.0) NOT found!
import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
