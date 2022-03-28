
import optparse
import socket
import json
import os,sys

STATUS_CODE = {
    250: "Invalid cmd format, e.g : {'action':'get','filename':'tset.py','size':334}",
    251: "Invalid cmd",
    252: "Invalid auth data",
    253: "Wrong username or password",
    254: "Passed authentication",
    255: "Filename doesn't provided",
    256: "File doesn't exist on server",
    257: "ready to send file",
    258: "md5 verification",

    800: "the file exist ,but not enough , is continue",
    801: "the file exist !",
    802: "ready to receive datas",

    900: "md5 valdate success"
    }


class ClientHandler():
    def __init__(self):
        #访问ip地址端口
        self.op=optparse.OptionParser()

        self.op.add_option("-s","--server",dest = "server")
        self.op.add_option("-p", "--port", dest="port")
        self.op.add_option("-u", "--username", dest="username")
        self.op.add_option("-p", "--password", dest="password")

        #参数解析
        self.options,self.args = self.op.parse_args()
        #参数验证
        self.verify_args(self.options,self.args)

        self.make_connection()  #创建一个连接
        self.mainPath = os.path.dirname(os.path.abspath(__file__))
        self.last = 0

    #获取参数，判断端口合不合法
    def verify_args(self,options,args):
        server = options.server
        port = options.port
        # username = options.username
        # password = options.password

        #对port校验
        if int(port)>0 and int(port)<65535:
            return True
        else:
            exit("the port is in 0-65535")  #端口错误

    #合法后连接到服务器中
    def make_connection(self):
        self.sock =socket.socket()
        self.sock.connect((self.options.server,int(self.options.port)))

    #交互方法
    def interactive(self):
        print("begun to interactive.......")
        if self.authenticate():
            cmd_info = input("[%s]"%self.current_dir).strip()  #put

            cmd_list = cmd_info.split()

            if hasattr(self,cmd_list[0]):
                func = getattr(self,cmd_list[0])
                func(*cmd_list)

    #上传功能
    def put(self,*cmd_list):
        #
        action,local_path,target_path = cmd_list
        local_path = os.path.join(self.mainPath,local_path)

        file_name = os.path.basename(local_path)
        file_size = os.stat(local_path).st_size

        data={
            "action":"put",
            "file_name":file_name,
            "file_size":file_size,
            "target_path":target_path
        }

        self.sock.send(json.dumps(data).encode("utf-8"))

        is_exist = self.sock.recv(1024).decode("utf-8")
        has_sent = 0
        if is_exist == "800":
            # 文件不完整
            choice=input("the file exist,but not enought ,is continue?[Y/N]").strip()
            if choice.upper()=="Y":
                self.sock.sendall("Y".encode("utf-8"))
                continue_position = self.sock.recv(1024).decode("utf-8")
                has_sent += int(continue_position)
            else:
                self.sock.sendall("X".encode("utf-8"))

        elif is_exist =="801":
            #文件完全存在
            return
        else:
            pass


        f=open(local_path,"rb")
        while has_sent< file_size:
            data = f.read(1024)
            self.sock.sendall(data)
            has_sent += len(data)
            self.show_progress(has_sent,file_size)

        f.close()
        print("put success!")

    #断点续传功能
    def show_progress(self,has,total):
        rate = float(has)/float(total)
        rate_num = int(rate*100)
        if self.last != rate_num:
            sys.stdout.write("%s%% %s\r"%(rate_num,"#"*rate_num))
        self.last = rate_num


    def ls(self,*cmd_list):
        data={
            "action":"ls"

        }
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        data = self.sock.recv(1024).decode("utf-8")
        print(data)

    # cd切换
    def cd(self,*cmd_list):
        data = {
            "action":"cd",
            "dirname":cmd_list[1]
        }
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        data = self.sock.recv(1024).decode("utf-8")
        print(os.path.basename(data))
        self.current_dir = os.path.basename(data)

    def mkdir(self,*cmd_list):
        data = {
            "action": "mkdir",
            "dirname":cmd_list[1]
        }
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        data = self.sock.recv(1024).decode("utf-8")


    #验证是否是自己的用户
    def authenticate(self):
        #判断是否有值
        if self.options.username is None or self.options.password is None:
            username = input("username:")
            password = input("password:")
            return  self.get_auth_result(username,password)
        return self.get_auth_result(self.options.username,self.options.password)

    #接收数据
    def response(self):
        data = self.sock.recv(1024).decode("utf-8")
        data = json.loads(data)
        return data


    #验证是否正确，并打包发送
    def get_auth_result(self,user,pwd):

        data={
            "action":"auth",
            "username":user,
            "password":pwd
        }

        #接收
        self.sock.send(json.dumps(data).encode("utf-8"))
        response = self.response()
        print("response:",response["status_code"])
        if response["status_code"] == 254:
            self.user =user
            self.current_dir = user
            print(STATUS_CODE[254])
            return True
        else:
            print(STATUS_CODE[response["status_code"]])

#实例一个类对象
ch = ClientHandler

ch.interactive()