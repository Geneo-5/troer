from yaml import safe_load
from collections import OrderedDict
from packaging.version import Version
from packaging.specifiers import SpecifierSet
from importlib.resources import read_text
from Cheetah.Template import Template
from troer import templates
from troer.schemas import validate
from textwrap import fill
from re import sub

class Doc():
    def __init__(self, yaml):
        self.yaml = yaml

    def hasDoc(self):
        return 'doc' in self.yaml

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return self.yaml.get(name, None)

    def getDoc(self, shift=0):
        d = self.yaml['doc']
        size = 80 - shift
        d = d.replace('\\\\\n','\\\\')
        d = d.replace('\n\n','\\\\')
        d = sub(' *\n *', ' ', d)
        d = d.replace('\\\\','\n')
        if '\n' in d:
            o = ''
            ii = ''
            for l in d.split('\n'):
                o += ii + fill(l, size, subsequent_indent=' * ')
                o += "\n"
                ii = " * "
            d = o[:-1]
        else:
            d = fill(d, size, subsequent_indent=' * ')
        return d

class Elem(Doc):
    def __init__(self, lib, yaml):
        super().__init__(yaml)
        self.tmpl      = None
        self.lib       = lib
        self.assert_fn = lib.assert_fn
        self.id        = self.yaml['name'].replace("-", "_")
        self.pre       = self.lib.prefix
        self.pid       = self.pre + self.name

        self.decode    = f"{self.pre}decode_{self.id}"
        self.encode    = f"{self.pre}encode_{self.id}"
        self.check     = f"{self.pre}check_{self.id}"

        self.deprecated = ""
        if self.yaml.get('deprecated', False):
            self.deprecated = "__deprecated"

    def getDeclaration(self):
        try:
            tmpl = read_text(templates, f"{self.tmpl}.h.tmpl")
        except:
            return ""
        return Template(tmpl, self)
            
    def getDefinition(self):
        try:
            tmpl = read_text(templates, f"{self.tmpl}.c.tmpl")
        except:
            return ""
        return Template(tmpl, self)

class BoolElem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'bool'
        self.pid = 'bool'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdbool.h>")

class U8Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'uint8'
        self.pid = 'uint8_t'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class U16Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'uint16'
        self.pid = 'uint16_t'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class U32Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'uint32'
        self.pid = 'uint32_t'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class U64Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'uint64'
        self.pid = 'uint64_t'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class S8Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'int8'
        self.pid = 'int8_t'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class S16Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'int16'
        self.pid = 'int16_t'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class S32Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'int32'
        self.pid = 'int32_t'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class S64Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'int64'
        self.pid = 'int64_t'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class Lib(Doc):
    def __init__(self, yaml):
        super().__init__(yaml)
        self.schema    = self.yaml["schema"]
        self.id        = self.yaml['name'].replace("-", "_")
        self.prefix    = self.yaml.get('prefix', self.id + "_")
        self.version   = Version(self.yaml['version'])
        self.assert_fn = f"{self.prefix}assert"
        self.subClass  = "Elem"
        self.header    = set()
        self.elems     = OrderedDict()
        self.libs      = {}

        self.header.add("<errno.h>")

        for i in self.yaml.get('structures', []):
            elem = newElem(i['type'], self, i)
            if elem.name in self.elems:
                raise Exception(f"{elem.name} early exist")
            self.elems[elem.name] = elem

    def getElem(name):
        if name in elems:
            return elems[name]
        return libs[name]

    def resolveLibs(self, includeDir):
        for f in self.yaml.get('includes', []):
            lastE = None
            versionSpec = SpecifierSet(f.get('version', ">=0"))
            for i in includeDir:
                try:
                    with open(f"{i}/{f['file']}.yaml", "r") as y:
                        spec = safe_load(y)
                except:
                    continue
                try:
                    validate(spec)
                    lib = Lib(spec)
                    if lib.version not in versionSpec:
                        raise Exception( \
                f"{f} find with version {lib.version} but want {versionSpec}")
                    for l in lib.elems:
                        self.libs[f"{f['file']}/{l}"] = lib.elem[l]
                    self.head.add(f.get('header', f"<{lib.id}.h>"))
                    break
                except Exception as e:
                    lastE = e
                    continue
                if lastE:
                    raise lastE
                else:
                    raise FileNotFoundError(f"{f}.yaml")

    def rendering(self, outputDir, indent=None):
        tmpl = read_text(templates, f"lib.h.tmpl")
        out =  Template(tmpl, self)
        if indent:
            out = indent(out)
        if outputDir:
            with open(f"{outputDir}/{self.name}.h", "w") as f:
                f.write(out)
        else:
            print(out)

        tmpl = read_text(templates, f"lib.c.tmpl")
        out =  Template(tmpl, self)
        if indent:
            out = indent(out)
        if outputDir:
            with open(f"{outputDir}/{self.name}.c", "w") as f:
                f.write(out)
        else:
            print(out)

def newElem(type, * args):
    return globals()[f"{type.title()}Elem"](* args)

def loadTroer(path, includeDir):
    with open(path, 'r') as f:
        yaml = safe_load(f)
    validate(yaml)
    troer = globals()[yaml["schema"].title()](yaml)
    troer.resolveLibs(includeDir)
    return troer

