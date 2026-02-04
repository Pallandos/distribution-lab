import io
import os

from pymemcache.client.base import Client
from PIL import Image

class Mem():
    def __init__(self, image_t : str, key : str = "k") -> None:
        self.client = Client("localhost")
        self.image = image_t
        self.array = bytearray()
        self.key = key
        
    def display(self):
        f = os.open(self.image, os.O_RDONLY)
        try:
            while True:
                b = os.read(f, 1)
                if not b:
                    break
                self.array.append(b[0])
        finally:
            os.close(f)
            self._display_image()
            
    def _display_image(self):
        image = Image.open(io.BytesIO(self.array))
        image.show()
        
    def store(self):
        array = bytes(self.array.copy())
        self.client.set(self.key, array)
    
    def display_from_store(self):
        content = self.client.get(self.key)
        
        image = Image.open(io.BytesIO(content))
        image.show()
        
if __name__ == "__main__":
    Meminstance = Mem("Lenna.png", "k")
    
    Meminstance.display()
    Meminstance.store()
    Meminstance.display_from_store()