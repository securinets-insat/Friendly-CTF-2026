import java.io.OutputStream;
import java.io.PrintStream;
import java.lang.reflect.Method;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.Base64;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Set;
import java.util.stream.Stream;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaCompiler;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;
import jdk.internal.reflect.Reflection;


public final class Main {
    private static final SecureRandom RANDOM = new SecureRandom();

    private static final String[] BLOCKED = {
        "getDeclaredFields0", "getDeclaredMethods0", "setAccessible",
        "trySetAccessible", "java/lang/System", "java/io/", "java/nio/file",
        "java/lang/Runtime", "java/lang/ProcessBuilder", "sun/misc/Unsafe",
        "jdk/internal/misc/Unsafe", "java/lang/invoke/MethodHandles$Lookup",
        "jdk/internal/reflect/Reflection", "com/sun/tools/attach", "/flag",
        "flag.txt"
    };

    static {
        Reflection.registerFieldsToFilter(LarpReview.class, Set.of("receipts"));
        Reflection.registerFieldsToFilter(MaxxingPermit.class, Reflection.ALL_MEMBERS);
        Reflection.registerFieldsToFilter(Envelope.class, Reflection.ALL_MEMBERS);
        Reflection.registerMethodsToFilter(
            MaxxingPermit.class, Set.of("dropReceipts", "manifest")
        );
    }

    public static final class LarpReview {
        private final String title = "beginner maxing session";
        private final Object[] receipts;

        private LarpReview(Object[] receipts) {
            this.receipts = receipts;
        }

        public String title() {
            return title;
        }
    }

    public static final class Trail {
        private Object[] exits;
        private final long graffiti = RANDOM.nextLong();

        private void connect(Object[] exits) {
            this.exits = exits;
        }

        public Object[] walk() {
            return exits.clone();
        }

        public long graffiti() {
            return graffiti;
        }
    }

    public static final class Envelope {
        private final byte[] ciphertext;
        private final ReceiptGate gate;

        private Envelope(byte[] ciphertext, ReceiptGate gate) {
            this.ciphertext = ciphertext;
            this.gate = gate;
        }

        public byte[] ciphertext() {
            if (gate.ready()) {
                return ciphertext.clone();
            }
            byte[] fake = new byte[ciphertext.length];
            RANDOM.nextBytes(fake);
            return fake;
        }

        public int size() {
            return ciphertext.length;
        }
    }

    private static final class MaxxingPermit {
        private final String shard;
        private final String bait;
        private final ReceiptGate gate;
        private final int slot;

        private MaxxingPermit(String shard, String bait, ReceiptGate gate, int slot) {
            this.shard = shard;
            this.bait = bait;
            this.gate = gate;
            this.slot = slot;
        }

        private String dropReceipts() {
            gate.touch(slot);
            return shard;
        }

        private String manifest() {
            return bait;
        }

        public String aura() {
            return "verified on main";
        }
    }

    private static final class ReceiptGate {
        private int opened;

        private synchronized void touch(int slot) {
            if (slot >= 0 && slot < 4) {
                opened |= 1 << slot;
            }
        }

        private synchronized boolean ready() {
            return opened == 15;
        }
    }

    private static byte[] digest(byte[]... chunks) throws Exception {
        MessageDigest hash = MessageDigest.getInstance("SHA-256");
        for (byte[] chunk : chunks) {
            hash.update(chunk);
        }
        return hash.digest();
    }

    private static LarpReview forge(
            String nonce, byte[] ciphertext, List<String> genuine) throws Exception {
        if (genuine.size() != 4) {
            throw new IllegalArgumentException("bad receipt bundle");
        }
        ReceiptGate gate = new ReceiptGate();

        List<Object> cargo = new ArrayList<>();
        boolean[] slots = new boolean[4];
        for (String value : genuine) {
            byte[] packed = Base64.getUrlDecoder().decode(value);
            if (packed.length != 13 || packed[0] < 0 || packed[0] > 3) {
                throw new IllegalArgumentException("bad receipt bundle");
            }
            int slot = packed[0];
            byte[] body = java.util.Arrays.copyOf(packed, 9);
            byte[] tag = digest(
                nonce.getBytes(StandardCharsets.US_ASCII), body,
                "MAX".getBytes(StandardCharsets.US_ASCII)
            );
            if (slots[slot] || !java.util.Arrays.equals(
                    java.util.Arrays.copyOfRange(packed, 9, 13),
                    java.util.Arrays.copyOf(tag, 4))) {
                throw new IllegalArgumentException("bad receipt bundle");
            }
            slots[slot] = true;
            cargo.add(new MaxxingPermit(
                value, "cope-" + RANDOM.nextLong(), gate, slot
            ));
        }
        for (int i = 0; i < 9; i++) {
            byte[] fake = new byte[13];
            RANDOM.nextBytes(fake);
            cargo.add(new MaxxingPermit(
                Base64.getUrlEncoder().withoutPadding().encodeToString(fake),
                "source: trust me bro " + i, gate, -1
            ));
        }
        cargo.add(new Envelope(ciphertext, gate));
        cargo.add("proof by screenshot");
        cargo.add(Integer.valueOf(900));
        Collections.shuffle(cargo, RANDOM);

        List<Trail> trails = new ArrayList<>();
        for (int i = 0; i < cargo.size(); i++) {
            trails.add(new Trail());
        }
        for (int i = 0; i < trails.size(); i++) {
            List<Object> exits = new ArrayList<>();
            exits.add(trails.get((i + 1) % trails.size()));
            exits.add(cargo.get(i));
            exits.add(trails.get(RANDOM.nextInt(trails.size())));
            if (RANDOM.nextBoolean()) {
                exits.add("larp-level-" + RANDOM.nextInt(1000));
            }
            Collections.shuffle(exits, RANDOM);
            trails.get(i).connect(exits.toArray());
        }

        List<Object> roots = new ArrayList<>();
        roots.add(trails.get(RANDOM.nextInt(trails.size())));
        roots.add(trails.get(RANDOM.nextInt(trails.size())));
        roots.add("nothing happened here");
        roots.add(Long.valueOf(RANDOM.nextLong()));
        Collections.shuffle(roots, RANDOM);
        return new LarpReview(roots.toArray());
    }

    private static boolean compile(String source, Path output) throws Exception {
        Path file = output.resolve("Exploit.java");
        Files.writeString(file, source, StandardCharsets.US_ASCII);
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
        try (StandardJavaFileManager files = compiler.getStandardFileManager(
                diagnostics, null, StandardCharsets.UTF_8)) {
            Iterable<? extends JavaFileObject> units =
                files.getJavaFileObjectsFromFiles(List.of(file.toFile()));
            List<String> options = List.of(
                "--release", "21", "-classpath",
                java.lang.System.getProperty("java.class.path"),
                "-d", output.toString(), "-g:none"
            );
            return Boolean.TRUE.equals(compiler.getTask(
                null, files, diagnostics, options, null, units
            ).call());
        }
    }

    private static String scan(Path output) throws Exception {
        int classes = 0;
        long total = 0;
        try (Stream<Path> paths = Files.walk(output)) {
            for (Path path : paths.filter(p -> p.toString().endsWith(".class")).toList()) {
                classes++;
                byte[] bytes = Files.readAllBytes(path);
                total += bytes.length;
                String raw = new String(bytes, StandardCharsets.ISO_8859_1);
                for (String word : BLOCKED) {
                    if (raw.contains(word)) {
                        return word;
                    }
                }
            }
        }
        if (classes == 0 || classes > 20 || total > 120_000) {
            return "class budget";
        }
        return null;
    }

    private static void erase(Path root) {
        try (Stream<Path> paths = Files.walk(root)) {
            paths.sorted(Comparator.reverseOrder()).forEach(path -> {
                try {
                    Files.deleteIfExists(path);
                } catch (Exception ignored) {
                }
            });
        } catch (Exception ignored) {
        }
    }

    public static void main(String[] args) throws Exception {
        PrintStream console = java.lang.System.out;
        String nonce;
        byte[] ciphertext;
        List<String> genuine;
        String source;
        try {
            var input = new java.io.BufferedReader(new java.io.InputStreamReader(
                java.lang.System.in, StandardCharsets.US_ASCII
            ));
            nonce = input.readLine();
            ciphertext = Base64.getDecoder().decode(input.readLine());
            genuine = List.of(input.readLine().split(",", -1));
            source = new String(
                Base64.getDecoder().decode(input.readLine()), StandardCharsets.US_ASCII
            );
        } catch (Exception error) {
            console.println("ERROR:bootstrap");
            return;
        }
        java.lang.System.setIn(new java.io.ByteArrayInputStream(new byte[0]));

        Path output = Files.createTempDirectory("maxing-");
        try {
            if (!compile(source, output)) {
                console.println("ERROR:compile");
                return;
            }
            String rejected = scan(output);
            if (rejected != null) {
                console.println("REJECTED:" + rejected);
                return;
            }

            try (URLClassLoader loader = new URLClassLoader(
                    new URL[]{output.toUri().toURL()}, Main.class.getClassLoader())) {
                Class<?> exploit = Class.forName("Exploit", false, loader);
                Method run = exploit.getMethod("run", LarpReview.class, String.class);
                if (run.getReturnType() != String.class ||
                        !java.lang.reflect.Modifier.isStatic(run.getModifiers())) {
                    console.println("ERROR:signature");
                    return;
                }

                LarpReview review = forge(nonce, ciphertext, genuine);
                OutputStream nowhere = OutputStream.nullOutputStream();
                java.lang.System.setOut(new PrintStream(nowhere));
                java.lang.System.setErr(new PrintStream(nowhere));
                Object answer = run.invoke(null, review, nonce);
                String proof = answer instanceof String ? (String) answer : "";
                if (!proof.matches("[0-9a-f]{64}")) {
                    console.println("ERROR:proof");
                    return;
                }
                console.println("RESULT:" + proof);
            }
        } catch (Throwable error) {
            console.println("ERROR:" + error.getClass().getSimpleName());
        } finally {
            erase(output);
        }
    }
}
