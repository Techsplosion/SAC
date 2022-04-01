import os


def endswiths(string, *endswiths):
    for i in endswiths:
        if string.endswith(i):
            return True
    return False


os.system("echo %username% > usrname.pass")
with open("usrname.pass", "r") as f:
    usrname = f.read()
    usrname = usrname.removesuffix(" \n")
os.remove("usrname.pass")
cppath = f"C:/Users/{usrname}/Desktop"
os.chdir(cppath)
for pth, drc, fil in os.walk(cppath):
    for i in fil:
        if endswiths(i, ".png", ".jpg", ".bmp", ".tiff", ".tif", ".ico", ".xcf"):
            pth = f"xcopy \"C:\\Users\\{usrname}\\Desktop\\{i}\" E:\\YKBPP\\img /E /H /C /I"
            os.system(f"{pth}")
