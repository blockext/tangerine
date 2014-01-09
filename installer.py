import json
import os
from pprint import pprint
import shutil
import sys
import traceback
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import pkg_resources
from setuptools.command import easy_install
from blockext import *



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def init():
    global packages_dir
    cwd = os.path.dirname(os.path.abspath(__file__))
    prefix = os.path.join(cwd, "extensions")
    packages_dir = os.path.join(prefix, "packages")

    for path in [prefix, packages_dir]:
        if not os.path.exists(path):
            os.mkdir(path)

    sys.path.insert(0, packages_dir)
    for name in os.listdir(packages_dir):
        path = os.path.join(packages_dir, name)
        sys.path.insert(0, path)

    os.environ["PYTHONPATH"] = packages_dir

init()


@handler("")
def index(is_browser=False):
    if not is_browser: return ("text/plain", "denied")

    return ("text/html", open(resource_path("index.html"), "rb").read())


def cmd(func):
    @handler(func.__name__)
    def wrapper(*args, **kwargs):
        if not kwargs["is_browser"]: return ("text/plain", "denied")
        init()
        result = func(*args)
        pprint(result)
        if result.get("traceback"):
            print("\n" + result.get("traceback"))
        data = json.dumps(result, indent=4, sort_keys=True)
        return ("application/json", data)
    return wrapper


@cmd
def install(name):
    sys.stdout = sys.stderr = ei_stdout = StringIO()
    try:
        easy_install.main(["--install-dir", packages_dir,
                           "--exclude-scripts",
                           name])
    except SystemExit as e:
        output = ei_stdout.getvalue()
        tb = StringIO()
        traceback.print_exc(8, tb)
        return {
            "success": False,
            "error": unicode(e),
            "traceback": tb.getvalue(),
            "output": output,
        }
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    for name in os.listdir(packages_dir):
        path = os.path.join(packages_dir, name)
        if path not in sys.path:
            sys.path.insert(0, path)

    return {
        "success": True,
        "output": ei_stdout.getvalue(),
    }


@cmd
def list_installed():
    return {"packages": list(pkg_resources.Environment(
        os.path.join(packages_dir, name) for name in os.listdir(packages_dir)
    ))}


@cmd
def test(name):
    try:
        __import__(name)
    except ImportError:
        return {"import_successful": False}
    else:
        return {"import_successful": True}


@cmd
def modules(name):
    import pkgutil
    return list(pkgutil.iter_modules(name))



blockext.run("Blockext Installer", "blockext", 9002)

