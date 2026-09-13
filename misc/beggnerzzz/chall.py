#!/usr/bin/env python3

import ast
import operator
import random
import unicodedata


BLOCKED = [
    "_", ".", "/", "\\",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "open", "flag", "read", "write", "import", "exec", "eval",
    "compile", "globals", "locals", "builtins", "getattr", "setattr",
    "vars", "dir", "type", "class", "help", "breakpoint", "input",
    "clear", "pop", "remove", "del", "closure", "cell_contents",
    "imul", "os", "sys", "system", "subprocess", "lambda", "yield",
]

REVIEW_NODES = {
    ast.Expression,
    ast.Call,
    ast.Name,
    ast.Constant,
    ast.BinOp,
    ast.Add,
    ast.Subscript,
    ast.Load,
    ast.Store,
    ast.NamedExpr,
}

ARCHIVE_NODES = {
    ast.Expression,
    ast.Call,
    ast.Name,
    ast.Constant,
    ast.Attribute,
    ast.Subscript,
    ast.Load,
}

ALLOWED_FIELDS = {"__closure__", "cell_contents", "__imul__"}


class LiveRules(list):
    pass


def pull(name):
    if type(name) is not str or name not in ALLOWED_FIELDS:
        raise ValueError("sealed")
    return operator.attrgetter(name)


def make_judge():
    rules = LiveRules(BLOCKED)
    memory = [rules, BLOCKED.copy(), BLOCKED.copy(), BLOCKED.copy()]
    random.SystemRandom().shuffle(memory)
    memory = tuple(memory)

    def judge(text):
        active = next(part for part in memory if isinstance(part, LiveRules))
        for word in active:
            if word in text:
                return word
        return None

    return judge, rules


def clean(text, limit):
    text = unicodedata.normalize("NFKC", text)
    if not text.isascii() or len(text) > limit:
        raise ValueError("bad input")
    return text


def review_expression(text, judge, scope):
    text = clean(text, 90)
    blocked = judge(text.casefold())
    if blocked is not None:
        return "blocked", None

    tree = ast.parse(text, mode="eval")
    for node in ast.walk(tree):
        if type(node) not in REVIEW_NODES:
            raise ValueError("bad expression")
        if isinstance(node, ast.Name) and node.id not in {
            "judge", "pull", "mark", "a", "b", "c", "d",
        }:
            raise ValueError("bad name")
        if isinstance(node, ast.Constant) and type(node.value) not in {str, bool}:
            raise ValueError("bad constant")

    return "result", eval(compile(tree, "<review>", "eval"), scope, scope)


def archive(first=None, second=None, third=None):
    return "Rockstar says the archive is definitely not leaking."


def make_route(function):
    def route():
        if function is None:
            return None
        raise ValueError("sealed")

    route.__name__ = "route"
    route.__qualname__ = "route"
    return route


def prepare_archive():
    routes = [make_route(abs), make_route(open), make_route(len)]
    random.SystemRandom().shuffle(routes)
    archive.__defaults__ = tuple(routes)


def archive_expression(text, final=False):
    text = clean(text, 120)
    tree = ast.parse(text, mode="eval")
    fields = {"__defaults__", "__closure__", "cell_contents"}
    if final:
        fields.add("read")

    for node in ast.walk(tree):
        if type(node) not in ARCHIVE_NODES:
            raise ValueError("bad expression")
        if isinstance(node, ast.Name) and node.id != "archive":
            raise ValueError("bad name")
        if isinstance(node, ast.Attribute) and node.attr not in fields:
            raise ValueError("sealed")
        if isinstance(node, ast.Constant):
            allowed = {str, int, bool} if final else {int, bool}
            if type(node.value) not in allowed:
                raise ValueError("bad constant")

    scope = {"__builtins__": {}, "archive": archive}
    return eval(compile(tree, "<archive>", "eval"), scope, scope)


def main():
    judge, rules = make_judge()
    prepare_archive()

    review_scope = {
        "__builtins__": {},
        "judge": judge,
        "pull": pull,
        "mark": "_",
    }

    print("BEGGNERZZZ")
    print("ROCKSTAR COMMUNITY REVIEW")
    print()
    print("One word sounded like LARP, so he built a whole personality around it.")
    print("A heavyweight opinion carrying featherweight evidence.")
    print("F.A.T. desk: Full-time Accusation Technician.")
    print("He swallowed the ragebait whole and asked whether dessert was also LARP.")
    print()
    print("Available objects: judge, pull, mark")
    print("pull(name)(object) retrieves a field from an object.")
    print("mark = '_'")
    print("Eight accepted reviews. Rejected posts are free.")

    used = 0
    solved = False
    while used < 8 and not solved:
        try:
            text = input(f"review[{8 - used}]> ")
        except EOFError:
            return

        try:
            status, value = review_expression(text, judge, review_scope)
            if status == "blocked":
                print("POST REJECTED.")
                print("One word found. Obviously the entire post is LARP now.")
                continue

            used += 1
            print(f"RESULT: {value!r}")
            closure = judge.__closure__
            solved = (
                not rules
                and review_scope.get("a") is closure
                and review_scope.get("b") is closure[0].cell_contents
            )
        except Exception:
            used += 1
            print("The moderator ate that argument before reading it.")

    if not solved:
        print("Eight reviews, zero progress: a full plate of confidence and not a crumb of evidence.")
        return

    print()
    print("The rulebook lost all its weight. The moderator kept his.")
    print("He swallowed the bait, the hook, and probably the plate.")
    print("Archive access unlocked.")
    print("Available object: archive")
    print("Four inspections, then one final upload.")

    seen = set()
    targets = {abs, open, len}
    for remaining in range(4, 0, -1):
        try:
            text = input(f"archive[{remaining}]> ")
        except EOFError:
            return

        try:
            result = archive_expression(text)
            print(f"RESULT: {result!r}")
            for target in targets:
                if result is target:
                    seen.add(target)
        except Exception:
            print("A whole archive in front of you and you still uploaded empty calories.")

    if seen != targets:
        print("You inspected four routes and somehow learned nothing from all three.")
        return

    try:
        text = input("final-upload> ")
    except EOFError:
        return

    try:
        result = archive_expression(text, final=True)
        print(f"RESULT: {result!r}")
        if isinstance(result, str) and result.startswith("Securinets{"):
            print("Upload accepted. Turns out the leak was the only honest thing here.")
            return
    except Exception:
        print("A whole archive in front of you and you still uploaded empty calories.")

    print("Rockstar marked the empty upload as another successful security review.")


if __name__ == "__main__":
    main()
