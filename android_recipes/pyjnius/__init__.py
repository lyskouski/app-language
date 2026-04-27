from pythonforandroid.recipes.pyjnius import PyjniusRecipe as OriginalPyjniusRecipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
import sh


class PyjniusRecipe(OriginalPyjniusRecipe):
    """
    Custom PyJNIus recipe that forces traditional setup.py build
    to avoid isolated environment issues with python -m build
    """

    # Clear patches - we don't need them and they reference files we don't have
    patches = []

    # Force the recipe to NOT use call_hostpython_via_targetpython
    # This makes it use the traditional build approach
    call_hostpython_via_targetpython = False

    # Don't override build_arch - let parent handle Cython compilation
    # The call_hostpython_via_targetpython = False is enough to avoid
    # the modern build system issues


recipe = PyjniusRecipe()

