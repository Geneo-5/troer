from .elem import Renderer

class Makefile(Renderer):
    def __init__(self, lib, mode):
        self.lib      = lib
        self.mode     = mode
        self.makefile = False
        self.builtin  = False
        self.static   = False
        self.shared   = False
        if self.mode not in ['builtin', 'static', 'shared', 'both']:
            raise Exception(f"invalid mode '{mode}'")
        if self.mode == 'builtin':
            self.builtin  = True
        if self.mode == 'static':
            self.static   = True
            self.makefile = True
        if self.mode == 'shared':
            self.shared   = True
            self.makefile = True
        if self.mode == 'both':
            self.static   = True
            self.shared   = True
            self.makefile = True

        if self.makefile:
            self.lib.includeDir = f'include/{self.lib.id}/'
            self.lib.kconfig = True

        self.pkgconfig = ""
        h = str(self.lib.header)
        if "dpack" in h:
            self.pkgconfig += " libdpack"

        if "stroll" in h:
            self.pkgconfig += " libstroll"

        if "pcre2" in h:
            self.pkgconfig += " libpcre2-8"

        if "json-c" in h:
            self.pkgconfig += " json-c"

    def rendering(self, outputDir, indent=None):
        if self.makefile:
            self.copy(outputDir, 'mit.rst',                'sphinx/license/mit.rst')
            self.copy(outputDir, 'doxyfile',               'sphinx/Doxyfile')
            self._rendering(outputDir, indent, 'api',      'sphinx/api.rst')
            self.copy(outputDir, 'conf.py',                'sphinx/conf.py')
            self.copy(outputDir, 'genindex.rst',           'sphinx/genindex.rst')
            self._rendering(outputDir, indent, 'doc',      'sphinx/index.rst')
            self._rendering(outputDir, indent, 'install',  'sphinx/install.rst')
            self.copy(outputDir, 'license.rst',            'sphinx/license.rst')
            self.copy(outputDir, 'COPYING',                'COPYING')
            self._rendering(outputDir, indent, 'kconfig',  'Config.in')
            self._rendering(outputDir, indent, 'makefile', 'Makefile')
            self._rendering(outputDir, indent, 'readme',   'README.rst')
        self._rendering(outputDir, indent, 'ebuild',       'ebuild.mk')
