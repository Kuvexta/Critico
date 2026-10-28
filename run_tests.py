"""English-named entry point for the shared regression suite."""
import sys

sys.dont_write_bytecode = True

from probar_todo import main

if __name__ == "__main__":
    raise SystemExit(main())
