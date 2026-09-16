from app.domain.abstract_usecases import AbstractHasher
import hashlib

class MD5Hasher:
    def __init__(self):
        pass
    def hash(self, text_to_encode: str)-> str:
        return hashlib.md5(text_to_encode.encode('utf-8')).hexdigest()
    
def get_hasher()->AbstractHasher:
    return MD5Hasher()
