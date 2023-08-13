import shutil
from pathlib import Path
import sys
import subprocess

comfy_path = Path(__file__).parent.parent.parent
extension_path = Path(__file__).parent
js_path = comfy_path / "web" / "extensions"


def packages(versions=False):
    import sys
    import subprocess
    return [(r.decode().split('==')[0] if not versions else r.decode()) for r in
            subprocess.check_output([sys.executable, '-s', '-m', 'pip', 'freeze']).split()]


def copy_web_extensions():
    shutil.copy(extension_path / "web-extensions/dp.js", str(js_path))


def pip_install(pkg):
    if pkg not in packages():
        print(f"installing {pkg}")
        subprocess.check_call([sys.executable, '-s', '-m', 'pip', '-q', 'install', f'{pkg}'])

def install():
    pip_install("pygoogletranslation")
    pip_install("googletrans==4.0.0-rc1")
    pip_install("dynamicprompts")

    copy_web_extensions()

install()