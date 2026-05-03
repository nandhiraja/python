import os
import sys
from plugin_manager import PluginManager

def main():
    # Force UTF-8 encoding for stdout on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=== Application Startup ===")
    print("$ sitegen build --theme dark-mode\n")

    plugin_dir = "./plugins/"
    
    # Initialize Plugin Manager
    manager = PluginManager(plugin_dir)
    
    # Discovery
    manager.discover_and_load()
    
    # Dependency Resolution
    manager.resolve_dependencies()
    
    # Activation
    manager.activate_all()
    
    # Simulation Output
    print("[CORE] Building site...")
    print("       Processed 24 pages | Theme: dark-mode | RSS: feed.xml generated")
    print("       Images optimized: 18 files, saved 4.2 MB")
    print("[CORE] Build complete -> ./dist/ (0.87s)")

if __name__ == "__main__":
    main()
