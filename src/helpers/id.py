from nanoid import generate

# Custom alphabet (optional)
alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"

def create_id_with_prefix(prefix, length=10):
    # Generate a NanoID with a custom alphabet and length
    nanoid = generate(alphabet, size=length)
    return f"{prefix}:{nanoid}"