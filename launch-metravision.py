#!/usr/bin/python3
import os
import sys
from subprocess import call

import pdb, traceback

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
            raise RuntimeError
        except RuntimeError:
            pdb.post_mortem()


try:
    # Relative location, within the project root directory
    pythonRelativeLocation = "lib/miniconda/python.exe"
    mainRelativeLocation = "src/main.py"

    # Establishing the list of directories to search for the executable
    filedir = Path(__file__).absolute().parent
    rootLocationList = []
    for di in [filedir, filedir.parent, filedir.parent.parent, Path("C:/Metravision")]:
        rootLocationList.append(di)
        rootLocationList.append(di / "metravision")
        rootLocationList.append(di / "Metravision") # Useless if on Windows


    for rootLocation in rootLocationList:
        metravisionRoot = Path(rootLocation).absolute()

        mainPath = Path(metravisionRoot / mainRelativeLocation)
        if mainPath.is_file():
            print(f"[MV] Found {str(mainPath)}")
            pythonPath = Path(metravisionRoot / pythonRelativeLocation)
            break
    else:
        # If break didn't occure
        print(
            f"[MV] Couldn't find '{mainRelativeLocation}' within directories:",
            '\n'.join(map(str,[""] + rootLocationList))
        )
        confirmExit()

    if not pythonPath.is_file():
        print(f"[MV] Missing '{pythonRelativeLocation}'")
        confirmExit()


    # Environement manipulation maybe unnecessary
    os.environ["PYTHONIOENCODING"] = "UTF-8"
    os.environ["PYTHONUNBUFFERED"] = "1"

    os.chdir(str(metravisionRoot))

    execMV(str(pythonPath), str(mainPath), *sys.argv[1:], replace=True)
    confirmExit()
except Exception: # pylint: disable=broad-except
    traceback.print_exc()
    pdb.post_mortem()