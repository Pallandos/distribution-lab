import io
import os
from PIL import Image
from pymemcache.client.base import Client

class Mem:
    # Variables de classe pour gérer le LRU partagé entre les instances
    # Liste des clés stockées, ordonnée du moins récemment utilisé (index 0) au plus récent
    _lru_keys = []
    # Taille maximale du cache
    _lru_limit = 5
    
    def __init__(self, image_t: str, key: str = "k") -> None:
        self.client = Client("localhost")
        self.image = image_t
        self.array = bytearray()
        self.key = key
        
    def display(self):
        """Lit l'image depuis le fichier et l'affiche."""
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
        """Affiche l'image depuis le buffer interne."""
        if not self.array:
            print("Buffer vide.")
            return
        image = Image.open(io.BytesIO(self.array))
        image.show()
        
    def store(self):
        """Stocke l'image dans memcached en appliquant la politique LRU."""
        if not self.array:
            # Si le tableau est vide, on essaie de charger l'image
            print("Attention : tentative de stockage d'une image vide.")
        
        array = bytes(self.array) # Copie implicite lors de la conversion
        self.client.set(self.key, array)
        self._update_lru_access()
        print(f"Stored {self.key}. LRU List: {Mem._lru_keys}")
    
    def display_from_store(self):
        """Récupère l'image depuis memcached et l'affiche, mettant à jour le LRU."""
        content = self.client.get(self.key)
        
        if content:
            self.array = bytearray(content) # Mise à jour du buffer local
            self._display_image()
            self._update_lru_access()
            print(f"Retrieved {self.key}. LRU List: {Mem._lru_keys}")
        else:
            print(f"Key '{self.key}' not found in cache (Evicted or never stored).")

    def _update_lru_access(self):
        """Met à jour la liste LRU lors d'un accès (store ou get)."""
        # Si la clé est déjà dans la liste, on l'enlève pour la remettre à la fin (plus récent)
        if self.key in Mem._lru_keys:
            Mem._lru_keys.remove(self.key)
        
        # On ajoute la clé à la fin (Most Recently Used)
        Mem._lru_keys.append(self.key)
        
        # Si on dépasse la limite, on retire les plus anciens (au début de la liste)
        while len(Mem._lru_keys) > Mem._lru_limit:
            key_to_evict = Mem._lru_keys.pop(0)
            self._evict_from_cache(key_to_evict)

    def _evict_from_cache(self, key):
        """Supprime une clé de memcached."""
        # Note: Chaque instance a son propre client, mais ils parlent au même serveur.
        self.client.delete(key)
        print(f"Evicted key: {key}")

if __name__ == "__main__":
    # Test du fonctionnement LRU
    print("--- Test LRU (Limit = 5) ---")
    
    # Création de plusieurs objets Mem
    # On utilise la même image pour simplifier, mais des clés différentes
    mems = []
    for i in range(1, 8): # 1 à 7
        key_name = f"k{i}"
        m = Mem("Lenna.png", key_name)
        # Pour le test, on triche un peu et on remplit self.array sans afficher l'image à chaque fois pour aller plus vite
        # Ou on appelle display() qui lit le fichier.
        print(f"Processing {key_name}...")
        m.display() # Lit le fichier
        m.store()   # Stocke et met à jour LRU
        mems.append(m)

    # À ce stade, k1 et k2 devraient être évincés (car limit=5, on a inséré 7 items : k1..k7)
    # Cache attendu : [k3, k4, k5, k6, k7]
    
    print("\n--- Vérification des évictions ---")
    # Tentative d'accès à k1 (devrait échouer)
    print("Accessing k1 (devrait être absent):")
    mems[0].display_from_store()
    
    # Accès à k3 (devrait être présent et passer en MRU)
    print("\nAccessing k3 (devrait être présent):")
    mems[2].display_from_store()
    # Cache attendu après accès k3 : [k4, k5, k6, k7, k3]
    
    # Insertion d'un nouveau k8 -> devrait évincer k4 (le plus ancien maintenant)
    print("\nStoring k8 (devrait évincer k4):")
    m8 = Mem("Lenna.png", "k8")
    m8.display()
    m8.store()
    
    print("\nAccessing k4 (devrait être absent):")
    mems[3].display_from_store()
