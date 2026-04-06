import struct
import math

VOLUME_SIZE = 1024 * 1024 * 1024
SECTOR_SIZE = 8192

def dimensional_collapse(key_int):
    mask_48 = (1 << 48) - 1
    chunk1 = key_int & mask_48
    chunk2 = (key_int >> 48) & mask_48
    chunk3 = (key_int >> 96) & mask_48
    chunk4 = (key_int >> 144)
    collapsed = chunk1 ^ (chunk2 << 1) ^ (chunk3 << 2) ^ (chunk4 << 3)
    final_lba = (collapsed & mask_48) % (VOLUME_SIZE // SECTOR_SIZE) * SECTOR_SIZE 
    return final_lba

def parse_origin(key):
    clean = key.replace("-", "").replace("0x", "")
    key_int = int(clean, 16)
    lba = dimensional_collapse(key_int)
    return lba, key_int

key = "53-49-4D-2D-33-38-32-35-35-35-33-39-36-38-2D-30-78-35-32-38"
lba, key_int = parse_origin(key)
print(f"Key: {key}")
print(f"LBA: {lba}")
print(f"Index: {lba // SECTOR_SIZE}")
