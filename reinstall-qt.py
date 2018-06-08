import os
from subprocess import call

import pathlib
from pathlib import Path


def execMV(*args):
    print("[MV] [exec]", *args)
    call(*args)


def confirmExit():
    print("[MV] The script will now exit-")
    inp = input()
    if inp and inp[0] in "dp":
        try:
            raise RunTimeError
        except RunTimeError:
            import pdb
            pdb.post_mortem()



# Relative location, within the project root directory
condaRelativeLocation = "lib/miniconda/Scripts/conda.exe"

# Establishing the list of directories to search for the executable
filedir = Path(__file__).absolute().parent
rootLocationList = []
for di in [filedir, filedir.parent, filedir.parent.parent, Path("C:/Metravision")]:
    rootLocationList.append(di)
    rootLocationList.append(di / "metravision")
    rootLocationList.append(di / "Metravision") # Useless if on Windows


for rootLocation in rootLocationList:
    metravisionRoot = Path(rootLocation).absolute()

    condaPath = pathlib.WindowsPath(metravisionRoot / condaRelativeLocation)
    if condaPath.is_file():
        print(f"[MV] Found {str(condaPath)}")
        break
else:
    # If break didn't occure
    print(
        f"[MV] Couldn't find '{condaRelativeLocation}' within directories:",
        '\n'.join(map(str,[""] + rootLocationList))
    )
    confirmExit()

os.chdir(str(condaPath.parent.parent))

try:
    execMV(str(condaPath), *"remove qt".split())
    execMV(str(condaPath), *"install -c conda-forge opencv".split())
    confirmExit()
except Exception: # pylint: disable=broad-except
    import pdb, traceback
    traceback.print_exc()
    pdb.post_mortem()