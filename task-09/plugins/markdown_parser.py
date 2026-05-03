from core import PluginBase

class MarkdownParserPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "markdown-parser"
        
    @property
    def version(self) -> str:
        return "2.1.0"
        
    @property
    def plugin_type(self) -> str:
        return "built-in"

    def activate(self) -> str:
        return ".md -> HTML converter"

    def deactivate(self):
        pass
