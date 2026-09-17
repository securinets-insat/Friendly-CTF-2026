# Human After All

The service puts the player's note in the last comment of `Submission.java` and
runs the supplied byte classifier. Notes are printable ASCII, at most 72 bytes,
and cannot contain `*/`.

The model has a byte embedding, four convolution widths (3, 5, 7, 11), ReLU,
global max pooling, and one linear output. The source, model, threshold and
weights given to players are the exact files used by the server.

The local detector, threshold, preprocessing, source template, and weights are
all public and deterministic.

## Intended solution

Look at channels with negative output weights. For each position in one of those
filters, try every printable byte and keep the embedding with the largest dot
product. This gives one good string per filter.

Not every recovered n-gram is useful:

- several negative channels are already saturated by `Submission.java`;
- some attractive negative channels also activate positive channels;
- all recovered strings do not fit in the note.

Score those strings locally and keep the best score reduction per byte. Some
negative filters are already active in the Java file, and a few candidate
strings also activate positive filters, so blindly joining all of them does not
work. See `solver.py` for the short reference implementation.

## Organizer commands

```bash
python3 generate_weights.py
python3 solver.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
docker compose up --build
python3 solver.py 127.0.0.1 9043
```
