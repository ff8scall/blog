import os
import shutil
from datetime import datetime

# [V1.0] Article Backup and Purge Script
def backup_and_purge():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = f"backups/legacy_articles_{timestamp}"
    os.makedirs(backup_root, exist_ok=True)
    
    content_root = "content"
    target_subs = ["posts", "guides"]
    
    moved_count = 0
    
    for lang in ["ko", "en"]:
        lang_dir = os.path.join(content_root, lang)
        if not os.path.exists(lang_dir): continue
        
        for sub in target_subs:
            sub_path = os.path.join(lang_dir, sub)
            if not os.path.exists(sub_path): continue
            
            # Create corresponding backup dir
            backup_sub_path = os.path.join(backup_root, lang, sub)
            os.makedirs(backup_sub_path, exist_ok=True)
            
            # Walk through sub_path
            for root, dirs, files in os.walk(sub_path):
                for file in files:
                    # Skip _index.md (Hugo meta)
                    if file == "_index.md": continue
                    
                    src_file = os.path.join(root, file)
                    
                    # Calculate relative path to preserve structure in backup
                    rel_path = os.path.relpath(root, sub_path)
                    dest_dir = os.path.join(backup_sub_path, rel_path)
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    dest_file = os.path.join(dest_dir, file)
                    
                    print(f"[*] Moving: {src_file} -> {dest_file}")
                    shutil.move(src_file, dest_file)
                    moved_count += 1
                    
    print(f"\n[DONE] Successfully backed up and removed {moved_count} articles.")
    print(f"[INFO] Backup location: {backup_root}")

if __name__ == "__main__":
    backup_and_purge()
