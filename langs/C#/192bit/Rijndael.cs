using System;
using System.Security.Cryptography;
using System.Text;

class RijndaelCbc
{
    private const int KeyBits = 192;
    private const string Plaintext = "The quick brown fox jumps over the lazy dog.";

    private static byte[] Sequence(int length)
    {
        byte[] bytes = new byte[length];
        for (int i = 0; i < length; i++)
        {
            bytes[i] = (byte)i;
        }
        return bytes;
    }

    static void Main()
    {
        byte[] key = Sequence(KeyBits / 8);
        byte[] iv = Sequence(16);
        byte[] input = Encoding.UTF8.GetBytes(Plaintext);

        using Aes aes = Aes.Create();
        aes.KeySize = KeyBits;
        aes.Mode = CipherMode.CBC;
        aes.Padding = PaddingMode.PKCS7;
        aes.Key = key;
        aes.IV = iv;

        byte[] ciphertext;
        using (ICryptoTransform encryptor = aes.CreateEncryptor())
        {
            ciphertext = encryptor.TransformFinalBlock(input, 0, input.Length);
        }

        Console.WriteLine($"AES-{KeyBits}-CBC");
        Console.WriteLine($"KEY={Convert.ToHexString(key).ToLowerInvariant()}");
        Console.WriteLine($"IV={Convert.ToHexString(iv).ToLowerInvariant()}");
        Console.WriteLine($"PLAINTEXT={Plaintext}");
        Console.WriteLine($"CIPHERTEXT={Convert.ToHexString(ciphertext).ToLowerInvariant()}");
    }
}
