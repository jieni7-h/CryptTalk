import base64
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# ========== RSA 相关 ==========
def generate_rsa_keypair():
    """生成 RSA 密钥对"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def rsa_encrypt(data, public_key):
    """RSA 公钥加密"""
    return public_key.encrypt(
        data,
        padding.PKCS1v15()
    )

def rsa_decrypt(data, private_key):
    """RSA 私钥解密"""
    return private_key.decrypt(
        data,
        padding.PKCS1v15()
    )

def public_key_to_base64(public_key):
    """公钥转 Base64 字符串"""
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return base64.b64encode(pem).decode()

def base64_to_public_key(base64_str):
    """Base64 字符串转公钥"""
    der_data = base64.b64decode(base64_str)
    return serialization.load_der_public_key(der_data, backend=default_backend())

# ========== DES 相关 ==========
def generate_des_key():
    """生成 DES 密钥（8 字节）"""
    return os.urandom(8)  # DES 密钥是 56 位有效位 + 8 位校验 = 8 字节

def des_encrypt(data, key):
    """DES 加密（ECB 模式）"""
    cipher = Cipher(algorithms.TripleDES(key), modes.ECB(), backend=default_backend())
    # 注意：cryptography 库的 DES 需要 8 字节密钥，实际是 TripleDES 兼容
    # 这里使用 DES 的替代方案
    encryptor = cipher.encryptor()
    # 需要 PKCS7 填充
    pad_len = 8 - (len(data) % 8)
    data += bytes([pad_len] * pad_len)
    return encryptor.update(data) + encryptor.finalize()

def des_decrypt(data, key):
    """DES 解密（ECB 模式）"""
    cipher = Cipher(algorithms.TripleDES(key), modes.ECB(), backend=default_backend())
    decryptor = cipher.decryptor()
    plain_padded = decryptor.update(data) + decryptor.finalize()
    # 去除 PKCS7 填充
    pad_len = plain_padded[-1]
    return plain_padded[:-pad_len]

# 更简单的 DES 实现（使用 pycryptodome 风格）
# 如果上面的 DES 有问题，我们改用 pycryptodome
# 但为了不增加依赖，先提供备用方案

# 实际上 cryptography 库的 TripleDES 使用 8 字节密钥时等同于 DES
# 所以上面的代码可以工作

# ========== MD5 相关 ==========
def md5(data):
    """计算 MD5 摘要"""
    return hashlib.md5(data).digest()

def bytes_to_hex(data):
    """字节转十六进制字符串"""
    return data.hex()

def bytes_to_base64(data):
    """字节转 Base64 字符串"""
    return base64.b64encode(data).decode()

def base64_to_bytes(base64_str):
    """Base64 字符串转字节"""
    return base64.b64decode(base64_str)