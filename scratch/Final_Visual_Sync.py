import os
import re

def sync_images():
    base_dir = "content/ko/posts/2026/04"
    if not os.path.exists(base_dir):
        print("Directory not found.")
        return

    files = [f for f in os.listdir(base_dir) if f.endswith('.md')]
    print(f"Syncing images for {len(files)} articles...")

    for f in files:
        path = os.path.join(base_dir, f)
        slug = f.replace('.md', '')
        try:
            with open(path, 'r', encoding='utf-8-sig') as file:
                content = file.read()

            # Inject Image Path if missing
            if 'image:' not in content:
                img_path = f"/images/posts/2026/04/{slug}.jpg"
                content = re.sub(
                    r'date: \".*?\"', 
                    f'date: "2026-04-13T10:00:00+09:00"\nimage: "{img_path}"', 
                    content
                )
                
                with open(path, 'w', encoding='utf-8-sig') as file:
                    file.write(content)
                print(f"Image Synced: {f}")
        except Exception as e:
            print(f"Error on {f}: {e}")

if __name__ == "__main__":
    sync_images()
