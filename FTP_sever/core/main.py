import optparse

import socketserver

from conf import settings

from core import server

#解析输入行的命令  如：start
class ArgvHandler():
    def __init__(self):
        self.op = optparse.OptionParser()   #参数解析功能

        # self.op.add_option("-s",'--server',dest = "server")
        # self.op.add_option("-P","--port",dest = "port")
        options,args = self.op.parse_args()

        self.verify_args(options,args)

    # 分发验证
    def verify_args(self,options,args):
        cmd =args[0]


        if hasattr(self,cmd):
            func = getattr(self,cmd)
            func()
    #启动socketserver，对应找到server.ServerHandler类，执行相应Handle方法
    def start(self):
        print("the server is working....")
        s = socketserver.ThreadingTCPServer((settings.IP,settings.PORT),server.ServerHandler)
        s.serve_forever()

