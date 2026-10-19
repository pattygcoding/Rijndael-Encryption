import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec

private const val KEY_BITS = 192
private const val PLAINTEXT = "The quick brown fox jumps over the lazy dog."

fun main() {
    val key = ByteArray(KEY_BITS / 8) { index -> index.toByte() }
    val iv = ByteArray(16) { index -> index.toByte() }

    val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
    cipher.init(Cipher.ENCRYPT_MODE, SecretKeySpec(key, "AES"), IvParameterSpec(iv))
    val ciphertext = cipher.doFinal(PLAINTEXT.toByteArray(Charsets.UTF_8))

    println("AES-$KEY_BITS-CBC")
    println("KEY=${hex(key)}")
    println("IV=${hex(iv)}")
    println("PLAINTEXT=$PLAINTEXT")
    println("CIPHERTEXT=${hex(ciphertext)}")
}

private fun hex(data: ByteArray): String =
    data.joinToString(separator = "") { byte -> "%02x".format(byte) }
