def write_file_bin(path, bstr):
    f = open(path, "wb")
    f.write(bstr)
    f.close()

def write_file(path, str):
    f = open(path, "w")
    f.write(str)
    f.close()

