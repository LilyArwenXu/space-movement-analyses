"""Current light-theme chart exporter; the old folder retains historical snapshots."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]

def export_chart():
    sys.path.insert(0,str(ROOT/'scripts'))
    from build_inclusive import build
    build(refresh=False)

if __name__=='__main__':export_chart()
