from openpyxl import Workbook

"""
def cleanCells(destFile)
    "Clear all file's cells"
    wb = Workbook()
    ws = wb.active
    if ws['A1'] is not None:
"""
def writeFile(fileData):
    wb = Workbook()
    # grab the active worksheet
    ws = wb.active
    i=0
    print(len(fileData))
    for i, par in enumerate(fileData):
        ws.cell(row=i+1, column=1).value = par[0]
        ws.cell(row=i+1, column=2).value = par[1]
    
    # Save the file
    wb.save("results.xlsx")