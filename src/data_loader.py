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

#Loads NSL-KDD text data, and applies columns.
def load_dataset(file_path:str) -> pd.DataFrame:
    if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset missing at {file_path}. Please download it into the data/ directory.")
    # Read CSV (NSL-KDD files are comma-delimited without headers)
    df = pd.read_csv(file_path, names=COLUMNS, header=None)
    return df
    

#Profiles the target labels.
def profile_dataset(df:pd.DataFrame,dataset_name:str) -> None:
    df_copy = df.copy()     
    print(f"\n{'='*20} PROFILING {dataset_name.upper()} {'='*20}")
    print(f"Shape: {df_copy.shape[0]} rows, {df_copy.shape[1]} columns")
    
    # Binary Label Profiling
    df_copy['is_attack'] = np.where(df_copy['target'] == 'normal', 'normal', 'attack')
    binary_counts = df_copy['is_attack'].value_counts()
    binary_pct = df_copy['is_attack'].value_counts(normalize=True) * 100
    
    print("\n--- Binary Target Distribution (Normal vs. Threat) ---")
    for idx in binary_counts.index:
        print(f"Class '{idx}': {binary_counts[idx]} instances ({binary_pct[idx]:.2f}%)")
        
    # Granular Attack Type Profiling
    attack_counts = df_copy[df_copy['is_attack'] == 'attack']['target'].value_counts()
    print("\n--- Granular Attack Type Breakdown ---")
    if len(attack_counts) == 0:
        print("No attacks found.")
    else:
        for idx in attack_counts.index:
            print(f" - {idx}: {attack_counts[idx]}")
            
    # Check for missing fields
    missing_values = df_copy.isnull().sum().sum()
    print(f"\nMissing values detected: {missing_values}")

#Creates a binary numeric target column and drops metadata.
def prepare_targets(df:pd.DataFrame) -> pd.DataFrame:
    processed_df = df.copy()
    
    # Map text target to binary: 0 for normal, 1 for attack
    processed_df['label'] = np.where(processed_df['target'] == 'normal', 0, 1)
    
    #Drop columns that shouldn't go into our machine learning model
    processed_df = processed_df.drop(columns=['target', 'difficulty_level'])
    return processed_df
    

if __name__ == "__main__":
    # Define paths relative to repo root
    train_path = os.path.join("data", "KDDTrain+.txt")
    test_path = os.path.join("data", "KDDTest+.txt")
    
    try:
        #Load raw data from disk.
        train_df = load_dataset(train_path)
        test_df = load_dataset(test_path)
        
        #Run diagnostic report
        profile_dataset(train_df, "Train Dataset (KDDTrain+)")
        profile_dataset(test_df, "Test Dataset (KDDTest+)")
        
        #Transform targets for the machine learning module
        train_df_prepped = prepare_targets(train_df)
        test_df_prepped = prepare_targets(test_df)
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
