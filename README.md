# PointCrypt

An educational cryptographic system exploring formula-based obfuscation and structure-mapping encryption for learning and experimentation.

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.17%2B-purple?style=flat-square&logo=plotly)
![PyCryptodome](https://img.shields.io/badge/PyCryptodome-3.18%2B-green?style=flat-square&logo=security)
![pytest](https://img.shields.io/badge/pytest-7.0%2B-yellow?style=flat-square&logo=pytest)

---

## Overview

**PointCrypt** is a learning project that implements a novel encryption technique based on:

1. **Polynomial Formulas** - Two independent polynomial functions for transformation
2. **3D Point Mapping** - Converting data blocks into 3D coordinate space
3. **Sequence Generation** - Deterministic but non-obvious input generation
4. **Structure Encryption** - Protecting the block-to-point mapping

### How It Works

```
SENDER:
  Data → Split into blocks → Generate sequence → Calculate 3D points 
       → Map blocks to points (random) → Send blocks + encrypted structure

RECEIVER:
  Receive blocks + encrypted structure → Decrypt structure (needs seed) 
       → Regenerate sequence & points → Match blocks to coordinates 
       → Reorder blocks → Recover original data
```

### Core Idea

The **security** comes from the formulas themselves and the shared seed:
- Without the seed, receiver cannot regenerate the polynomial coefficients
- Without knowing the exact sequence of inputs, the 3D point order is unpredictable
- Even if blocks are visible, their order is scrambled across point space
- The `data_hash` ensures different data produces different point structures

---

## Features

- ✅ **Sequencing Formula** - Polynomial-based input generation
- ✅ **Main Formula** - Cubic polynomial for 3D point calculation
- ✅ **Block Operations** - Split, verify, and reassemble data
- ✅ **Interactive Streamlit App** - Visualize every step of encryption/decryption
- ✅ **3D Visualization** - Plotly 3D scatter plots of generated points
- ✅ **Comprehensive Tests** - Formula validation and integration tests
- ✅ **Sender/Receiver Classes** - Modular encryption and decryption
- ✅ **Educational Focus** - Learn cryptographic thinking through implementation

---

## Project Structure

```
PointCrypt/
├── README.md                      # This file
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Python dependencies
├── Makefile                       # Build & run commands
│
├── core/                          # Core cryptographic logic
│   ├── __init__.py
│   ├── formulas.py               # Sequencing & main formulas
│   ├── blocks.py                 # Block splitting & reassembly
│   └── utils.py                  # Utility functions & hashing
│
├── sender/                        # Sender-side operations
│   ├── __init__.py
│   └── encryptor.py              # Encryption logic
│
├── receiver/                      # Receiver-side operations
│   ├── __init__.py
│   └── decryptor.py              # Decryption logic
│
├── app/                           # Interactive prototype
│   ├── __init__.py
│   └── streamlit_app.py          # Main Streamlit dashboard
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_formulas.py
│   ├── test_blocks.py
│   └── test_integration.py
│
└── examples/                      # Usage examples
    └── console_demo.py           # Non-interactive demo
```

---

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/PointCrypt.git
cd PointCrypt

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Run Interactive Streamlit App

The easiest way to see everything in action:

```bash
streamlit run app/streamlit_app.py
```

This opens an interactive dashboard where you can:
1. Enter custom seed, data, and block size
2. Watch the encryption process step-by-step
3. Visualize 3D points in interactive plots
4. See block-to-point mappings
5. Decrypt and verify data recovery

### Run Console Demo

For a quick non-interactive demonstration:

```bash
python examples/console_demo.py
```

### Run Tests

```bash
pytest tests/ -v
```

Or use the Makefile:

```bash
make test
```

---

## Formulas Explained

### Formula 1: Sequencing Formula

Generates a sequence of input numbers from:
- `block_count` - Number of blocks
- `seed` - Secret key
- `data_hash` - Hash of the data being encrypted

**Output:** Array of numbers `[input_0, input_1, ..., input_n]`

### Formula 2: Main Formula (3D Point Generation)

Takes each input from the sequence and generates a 3D point:
- **Input:** Single number from sequence
- **Polynomial:** Cubic polynomial with coefficients derived from seed
- **Output:** 3D coordinate `(x, y, z)`

The polynomial is: `f(x) = a·x³ + b·x² + c·x + d (mod N)`

Where `a, b, c, d` are computed from the seed and block_count.

---

## Makefile Commands

```bash
make install       # Install dependencies
make run           # Run Streamlit app
make test          # Run all tests
make test-verbose  # Run tests with detailed output
make clean         # Remove __pycache__ and .pytest_cache
make format        # Format code with standard conventions
help               # Show all available commands
```

---

## Example Usage

### Sender Side

```python
from sender.encryptor import PointCryptEncryptor

encryptor = PointCryptEncryptor(seed="my_secret_seed")

data = "HELLO WORLD"
block_size = 4

encrypted_data, structure = encryptor.encrypt(data, block_size)

# Send encrypted_data['blocks'] and structure to receiver
```

### Receiver Side

```python
from receiver.decryptor import PointCryptDecryptor

decryptor = PointCryptDecryptor(seed="my_secret_seed")

recovered_data = decryptor.decrypt(encrypted_data, structure)

print(recovered_data)  # "HELLO WORLD"
```

---

## Learning Goals

This project teaches:

1. **Cryptographic Thinking**
   - How obfuscation differs from encryption
   - The importance of key management
   - Why simple formulas might have vulnerabilities

2. **Polynomial Mathematics**
   - Using polynomials for data transformation
   - Modular arithmetic in cryptography
   - Coordinate system conversions

3. **System Design**
   - Sender-receiver architecture
   - Deterministic pseudorandom generation
   - State management and synchronization

4. **Python Best Practices**
   - Modular code organization
   - Testing frameworks (pytest)
   - Interactive data visualization (Streamlit)

---

## Limitations & Disclaimers

⚠️ **This is an educational project, NOT production-ready cryptography**

- No formal security proof
- Not suitable for real-world encryption
- Designed for learning purposes
- Vulnerabilities may exist

If you need actual cryptography, use established libraries like:
- `cryptography` (industry standard)
- `PyCryptodome` (for low-level operations)
- Post-quantum options (liboqs-python)

---

## Testing

Run the full test suite:

```bash
pytest tests/ -v --cov=core --cov=sender --cov=receiver
```

Individual test files:
```bash
pytest tests/test_formulas.py -v
pytest tests/test_blocks.py -v
pytest tests/test_integration.py -v
```

---

## Contributing

This is a personal learning project. Feel free to:
- Fork and experiment
- Suggest improvements
- Break it intentionally to learn why it breaks
- Document your findings

---

## Future Enhancements

- [ ] Add 4D/5D point generation
- [ ] Explore different polynomial degrees
- [ ] Implement integrity checking (HMAC)
- [ ] Add performance benchmarks
- [ ] Create attack simulation module
- [ ] Support for larger datasets

---

## References

- Polynomial-based cryptography concepts
- Coordinate system transformations
- Modular arithmetic in computer science
- Streamlit documentation: https://docs.streamlit.io/
- PyCryptodome docs: https://pycryptodome.readthedocs.io/

---

## Author

**Arnav** - Graduation project exploring novel encryption techniques

---

## License

MIT License - Feel free to use for learning purposes.

---

## Questions or Feedback?

This project is meant for exploration and learning. Document your discoveries!

Happy learning! 🚀
