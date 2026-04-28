from pythonforandroid.recipe import CythonRecipe
from pythonforandroid.toolchain import shprint, current_directory, info
import sh
from os.path import join


class PyjniusRecipe(CythonRecipe):
    """
    Custom PyJNIus recipe using CythonRecipe to handle .pyx -> .c compilation.

    PyProjectRecipe (used by original) calls 'python -m build' with isolated environments that fail.
    CythonRecipe compiles Cython files then uses 'setup.py install', avoiding build isolation.

    Key differences from original:
    - No patches (they don't exist locally and may not be essential)
    - Uses CythonRecipe's build_cython_components() to generate .c files
    - Preserves Android-specific environment setup (NDKPLATFORM, LDFLAGS)
    """

    version = '1.7.0'
    url = 'https://github.com/kivy/pyjnius/archive/{version}.zip'
    name = 'pyjnius'
    depends = [('genericndkbuild', 'sdl2', 'sdl3'), 'six']
    site_packages_name = 'jnius'

    # No patches - they don't exist in local recipes and build may work without them
    patches = []

    # Cython needed for .pyx compilation
    hostpython_prerequisites = ["Cython<3.2"]

    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch, **kwargs):
        """Add NDKPLATFORM to signal Android build mode to PyJNIus setup.py"""
        env = super().get_recipe_env(arch, **kwargs)

        # NDKPLATFORM tells setup.py to use Android mode
        # (CythonRecipe already sets LDFLAGS, LDSHARED, LIBLINK correctly)
        env['NDKPLATFORM'] = "NOTNONE"

        return env

    def postbuild_arch(self, arch):
        """Copy PyJNIus Java classes to build directory (from original recipe)"""
        super().postbuild_arch(arch)
        info('Copying pyjnius java class to classes build dir')
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.cp, '-a', join('jnius', 'src', 'org'), self.ctx.javaclass_dir)


recipe = PyjniusRecipe()
