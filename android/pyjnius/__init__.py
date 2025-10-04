from pythonforandroid.recipe import CythonRecipe

class PyJNIusRecipe(CythonRecipe):
    name = "pyjnius"
    version = "master"
    url = "https://github.com/kivy/pyjnius/archive/master.zip"
    depends = ["python3"]
    cythonize = True

recipe = PyJNIusRecipe()