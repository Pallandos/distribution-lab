import os
from PIL import Image
import io

class FS():
    def __init__(self, dir_t, image_t, file_t) -> None:
        self.dir = dir_t
        self.image = image_t
        self.file = file_t
        self.array = bytearray()
    
    def create_dir(self) -> None:
        os.mkdir(self.dir)
        
    def read_dir(self) -> None:
        content = os.listdir(self.dir)
        print(f"Content of {self.dir} :\n {content}")
        
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
            self._display_array()
    
    def _display_array(self):
        image = Image.open(io.BytesIO(self.array))
        image.show()
        
    def write(self):
        f = os.open(self.file, os.O_APPEND | os.O_CREAT | os.O_TRUNC)
        try: 
            os.write(f, self.array)
        finally:
            os.close(f)
        
if __name__ == "__main__":
    pass