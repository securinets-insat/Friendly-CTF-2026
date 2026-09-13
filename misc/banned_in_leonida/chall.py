#!/usr/bin/env python3

import builtins


def main():
    blocked = ["open", "flag", "import", "os", "system", "breakpoint", "help"]

    print("BANNED IN LEONIDA")
    print("Rockstar patched the leak. Apparently.")

    code = input("> ")

    if any(word in code.lower() for word in blocked):
        print("That word is banned in Leonida.")
        return

    try:
        print(eval(code, {"__builtins__": builtins}))
    except Exception:
        print("Access denied.")


if __name__ == "__main__":
    main()
