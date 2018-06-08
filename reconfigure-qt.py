import os
from subprocess import call

import pathlib
from pathlib import Path


def execMV(*args, replace=False):
    executablePath = Path(args[0]).absolute()
    executableLocation = str(executablePath)
    if replace:
        print("[MV] [exec]", *args)
    else:
        print("[MV] [call]", *args)
    
    if replace:
        executableName = str(executablePath.name)
        os.execv(str(executablePath), [executableName, *args[1:]])
    else:
        call([executableLocation, *args[1:]])


def confirmExit():
    print("[MV] The script will exit when Enter is pressed.")
    inp = input()
    if inp and inp[0] in "dp":
        try:
            raise RunTimeError
        except RunTimeError:
            import pdb
            pdb.post_mortem()


try:
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

    execMV(str(condaPath), *"remove -y qt".split(), replace=False)
    execMV(str(condaPath), *"install -y -c conda-forge opencv".split(), replace=False)
    confirmExit()
except Exception: # pylint: disable=broad-except
    import pdb, traceback
    traceback.print_exc()
    pdb.post_mortem()