"""
PointCrypt Interactive Dashboard

Streamlit app for visualizing the encryption and decryption process.
Shows each step of the PointCrypt algorithm interactively.
"""

import streamlit as st
import json
from sender.encryptor import PointCryptEncryptor
from receiver.decryptor import PointCryptDecryptor
from core.formulas import PointCryptFormulas


# Page configuration
st.set_page_config(
    page_title="PointCrypt Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and introduction
st.title("🔐 PointCrypt - Interactive Encryption Dashboard")
st.markdown("""
A learning project exploring formula-based obfuscation through polynomial mappings and 3D point generation.
""")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")
seed = st.sidebar.text_input(
    "Enter Secret Seed:",
    value="my_secret_key",
    help="Shared secret between sender and receiver"
)

block_size = st.sidebar.slider(
    "Block Size:",
    min_value=1,
    max_value=20,
    value=4,
    help="Size of each data block in characters"
)

tab1, tab2, tab3 = st.tabs(["📤 Encrypt", "📥 Decrypt", "🔄 Full Demo"])

# ============================================================================
# TAB 1: ENCRYPTION
# ============================================================================
with tab1:
    st.header("📤 Encryption Process")
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        data_to_encrypt = st.text_area(
            "Enter data to encrypt:",
            value="HELLO WORLD",
            height=100,
            help="The data you want to encrypt"
        )
    
    with col2:
        st.info(f"📊 Data Length: {len(data_to_encrypt)} chars")
    
    if st.button("🔒 Encrypt", key="encrypt_btn", use_container_width=True):
        try:
            # Perform encryption
            encryptor = PointCryptEncryptor(seed=seed, block_size=block_size)
            encrypted_result = encryptor.encrypt(data_to_encrypt)
            
            # Store in session for later use
            st.session_state.last_encrypted = encrypted_result
            st.session_state.original_data = data_to_encrypt
            
            # Display results
            st.success("✅ Encryption successful!")
            
            # Step 1: Blocks
            st.subheader("Step 1️⃣ - Split into Blocks")
            blocks = encrypted_result['blocks']
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Original blocks (before shuffle):**")
                for i, block in enumerate(blocks):
                    st.code(f"[{i}] = '{block}'")
            
            with col2:
                st.info(
                    f"📊 Block Statistics:\n"
                    f"- Total blocks: {encrypted_result['block_count']}\n"
                    f"- Block size: {block_size}\n"
                    f"- Original size: {len(data_to_encrypt)} chars"
                )
            
            # Step 2: Formulas
            st.subheader("Step 2️⃣ - Generate Formulas")
            
            formulas = PointCryptFormulas(
                seed=seed,
                block_count=encrypted_result['block_count'],
                data_hash=encrypted_result['data_hash']
            )
            sequence, points = formulas.generate_sequence_and_points()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Sequence Inputs:**")
                for i, seq in enumerate(sequence[:5]):
                    st.code(f"[{i}] = {seq}")
                if len(sequence) > 5:
                    st.caption(f"... and {len(sequence) - 5} more")
            
            with col2:
                st.write("**Generated Points (3D):**")
                for i, point in enumerate(points[:5]):
                    st.code(f"[{i}] = {point}")
                if len(points) > 5:
                    st.caption(f"... and {len(points) - 5} more")
            
            with col3:
                formula_info = formulas.get_formula_info()
                st.info(
                    f"📐 Formula Info:\n"
                    f"- Starting point: {formula_info['starting_point']}\n"
                    f"- Base step: {formula_info['base_step']}\n"
                    f"- Coefficients: {formula_info['coefficients']}"
                )
            
            # Step 3: Block Shuffling and Mapping
            st.subheader("Step 3️⃣ - Shuffle and Map")
            
            structure_dict = json.loads(encrypted_result['structure'])
            shuffled_blocks = encrypted_result['blocks']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Shuffled blocks (sent):**")
                for i, block in enumerate(shuffled_blocks):
                    st.code(f"[{i}] = '{block}'")
            
            with col2:
                st.write("**Mapping (point → original position):**")
                for key, val in structure_dict.items():
                    st.code(f"{key} → {val}")
            
            # Step 4: Final Result
            st.subheader("Step 4️⃣ - Encrypted Package")
            
            col1, col2 = st.columns(2)
            
            with col1:
                size_info = {
                    'blocks_size': sum(len(b.encode('utf-8')) for b in blocks),
                    'structure_size': len(encrypted_result['structure'].encode('utf-8'))
                }
                
                st.metric("Blocks Size", f"{size_info['blocks_size']} bytes")
                st.metric("Structure Size", f"{size_info['structure_size']} bytes")
                st.metric(
                    "Total Size",
                    f"{size_info['blocks_size'] + size_info['structure_size']} bytes"
                )
            
            with col2:
                st.write("**Data Hash:**")
                st.code(encrypted_result['data_hash'][:32] + "...")
                
                st.write("**Block Count:**")
                st.code(encrypted_result['block_count'])
            
            # Show JSON
            st.write("**Full encrypted package (JSON):**")
            st.json({
                'blocks': encrypted_result['blocks'],
                'structure': structure_dict,
                'block_count': encrypted_result['block_count'],
                'data_hash': encrypted_result['data_hash'][:16] + "..."
            })
        
        except Exception as e:
            st.error(f"❌ Encryption failed: {e}")


# ============================================================================
# TAB 2: DECRYPTION
# ============================================================================
with tab2:
    st.header("📥 Decryption Process")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        encrypted_json = st.text_area(
            "Paste encrypted data (JSON):",
            height=200,
            help="Paste the encrypted package here"
        )
    
    with col2:
        use_last = st.checkbox("Use last encrypted data", value=True)
        if use_last and hasattr(st.session_state, 'last_encrypted'):
            st.info("✅ Using encrypted data from Encrypt tab")
    
    if st.button("🔓 Decrypt", key="decrypt_btn", use_container_width=True):
        try:
            # Get encrypted data
            if use_last and hasattr(st.session_state, 'last_encrypted'):
                encrypted_data = st.session_state.last_encrypted
            else:
                # Parse JSON from textarea
                encrypted_dict = json.loads(encrypted_json)
                encrypted_data = {
                    'blocks': encrypted_dict['blocks'],
                    'structure': json.dumps(encrypted_dict['structure']),
                    'block_count': encrypted_dict['block_count'],
                    'data_hash': encrypted_dict['data_hash']
                }
            
            # Perform decryption with debug
            decryptor = PointCryptDecryptor(seed=seed, block_size=block_size)
            decrypted_data = decryptor.decrypt(encrypted_data, debug=False)
            
            st.success("✅ Decryption successful!")
            
            # Step 1: Received data
            st.subheader("Step 1️⃣ - Received Encrypted Package")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Shuffled blocks received:**")
                for i, block in enumerate(encrypted_data['blocks'][:5]):
                    st.code(f"[{i}] = '{block}'")
                if len(encrypted_data['blocks']) > 5:
                    st.caption(f"... and {len(encrypted_data['blocks']) - 5} more")
            
            with col2:
                st.write("**Structure mapping:**")
                structure = json.loads(encrypted_data['structure'])
                for key, val in list(structure.items())[:5]:
                    st.code(f"{key} → {val}")
                if len(structure) > 5:
                    st.caption(f"... and {len(structure) - 5} more")
            
            # Step 2: Regenerate formulas
            st.subheader("Step 2️⃣ - Regenerate Formulas")
            
            formulas = PointCryptFormulas(
                seed=seed,
                block_count=encrypted_data['block_count'],
                data_hash=encrypted_data['data_hash']
            )
            sequence, points = formulas.generate_sequence_and_points()
            
            st.info(f"✅ Regenerated {len(sequence)} sequence inputs and {len(points)} points")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Sequence inputs (first 5):**")
                for i, seq in enumerate(sequence[:5]):
                    st.code(f"[{i}] = {seq}")
            
            with col2:
                st.write("**Generated points (first 5):**")
                for i, point in enumerate(points[:5]):
                    st.code(f"[{i}] = {point}")
            
            # Step 3: Unscramble blocks
            st.subheader("Step 3️⃣ - Unscramble Blocks")
            
            st.write("**Reconstruction process:**")
            for i in range(min(3, len(encrypted_data['blocks']))):
                point_key = f"point_{i}"
                original_pos = structure[point_key]
                st.code(
                    f"shuffled_blocks[{i}]='{encrypted_data['blocks'][i]}' → "
                    f"original position {original_pos}"
                )
            if len(encrypted_data['blocks']) > 3:
                st.caption(f"... and {len(encrypted_data['blocks']) - 3} more")
            
            # Step 4: Final result
            st.subheader("Step 4️⃣ - Decrypted Data")
            
            st.success(f"**Decrypted: '{decrypted_data}'**")
            
            if hasattr(st.session_state, 'original_data'):
                if decrypted_data == st.session_state.original_data:
                    st.info(f"✅ **MATCH!** Matches original data: '{st.session_state.original_data}'")
                else:
                    st.warning(
                        f"⚠️ **MISMATCH**\n"
                        f"- Expected: '{st.session_state.original_data}'\n"
                        f"- Got: '{decrypted_data}'"
                    )
        
        except Exception as e:
            st.error(f"❌ Decryption failed: {e}")


# ============================================================================
# TAB 3: FULL DEMO
# ============================================================================
with tab3:
    st.header("🔄 Full Encryption-Decryption Demo")
    
    st.write("Enter your data and watch it get encrypted and decrypted in real-time!")
    
    demo_data = st.text_input(
        "Enter data for demo:",
        value="POINTCRYPT",
        help="Demo data to encrypt and decrypt"
    )
    
    if st.button("▶️ Run Full Demo", key="demo_btn", use_container_width=True):
        try:
            # Create two columns for side-by-side view
            col_encrypt, col_decrypt = st.columns(2)
            
            # ENCRYPTION SIDE
            with col_encrypt:
                st.subheader("🔒 Encryption Side")
                
                encryptor = PointCryptEncryptor(seed=seed, block_size=block_size)
                encrypted = encryptor.encrypt(demo_data)
                
                st.success("✅ Encrypted")
                st.write(f"**Original:** `{demo_data}`")
                st.write(f"**Blocks:** {encrypted['blocks']}")
                
                structure = json.loads(encrypted['structure'])
                st.write("**Mapping:**")
                for key, val in structure.items():
                    st.write(f"- {key} → {val}")
            
            # DECRYPTION SIDE
            with col_decrypt:
                st.subheader("🔓 Decryption Side")
                
                decryptor = PointCryptDecryptor(seed=seed, block_size=block_size)
                decrypted = decryptor.decrypt(encrypted, debug=False)
                
                st.success("✅ Decrypted")
                st.write(f"**Recovered:** `{decrypted}`")
                
                # Verification
                if decrypted == demo_data:
                    st.balloons()
                    st.success(f"✅ **SUCCESS!** Data matches perfectly!")
                else:
                    st.error(f"❌ **FAILED!** Data mismatch")
            
            # Summary statistics
            st.divider()
            st.subheader("📊 Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Original Size", f"{len(demo_data)} chars")
            
            with col2:
                st.metric("Blocks", encrypted['block_count'])
            
            with col3:
                structure_size = len(encrypted['structure'].encode('utf-8'))
                st.metric("Structure Size", f"{structure_size} bytes")
            
            with col4:
                total = len(demo_data) + structure_size
                st.metric("Total Overhead", f"{structure_size} bytes")
        
        except Exception as e:
            st.error(f"❌ Demo failed: {e}")


# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.markdown("""
---
**PointCrypt** - Educational cryptographic system exploring formula-based obfuscation
- 📚 Learn: Understand polynomial formulas and block mapping
- 🔐 Secure: Deterministic shuffling with seed-based randomness
- 🚀 Interactive: Visualize every step of encryption/decryption

Built with ❤️ for learning cryptographic concepts
""")