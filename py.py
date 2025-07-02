import ctypes

dll_path = r"C:\Users\BIBLIOTECA01\AppData\Local\Programs\Python\Python313\Lib\site-packages\pyzbar\libzbar-64.dll"
ctypes.cdll.LoadLibrary(dll_path)

from pyzbar import pyzbar

print("pyzbar funcionando!")
