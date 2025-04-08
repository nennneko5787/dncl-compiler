import sys

from .compiler import compileScript, variables


def main():
    if len(sys.argv) <= 1:
        print("== DNCL Compiler ==")
        print("How to use: dncl <path>")
        return

    with open(sys.argv[1]) as f:
        script = f.read()

    compileScript(script)

    print(variables)


if __name__ == "__main__":
    main()
