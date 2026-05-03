from core import PluginBase

class DarkModeThemePlugin(PluginBase):
    @property
    def name(self) -> str:
        return "dark-mode-theme"
        
    @property
    def version(self) -> str:
        return "1.3.2"
        
    @property
    def plugin_type(self) -> str:
        return "third-party"

    def activate(self) -> str:
        return 'theme "dark-mode"'

    def deactivate(self):
        pass
