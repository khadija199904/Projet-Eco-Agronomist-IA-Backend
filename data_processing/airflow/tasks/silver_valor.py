import os
import shutil
import yaml

def valorisation_fusion():
    
    
    STATION_DIR = os.path.join("/opt/airflow/data/raw/station")
    SILVER_DIR = os.path.join("/opt/airflow/data/silver", "fruits-vegetables-disease-detection")
    
    
    # 1. Fruit Disease Detection (Specific removals)
    FRUIT_DS = os.path.join(STATION_DIR, "Fruit Disease Detection Dataset")
    fruit_to_remove = [
        'Pineapple Fusariosis', 
        'Pineapple Green Fruit Rot', 
        'Guava Rust', 
        'Guava rust', 
        'Guava rot', 
        'Papaya ring spot'
    ]

    # 2. Tomato (All classes, prefix with tomate_)
    TOMATE_DS = os.path.join(STATION_DIR, "Tomate")

    # 3. Pepper Anthracnose (Only anthracnose, rename to pepper_anthracnose)
    PEPPER_ANTH_DS = os.path.join(STATION_DIR, "pepper-anthracnose")

    # 4. Tomato Blossom (Only blossom end rot )
    TOMATO_BLOSSOM_DS = os.path.join(STATION_DIR, "tomato-blossom-end-rot.v1i.yolov11")

    final_names = []
    dataset_mappings = [] 

    curr_idx = 0

    # Helper to add dataset to mapping
    def add_dataset(path, prefix, filter_fn=None, rename_fn=None):
        nonlocal curr_idx
        with open(os.path.join(path, "data.yaml"), 'r') as f:
            cfg = yaml.safe_load(f)
        
        names = cfg['names']
        mapping = {}
        filter_classes = False

        for i, name in enumerate(names):
            if filter_fn and not filter_fn(name):
                filter_classes = True
                continue
            
            new_name = name
            if rename_fn:
                new_name = rename_fn(name)
            
            mapping[str(i)] = str(curr_idx)
            final_names.append(new_name)
            curr_idx += 1
            
        dataset_mappings.append((path, prefix, mapping, filter_classes))

    # Add Fruit DS
    add_dataset(FRUIT_DS, "fruit", filter_fn=lambda n: n not in fruit_to_remove)
    
    # Add Tomate DS
    add_dataset(TOMATE_DS, "tomato", rename_fn=lambda n: f"tomate_{n.lower().replace(' ', '_')}")
    
    # Add Pepper Anthracnose
    add_dataset(PEPPER_ANTH_DS, "pepper_anth", 
                filter_fn=lambda n: n == 'anthracnose',
                rename_fn=lambda n: 'pepper_anthracnose')
    
    # Add Tomato Blossom
    add_dataset(TOMATO_BLOSSOM_DS, "tomato_blossom", 
                filter_fn=lambda n: n == 'Tomato Blossom End Rot',
                rename_fn=lambda n: "tomate_necrosis")

    # Prepare target directory
    if os.path.exists(SILVER_DIR):
        shutil.rmtree(SILVER_DIR)
    
    splits = ["train", "valid", "test"]
    for split in splits:
        target_split = "val" if split == "valid" else split
        os.makedirs(os.path.join(SILVER_DIR, target_split, "images"), exist_ok=True)
        os.makedirs(os.path.join(SILVER_DIR, target_split, "labels"), exist_ok=True)

    # Process and copy
    for ds_path, prefix, mapping, filter_active in dataset_mappings:
        print(f"Processing {os.path.basename(ds_path)}...")
        for split in splits:
            target_split = "val" if split == "valid" else split
            img_src = os.path.join(ds_path, split, "images")
            lbl_src = os.path.join(ds_path, split, "labels")
            
            if not os.path.exists(img_src):
                continue

            for img_file in os.listdir(img_src):
                if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                    
                new_img_name = f"{prefix}_{img_file}"
                label_file = img_file.rsplit('.', 1)[0] + ".txt"
                label_src_path = os.path.join(lbl_src, label_file)
                
                processed_lines = []
                valid_label = False
                
                if os.path.exists(label_src_path):
                    with open(label_src_path, 'r') as f:
                        lines = f.readlines()
                    
                    for line in lines:
                        parts = line.strip().split()
                        if not parts: continue
                        old_id = parts[0]
                        if old_id in mapping:
                            parts[0] = mapping[old_id]
                            processed_lines.append(" ".join(parts))
                            valid_label = True
                
               
                if filter_active:
                    if valid_label:
                        shutil.copy2(os.path.join(img_src, img_file), os.path.join(SILVER_DIR, target_split, "images", new_img_name))
                        with open(os.path.join(SILVER_DIR, target_split, "labels", f"{prefix}_{label_file}"), 'w') as f:
                            f.write("\n".join(processed_lines) + "\n")
                else:
                    shutil.copy2(os.path.join(img_src, img_file), os.path.join(SILVER_DIR, target_split, "images", new_img_name))
                    with open(os.path.join(SILVER_DIR, target_split, "labels", f"{prefix}_{label_file}"), 'w') as f:
                        f.write("\n".join(processed_lines) + "\n")

    # Create final data.yaml
    final_yaml = {
        'train': './train/images',
        'val': './val/images',
        'test': './test/images',
        'nc': len(final_names),
        'names': final_names
    }
    
    with open(os.path.join(SILVER_DIR, "data.yaml"), 'w') as f:
        yaml.dump(final_yaml, f, default_flow_style=False)

    # 7. Create README.md 
    readme_content = f"""# fruit and vegetable disease detection

This dataset is a collection of images and labels from multiple sources, curated for fruit and vegetable disease detection.

## Data Sources
1. **Fruit Disease Detection**: Multi-fruit disease dataset (Citrus, Guava, Mango, etc.) with specific classes filtered out.
   url: https://universe.roboflow.com/shreya-b-sesje/fruit-disease-detection-dataset/dataset/4
2. **Tomato Disease Detection**: Fusion of 'Tomate' and 'Tomato Blossom End Rot' datasets, with classes prefixed as `tomate_`.
   url: https://universe.roboflow.com/letspro-uvmvg/tomato-w4fvj/dataset/3
   url: https://universe.roboflow.com/agrosight/tomato-blossom-end-rot/dataset/1
3. **Pepper Disease Detection**: 'Pepper-anthracnose' dataset, specifically extracting and renaming the anthracnose class.
   url: https://universe.roboflow.com/yolo-erkdb/yolo-jmpis/dataset/10

## Statistics
- **Total Classes**: {len(final_names)}
- **Generated on**: {os.popen('date').read().strip()}
"""
    with open(os.path.join(SILVER_DIR, "README.md"), 'w') as f:
        f.write(readme_content)

    print(f"Fusion completed in {SILVER_DIR}.")
    print(f"Total classes: {len(final_names)}")
    print(f"README.md created with the 3 main data sources.")

if __name__ == "__main__":
    valorisation_fusion()
