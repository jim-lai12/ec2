from Crypto.Cipher import AES
import base64
from hashlib import md5
from Crypto import Random
import getpass




def pad(data):
    length = 16 - (len(data) % 16)
    return data + (chr(length)*length).encode()

def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

def bytes_to_key(data, salt, output=48):
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]

def encrypt_aes(message, passphrase):
    salt = Random.new().read(8)
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message)))

def decrypt_aes(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:]))


def encryptfile(password):
    with open("config/credentials", "rb+") as f:
        text = f.read()
        encrypttext = encrypt_aes(text, password.encode('utf-8'))
        f.seek(0)
        f.truncate(0)
        f.write(encrypttext)
    with open("config/config", "rb+") as f:
        text = f.read()
        encrypttext = encrypt_aes(text, password.encode('utf-8'))
        f.seek(0)
        f.truncate(0)
        f.write(encrypttext)
    with open("config/ec2key.pem", "rb+") as f:
        text = f.read()
        encrypttext = encrypt_aes(text, password.encode('utf-8'))
        f.seek(0)
        f.truncate(0)
        f.write(encrypttext)


def decryptfile(password):
    with open("config/credentials", "rb+") as f:
        text = f.read()
        encrypttext = decrypt_aes(text, password.encode('utf-8'))
        with open("/root/.aws/credentials", "rb+") as f1:
            f1.seek(0)
            f1.truncate(0)
            f1.write(encrypttext)

    with open("config/config", "rb+") as f:
        text = f.read()
        encrypttext = decrypt_aes(text, password.encode('utf-8'))
        with open("/root/.aws/config", "rb+") as f1:
            f1.seek(0)
            f1.truncate(0)
            f1.write(encrypttext)

    with open("config/ec2key.pem", "rb+") as f:
        text = f.read()
        encrypttext = decrypt_aes(text, password.encode('utf-8'))
        f.seek(0)
        f.truncate(0)
        f.write(encrypttext)



if __name__ == '__main__':
    password = getpass.getpass("Input password:\n")
    #encryptfile(password)
    decryptfile(password)
