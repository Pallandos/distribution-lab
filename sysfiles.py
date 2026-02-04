import os

class FS():
    def __init__(self, dir_t) -> None:
        self.dir = dir_t
    
    def create_dir(self) -> None:
        os.mkdir(self.dir)
        
    def read_dir(self) -> None:
        content = os.listdir(self.dir)
        print(f"Content of {self.dir} :\n {content}")
