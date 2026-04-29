from os.path import join
import sys
import packaging.version

import sh
from pythonforandroid.recipe import PyProjectRecipe
from pythonforandroid.toolchain import current_directory, shprint


def is_kivy_affected_by_deadlock_issue(recipe=None, arch=None):
    with current_directory(join(recipe.get_build_dir(arch.arch), "kivy")):
        kivy_version = shprint(
            sh.Command(sys.executable),
            "-c",
            "import _version; print(_version.__version__)",
        )

        return packaging.version.parse(
            str(kivy_version)
        ) < packaging.version.Version("2.2.0.dev0")


class KivyRecipe(PyProjectRecipe):
    """Custom Kivy recipe that pins build<1.4.0 to avoid isolated environment issues.
    
    build 1.4.0+ (Jan 2026) changed behavior for pyproject.toml files without explicit
    build-backend, forcing setuptools.build_meta:__legacy__ which fails in p4a's
    hostpython environment. build 1.3.0 correctly falls back to setup.py.
    """
    version = '2.3.0'
    url = 'https://github.com/kivy/kivy/archive/{version}.zip'
    name = 'kivy'

    depends = [('sdl2', 'sdl3'), 'pyjnius', 'setuptools', 'android']
    python_depends = ['certifi', 'chardet', 'idna', 'requests', 'urllib3', 'filetype']
    
    # Pin build<1.4.0 to avoid isolated environment issues with setuptools.build_meta
    # Also include cython as required by Kivy
    hostpython_prerequisites = ["cython>=0.29.1,<=3.0.12", "build<1.4.0"]

    # sdl-gl-swapwindow-nogil.patch is needed to avoid a deadlock.
    # See: https://github.com/kivy/kivy/pull/8025
    patches = [("sdl-gl-swapwindow-nogil.patch", is_kivy_affected_by_deadlock_issue), "use_cython.patch"]

    @property
    def need_stl_shared(self):
        if "sdl3" in self.ctx.recipe_build_order:
            return True
        else:
            return False

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)

        # Taken from CythonRecipe
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{} '.format(
            self.ctx.get_libs_dir(arch.arch) +
            ' -L{} '.format(self.ctx.libs_dir) +
            ' -L{}'.format(join(self.ctx.bootstrap.build_dir, 'obj', 'local',
                                arch.arch)))
        env['LDSHARED'] = env['CC'] + ' -shared'
        env['LIBLINK'] = 'NOTNONE'

        # NDKPLATFORM is our switch for detecting Android platform, so can't be None
        env['NDKPLATFORM'] = "NOTNONE"
        if 'sdl2' in self.ctx.recipe_build_order:
            env['USE_SDL2'] = '1'
            env['KIVY_SPLIT_EXAMPLES'] = '1'
            sdl2_mixer_recipe = self.get_recipe('sdl2_mixer', self.ctx)
            sdl2_image_recipe = self.get_recipe('sdl2_image', self.ctx)
            env['KIVY_SDL2_PATH'] = ':'.join([
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
                *sdl2_image_recipe.get_include_dirs(arch),
                *sdl2_mixer_recipe.get_include_dirs(arch),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
            ])
        if "sdl3" in self.ctx.recipe_build_order:
            sdl3_mixer_recipe = self.get_recipe("sdl3_mixer", self.ctx)
            sdl3_image_recipe = self.get_recipe("sdl3_image", self.ctx)
            sdl3_ttf_recipe = self.get_recipe("sdl3_ttf", self.ctx)
            sdl3_recipe = self.get_recipe("sdl3", self.ctx)
            env["USE_SDL3"] = "1"
            env["KIVY_SPLIT_EXAMPLES"] = "1"
            env["KIVY_SDL3_PATH"] = ":".join(
                [
                    *sdl3_mixer_recipe.get_include_dirs(arch),
                    *sdl3_image_recipe.get_include_dirs(arch),
                    *sdl3_ttf_recipe.get_include_dirs(arch),
                    *sdl3_recipe.get_include_dirs(arch),
                ]
            )

        return env


recipe = KivyRecipe()
