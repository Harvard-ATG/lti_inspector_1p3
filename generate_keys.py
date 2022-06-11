from Crypto.PublicKey import RSA
import json
from jwcrypto.jwk import JWK


key = RSA.generate(4096)
private_key = key.exportKey()
public_key = key.publickey().exportKey()

print('Generating keys...')

with open('inspector_key', 'w') as f:
    f.write(private_key.decode('utf-8'))

with open('inspector_key.pub', 'w') as f:
    f.write(public_key.decode('utf-8'))

print('Keys generated.')