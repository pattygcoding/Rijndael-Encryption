import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;

public class Rijndael {

    private static final int KEY_BITS = 192;
    private static final String PLAINTEXT = "The quick brown fox jumps over the lazy dog.";

    public static void main(String[] args) throws Exception {
        byte[] key = sequence(KEY_BITS / 8);
        byte[] iv = sequence(16);

        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(key, "AES"), new IvParameterSpec(iv));
        byte[] ciphertext = cipher.doFinal(PLAINTEXT.getBytes(StandardCharsets.UTF_8));

        System.out.println("AES-" + KEY_BITS + "-CBC");
        System.out.println("KEY=" + hex(key));
        System.out.println("IV=" + hex(iv));
        System.out.println("PLAINTEXT=" + PLAINTEXT);
        System.out.println("CIPHERTEXT=" + hex(ciphertext));
    }

    private static byte[] sequence(int length) {
        byte[] bytes = new byte[length];
        for (int i = 0; i < length; i++) {
            bytes[i] = (byte) i;
        }
        return bytes;
    }

    private static String hex(byte[] data) {
        StringBuilder out = new StringBuilder(data.length * 2);
        for (byte value : data) {
            out.append(String.format("%02x", value));
        }
        return out.toString();
    }
}
