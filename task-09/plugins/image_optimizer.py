from core import PluginBase

class ImageOptimizerPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "image-optimizer"
        
    @property
    def version(self) -> str:
        return "0.9.1"
        
    @property
    def plugin_type(self) -> str:
        return "third-party"

    def activate(self) -> str:
        return "post-processor for .png/.jpg"

    def deactivate(self):
        pass
