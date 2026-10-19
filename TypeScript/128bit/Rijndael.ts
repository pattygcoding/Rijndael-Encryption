import { createCipheriv } from "node:crypto";

const KEY_BITS = 128;
const PLAINTEXT = "The quick brown fox jumps over the lazy dog.";

function sequence(length: number): Buffer {
    return Buffer.from(Array.from({ length }, (_, index) => index));
}

function main(): void {
    const key = sequence(KEY_BITS / 8);
    const iv = sequence(16);
    const cipher = createCipheriv(`aes-${KEY_BITS}-cbc`, key, iv);
    const ciphertext = Buffer.concat([cipher.update(PLAINTEXT, "utf8"), cipher.final()]);

    console.log(`AES-${KEY_BITS}-CBC`);
    console.log(`KEY=${key.toString("hex")}`);
    console.log(`IV=${iv.toString("hex")}`);
    console.log(`PLAINTEXT=${PLAINTEXT}`);
    console.log(`CIPHERTEXT=${ciphertext.toString("hex")}`);
}

main();
