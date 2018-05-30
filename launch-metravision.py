import os

import pathlib
from pathlib import Path

fdir = Path(__file__).parent

pythonExecutableName = "python.exe"

rootLocationList = []
for di in [fdir, fdir.parent, fdir.parent.parent, "C:/Metravision"]:
    rootLocationList.append(di)
    rootLocationList.append(di / "metravision")

for rootLocation in rootLocationList:
    metravisionRoot = Path(rootLocation).absolute()

    mainPath = pathlib.WindowsPath(metravisionRoot / "src/main.py")
    if mainPath.is_file():
        print(f"[MV] Found {str(mainPath)}")
        pythonPath = metravisionRoot / "lib/miniconda" / pythonExecutableName
        break
else:
    # If break didn't occure
    print(f"""[MV] Couldn't find 'src/main.py' within directories:{'\n'.join(map(str,[""] + rootLocationList))}""")


# Environement manipulation maybe unnecessary
os.environ["PYTHONIOENCODING"] = "UTF-8"
os.environ["PYTHONUNBUFFERED"] = "1"

os.chdir(str(metravisionRoot))


try:
    print(f"os.execve({str(pythonPath)}, [{pythonExecutableName}, {str(mainPath)}], os.environ)")
    os.execve(str(pythonPath), [pythonExecutableName, str(mainPath)], os.environ)
    input()
except Exception: # pylint: disable=broad-except
    import pdb, traceback
    traceback.print_exc()
    pdb.post_mortem()