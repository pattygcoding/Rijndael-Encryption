{-# LANGUAGE OverloadedStrings #-}

import Crypto.Cipher.AES (AES128)
import Crypto.Cipher.Types (IV, cbcEncrypt, cipherInit, makeIV)
import Crypto.Error (CryptoFailable(..))
import Data.ByteArray.Encoding (Base(Base16), convertToBase)
import Data.ByteString (ByteString)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C8

keyBits :: Int
keyBits = 128

keyBytes :: ByteString
keyBytes = B.pack [0 .. fromIntegral (keyBits `div` 8 - 1)]

ivBytes :: ByteString
ivBytes = B.pack [0 .. 15]

plaintext :: ByteString
plaintext = "The quick brown fox jumps over the lazy dog."

padPkcs7 :: ByteString -> ByteString
padPkcs7 input =
    let padLength = 16 - (B.length input `mod` 16)
    in input <> B.replicate padLength (fromIntegral padLength)

hex :: ByteString -> String
hex = C8.unpack . (convertToBase Base16 :: ByteString -> ByteString)

main :: IO ()
main =
    case cipherInit keyBytes :: CryptoFailable AES128 of
        CryptoFailed err -> error (show err)
        CryptoPassed cipher ->
            case makeIV ivBytes :: Maybe (IV AES128) of
                Nothing -> error "invalid IV"
                Just iv -> do
                    let ciphertext = cbcEncrypt cipher iv (padPkcs7 plaintext)
                    putStrLn ("AES-" ++ show keyBits ++ "-CBC")
                    putStrLn ("KEY=" ++ hex keyBytes)
                    putStrLn ("IV=" ++ hex ivBytes)
                    putStrLn ("PLAINTEXT=" ++ C8.unpack plaintext)
                    putStrLn ("CIPHERTEXT=" ++ hex ciphertext)
