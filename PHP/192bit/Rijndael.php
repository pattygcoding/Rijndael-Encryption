<?php
const KEY_BITS = 192;
const PLAINTEXT = "The quick brown fox jumps over the lazy dog.";

function sequence(int $length): string {
    return implode("", array_map("chr", range(0, $length - 1)));
}

$key = sequence(KEY_BITS / 8);
$iv = sequence(16);
$ciphertext = openssl_encrypt(
    PLAINTEXT,
    "aes-" . KEY_BITS . "-cbc",
    $key,
    OPENSSL_RAW_DATA,
    $iv
);

if ($ciphertext === false) {
    fwrite(STDERR, "encryption failed\n");
    exit(1);
}

echo "AES-" . KEY_BITS . "-CBC\n";
echo "KEY=" . bin2hex($key) . "\n";
echo "IV=" . bin2hex($iv) . "\n";
echo "PLAINTEXT=" . PLAINTEXT . "\n";
echo "CIPHERTEXT=" . bin2hex($ciphertext) . "\n";
