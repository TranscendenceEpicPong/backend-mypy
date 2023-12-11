import hashlib

def sha256_hash(data):
    # Créer un objet hashlib pour l'algorithme SHA-256
    sha256 = hashlib.sha256()

    # Mettre à jour le hash avec les données à hasher
    # Les données doivent être converties en bytes avant d'être utilisées
    sha256.update(data.encode('utf-8'))

    # Obtenir le résultat sous forme de chaîne hexadécimale
    hash_result = sha256.hexdigest()

    return hash_result

def sha256_verify(data, _hash):
    return sha256_hash(data) == _hash

def encode_to_hex(data):
    return data.encode('utf-8').hex()

def decode_from_hex(data):
    return bytes.fromhex(data).decode('utf-8')