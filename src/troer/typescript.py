from .elem import Renderer, StructElem, RefElem
from collections import OrderedDict

class TypeScript(Renderer):
    def __init__(self, lib):
        self.lib = lib
        if lib.schema != "exchange":
            raise Exception(f"Only exchange schema supported")
        self.type = OrderedDict()
        tmp = []
        self.rpc= []
        for e in lib.rpc["entries"]:
            if "request" in e:
                r = lib.getElem(e["request"][1:])
                if isinstance(r, RefElem):
                    r = r.elem
                tmp.append(r)
                self.rpc.append((f"req_{self.name2id(e['name'])}",r.pid))
            if "response" in e:
                r = lib.getElem(e["response"][1:])
                if isinstance(r, RefElem):
                    r = r.elem
                tmp.append(r)
                self.rpc.append((f"res_{self.name2id(e['name'])}", r.pid))
        while(tmp):
            t = tmp.pop(0)
            if t.pid in self.type:
                continue

            self.type[t.pid] = t
            if isinstance(t, StructElem):
                for e in t.entries:
                    if isinstance(e, RefElem):
                        tmp.append(e.elem)
        self.type = reversed(list(self.type.values()))

    def rendering(self, outputDir, indent=None):
        self._rendering(outputDir, indent, 'typescript', 'types.tsx')

