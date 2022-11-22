import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad


class EncryptClass:
    def __init__(self, key):
        # 初始化密钥
        self.key = key
        # 初始化数据块大小
        self.length = AES.block_size
        # 初始化AES,ECB模式的实例
        self.aes = AES.new(self.key.encode("utf-8"), AES.MODE_ECB)
        # 截断函数，去除填充的字符
        self.unpad = lambda date: date[0:-ord(date[-1])]

    def fill_method(self, aes_str):
        '''pkcs7补全'''
        pad_pkcs7 = pad(aes_str.encode('utf-8'), AES.block_size, style='pkcs7')

        return pad_pkcs7

    def encrypt(self, encrData):
        # 加密函数,使用pkcs7补全
        res = self.aes.encrypt(self.fill_method(encrData))
        # 转换为base64
        msg = str(base64.b64encode(res), encoding="utf-8")

        return msg

    def decrypt(self, decrData):
        # base64解码
        res = base64.decodebytes(decrData.encode("utf-8"))
        # 解密函数
        msg = self.aes.decrypt(res).decode("utf-8")

        return self.unpad(msg)


if __name__ == '__main__':
    # key的长度需要补长(16倍数),补全方式根据情况而定,未补齐会报错
    # key字符长度决定加密结果,长度16：加密结果AES(128),长度32：结果就是AES(256)
    eg = EncryptDate("asdfghjklqwertyu")
    # 加密字符串长同样需要16倍数：需注意,不过代码中pad()方法里，帮助实现了补全（补全方式就是pkcs7）
    en = eg.encrypt("测试数据")
    de = eg.decrypt(en)
    print(f"加密结果：{en}")
    print(f"解密结果：{de}")
