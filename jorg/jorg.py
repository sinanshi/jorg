import os, sys
import yaml
import datetime
from shutil import copyfile
import subprocess

def parse_yaml_conf(path): 
    with open(path, 'r') as stream:
        try:
            conf = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return(conf)



class Jorg:
    def __init__(self, path):
        self.items = ['title', 'details','timeout', 'inputs', 'command']
        self.conf = parse_yaml_conf(path)
        self.check_conf_yaml()
        self.thidir = "."

    def __call__(self, confpath, outpath):
        self.conf = parse_yaml_conf(confpath)
        self.create_new_outpath(outpath)
        self.copy_conf_file(confpath, outpath)
        self.link_input_files(outpath)
        self.execute()

    def check_conf_yaml(self): 
        if not isinstance(self.conf, dict):
            print(self.conf)
            raise IOError("is not a dictionary")
            
        for key in self.conf:
            if key not in self.items:
                raise KeyError("keys not found")
        

    def create_new_outpath(self, outpath):
        nw = datetime.datetime.now()
        nws = nw.strftime("%b%d_%H:%M:%S")

        title = self.conf['title']
        title = title.replace(" ", "_")
        thisdir = outpath + '/' + nws + '_' + title
        if not os.path.exists(thisdir):
            print("[working directory]: " + thisdir)
            os.makedirs(thisdir)
            self.thisdir = thisdir


    def copy_conf_file(self, confpath, outpath):
        copyfile(confpath, self.thisdir + '/conf')

    def link_input_files(self, outpath):
        print("[Link input files]: ")
        assert(self.thisdir != ".")
        for k, v in self.conf['inputs'].items():
            vs = v.split("/")
            name = vs[len(vs) - 1]
            print("   " + v + " ==> " + self.thisdir + '/' + name)
            os.symlink(v, self.thisdir + '/' + name)

    def execute(self):
        cmd = 'cd ' + self.thisdir + ' && ' + self.conf['command']
        with open(self.thisdir + "/log.txt", "w") as f:
            try:
                df = subprocess.Popen(cmd, stdout=f, stderr=f, shell=True)
                print("[pid]: " + str(df.pid))
#                if 'timeout' in self.conf.keys():
#                    if self.conf['timeout'] is not None:
#                        df.communicate(timeout=self.conf['timeout'] * 60 * 60)

            except subprocess.CalledProcessError as e:
                f.write(e.message)
                print(e.message)
            except KeyboardInterrupt as e:
                df.kill()
                n = str(datetime.datetime.now())
                emessage = "Stoped by user at " + n 
                f.write(emessage)
                print(emessage)
            except subprocess.TimeoutExpired as e:
                df.kill()
                print("timeout!")
            except:
                df.kill()
                raise
