from collections import OrderedDict
from .elem import *

class TypeScript(Renderer):
    def __init__(self, lib):
        self.lib = lib
        if lib.schema != "exchange":
            raise Exception(f"Only exchange schema supported")
        self.struct = OrderedDict()
        self.enum   = OrderedDict()
        tmp = []
        self.rpc= []
        for e in lib.rpc["entries"]:
            cmd = []
            cmd.append(self.name2id(e['name']))
            cmd.append(e['name'])
            if "request" in e:
                r = lib.getElem(e["request"][1:])
                while isinstance(r, RefElem):
                    r = r.elem
                tmp.append(r)
                cmd.append(self.paramType(r))
            else:
                cmd.append('undefined')

            if "response" in e:
                r = lib.getElem(e["response"][1:])
                while isinstance(r, RefElem):
                    r = r.elem
                tmp.append(r)
                cmd.append(self.paramType(r))
            else:
                cmd.append('void')
            self.rpc.append(cmd)

        seen = []
        while(tmp):
            t = tmp.pop(0)
            if t.pid in seen:
                continue

            seen.append(t.pid)
            if isinstance(t, RefElem):
                tmp.append(t.elem)

            self.checkEnum(t)
            if isinstance(t, StructElem):
                if t.pid in self.struct:
                    continue
                self.struct[t.pid] = t
                t.pids = []
                for e in t.entries:
                    self.checkEnum(e)
                    if isinstance(e, RefElem):
                        tmp.append(e.elem)
                    t.pids.append((e, self.paramType(e)))

        self.enum   = list(self.enum.values())
        self.struct = list(self.struct.values())

    def checkEnum(self, elem):
        if not isinstance(elem, ( EnumElem, FlagsElem )):
            return

        if elem.pid in self.enum:
            return

        self.enum[elem.pid] = elem

    def paramType(self, p):
        if isinstance(p, StrElem):
            return "string"
        elif isinstance(p, (U8Elem, U16Elem, U32Elem, U64Elem, S8Elem, S16Elem, S32Elem, S64Elem, F32Elem, F64Elem)):
            return "number"
        elif isinstance(p, BmapElem):
            return "Array<number>"
        elif isinstance(p, FlagsElem):
            return f"Array<{p.pid}>"
        elif isinstance(p, BoolElem):
            return "boolean"
        elif isinstance(p, RefElem):
            return self.paramType(p.elem)
        elif isinstance(p, CustomElem):
            return "string"
        else:
            return p.pid

    def rendering(self, outputDir, indent=None):
        print(f"  GEN {outputDir}/{self.lib.name}.tsx")
        self._rendering(outputDir, indent, 'typescript', f"{self.lib.name}.tsx")

