# -*- coding: UTF-8 -*-

# import glob as __glob__
# import os as __os__


# def __getModules():
#     _ext = []
#     _ext_dir = __os__.path.dirname(__file__)
#     for file_ in __glob__.glob(_ext_dir + "/*.py"):
#         if file_ == "__init__.py":
#             continue
#         _ext_name = __os__.path.basename(file_).split('.py')[0]
#         if _ext_name == "__init__":
#             continue
#         _ext.append('sssa.helpers.' + _ext_name)
#     return _ext

# modules = map(__import__, __getModules())
# del __glob__
# del __os__

import os
modules = []
for module in os.listdir(os.path.dirname(__file__)):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    modules.append('sssa.helpers.' + module[:-3])
    __import__(module[:-3], locals(), globals())
del module
del os
