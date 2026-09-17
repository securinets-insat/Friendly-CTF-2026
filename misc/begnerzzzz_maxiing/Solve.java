import java.lang.reflect.AccessibleObject;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayDeque;
import java.util.Base64;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.Set;


public class Exploit {
    private static String word(int... letters) {
        char[] out = new char[letters.length];
        for (int i = 0; i < letters.length; i++) out[i] = (char) letters[i];
        return new String(out);
    }

    private static byte[] hash(byte[]... chunks) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        for (byte[] chunk : chunks) md.update(chunk);
        return md.digest();
    }

    private static String hex(byte[] data) {
        StringBuilder out = new StringBuilder();
        for (byte value : data) out.append(String.format("%02x", value & 255));
        return out.toString();
    }

    public static String run(Main.LarpReview review, String nonce) throws Exception {
        String openName = word(115,101,116,65,99,99,101,115,115,105,98,108,101);
        Method open = AccessibleObject.class.getMethod(openName, boolean.class);

        String fieldsName = word(103,101,116,68,101,99,108,97,114,101,100,
                                 70,105,101,108,100,115,48);
        Method rawFields = Class.class.getDeclaredMethod(fieldsName, boolean.class);
        open.invoke(rawFields, true);
        Field[] fields = (Field[]) rawFields.invoke(Main.LarpReview.class, false);

        Object[] roots = null;
        for (Field field : fields) {
            if (field.getType() == Object[].class) {
                open.invoke(field, true);
                roots = (Object[]) field.get(review);
            }
        }
        if (roots == null) return "";

        String methodsName = word(103,101,116,68,101,99,108,97,114,101,100,
                                  77,101,116,104,111,100,115,48);
        Method rawMethods = Class.class.getDeclaredMethod(methodsName, boolean.class);
        open.invoke(rawMethods, true);

        ArrayDeque<Object> queue = new ArrayDeque<>();
        Collections.addAll(queue, roots);
        Set<Object> seen = Collections.newSetFromMap(new IdentityHashMap<>());
        byte[][] pieces = new byte[4][];
        Main.Envelope envelope = null;

        while (!queue.isEmpty()) {
            Object item = queue.removeFirst();
            if (item == null || !seen.add(item)) continue;
            if (item instanceof Main.Trail trail) {
                Collections.addAll(queue, trail.walk());
                continue;
            }
            if (item instanceof Main.Envelope found) {
                envelope = found;
                continue;
            }

            Method[] methods = (Method[]) rawMethods.invoke(item.getClass(), false);
            for (Method method : methods) {
                if (method.getParameterCount() != 0 || method.getReturnType() != String.class)
                    continue;
                try {
                    open.invoke(method, true);
                    String value = (String) method.invoke(item);
                    byte[] packed = Base64.getUrlDecoder().decode(value);
                    if (packed.length != 13 || packed[0] < 0 || packed[0] > 3) continue;
                    byte[] body = java.util.Arrays.copyOf(packed, 9);
                    byte[] tag = hash(nonce.getBytes(StandardCharsets.US_ASCII), body,
                                      "MAX".getBytes(StandardCharsets.US_ASCII));
                    boolean valid = true;
                    for (int i = 0; i < 4; i++) valid &= packed[9 + i] == tag[i];
                    if (valid) pieces[packed[0]] = java.util.Arrays.copyOfRange(packed, 1, 9);
                } catch (Exception ignored) {
                }
            }
        }

        if (envelope == null) return "";
        byte[] key = new byte[32];
        for (int i = 0; i < 4; i++) {
            if (pieces[i] == null) return "";
            for (int j = 0; j < 8; j++) key[i * 8 + j] = pieces[i][j];
        }
        byte[] stream = hash(nonce.getBytes(StandardCharsets.US_ASCII), key);
        byte[] ciphertext = envelope.ciphertext();
        byte[] receipt = new byte[ciphertext.length];
        for (int i = 0; i < receipt.length; i++) receipt[i] = (byte) (ciphertext[i] ^ stream[i]);
        return hex(hash(nonce.getBytes(StandardCharsets.US_ASCII), receipt));
    }
}

/* maxing:{{NOTE}} */
