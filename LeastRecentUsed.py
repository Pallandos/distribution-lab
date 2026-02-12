from typing import override

from mem import Mem

class LRU(Mem):
    
    def __init__(self, image_t : str, key_t : str = "k", list_size : int = 10, limit : int = 5) -> None:
        super().__init__(image_t, key_t)
        self.list = []
        self.list_size = list_size
        self.limit = limit
             
    @override
    def store(self) -> None:
        super().store()
        self.list.append(self.key)
        self._check_list()
        
    @override
    def display_from_store(self):
        super().display_from_store()
        
        self.list.remove(self.key)
        self.list.append(self.key)
        self._check_list()
    
    def delete(self):
        self.client.delete(self.key)
        self.list.remove(self.key)
        
    def _check_list(self):
        """Check if the list is oversize
        """
        if len(self.list) >= self.list_size:
            for i in range(self.limit):
                self.list.pop(1)