#!/usr/bin/python3
"""
Script to help launch metravision, finding and using the conda environnement.
"""


import os
import sys
import pdb, traceback


try:
    from subprocess import call
    from pathlib import Path

    isWindows = (os.name == "nt")


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


    def confirmExit(retcode=0):
        print("[MV] The script will exit when Enter is pressed.")
        inp = input()
        if inp and inp[0] in "dp":
            try:
                raise RuntimeError
            except RuntimeError:
                pdb.post_mortem()
        else:
            exit(retcode)


    # Relative location, within the project root directory
    mainRelativeLocation = "src/main.py"

    # Establishing the list of directories to search for the executable
    filedir = Path(__file__).absolute().parent
    rootLocationList = []
    for di in [filedir, filedir.parent, filedir.parent.parent, Path("C:/Metravision")]:
        rootLocationList.append(di)
        rootLocationList.append(di / "metravision")
        rootLocationList.append(di / "Metravision") # Useless if on Windows

    # Finding the python sources
    for rootLocation in rootLocationList:
        metravisionRoot = Path(rootLocation).absolute()
        mainPath = Path(metravisionRoot / mainRelativeLocation)
        if mainPath.is_file():
            print(f"[MV] Found {str(mainPath)}")
            break
    else:
        # If break didn't occur
        print(
            f"[MV] Couldn't find '{mainRelativeLocation}' within directories:",
            '\n'.join(map(str,[""] + rootLocationList)),
        )
        confirmExit(retcode=2)
    
    # Finding the python environnement
    # Relative location within the conda directory
    pythonRelativeLocation = "python.exe" if isWindows else "bin/python"
    condaLocationList = []
    condaParentLocationList = [Path("/"), Path.home(), rootLocation / "lib", rootLocation.parent]
    if not isWindows:
        condaParentLocationList.append(Path("/opt"))
        condaParentLocationList.append(Path.home() / "opt")
    for di in condaParentLocationList:
        condaLocationList.append(di / "conda")
        condaLocationList.append(di / "Miniconda")
        condaLocationList.append(di / "miniconda")
        condaLocationList.append(di / "Miniconda3")
        condaLocationList.append(di / "miniconda3")

    # COPYPASTA COPYPASTA COPYPASTA COPYPASTA COPYPASTA COPYPASTA COPYPASTA
    # Finding the python sources
    for condaLocation in condaLocationList:
        condaRoot = Path(condaLocation).absolute()
        pythonPath = Path(condaRoot / pythonRelativeLocation)
        if pythonPath.is_file():
            print(f"[MV] Found {str(pythonPath)}")
            break
    else:
        # If break didn't occur
        print(
            f"[MV] Couldn't find '{pythonPath}' within directories:",
            '\n'.join(map(str,[""] + condaLocationList))
        )
        confirmExit(retcode=4)

    # Environement manipulation maybe unnecessary
    os.environ["PYTHONIOENCODING"] = "UTF-8"
    os.environ["PYTHONUNBUFFERED"] = "1"

    os.chdir(str(metravisionRoot))

    execMV(str(pythonPath), str(mainPath), *sys.argv[1:], replace=True)
    confirmExit(retcode=255)
except Exception: # pylint: disable=broad-except
    traceback.print_exc()
    pdb.post_mortem()