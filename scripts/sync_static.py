"""Skip unchanged assets and replace changed files without truncating open previews."""
from pathlib import Path
import os,shutil,tempfile

def copy_static(source,destination):
    source,destination=Path(source),Path(destination)
    if destination.is_file() and source.read_bytes()==destination.read_bytes():return str(destination)
    fd,name=tempfile.mkstemp(prefix='.sync-',dir=destination.parent)
    os.close(fd)
    try:
        shutil.copy2(source,name)
        os.replace(name,destination)
    finally:
        if os.path.exists(name):os.unlink(name)
    return str(destination)
