import os
import pandas as pd
import numpy as np

# Official 41 feature names of the NSL-KDD dataset
COLUMNS = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login",
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate",
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
    "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
    "dst_host_rerror_rate", "dst_host_srv_rerror_rate", "target", "difficulty_level"
]

def load_and_profile_dataset(file_path: str, dataset_name: str) -> pd.DataFrame:
    """Loads NSL-KDD text data, applies columns, and profiles the target labels."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset missing at {file_path}. Please download it into the data/ directory.")
        
    print(f"\n{'='*20} PROFILING {dataset_name.upper()} {'='*20}")
    
    # Read CSV (NSL-KDD files are comma-delimited without headers)
    df = pd.read_csv(file_path, names=COLUMNS, header=None)
    
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Binary Label Profiling
    df['is_attack'] = np.where(df['target'] == 'normal', 'normal', 'attack')
    binary_counts = df['is_attack'].value_counts()
    binary_pct = df['is_attack'].value_counts(normalize=True) * 100
    
    print("\n--- Binary Target Distribution (Normal vs. Threat) ---")
    for idx in binary_counts.index:
        print(f"Class '{idx}': {binary_counts[idx]} instances ({binary_pct[idx]:.2f}%)")
        
    # Granular Attack Type Profiling
    attack_counts = df[df['is_attack'] == 'attack']['target'].value_counts()
    print("\n--- Granular Attack Type Breakdown ---")
    if len(attack_counts) == 0:
        print("No attacks found.")
    else:
        for idx in attack_counts.index:
            print(f" - {idx}: {attack_counts[idx]}")
            
    # Audit for missing fields
    missing_values = df.isnull().sum().sum()
    print(f"\nMissing values detected: {missing_values}")
    
    return df

if __name__ == "__main__":
    # Define paths relative to repo root
    train_path = os.path.join("data", "KDDTrain+.txt")
    test_path = os.path.join("data", "KDDTest+.txt")
    
    try:
        train_df = load_and_profile_dataset(train_path, "Train Dataset (KDDTrain+)")
        test_df = load_and_profile_dataset(test_path, "Test Dataset (KDDTest+)")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
