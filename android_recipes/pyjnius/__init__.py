from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.toolchain import shprint, current_directory, info
from pythonforandroid.patching import will_build
import sh
from os.path import join


class PyjniusRecipe(PythonRecipe):
    """
    Custom PyJNIus recipe using PythonRecipe instead of PyProjectRecipe.

    PyProjectRecipe always calls 'python -m build' with isolated environments that fail.
    PythonRecipe uses traditional 'setup.py install', which works with p4a's environment.

    This recipe replicates the environment setup from the original but uses the simpler
    PythonRecipe base class that doesn't require modern build tools.
    """

    version = '1.7.0'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    name = 'pyjnius'
    depends = [('genericndkbuild', 'sdl2', 'sdl3'), 'six']
    site_packages_name = 'jnius'

    # Use hostpython to install, with Cython available
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def get_recipe_env(self, arch, **kwargs):
        """Environment setup copied from original PyProjectRecipe-based recipe"""
        env = super().get_recipe_env(arch, **kwargs)

        # Critical LDFLAGS for Android JNI linking
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{} '.format(
            self.ctx.get_libs_dir(arch.arch) +
            ' -L{} '.format(self.ctx.libs_dir) +
            ' -L{}'.format(join(self.ctx.bootstrap.build_dir, 'obj', 'local', arch.arch)))

        env['LDSHARED'] = env['CC'] + ' -shared'
        env['LIBLINK'] = 'NOTNONE'

        # NDKPLATFORM signals Android build mode to setup.py
        env['NDKPLATFORM'] = "NOTNONE"

        return env

    def prebuild_arch(self, arch):
        """Ensure Cython is available in hostpython"""
        super().prebuild_arch(arch)
        # Cython is needed for setup.py to work
        self.install_hostpython_prerequisites(packages=['Cython<3.2'])

    def postbuild_arch(self, arch):
        """Copy PyJNIus Java classes to build directory (from original recipe)"""
        super().postbuild_arch(arch)
        info('Copying pyjnius java class to classes build dir')
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.cp, '-a', join('jnius', 'src', 'org'), self.ctx.javaclass_dir)


recipe = PyjniusRecipe()
