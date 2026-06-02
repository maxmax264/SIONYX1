import ctypes
user32 = ctypes.windll.user32
w = user32.GetSystemMetrics(0)
h = user32.GetSystemMetrics(1)
print(f'Screen: {w}x{h}')
