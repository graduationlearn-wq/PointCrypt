# PointCrypt

An educational cryptographic system exploring formula-based obfuscation through polynomial mappings and 3D point generation.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.17%2B-purple?style=flat-square&logo=plotly)
![PyCryptodome](https://img.shields.io/badge/PyCryptodome-3.18%2B-green?style=flat-square&logo=security)
![pytest](https://img.shields.io/badge/pytest-7.0%2B-yellow?style=flat-square&logo=pytest)

---

## Overview

**PointCrypt** is a learning project that implements a novel encryption technique based on:

1. **Polynomial Formulas** - Two independent polynomial functions for data transformation
2. **Block Shuffling** - Deterministic randomization of data blocks using a seed
3. **Structure Mapping** - Encoding block positions for recovery during decryption
4. **Symmetric Key Exchange** - Same seed generates identical shuffling on both sides

### How It Works

```
SENDER SIDE:
  Data → Split into blocks → Shuffle blocks (seed-based)
       → Create point-to-position mapping → Send blocks + encrypted structure

RECEIVER SIDE:
  Receive shuffled blocks + encrypted structure → Regenerate same shuffle (same seed)
       → Use mapping to unscramble → Reassemble original data
```

### Core Concept

The **security** comes from the formulas and the shared seed:
- Without the seed, receiver cannot regenerate the polynomial coefficients
- Without knowing the shuffle order, blocks are meaningless
- Same seed = deterministic, reproducible shuffling
- Different seeds = completely different shuffled patterns each time

---

## Features

✅ **Two-Step Polynomial System**
- Sequencing formula: Generates input numbers from seed + block_count + data_hash
- Main formula: Cubic polynomial for creating point mappings

✅ **Deterministic Block Shuffling**
- Seed-based random shuffling (same seed = same shuffle)
- Structure mapping for block recovery
- All operations reversible with correct seed

✅ **Interactive Streamlit Dashboard**
- Real-time encryption/decryption visualization
- Step-by-step process breakdown
- Side-by-side encryption and decryption views
- Full demo mode with statistics

✅ **Modular Architecture**
- Core utilities and formulas
- Separate sender and receiver classes
- Clean separation of concerns
- Easy to understand and extend

✅ **Comprehensive Testing**
- Inline tests in each module
- End-to-end encryption/decryption tests
- Multiple data size testing
- All roundtrip tests passing ✅

---

## Project Structure

```
PointCrypt/
├── README.md                      # This file
├── .gitignore                     # Git ignore rules
├── Makefile                       # Build and development commands
│
├── core/                          # Core cryptographic logic
│   ├── __init__.py
│   ├── utils.py                   # Hashing and utility functions
│   ├── formulas.py                # Sequencing & main polynomial formulas
│   └── blocks.py                  # Block splitting & reassembly
│
├── sender/                        # Sender-side operations
│   ├── __init__.py
│   └── encryptor.py               # Encryption orchestration
│
├── receiver/                      # Receiver-side operations
│   ├── __init__.py
│   └── decryptor.py               # Decryption orchestration
│
├── app/                           # Interactive dashboard
│   ├── __init__.py
│   └── streamlit_app.py           # Streamlit visualization dashboard
│
└── tests/                         # Test suite (expandable)
    └── __init__.py
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

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install pycryptodome streamlit plotly pytest
```

---

## Quick Start

### Run Interactive Dashboard

The easiest way to see everything in action:

```bash
streamlit run app/streamlit_app.py
```

Opens at `http://localhost:8501` with three tabs:
- **📤 Encrypt** - Visualize encryption step-by-step
- **📥 Decrypt** - Visualize decryption step-by-step
- **🔄 Full Demo** - Side-by-side encryption and decryption

### Run Tests

```bash
# Test core module
python -m core.utils
python -m core.formulas
python -m core.blocks

# Test sender
python -m sender.encryptor

# Test receiver
python -m receiver.decryptor
```

### Use as a Library

```python
from sender.encryptor import PointCryptEncryptor
from receiver.decryptor import PointCryptDecryptor

# Sender side
encryptor = PointCryptEncryptor(seed="my_secret_key", block_size=4)
encrypted = encryptor.encrypt("HELLO WORLD")
print(f"Encrypted blocks: {encrypted['blocks']}")

# Receiver side (same seed!)
decryptor = PointCryptDecryptor(seed="my_secret_key", block_size=4)
decrypted = decryptor.decrypt(encrypted)
print(f"Decrypted: {decrypted}")  # "HELLO WORLD"
```

---

## How It Works in Detail

### Step 1: Block Splitting
Data is split into fixed-size blocks (default 4 characters):
```
"HELLO WORLD" → ["HELL", "O WO", "RLD"]
```

### Step 2: Sequencing Formula
Generates input numbers based on `seed`, `block_count`, and `data_hash`:
```python
# Inputs: seed="secret", block_count=3, data_hash="..."
# Output: [263, 271, 278]  # Deterministic sequence
```

### Step 3: Main Formula (Cubic Polynomial)
Generates unique block positions from the sequence:
```python
# For each input, generates a position via polynomial
f(x) = ax³ + bx² + cx + d (mod 1000000007)
# Coefficients a, b, c, d derived from seed
```

### Step 4: Block Shuffling
Blocks are shuffled deterministically:
```python
# Original: ["HELL", "O WO", "RLD"]
# Shuffled: ["RLD", "HELL", "O WO"]  # Based on seed
# Mapping: {point_0→2, point_1→0, point_2→1}
```

### Step 5: Transmission
Send:
- **Blocks**: Shuffled blocks (visible but meaningless without mapping)
- **Structure**: Point-to-position mapping (encrypted in real systems)
- **Metadata**: Block count, data hash for verification

### Step 6: Recovery
Receiver with same seed:
1. Regenerates same shuffled order
2. Uses mapping to unscramble
3. Reassembles blocks in original order
4. Gets original data back

---

## Formulas Explained

### Sequencing Formula

Generates a deterministic sequence based on three inputs:

**Inputs:**
- `seed` - Secret key (e.g., "my_secret")
- `block_count` - Number of blocks (e.g., 7)
- `data_hash` - SHA3-256 hash of data (e.g., "f2df...")

**Process:**
1. Combine all inputs: `"secret|7|f2df..."`
2. Hash the combination
3. Extract starting point and step size
4. Generate ascending sequence with variable steps

**Output:** Array of numbers `[263, 271, 278, ...]`

### Main Formula (Cubic Polynomial)

Generates point mappings from the sequence:

**Polynomial:** `f(x) = a·x³ + b·x² + c·x + d (mod 1000000007)`

**Coefficients:**
- `a = (seed_value * 73) XOR block_count`
- `b = (seed_value * 97) XOR block_count`
- `c = (seed_value * 127) XOR block_count`
- `d = (seed_value * 137) XOR block_count`

**Output:** 3D points `(x, y, z)` for visualization

---

## Testing

All components have built-in tests. Run them:

```bash
# Run all module tests
python -m core.utils
python -m core.formulas
python -m core.blocks
python -m sender.encryptor
python -m receiver.decryptor

# Expected output: ✅ All tests passed!
```

### Test Coverage

- ✅ Block splitting and reassembly
- ✅ Sequencing formula generation
- ✅ Polynomial evaluation
- ✅ Block shuffling and mapping
- ✅ Encryption/decryption roundtrips
- ✅ Multiple data sizes (1 char, 11 chars, 1000 chars, 43+ chars)
- ✅ Data integrity verification

---

## Learning Goals

This project teaches:

### 1. Cryptographic Thinking
- How obfuscation differs from encryption
- The importance of key management
- Why simple formulas might have vulnerabilities

### 2. Polynomial Mathematics
- Using polynomials for data transformation
- Modular arithmetic in cryptography
- Coordinate system conversions

### 3. System Design
- Sender-receiver architecture
- Deterministic pseudorandom generation
- State management and synchronization

### 4. Python Best Practices
- Modular code organization
- Clean class hierarchies
- Error handling and validation

---

## Limitations & Disclaimers

⚠️ **This is an EDUCATIONAL project, NOT production-ready cryptography**

- No formal security proof
- Not suitable for real-world encryption
- Designed for learning purposes
- May have theoretical vulnerabilities

### If You Need Real Cryptography:

Use established libraries like:
- `cryptography` (industry standard)
- `PyCryptodome` (for low-level operations)
- Post-quantum options (liboqs-python)

---

## Architecture Highlights

### Modular Design
```
Core Logic (formulas, utilities)
    ↓
Sender (orchestration)  ←→  Receiver (orchestration)
    ↓
Streamlit Dashboard (visualization)
```

### Clean Separation
- **Core**: Pure mathematical operations
- **Sender**: Encryption workflow only
- **Receiver**: Decryption workflow only
- **App**: Visualization and interaction

### No External Encryption Dependencies
- Uses only deterministic formulas
- Seed-based shuffling for obfuscation
- Suitable for learning and demonstration

---

## Future Enhancements

- [ ] Add 4D/5D point generation for larger datasets
- [ ] Explore different polynomial degrees
- [ ] Implement integrity checking (HMAC)
- [ ] Add performance benchmarks
- [ ] Create attack simulation module
- [ ] Support streaming/chunked encryption
- [ ] Add formal security analysis

---

## Usage Examples

### Example 1: Simple Encryption

```python
from sender.encryptor import PointCryptEncryptor

encryptor = PointCryptEncryptor(seed="graduation_project", block_size=4)
result = encryptor.encrypt("POINTCRYPT")

print("Shuffled blocks:", result['blocks'])
print("Data hash:", result['data_hash'][:16] + "...")
```

### Example 2: Full Roundtrip

```python
from sender.encryptor import PointCryptEncryptor
from receiver.decryptor import PointCryptDecryptor

seed = "secret_key"
original = "HELLO WORLD"

# Encrypt
encryptor = PointCryptEncryptor(seed=seed)
encrypted = encryptor.encrypt(original)

# Decrypt
decryptor = PointCryptDecryptor(seed=seed)
decrypted = decryptor.decrypt(encrypted)

assert decrypted == original  # ✅ Success!
```

### Example 3: With Dashboard

```bash
# Run the Streamlit app
streamlit run app/streamlit_app.py

# Then interact with:
# - Encrypt tab: Input custom data, see step-by-step visualization
# - Decrypt tab: Decrypt the encrypted data
# - Demo tab: See full process with statistics
```

---

## Command Reference

```bash
# Install dependencies
pip install pycryptodome streamlit plotly pytest

# Run interactive dashboard
streamlit run app/streamlit_app.py

# Run core tests
python -m core.utils
python -m core.formulas
python -m core.blocks

# Run sender/receiver tests
python -m sender.encryptor
python -m receiver.decryptor

# Clean cache (Unix/Mac/WSL)
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +
```

---

## References & Learning Resources

- Polynomial cryptography concepts
- Coordinate system transformations
- Modular arithmetic in computer science
- Streamlit documentation: https://docs.streamlit.io/
- PyCryptodome docs: https://pycryptodome.readthedocs.io/

---

## Project Statistics

- **Language**: Python 3.8+
- **Core Modules**: 3 (utils, formulas, blocks)
- **Encryption/Decryption Classes**: 2 (Encryptor, Decryptor)
- **Dashboard Tabs**: 3 (Encrypt, Decrypt, Demo)
- **Total Lines of Code**: ~2500+
- **Test Coverage**: All modules included
- **Documentation**: Comprehensive inline comments

---

## Author

**Arnav** - Graduation Project

Exploring novel encryption techniques and cryptographic thinking through hands-on implementation.

---

## License

MIT License - Feel free to use for learning purposes.

---

## Questions or Feedback?

This is a learning project. Document your discoveries and improvements as you explore! 🚀

---

## Changelog

### v1.0.0 - Initial Release
- ✅ Core polynomial formulas
- ✅ Block-based encryption/decryption
- ✅ Deterministic shuffling
- ✅ Interactive Streamlit dashboard
- ✅ All tests passing
- ✅ Comprehensive documentation

---

**Happy learning! 🎓**
