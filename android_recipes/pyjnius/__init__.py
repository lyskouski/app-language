from pythonforandroid.recipe import CythonRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.toolchain import current_directory
from pythonforandroid.patching import will_build
import sh
from os.path import join
import os


class PyjniusRecipe(CythonRecipe):
    """
    Custom PyJNIus recipe using CythonRecipe to bypass PyProjectRecipe's 'python -m build'.

    Inherits from CythonRecipe instead of the original PyjniusRecipe (which uses PyProjectRecipe).
    This forces traditional setup.py install, avoiding isolated build environment issues.
    """

    version = '1.7.0'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    name = 'pyjnius'
    depends = [('genericndkbuild', 'sdl2', 'sdl3'), 'six']
    site_packages_name = 'jnius'
    hostpython_prerequisites = ["Cython<3.2"]

    # Patches removed - we don't have them locally and they may not be critical
    patches = []

    call_hostpython_via_targetpython = False

    def prebuild_arch(self, arch):
        """Remove pyproject.toml BEFORE parent prebuild runs"""
        build_dir = self.get_build_dir(arch.arch)

        # Remove modern build files before any detection
        pyproject = join(build_dir, 'pyproject.toml')
        if os.path.exists(pyproject):
            info('Removing pyproject.toml to force traditional setup.py build')
            os.remove(pyproject)

        setup_cfg = join(build_dir, 'setup.cfg')
        if os.path.exists(setup_cfg):
            info('Removing setup.cfg')
            os.remove(setup_cfg)

        # Now call parent prebuild
        super().prebuild_arch(arch)

    def get_recipe_env(self, arch, **kwargs):
        """Custom environment variables for PyJNIus Android build"""
        env = super().get_recipe_env(arch, **kwargs)

        # From original recipe - needed for Android JNI
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{} '.format(
            self.ctx.get_libs_dir(arch.arch) +
            ' -L{} '.format(self.ctx.libs_dir) +
            ' -L{}'.format(join(self.ctx.bootstrap.build_dir, 'obj', 'local', arch.arch)))
        env['LDSHARED'] = env['CC'] + ' -shared'
        env['LIBLINK'] = 'NOTNONE'

        # NDKPLATFORM is the switch for detecting Android platform
        env['NDKPLATFORM'] = "NOTNONE"
        return env

    def postbuild_arch(self, arch):
        """Copy Java classes to build directory"""
        super().postbuild_arch(arch)
        info('Copying pyjnius java class to classes build dir')
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.cp, '-a', join('jnius', 'src', 'org'), self.ctx.javaclass_dir)


recipe = PyjniusRecipe()
