import sys, os

# Ensure project root is on sys.path so `import migrator` works when
# running the script from the scripts/ folder.
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root not in sys.path:
    sys.path.insert(0, root)

import migrator

print("migrator imported")
print("has connection_manager:", hasattr(migrator, 'connection_manager'))
print("connection callable:", callable(getattr(migrator, 'connection', None)))

try:
    ok = migrator.test_connection()
    print("test_connection() returned:", ok)
except Exception as e:
    print("test_connection raised:", repr(e))
