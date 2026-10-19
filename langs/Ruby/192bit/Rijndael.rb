require "openssl"

KEY_BITS = 192
PLAINTEXT = "The quick brown fox jumps over the lazy dog."

key = (0...(KEY_BITS / 8)).map(&:chr).join
iv = (0...16).map(&:chr).join

cipher = OpenSSL::Cipher.new("aes-#{KEY_BITS}-cbc")
cipher.encrypt
cipher.key = key
cipher.iv = iv
ciphertext = cipher.update(PLAINTEXT) + cipher.final

puts "AES-#{KEY_BITS}-CBC"
puts "KEY=#{key.unpack1("H*")}"
puts "IV=#{iv.unpack1("H*")}"
puts "PLAINTEXT=#{PLAINTEXT}"
puts "CIPHERTEXT=#{ciphertext.unpack1("H*")}"
