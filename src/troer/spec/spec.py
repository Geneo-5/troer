import sys
from yaml import safe_load, YAMLError
from jsonschema import validate
from collections import OrderedDict
from importlib.resources import open_text, read_text
from Cheetah.Template import Template
from troer import schemas
from troer import templates
from textwrap import wrap

def newElement(name):
    return globals()[f"Spec{name.title()}"]

def make_doc(doc, indent=""):
    if not doc:
            return ""
    if len(doc) < (80 - len(indent.replace("\t", " " * 8) + "/*  */")):
        return f"{indent}/* {doc} */\n"
    else:
        s = 80 - len(indent.replace("\t", " " * 8) + " * ")
        m = f"\n{indent} * ".join(wrap(doc, s))
        return f"{indent}/*\n{indent} * {m}\n{indent} */\n"

def align(f, s, a):
    return f"{f}{' ' * (a - len(f))}{s}"

class SpecElement:
    def __init__(self, family, yaml):
        self.tmpl = None
        self.family = family
        self.yaml = yaml
        self.doc = yaml.get('doc', None)

        if 'name' in self.yaml:
            self.name = self.yaml['name']
            self.ident_name = self.family.prefix + self.name.replace('-', '_')

        self._super_resolved = False
        family.add_unresolved(self)

    def resolve_up(self, up):
        if not self._super_resolved:
            up.resolve()
            self._super_resolved = True

    def resolve(self):
        pass

    def rendering(self):
        if self.tmpl:
            tmpl = read_text(templates, f"{self.tmpl}.tmpl")
            return Template(tmpl, self)
        else:
            raise Exception("Cannot randering SpecElement")

class ConstElement(SpecElement):
    def __init__(self, family, yaml):
        super().__init__(family, yaml)
        if 'header' in yaml:
            family.add_header(yaml['header'])
            self.prefix = ''
        else:
            self.prefix = self.family.prefix

class SpecConst(ConstElement):
    def __init__(self, family, yaml):
        super().__init__(family, yaml)

class SpecEnum(ConstElement):
    def __init__(self, family, yaml):
        super().__init__(family, yaml)
        self.tmpl = 'enum'
        if 'header' not in yaml:
            family.add_enum(self.name, self)
        self.entries = []
        for e in yaml['entries']:
            if isinstance(e, str):
                name = (self.prefix + e).replace('-', '_').upper()
                value = None
                doc = None
            else:
                name = (self.prefix + e['name']).replace('-', '_').upper()
                value = e.get('value', None)
                doc = e.get('doc', None)
            self.entries.append((name, value, doc))

class SpecFlags(ConstElement):
    def __init__(self, family, yaml):
        super().__init__(family, yaml)

class SpecRef(ConstElement):
    def __init__(self, family, yaml):
        super().__init__(family, yaml)

class SpecFamily(SpecElement):
    def __init__(self, spec_path):
        with open(spec_path, "r") as f:
            spec = safe_load(f)
        self.schema = spec.get("schema", None)
        if not self.schema:
            raise YAMLError("Missing schema definition")
        with open_text(schemas, f"{self.schema}.yaml") as f:
            schema = safe_load(f)
        validate(spec, schema)

        self.prefix = ""
        self._resolution_list = []
        super().__init__(self, spec)

        self.header = set()
        self.defines = OrderedDict()
        self.enums = OrderedDict()

        last_exception = None
        while len(self._resolution_list) > 0:
            resolved = []
            unresolved = self._resolution_list
            self._resolution_list = []

            for elem in unresolved:
                try:
                    elem.resolve()
                except (KeyError, AttributeError) as e:
                    self._resolution_list.append(elem)
                    last_exception = e
                    continue
                resolved.append(elem)

            if len(resolved) == 0:
                raise last_exception

    def add_header(self, header):
        self.header.add(header)

    def add_define(self, name, define):
        self.defines[name] = define

    def add_enum(self, name, enum):
        self.enums[name] = enum

    def add_unresolved(self, elem):
        self._resolution_list.append(elem)

    def _resolve_definitions(self):
        for elem in self.yaml.get('definitions', []):
            newElement(elem['type'])(self, elem)

    def _resolve_attribute(self):
        pass

    def _resolve_operations(self):
        pass

    def resolve(self):
        self.resolve_up(super())
        if 'prefix' in self.yaml:
            self.prefix = self.yaml['prefix']
        self._resolve_definitions()
        self._resolve_attribute()
        if self.schema == "exchange":
            self._resolve_operations()

    def rendering(self, mode):
        tmpl = read_text(templates, f"{mode}.tmpl")
        return Template(tmpl, self)

