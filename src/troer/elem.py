from yaml import safe_load
from collections import OrderedDict
from packaging.version import Version
from packaging.specifiers import SpecifierSet
from importlib.resources import read_text
from Cheetah.Template import Template
from troer import templates, resources
from troer.schemas import validate
from textwrap import fill
from re import sub, compile
import os
try:
    import pcre2
except:
    pass

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

    def isElem(self, type: list[str] | str) -> bool:
        if isinstance(type, str):
            type = [ type ]
        for t in type:
            if isinstance(self, globals()[f"{t.title()}Elem"]):
                return True
        return False

    def rendering(self):
        raise Exception(f"Unimplemented function")

    def formatMaxSize(self, r, s, end = ')'):
        while len(r) > 1:
            R = set()
            while len(r) > 1:
                r1 = r.pop()
                r2 = r.pop()
                R.add(f'STROLL_CONST_MAX( {r1}, {r2})')
            if r:
                R.add(r.pop())
            r = R
        c = len(s);
        for e in r.pop().split(' '):
            if c + len(e) + 1 < (80 - 9):
                s += e + ' '
            else:
                s += '\\\n\t ' + e + ' '
                c = 0
            c += len(e) + 1
        return s[:-1] + end

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
        self.pre       = self.lib.pre
        self.pid       = self.pre + self.id
        self.json      = lib.json
        self.ampersand = ''
        self.asterisk  = ''

        self.packed_size = f"{self.pid.upper()}_PACKED_SIZE"
        self.decode      = f"{self.pre}dec_{self.id}"
        self.encode      = f"{self.pre}enc_{self.id}"
        self.check       = f"{self.pre}chk_{self.id}"
        self.init        = None
        self.fini        = None
        self.app_check   = self.yaml.get('check', None)

        self.deprecated = ""
        if self.yaml.get('deprecated', False):
            self.deprecated = "__deprecated"

    def getDeclaration(self):
        try:
            tmpl = read_text(templates, f"{self.tmpl}.h.tmpl")
        except:
            return ""
        return Template(tmpl, self)
            
    def getDefinition(self, sub = ''):
        try:
            tmpl = read_text(templates, f"{self.tmpl}{sub}.c.tmpl")
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
        self.ampersand = '&'
        self.asterisk  = '*'
        self.init  = f"{self.pre}init_{self.id}"
        self.fini  = f"{self.pre}fini_{self.id}"
        lib.header.add("<dpack/lvstr.h>")
        if 'pattern' in self.yaml:
            if lib.args.regex == 'pcre2':
                lib.header.add("<pcre2.h>")
                pcre2.compile(self.yaml['pattern'])
            else:
                lib.header.add("<regex.h>")
                if self.yaml['pattern'][0] != '^':
                    self.yaml['pattern'] = '^' + self.yaml['pattern']
                if self.yaml['pattern'][-1] != '$':
                    self.yaml['pattern'] += '$'
                compile(self.yaml['pattern'])

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
        lib.header.add("<dpack/scalar.h>")
        lib.header.add("<stroll/array.h>")

        for i in self.yaml['entries']:
            if 'name' in i:
                e = EnumEntry(self.lib, i)
            else:
                e = EnumEntry(self.lib, {'name':i})
            self.entries.append(e)
            name = f"{self.name}_{e.name}"
            if name in self.lib.elems:
                raise Exception(f"{name} early exist")
            self.lib.elems[name] = e

class RpcEntry(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)

        self.roles = []
        for r in yaml['roles']:
            self.roles.append(RefElem(r[1:], lib, yaml))

        if 'request' in yaml:
            self.request = RefElem(yaml['request'][1:], lib, yaml)
        if 'response' in yaml:
            self.response = RefElem(yaml['response'][1:], lib, yaml)

class RpcElem(EnumElem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        lib.header.add("<hed/rpc.h>")
        lib.header.add("<hed/codec.h>")

        self.req  = []
        self.evnt = []
        self.ntfy = []
        values = {}
        self.maxid = 0
        for i in self.yaml['entries']:
            v = i['value']
            self.maxid = max(self.maxid, v)
            if v in values:
                raise Exception(f"RPC {i['name']} id value ({v}) conflict with {values[v]}")
            values[v] = i['name']

            e = RpcEntry(self.lib, i)
            if i['type'] == 'request':
                self.req.append(e)
            elif i['type'] == 'event':
                self.evnt.append(e)
            elif i['type'] == 'notify':
                self.ntfy.append(e)

    def getSrvMaxSize(self):
        r = set()
        for e in self.req + self.ntfy:
            if e.request:
                r.add(f"{e.request.elem.pid.upper()}_PACKED_SIZE_MAX")
        if not r:
            return '(DPACK_UINT32_SIZE_MAX)'
        s = '\\\n\t(DPACK_UINT32_SIZE_MAX + '
        return self.formatMaxSize(r, s)
    
    def getCltMaxSize(self):
        r = set()
        for e in self.req:
            if e.response:
                r.add(f"{e.response.elem.pid.upper()}_PACKED_SIZE_MAX")
        for e in self.evnt:
            if e.request:
                r.add(f"{e.request.elem.pid.upper()}_PACKED_SIZE_MAX")
        if not r:
            return '(DPACK_UINT32_SIZE_MAX + DPACK_UINT32_SIZE_MAX)'
        s = '\\\n\t(DPACK_UINT32_SIZE_MAX + DPACK_UINT32_SIZE_MAX + '
        return self.formatMaxSize(r, s)

    def getDeclaration(self):
        hdr = super().getDeclaration()
        tmpl = read_text(templates, f"rpc.h.tmpl")
        return str(hdr) + '\n'  + str(Template(tmpl, self))

class RepoEntry(Elem):
    def __init__(self, lib, yaml, parent):
        super().__init__(lib, yaml)
        self.tmpl  = 'repo-' + yaml['type']

        if yaml['type'] == 'object':
            lib.header.add("<utils/file.h>")
        if yaml['type'] == 'collection':
            parent.flags2gdbm = True
            lib.header.add("<gdbm.h>")
            lib.header.add("<stroll/page.h>")

        self.parent = parent
        self.object = RefElem(yaml['object'][1:], lib, yaml)
        if 'key' in yaml:
            self.key = RefElem(yaml['key'][1:], lib, yaml)

class RepoElem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        lib.header.add("<stroll/lvstr.h>")
        lib.header.add("<stdio.h>")
        lib.header.add("<string.h>")
        self.tmpl  = 'repo'
        self.type  = f"struct {self.pid}"
        self.ampersand = '&'
        self.asterisk  = '*'
        self.init    = f"{self.pre}init_{self.id}"
        self.fini    = f"{self.pre}fini_{self.id}"
        self.entries = []
        self.max_path = 0
        self.flags2gdbm = False
        for i in self.yaml['entries']:
            e = RepoEntry(self.lib, i, self)
            self.entries.append(e)
            self.max_path = max(self.max_path, len(e.name) + 1 + 4 + 1)

    def getMaxSize(self):
        r = set()
        for e in self.entries:
            r.add(f"{e.object.elem.pid.upper()}_PACKED_SIZE_MAX")
            if 'key' in e:
                r.add(f"{e.key.elem.pid.upper()}_PACKED_SIZE_MAX")
        return self.formatMaxSize(r, '\\\n\t(')

class RefElem(Elem):
    def __init__(self, elem, lib, yaml):
        super().__init__(lib, yaml)
        self.elem        = lib.getElem(elem)
        self.type        = self.elem.type
        self.decode      = self.elem.decode
        self.encode      = self.elem.encode
        self.check       = self.elem.check
        self.init        = self.elem.init
        self.fini        = self.elem.fini
        self.packed_size = self.elem.packed_size
        self.ampersand   = self.elem.ampersand
        self.asterisk    = self.elem.asterisk

class StructElem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl    = "struct"
        self.type    = f"struct {self.pid}"
        self.entries = []
        self.ampersand = '&'
        self.asterisk  = '*'
        self.init    = f"{self.pre}init_{self.id}"
        self.fini    = f"{self.pre}fini_{self.id}"

        for i in self.yaml['entries']:
            lib.addElem(i['type'], f"{self.name}_", i)
            e = lib.getElem(f"{self.name}_{i['name']}")
            self.entries.append(e)
            if 'repeated' in i:
                lib.header.add("<dpack/array.h>")
                if isinstance(i['repeated'], (int, str)):
                    if isinstance(i['repeated'], str):
                        print(f"WARNING: cannot check {e.repeated} value")
                    e.repeated_min = i['repeated']
                    e.repeated_max = i['repeated']
                else:
                    e.repeated_min = i['repeated']['min']
                    e.repeated_max = i['repeated']['max']
                    if isinstance(e.repeated_min, int) and \
                       isinstance(e.repeated_max, int):
                        if e.repeated_min >= e.repeated_max:
                            raise Exception("min value >= max value")
                    else:
                        print(f"WARNING: cannot check {e.repeated_min} and {e.repeated_max} values")

    def defineMinMax(self, t):
        r = []
        for e in self.entries:
            if 'repeated' in e:
                if t == "MIN":
                    r.append(f"DPACK_ARRAY_FIXED_SIZE({e.repeated_min},{e.packed_size}_{t})")
                else:
                    r.append(f"DPACK_ARRAY_FIXED_SIZE({e.repeated_max},{e.packed_size}_{t})")
            else:
                r.append(f"{e.packed_size}_{t}")
        return "\\\n\t(" + " + \\\n\t ".join(r) + ")"

    def defineMIN(self):
        return self.defineMinMax("MIN")

    def defineMAX(self):
        return self.defineMinMax("MAX")

class CustomElem(Elem):
    def __init__(self, lib, yaml):
        super().__init__(lib, yaml)
        self.tmpl        = 'defCustom'
        self.type        = yaml.get("struct")
        self.decode      = yaml.get("decode")
        self.encode      = yaml.get("encode")
        self.check       = yaml.get("check")
        self.init        = yaml.get("init", None)
        self.fini        = yaml.get("fini", None)
        self.min_size    = yaml.get("min")
        self.max_size    = yaml.get("max")
        self.ampersand   = '&'
        self.asterisk    = '*'
        if "header" in yaml:
            lib.header.add(yaml.get("header"))
        self.app_check   = None

class Lib(Doc):
    def __init__(self, yaml, args):
        super().__init__(yaml)
        self.args      = args
        self.json      = args.json
        self.schema    = self.yaml["schema"]
        self.name      = self.yaml['name']
        self.id        = self.name.replace("-", "_")
        self.pre       = self.yaml.get('prefix', self.id + "_")
        self.version   = Version(self.yaml['version'])
        self.assert_fn = f"{self.pre}assert"
        self.subClass  = "Elem"
        self.header    = set()
        self.elems     = OrderedDict()
        self.libs      = {}
        self.kconfig   = False
    
        self.resolveLibs(args.includeDir, args)

        self.header.add("<errno.h>")
        self.header.add("<dpack/codec.h>")
        self.header.add("<stroll/cdefs.h>")
        if self.json:
            self.header.add("<json-c/json_object.h>")

        for h in self.yaml.get('headers', []):
            self.header.add(h)

        for d in  self.yaml.get('declarations', []):
            self.addElem(d['type'], "", d)

    def addElem(self, type, p, *args):
        elem = newElem(type, self, *args)
        name = f"{p}{elem.name}"
        if name in self.elems:
            raise Exception(f"{name} early exist")
        self.elems[name] = elem

    def getElem(self, name):
        if name in self.elems:
            return self.elems[name]
        return self.libs[name]

    def resolveLibs(self, includeDir, args):
        for f in self.yaml.get('includes', []):
            lastE = FileNotFoundError(f"{f['file']}.yml")
            versionSpec = SpecifierSet(f.get('version', ">=0"))
            for i in includeDir:
                try:
                    with open(f"{i}/{f['file']}.yml", "r") as y:
                        spec = safe_load(y)
                except:
                    try:
                        with open(f"{i}/{f['file']}.yaml", "r") as y:
                            spec = safe_load(y)
                    except:
                        continue
                try:
                    validate(spec)
                    lib = Lib(spec, args)
                    if lib.version not in versionSpec:
                        raise Exception( \
                f"{f} find with version {lib.version} but want {versionSpec}")
                    for l in lib.elems:
                        self.libs[f"{f['file']}/{l}"] = lib.elems[l]
                    self.header.add(f.get('header', f"<{f['file']}.h>"))
                    lastE = None
                    break
                except Exception as e:
                    lastE = e
                    continue
            if lastE:
                raise lastE

    def rendering(self, outputDir, indent=None):
        if self.kconfig:
            print(f"  GEN {outputDir}/include/{self.name}/lib.h")
            self._rendering(outputDir, indent, 'lib.h', f'include/{self.name}/lib.h')
        else:
            out = self.args.include_dir if self.args.include_dir else outputDir
            print(f"  GEN {out}/{self.name}.h")
            self._rendering(out, indent, 'lib.h', f'{self.name}.h')
        print(f"  GEN {outputDir}/{self.name}.c")
        self._rendering(outputDir, indent, 'lib.c', f'{self.name}.c')
        print(f"  GEN {outputDir}/{self.name}-json.c")
        self._rendering(outputDir, indent, 'lib-json.c', f'{self.name}-json.c')

class Exchange(Lib):
    def __init__(self, yaml, args):
        super().__init__(yaml, args)
        self.header.add("<hed/server.h>")
        self.rpc = {
                'name': 'rpc-enum',
                'entries': yaml['rpc']
        }
        self.addElem('rpc', "", self.rpc)

    def rendering(self, outputDir, indent=None):
        super().rendering(outputDir, indent)
        print(f"  GEN {outputDir}/{self.name}-srv.c")
        self._rendering(outputDir, indent, 'rpc-srv.c', f'{self.name}-srv.c')
        print(f"  GEN {outputDir}/{self.name}-clt.c")
        self._rendering(outputDir, indent, 'rpc-clt.c', f'{self.name}-clt.c')

class Storage(Lib):
    def __init__(self, yaml, args):
        super().__init__(yaml, args)
        self.rpc = {
                'name': 'repo',
                'entries': yaml['repositories']
        }
        self.addElem('repo', "", self.rpc)

def newElem(type, * args):
    if type[0] == '$':
        return RefElem(type[1:], * args)
    return globals()[f"{type.title()}Elem"](* args)

def loadTroer(path, args):
    with open(path, 'r') as f:
        yaml = safe_load(f)
    validate(yaml)
    troer = globals()[yaml["schema"].title()](yaml, args)
    return troer

