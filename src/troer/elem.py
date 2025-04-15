from yaml import safe_load
from collections import OrderedDict
from packaging.version import Version
from packaging.specifiers import SpecifierSet
from importlib.resources import read_text
from Cheetah.Template import Template
from troer import templates, resources
from troer.schemas import validate
from textwrap import fill
from re import sub
import os

class Renderer():
    def __init__(self):
        pass

    def copy(self, outputDir, file, dest):
        if not outputDir:
            return
        os.makedirs(os.path.dirname(f"{outputDir}/{dest}"), exist_ok=True)
        data = read_text(resources, f"{file}")
        with open(f"{outputDir}/{dest}", "w") as f:
            f.write(data)

    def _rendering(self, outputDir, indent, tmpl, file):
        tmpl = read_text(templates, f"{tmpl}.tmpl")
        out  = str(Template(tmpl, self))
        if indent:
            out = indent(out)
        if outputDir:
            os.makedirs(os.path.dirname(f"{outputDir}/{file}"), exist_ok=True)
            with open(f"{outputDir}/{file}", "w") as f:
                f.write(out)
        else:
            print(out)

    def title(self, title, char = '*'):
        return title + '\n' + char * len(title)

    def doxyRef(self, type, ref):
        return f'\n.. doxygen{type}:: {ref}\n'

    def doxyDefine(self, ref):
        return self.title(ref) + '\n' + self.doxyRef('define', ref)

    def doxyEnum(self, ref):
        return self.title(ref) + '\n' + self.doxyRef('enum', ref)

    def doxyStruct(self, ref):
        return self.title(ref) + '\n' + self.doxyRef('struct', ref)

    def doxyFunction(self, ref):
        return self.title(ref) + '\n' + self.doxyRef('function', ref)

    def isElem(self, type):
        return isinstance(self, globals()[f"{type.title()}Elem"])

    def rendering(self):
        raise Exception(f"Unimplemented function")

class Doc(Renderer):
    def __init__(self, yaml):
        self.yaml = yaml

    def hasDoc(self):
        return 'doc' in self.yaml

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return self.yaml.get(name, None)

    def __iter__(self):
        return iter(self.__dict__ | self.yaml)

    def getDoc(self, shift=0):
        if not self.hasDoc():
            return ''

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
        self.pid       = self.pre + self.id
        self.json      = lib.json
        self.vref      = ''

        self.packed_size = f"{self.pid.upper()}_PACKED_SIZE"
        self.decode      = f"{self.pre}decode_{self.id}"
        self.encode      = f"{self.pre}encode_{self.id}"
        self.check       = f"{self.pre}check_{self.id}"
        self.init        = None
        self.fini        = None

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
        self.type = 'bool'
        self.jsonc = 'boolean'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdbool.h>")

class U8Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'uint8'
        self.type = 'uint8_t'
        self.jsonc = 'int'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class U16Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'uint16'
        self.type = 'uint16_t'
        self.jsonc = 'int'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class U32Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'uint32'
        self.type = 'uint32_t'
        self.jsonc = 'uint64'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class U64Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'uint64'
        self.type = 'uint64_t'
        self.jsonc = 'uint64'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class S8Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'int8'
        self.type = 'int8_t'
        self.jsonc = 'int'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class S16Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'int16'
        self.type = 'int16_t'
        self.jsonc = 'int'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class S32Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'int32'
        self.type = 'int32_t'
        self.jsonc = 'int'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class S64Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'int64'
        self.type = 'int64_t'
        self.jsonc = 'int64'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stdint.h>")

class F32Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'float'
        self.type = 'float_t'
        self.jsonc = 'double'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<math.h>")

class F64Elem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'scalar'
        self.dpack = 'double'
        self.type = 'double_t'
        self.jsonc = 'double'
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<math.h>")

class StrElem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'lvstr'
        self.dpack = 'lvstr'
        self.type  = 'struct stroll_lvstr'
        self.jsonc = 'string'
        self.vref  = '&'
        self.init  = f"{self.pre}init_{self.id}"
        self.fini  = f"{self.pre}fini_{self.id}"
        lib.header.add("<dpack/lvstr.h>")
        if 'pattern' in self.yaml:
            lib.header.add("<pcre2.h>")

class EnumEntry(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)

class EnumElem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl  = 'enum'
        self.type  = f'enum {self.pid}'
        self.entries = []
        lib.header.add("<string.h>")
        lib.header.add("<stroll/array.h>")

        for i in self.yaml['entries']:
            if 'name' in i:
                e = EnumEntry(self.lib, i)
            else:
                e = EnumEntry(self.lib, {'name':i})
            self.entries.append(e)


class RefElem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.elem        = lib.getElem(self.yaml['ref'])
        self.type        = self.elem.type
        self.decode      = self.elem.decode
        self.encode      = self.elem.encode
        self.check       = self.elem.check
        self.init        = self.elem.init
        self.fini        = self.elem.fini
        self.packed_size = self.elem.packed_size
        self.vref        = self.elem.vref

class StructElem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl    = "struct"
        self.type    = f"struct {self.pid}"
        self.entries = []
        self.vref    = '&'
        self.init    = f"{self.pre}init_{self.id}"
        self.fini    = f"{self.pre}fini_{self.id}"

        for i in self.yaml['entries']:
            lib.addElem(i['type'], i)
            self.entries.append(lib.getElem(i['name']))
            if 'repeated' in i:
                lib.header.add("<dpack/array.h>")

    def defineMinMax(self, t):
        r = []
        for e in self.entries:
            if 'repeated' in e:
                r.append(f"DPACK_ARRAY_FIXED_SIZE({e.repeated},{e.packed_size}_{t})")
            else:
                r.append(f"{e.packed_size}_{t}")
        return "\\\n\t" + " + \\\n\t".join(r)

    def defineMIN(self):
        return self.defineMinMax("MIN")

    def defineMAX(self):
        return self.defineMinMax("MAX")

class Lib(Doc):
    def __init__(self, yaml, json=False):
        super().__init__(yaml)
        self.json      = json
        self.schema    = self.yaml["schema"]
        self.name      = self.yaml['name']
        self.id        = self.name.replace("-", "_")
        self.prefix    = self.yaml.get('prefix', self.id + "_")
        self.version   = Version(self.yaml['version'])
        self.assert_fn = f"{self.prefix}assert"
        self.subClass  = "Elem"
        self.header    = set()
        self.elems     = OrderedDict()
        self.libs      = {}
        self.includeDir= ''
        self.kconfig   = False

        self.header.add("<errno.h>")
        self.header.add("<dpack/codec.h>")
        self.header.add("<stroll/cdefs.h>")
        if json:
            self.header.add("<json-c/json_object.h>")

        for i in self.yaml.get('structures', []):
            self.addElem(i['type'], i)

    def addElem(self, type, *args):
        elem = newElem(type, self, *args)
        if elem.name in self.elems:
            raise Exception(f"{elem.name} early exist")
        self.elems[elem.name] = elem

    def getElem(self, name):
        if name in self.elems:
            return self.elems[name]
        return self.libs[name]

    def resolveLibs(self, includeDir):
        for f in self.yaml.get('includes', []):
            lastE = FileNotFoundError(f"{f}.yaml")
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
                        self.libs[f"{f['file']}/{l}"] = lib.elems[l]
                    self.header.add(f.get('header', f"<{lib.id}.h>"))
                    lastE = None
                    break
                except Exception as e:
                    lastE = e
                    continue
            if lastE:
                raise lastE

    def rendering(self, outputDir, indent=None):
        self._rendering(outputDir, indent, 'lib.h', f'{self.includeDir}{self.name}.h')
        self._rendering(outputDir, indent, 'lib.c', f'{self.name}.c')

def newElem(type, * args):
    return globals()[f"{type.title()}Elem"](* args)

def loadTroer(path, includeDir, json=False):
    with open(path, 'r') as f:
        yaml = safe_load(f)
    validate(yaml)
    troer = globals()[yaml["schema"].title()](yaml, json)
    troer.resolveLibs(includeDir)
    return troer

