# core/keys.py
from bip_utils import (
    Bip32Ed25519Slip,
    Bip39SeedGenerator,
    Bip39MnemonicValidator
)
from stellar_sdk import Keypair

def derive_keypair_from_mnemonic(mnemonic):
    if not Bip39MnemonicValidator().IsValid(mnemonic):
        return None
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip32 = Bip32Ed25519Slip.FromSeed(seed)
    derived = bip32.DerivePath("m/44'/314159'/0'")
    return Keypair.from_raw_ed25519_seed(
        derived.PrivateKey().Raw().ToBytes()
    )
