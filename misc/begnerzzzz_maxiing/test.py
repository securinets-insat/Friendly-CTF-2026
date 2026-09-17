#!/usr/bin/env python3

import base64
import hashlib
import os
from pathlib import Path
import secrets
import subprocess
import tempfile

from detector import BadSource, Detector, PRINTABLE
from chall import seal


ROOT = Path(__file__).resolve().parent
JAVA = "/home/ghaith/jdk21/bin/java"
JAVAC = "/home/ghaith/jdk21/bin/javac"
RUN = [
    JAVA, "-Xmx192m",
    "--add-exports=java.base/jdk.internal.reflect=ALL-UNNAMED",
    "--add-opens=java.base/java.lang=ALL-UNNAMED",
    "-cp", str(ROOT), "Main",
]


def source_with_note(template, nonce):
    detector = Detector()
    active = detector.active(nonce)
    words = []

    for branch in detector.branches:
        for table, head, scope, gate in zip(
            branch["table"], branch["head"], branch["scope"], branch["gate"]
        ):
            if scope != "note" or head >= 0 or gate not in active:
                continue
            word = bytes(
                max(PRINTABLE, key=lambda char: table[i][char])
                for i in range(branch["width"])
            )
            words.append((gate, word))

    note = b""
    render = lambda value: template.replace(b"{{NOTE}}", value)
    score = detector.score(nonce, render(note))
    while score >= detector.threshold:
        choices = []
        for gate, word in words:
            trial = note + (b"_" if note else b"") + word
            if len(trial) > detector.max_note:
                continue
            new_score = detector.score(nonce, render(trial))
            choices.append((score - new_score, gate, word, trial, new_score))
        if not choices:
            raise AssertionError("detector has no solution")
        gain, gate, word, note, score = max(choices)
        if gain <= 0:
            raise AssertionError("detector got stuck")
        words = [item for item in words if item[0] != gate]
    return render(note), note


def run_main(source, nonce=None, receipt=None):
    nonce = nonce or secrets.token_hex(8)
    receipt = receipt or secrets.token_bytes(24)
    ciphertext, shards = seal(nonce, receipt)
    payload = b"\n".join([
        nonce.encode(), base64.b64encode(ciphertext), shards,
        base64.b64encode(source)
    ]) + b"\n"
    result = subprocess.run(
        RUN, input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=20, cwd=ROOT
    )
    return result.stdout.decode().strip(), hashlib.sha256(
        nonce.encode() + receipt
    ).hexdigest()


def compile_main():
    subprocess.run([
        JAVAC, "--add-exports", "java.base/jdk.internal.reflect=ALL-UNNAMED",
        "Main.java"
    ], cwd=ROOT, check=True)


def filter_probe():
    code = r'''
public class FilterProbe {
    public static void main(String[] args) throws Exception {
        Class.forName("Main");
        boolean field = false, method = false;
        for (var f : Main.LarpReview.class.getDeclaredFields())
            field |= f.getName().equals("receipts");
        for (var c : Main.class.getDeclaredClasses())
            if (c.getName().endsWith("MaxxingPermit"))
                for (var m : c.getDeclaredMethods())
                    method |= m.getName().equals("dropReceipts");

        var genuine = new java.util.ArrayList<String>();
        for (int slot = 0; slot < 4; slot++) {
            byte[] body = new byte[9];
            body[0] = (byte) slot;
            var hash = java.security.MessageDigest.getInstance("SHA-256");
            hash.update("0123456789abcdef".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
            hash.update(body);
            byte[] tag = hash.digest("MAX".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
            byte[] packed = java.util.Arrays.copyOf(body, 13);
            java.lang.System.arraycopy(tag, 0, packed, 9, 4);
            genuine.add(java.util.Base64.getUrlEncoder().withoutPadding().encodeToString(packed));
        }
        var forge = Main.class.getDeclaredMethod(
            "forge", String.class, byte[].class, java.util.List.class
        );
        forge.setAccessible(true);
        var review = (Main.LarpReview) forge.invoke(
            null, "0123456789abcdef", new byte[24], genuine
        );
        var rawFields = Class.class.getDeclaredMethod("getDeclaredFields0", boolean.class);
        var rawMethods = Class.class.getDeclaredMethod("getDeclaredMethods0", boolean.class);
        rawFields.setAccessible(true);
        rawMethods.setAccessible(true);
        Object[] roots = null;
        for (var f : (java.lang.reflect.Field[]) rawFields.invoke(Main.LarpReview.class, false)) {
            if (f.getType() == Object[].class) {
                f.setAccessible(true);
                roots = (Object[]) f.get(review);
            }
        }
        var queue = new java.util.ArrayDeque<Object>();
        java.util.Collections.addAll(queue, roots);
        var seen = java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<>());
        var permits = new java.util.ArrayList<Object>();
        Main.Envelope envelope = null;
        while (!queue.isEmpty()) {
            Object item = queue.remove();
            if (item == null || !seen.add(item)) continue;
            if (item instanceof Main.Trail trail) java.util.Collections.addAll(queue, trail.walk());
            else if (item instanceof Main.Envelope found) envelope = found;
            else if (item.getClass().getName().endsWith("MaxxingPermit")) permits.add(item);
        }
        byte[] locked = envelope.ciphertext();
        for (Object permit : permits) {
            for (var m : (java.lang.reflect.Method[]) rawMethods.invoke(permit.getClass(), false)) {
                if (m.getParameterCount() == 0 && m.getReturnType() == String.class) {
                    m.setAccessible(true);
                    m.invoke(permit);
                }
            }
        }
        byte[] opened = envelope.ciphertext();
        byte[] openedAgain = envelope.ciphertext();
        System.out.print(field + ":" + method + ":" +
            java.util.Arrays.equals(locked, opened) + ":" +
            java.util.Arrays.equals(opened, openedAgain));
    }
}
'''
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "FilterProbe.java"
        path.write_text(code)
        subprocess.run([JAVAC, "-cp", str(ROOT), str(path)], check=True)
        result = subprocess.run([
            JAVA, "--add-exports=java.base/jdk.internal.reflect=ALL-UNNAMED",
            "--add-opens=java.base/java.lang=ALL-UNNAMED",
            "-cp", f"{ROOT}:{folder}", "FilterProbe"
        ], stdout=subprocess.PIPE, check=True)
        return result.stdout.decode()


def handler_test(template):
    process = subprocess.Popen(
        ["python3", "-u", "chall.py"], cwd=ROOT,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    banner = b""
    while b"source> " not in banner:
        block = os.read(process.stdout.fileno(), 1)
        if not block:
            raise AssertionError(process.stderr.read().decode())
        banner += block
    nonce = next(
        line.split(b": ", 1)[1].decode()
        for line in banner.splitlines() if line.startswith(b"session nonce:")
    )
    source, _ = source_with_note(template, nonce)
    process.stdin.write(base64.b64encode(source) + b"\n")
    process.stdin.flush()
    tail, errors = process.communicate(timeout=25)
    transcript = (banner + tail).decode()
    if process.returncode or errors:
        raise AssertionError(errors.decode())
    return transcript


def main():
    compile_main()
    detector = Detector()
    solve = (ROOT / "Solve.java").read_bytes()

    nonce = "0123456789abcdef"
    blank = solve.replace(b"{{NOTE}}", b"")
    assert detector.classify(nonce, blank)[2] == "AI"
    attack, note = source_with_note(solve, nonce)
    assert detector.classify(nonce, attack)[2] == "HUMAN"
    assert len(note) <= detector.max_note
    print("[+] blank exploit is AI; optimized exploit is HUMAN")

    misses = 0
    for _ in range(16):
        other = secrets.token_hex(8)
        misses += detector.classify(other, attack)[2] == "AI"
    assert misses >= 14
    print(f"[+] fixed note rejected by {misses}/16 fresh nonces")

    try:
        detector.classify(nonce, b"public class Exploit {}")
        raise AssertionError("source without note accepted")
    except BadSource:
        pass
    print("[+] malformed and marker-free sources rejected")

    assert filter_probe() == "false:false:false:true"
    print("[+] filters hide both members; envelope stays locked until method calls")

    direct = b'''
public class Exploit {
 public static String run(Main.LarpReview r, String n) throws Exception {
  Class.class.getDeclaredMethod("getDeclaredFields0", boolean.class);
  return "0".repeat(64);
 }
}
/* maxing:{{NOTE}} */
'''.replace(b"{{NOTE}}", b"")
    output, _ = run_main(direct)
    assert output == "REJECTED:getDeclaredFields0", output
    print("[+] direct raw-reflection literal rejected")

    nested = b'''
public class Exploit {
 static class SideDoor { static long x() { return java.lang.System.nanoTime(); } }
 public static String run(Main.LarpReview r, String n) { return "0".repeat(64); }
}
/* maxing: */
'''
    output, _ = run_main(nested)
    assert output == "REJECTED:java/lang/System", output
    print("[+] nested classes are scanned")

    file_read = b'''
public class Exploit {
 public static String run(Main.LarpReview r, String n) throws Exception {
  return java.nio.file.Files.readString(java.nio.file.Path.of("/flag.txt"));
 }
}
/* maxing: */
'''
    output, _ = run_main(file_read)
    assert output in {"REJECTED:java/nio/file", "REJECTED:/flag"}, output
    print("[+] direct flag-file route rejected")

    for _ in range(5):
        fresh = secrets.token_hex(8)
        attack, _ = source_with_note(solve, fresh)
        output, expected = run_main(attack, fresh)
        assert output == "RESULT:" + expected, output
    print("[+] intended exploit survived five randomized graphs")

    transcript = handler_test(solve)
    flag = (ROOT / "flag.txt").read_text().strip()
    assert "verdict: HUMAN" in transcript and flag in transcript
    print("[+] complete Python handler released the flag for a valid proof")
    print("all tests passed")


if __name__ == "__main__":
    main()
