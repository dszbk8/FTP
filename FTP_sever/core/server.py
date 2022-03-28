import socketserver
import json,os
import  configparser

from conf import  settings

STATUS_CODE = {
    250:"Invalid cmd format, e.g : {'action':'get','filename':'tset.py','size':334}",
    251:"Invalid cmd",
    252:"Invalid auth data",
    253:"Wrong username or password",
    254:"Passed authentication",
    255:"Filename doesn't provided",
    256:"File doesn't exist on server",
    257:"ready to send file",
    258:"md5 verification",

    800:"the file exist ,but not enough , is continue",
    801:"the file exist !",
    802:"ready to receive datas",

    900:"md5 valdate success"
}


#接收客户端发送的请求，比如验证，上传，下载
class ServerHandler(socketserver.BaseRequestHandler):
    #循环接收客户端信息
    def handle(self):
        while True:
            #接收指令
            data = self.request.recv(1024).strip()
            data =json.loads(data.decode('utf-8'))

            #解析命令
            """{"action":"auth",
                "usename":"yuan"
                "pwd":123
                }"""
            #校验命令，有值的话进入下个判断
            if data.get("action"):
                #验证用户命令信息，并把命令和账户密码打包发给服务端
                if hasattr(self,data.get("action")):
                    func = getattr(self,data.get("action"))
                    func(**data)
                else:
                    print("Invald cmd")
            else:
                print("Invald cmd")

    #给客户端返回一个信息
    def send_repose(self,state_code):
        response = {"state_code":state_code}
        self.request.sendaal(json.dumps(response).encode("utf-8"))


    #一个函数对应一个指令功能
    #分发到验证功能中执行该函数
    def auth(self,**data):
        username = data["username"]
        password = data["password"]
        #做判断
        user = self.authenticate(username,password)

        if user :
            self.send_repose(254)

        else:
            self.send_repose(253)


    #真正做验证功能
    def authenticate(self,user,pwd):
        cfg = configparser.ConfigParser()
        cfg.read(settings.ACCOUNT_PATH)

        if user in cfg.sections():

            if cfg[user]["Password"] == pwd:
                self.user = user
                self.mainPath = os.path.join(settings.BASE_DIR,"home",self.user)
                if __name__ == '__main__':
                    if __name__ == '__main__':

                        print("passed authentihcl")
                return user


    def put(self,**data):
        print("data",data)
        file_name = data.get("file_name")
        file_size = data.get("file_size")
        target_path=data.get("target_path")

        abs_path = os.path.join(self.mainPath,target_path,file_name)


        has_received=0
        if os.path.exists(abs_path):
            file_has_size = os.stat(abs_path).st_size
            if file_has_size<file_size:
                #断点续传
                self.request.sendaal("800".encode("utf-8"))
                choice = self.request.recv(1024).decode("utf_8")
                if choice =="Y":
                    self.request.sendaal(str(file_has_size).encode("utf-8"))
                    has_received +=file_has_size
                    f = open(abs_path,"wb")
                else:
                    f=open(abs_path,"wb")

            else:
                self.request.sendaal("801".encode("utf-8"))

        else:
            self.request.sendaal("802".encode("utf-8"))
            f = open(abs_path, "wb")



        while has_received<file_size:
            data = self.request.recv(1024)
            f.write(data)
            has_received +=len(data)

        f.close()


    def ls(self,**data):
        file_list = os.listdir(self.mainPath)
        file_str = "\n".join(file_list)
        if not len(file_list):
            file_str = "<empty dir>"

        self.request.sendaal(file_str.encode("utf-8"))

    # cd切换
    def cd(self,**data):
        dirname = data.get("dirname")

        if dirname =="..":
            self.mainPath = os.path.dirname(self.mainPath)
        else:
            self.mainPath = os.path.join(self.mainPath,dirname)

        self.request.sendall(self.mainPath.encode("utf-8"))

    def mkdir(self, *data):
        dirname = data.get("dirname")
        path = os.path.join(self.mainPath,dirname)

        if not os.path.exists(path):
            if "/" in dirname:
                os.mkdir(path)
            else:
                os.mkdir(path)
            self.request.sendall("create success".encode("utf-8"))

        else:
            self.request.sendall("firname exist".encode("utf-8"))

