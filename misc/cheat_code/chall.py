#!/usr/bin/env python3


def main():
    print("CHEAT CODE")
    print("Rockstar left the developer console in the release build.")

    try:
        code = input("> ")
        print(eval(code))
    except Exception:
        print("Cheat failed.")


if __name__ == "__main__":
    main()
