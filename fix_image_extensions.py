import os
import glob
from PIL import Image

def fix_extensions():
    images_dir = os.path.join("solved paper/drishti ias", "images")
    if not os.path.exists(images_dir):
        print("Images directory not found.")
        return
        
    print("Inspecting image files in:", images_dir)
    image_files = glob.glob(os.path.join(images_dir, "*"))
    
    renamed_map = {}
    
    for filepath in image_files:
        if os.path.isdir(filepath):
            continue
            
        filename = os.path.basename(filepath)
        # Try to identify image format using PIL
        try:
            with Image.open(filepath) as img:
                img_format = img.format # 'JPEG', 'PNG', 'WEBP', etc.
            
            # Map PIL format to file extension
            ext_map = {
                'JPEG': '.jpg',
                'PNG': '.png',
                'WEBP': '.webp',
                'GIF': '.gif'
            }
            correct_ext = ext_map.get(img_format, None)
            
            if correct_ext:
                base, current_ext = os.path.splitext(filename)
                if current_ext.lower() != correct_ext.lower():
                    new_filename = base + correct_ext
                    new_filepath = os.path.join(images_dir, new_filename)
                    
                    # Rename the file
                    os.rename(filepath, new_filepath)
                    print(f"  Renamed: {filename} -> {new_filename} (Format: {img_format})")
                    renamed_map[f"images/{filename}"] = f"images/{new_filename}"
            else:
                print(f"  Unknown format for {filename}: {img_format}")
        except Exception as e:
            print(f"  Error reading {filename}: {e}")
            
    if not renamed_map:
        print("No file extensions needed fixing.")
        return
        
    # Now update all references in all markdown files
    print("\nUpdating image references in markdown files...")
    md_files = glob.glob(os.path.join("solved paper/drishti ias", "*.md"))
    
    for md_filepath in md_files:
        with open(md_filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        modified = False
        for old_ref, new_ref in renamed_map.items():
            if old_ref in content:
                content = content.replace(old_ref, new_ref)
                modified = True
                
        if modified:
            with open(md_filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Updated references in: {os.path.basename(md_filepath)}")
            
    print("\nExtension fixing and link updates completed successfully!")

if __name__ == "__main__":
    fix_extensions()
