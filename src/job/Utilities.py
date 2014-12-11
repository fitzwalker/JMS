import os, shutil, pexpect, pwd, grp

class File:
    
    @staticmethod
    def print_to_file(filename, data, mode = 'w', permissions = 0775):
        with open(filename, mode) as f:
            print >> f, str(data)
        os.chmod(filename, permissions)    
            
        
    @staticmethod
    def copy_file(source, destination, permissions = 0775):
        if (os.path.isfile(source)):
            shutil.copy(source, destination)
            os.chmod(destination, permissions)
    
    
    @staticmethod
    def set_owner(path, user, group, recursive=False, exclude=[]):  
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid
        
        if recursive:
            for root, dirs, files in os.walk(path):  
                for momo in dirs:
                    full_path = os.path.join(root, momo)
                    if full_path not in exclude:
                        os.chown(full_path, uid, gid)
                for momo in files:
                    full_path = os.path.join(root, momo)
                    if full_path not in exclude:
                        os.chown(full_path, uid, gid)
        else:
            os.chown(path, uid, gid)
    
        
class Directory:

    @staticmethod
    def create_directory(path, permissions = 0775):
        if not os.path.exists(path):
            os.makedirs(path)
            os.chmod(path, permissions)


class UserProcess:

    def __init__(self, username, password, host=None):
        self.username = username
        self.password = password
        self.host = host
        
        if host == None:
            self.login(username, password)
    
    
    def login(self, username, password):
        child = pexpect.spawn('su - %s' % username)
        child.expect("Password:")
        child.sendline(password)        

        i = child.expect(['su: Authentication failure', '[#\$] '], timeout=6)
        if i == 1:
            self.process = child
        else:
            raise Exception("Authentication failed")    
    
    
    def run_command(self, command, expect='[#\$] ', timeout=6):
        self.process.sendline(command)
        i = self.process.expect(expect, timeout=timeout)
        return '\n'.join(self.process.before.split('\n')[1:-1])    
        
    
    def close(self):
        self.process.close(force=True)
        
        
        
        
