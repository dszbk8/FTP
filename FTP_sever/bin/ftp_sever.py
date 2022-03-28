
import sys,os
# lst = __file__.split('/')   #切割当前文件  __file__拿到当前文件的绝对路径
# base_path  = '/'.join(lst[:-2])
# sys.path.append(base_path)
# from FTP_sever.core import main

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PATH)

from core import main

if __name__ == '__main__':
    main.ArgvHandler()




