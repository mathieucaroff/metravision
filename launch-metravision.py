import os

from pathlib import Path

rootLocationList = [".", "metravision", "C:/Metravision/metravision"]

for rootLocation in rootLocationList:
    metravisionRoot = Path(rootLocation).absolute()

    pythonExecutableName = "python.exe"

    pythonPath = metravisionRoot / "lib/miniconda" / pythonExecutableName
    mainPath = metravisionRoot / "src/main.py"
    if mainPath.is_file():
        print(f"[MV] Found {str(mainPath)}")
        break
else:
    # If break didn't occure
    print(f"[MV] Couldn't find 'src/main.py' within directories: {rootLocationList}")


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