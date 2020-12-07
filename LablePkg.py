import json
import os
import random

class LablePkg:

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.log = set()
        self.load_log()

    def load_log(self):
        if not os.path.exists(os.path.join(self.base_dir, 'pkg_log.json')):
            self.write_log()
        with open(os.path.join(self.base_dir, 'pkg_log.json'), 'r', encoding='utf-8') as f:
            self.log = set(json.load(f))

    def remove_log(self, pkgname):
        if pkgname not in self.log:
            print("-------->" + pkgname + "has not been labled")
            return
        self.log.remove(pkgname)
        self.write_log()

    def lable_pkg(self, pkgname):
        if pkgname in self.log:
            print("-------->" + pkgname + "has been labled")
            return
        self.log.add(pkgname)
        self.write_log()
    
    def write_log(self):
        with open(os.path.join(self.base_dir, 'pkg_log.json'), 'w', encoding='utf-8') as f:
            json.dump(list(self.log), f, indent=4, ensure_ascii=False)
