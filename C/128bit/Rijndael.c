#include <openssl/evp.h>
#include <stdio.h>
#include <string.h>

#define KEY_BITS 128
#define KEY_LENGTH (KEY_BITS / 8)

static const char *PLAINTEXT = "The quick brown fox jumps over the lazy dog.";

static void make_bytes(unsigned char *buffer, int length) {
    for (int i = 0; i < length; i++) {
        buffer[i] = (unsigned char)i;
    }
}

static void print_hex(const char *label, const unsigned char *data, int length) {
    printf("%s=", label);
    for (int i = 0; i < length; i++) {
        printf("%02x", data[i]);
    }
    printf("\n");
}

int main(void) {
    unsigned char key[KEY_LENGTH];
    unsigned char iv[16];
    unsigned char ciphertext[256];
    int written = 0;
    int final_length = 0;

    make_bytes(key, KEY_LENGTH);
    make_bytes(iv, 16);

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (ctx == NULL) {
        return 1;
    }
    if (EVP_EncryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, key, iv) != 1) {
        return 2;
    }
    if (EVP_EncryptUpdate(ctx, ciphertext, &written,
                          (const unsigned char *)PLAINTEXT,
                          (int)strlen(PLAINTEXT)) != 1) {
        return 3;
    }
    if (EVP_EncryptFinal_ex(ctx, ciphertext + written, &final_length) != 1) {
        return 4;
    }
    EVP_CIPHER_CTX_free(ctx);

    printf("AES-%d-CBC\n", KEY_BITS);
    print_hex("KEY", key, KEY_LENGTH);
    print_hex("IV", iv, 16);
    printf("PLAINTEXT=%s\n", PLAINTEXT);
    print_hex("CIPHERTEXT", ciphertext, written + final_length);
    return 0;
}
