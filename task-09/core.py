from abc import ABC, abstractmethod

class PluginBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the plugin"""
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the plugin"""
        pass
        
    @property
    @abstractmethod
    def plugin_type(self) -> str:
        """Type of the plugin: 'built-in' or 'third-party'"""
        pass

    @property
    def dependencies(self) -> list[str]:
        """List of plugin names this plugin depends on"""
        return []

    @abstractmethod
    def activate(self) -> str:
        """Activate the plugin and return its registration info"""
        pass

    @abstractmethod
    def deactivate(self):
        """Deactivate the plugin"""
        pass
