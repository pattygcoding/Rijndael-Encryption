#include <openssl/evp.h>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

namespace {

constexpr int kKeyBits = 192;
constexpr int kKeyLength = kKeyBits / 8;
constexpr const char *kPlaintext = "The quick brown fox jumps over the lazy dog.";

std::vector<unsigned char> sequence(int length) {
    std::vector<unsigned char> bytes(static_cast<std::size_t>(length));
    for (int i = 0; i < length; ++i) {
        bytes[static_cast<std::size_t>(i)] = static_cast<unsigned char>(i);
    }
    return bytes;
}

void print_hex(const char *label, const std::vector<unsigned char> &data) {
    std::cout << label << "=";
    for (unsigned char byte : data) {
        std::cout << std::hex << std::setw(2) << std::setfill('0')
                  << static_cast<int>(byte);
    }
    std::cout << std::dec << "\n";
}

}  // namespace

int main() {
    const std::vector<unsigned char> key = sequence(kKeyLength);
    const std::vector<unsigned char> iv = sequence(16);
    const std::size_t plaintext_length = std::strlen(kPlaintext);
    std::vector<unsigned char> ciphertext(plaintext_length + 16);

    int written = 0;
    int final_length = 0;

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (ctx == nullptr) {
        return 1;
    }
    if (EVP_EncryptInit_ex(ctx, EVP_aes_192_cbc(), nullptr, key.data(), iv.data()) != 1) {
        return 2;
    }
    if (EVP_EncryptUpdate(ctx, ciphertext.data(), &written,
                          reinterpret_cast<const unsigned char *>(kPlaintext),
                          static_cast<int>(plaintext_length)) != 1) {
        return 3;
    }
    if (EVP_EncryptFinal_ex(ctx, ciphertext.data() + written, &final_length) != 1) {
        return 4;
    }
    EVP_CIPHER_CTX_free(ctx);
    ciphertext.resize(static_cast<std::size_t>(written + final_length));

    std::cout << "AES-" << kKeyBits << "-CBC\n";
    print_hex("KEY", key);
    print_hex("IV", iv);
    std::cout << "PLAINTEXT=" << kPlaintext << "\n";
    print_hex("CIPHERTEXT", ciphertext);
    return 0;
}
