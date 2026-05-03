from core import PluginBase

class RssFeedPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "rss-feed"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def plugin_type(self) -> str:
        return "third-party"

    @property
    def dependencies(self) -> list[str]:
        return ["markdown-parser"]

    def activate(self) -> str:
        return 'command "generate-rss"'

    def deactivate(self):
        pass
