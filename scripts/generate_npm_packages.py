import json
import os
from pathlib import Path

# Mapping of nodes OS/Arch to their package folder
PLATFORMS = {
    "win32-x64": {"os": "win32", "cpu": "x64", "ext": ".exe"},
    "darwin-x64": {"os": "darwin", "cpu": "x64", "ext": ""},
    "darwin-arm64": {"os": "darwin", "cpu": "arm64", "ext": ""},
    "linux-x64": {"os": "linux", "cpu": "x64", "ext": ""},
    "linux-arm64": {"os": "linux", "cpu": "arm64", "ext": ""},
}

VERSION = "0.1.0"
AUTHOR = "Fernando"
REPOSITORY = "git+https://github.com/fernansd/koff.git"

def main():
    base_dir = Path(__file__).parent.parent / "npm" / "packages"
    base_dir.mkdir(parents=True, exist_ok=True)
    
    for platform, info in PLATFORMS.items():
        pkg_name = f"koff-{platform}"
        pkg_dir = base_dir / pkg_name
        pkg_dir.mkdir(parents=True, exist_ok=True)
        
        main_binary = f"koff{info['ext']}"
        
        pkg_json = {
            "name": f"@fernansd/{pkg_name}",
            "version": VERSION,
            "description": f"The {platform} binary for koff",
            "os": [info["os"]],
            "cpu": [info["cpu"]],
            "repository": {
                "type": "git",
                "url": REPOSITORY
            },
            "author": AUTHOR,
            "license": "MIT",
            "bugs": {
                "url": "https://github.com/fernansd/koff/issues"
            },
            "homepage": "https://github.com/fernansd/koff#readme",
            "preferUnplugged": False,
        }
        
        with open(pkg_dir / "package.json", "w") as f:
            json.dump(pkg_json, f, indent=2)
            
        print(f"Generated {pkg_dir / 'package.json'}")

if __name__ == "__main__":
    main()
