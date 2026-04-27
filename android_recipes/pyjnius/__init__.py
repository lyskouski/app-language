from pythonforandroid.recipes.pyjnius import PyjniusRecipe as OriginalPyjniusRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory
import sh
import os


class PyjniusRecipe(OriginalPyjniusRecipe):
    """
    Custom PyJNIus recipe that completely bypasses pyproject.toml/PEP 517
    and uses traditional setup.py install to avoid isolated environment issues.

    The issue: PyJNIus has a pyproject.toml that declares it uses setuptools.build_meta.
    When p4a builds it with the modern backend, it creates an isolated environment where
    setuptools fails to import properly. This recipe removes all modern build config and
    uses the legacy setup.py approach instead.
    """

    # Clear patches - we don't need them and they reference files we don't have
    patches = []

    def build_arch(self, arch):
        """
        Override to:
        1. Run parent's base Recipe.build_arch() for any NDK setup
        2. Compile Cython components (essential for PyJNIus .pyx files)
        3. Remove pyproject.toml to force legacy setup.py
        4. Call setup.py install directly
        """
        from pythonforandroid.recipe import Recipe

        build_dir = self.get_build_dir(arch.arch)

        # Step 1: Run base build (handles NDK and recipe-level setup)
        Recipe.build_arch(self, arch)

        # Step 2: Compile Cython components (.pyx -> .c)
        info('Building Cython components for PyJNIus')
        env = self.get_recipe_env(arch)

        # Find all .pyx files in the source tree
        pyx_files = []
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith('.pyx'):
                    pyx_files.append(os.path.join(root, file))

        if pyx_files:
            info(f'Found {len(pyx_files)} Cython files to compile')
            # Try compiling each .pyx file
            with current_directory(build_dir):
                for pyx_file in pyx_files:
                    rel_path = os.path.relpath(pyx_file, build_dir)
                    info(f'Compiling {rel_path} with Cython...')
                    try:
                        # Method 1: Try using python -m cython (most reliable)
                        shprint(
                            sh.Command(self.hostpython_location),
                            '-m', 'cython',
                            pyx_file,
                            _env=env
                        )
                        info(f'✓ Successfully compiled {rel_path}')
                    except Exception as e:
                        # This is non-fatal - setup.py might compile inline
                        info(f'Note: Cython pre-compilation of {rel_path} skipped: {e}')
                        continue
        else:
            info('No .pyx files found in PyJNIus source')

        # Step 3: Remove modern build configurations to force legacy setup.py
        files_to_remove = [
            os.path.join(build_dir, 'pyproject.toml'),
            os.path.join(build_dir, 'setup.cfg'),
            os.path.join(build_dir, 'MANIFEST.in'),
        ]

        for filepath in files_to_remove:
            if os.path.exists(filepath):
                info(f'Removing {os.path.basename(filepath)} to force setup.py')
                os.remove(filepath)

        # Step 4: Verify setup.py exists
        setup_py = os.path.join(build_dir, 'setup.py')
        if not os.path.exists(setup_py):
            raise Exception('setup.py not found in PyJNIus source')

        # Step 5: Get the environment and install using setup.py
        info('Installing PyJNIus using setup.py')

        with current_directory(build_dir):
            shprint(
                sh.Command(self.hostpython_location),
                'setup.py',
                'install',
                '-O2',
                '--root={}'.format(self.ctx.get_python_install_dir(arch.arch)),
                '--install-lib=.',
                _env=env,
                *self.setup_extra_args
            )

        info('PyJNIus build completed successfully')

recipe = PyjniusRecipe()
