# BEGNERZZZZ MAXIING

## What players receive

- `Main.java`
- `detector.py`
- `detector_weights.json`

The service prints a fresh 16-character nonce and accepts one Base64-encoded
`Exploit.java`. The submitted class must expose:

```java
public static String run(Main.LarpReview review, String nonce) throws Exception
```

The source must finish with `/* maxing:... */`.

## Intended solve

The detector is a byte CNN with a nonce-gated bank of negative filters. Its
weights are public. Recover a printable word for each active negative channel
by choosing, at every convolution position, the byte whose embedding has the
largest dot product with that position's weights. Greedily append recovered
words to the final comment until the logit is negative. A note made for one
nonce normally fails on another nonce.

After `javac`, every generated class is scanned. Literal references to the raw
reflection methods, accessibility helpers, file APIs, process APIs and common
JVM escape primitives are rejected. String concatenation with literals does
not help because `javac` folds it into the same constant pool entry. Construct
the three required names from character codes at runtime.

Ordinary `getDeclaredFields()` cannot see `LarpReview.receipts`. Obtain the
private native `Class.getDeclaredFields0(false)` method, make it accessible
through a dynamically located accessibility method, then recover the hidden
root array.

Walk `Main.Trail` objects by identity rather than recursively. The graph has
cycles and a fresh order on every run. Save the `Main.Envelope` and inspect the
other objects. Ordinary `getDeclaredMethods()` cannot see the useful method on
the permit class, so repeat the raw metadata bypass with
`Class.getDeclaredMethods0(false)`.

Calling the private zero-argument String methods yields many decoys and four
real Base64URL shards. A real shard is 13 bytes:

```text
index (1) || key bytes (8) || SHA256(nonce || first 9 bytes || "MAX")[:4]
```

Place the four valid parts by index to rebuild the 32-byte key. The encryption
stream is `SHA256(nonce || key)`, and the receipt is the envelope ciphertext
XORed with that stream. Return the lowercase hexadecimal value of
`SHA256(nonce || receipt)`. Python verifies it and releases the flag; the flag
itself never enters the submitted JVM.

The envelope is also stateful: before all four genuine `dropReceipts()` calls,
its public getter returns fresh decoy bytes. Reading the graph but skipping the
filtered-method stage therefore produces a bad proof.

`Solve.java` is the organizer implementation. `test.py` derives a new note and
runs it, so no separate solver script is needed.

## Local organizer commands

```bash
python3 make_model.py
/home/ghaith/jdk21/bin/javac \
  --add-exports java.base/jdk.internal.reflect=ALL-UNNAMED Main.java
python3 test.py
docker compose up --build
```

## Security boundaries

The network handler reads the root-only flag, but it starts Java as `ctf`.
Plaintext receipt bytes never enter Java: Python sends only the ciphertext and
authenticated shards used to build the graph. Bootstrap input is consumed
before the submission is initialized, and `System.in` is replaced with EOF.
User output is discarded. Only a valid proof makes the privileged Python
process print the flag.

The class scanner covers top-level, nested, anonymous and lambda-generated
class files. It is intentionally a CTF filter, not a claim that arbitrary Java
is a secure same-process sandbox. The meaningful security boundary is the
unprivileged child process and keeping the flag outside that child.

## Regression checks

`test.py` verifies:

- blank exploit is classified AI;
- an optimized nonce-bound note is classified HUMAN;
- the same note fails on almost all fresh nonces;
- malformed submissions are rejected;
- normal reflection hides both protected members;
- the envelope remains locked until the genuine permit methods run;
- forbidden raw-reflection literals are caught;
- forbidden references inside a nested class are caught;
- direct file access is caught;
- the official exploit works across five shuffled graphs.
