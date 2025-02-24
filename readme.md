# Image Labeling Program

A simple GUI program for labeling images with intention levels and tasks.

## Features

- Select a folder containing images (supports .jpg, .jpeg, .png)
- Assign tasks and intention levels to images
- Navigate through images using arrow keys or file list
- Color-coded labeling for easy visualization
- Auto-saves labels to CSV file
- Preview window for selected images

## Usage

1. Run the program:
```
python image_labeler.py
```

2. Click "Select Folder" to choose a directory containing images

3. Enter a task and click "Confirm Task"
   - Use "Edit Task" to modify the task later

4. Label images using:
   - Keyboard numbers (1, 2, 3)
   - Numpad numbers (1, 2, 3)
   - Click the level buttons
   
   Level meanings:
   - Level 1 (Red): Low
   - Level 2 (Orange): Medium
   - Level 3 (Green): High

5. Navigate images using:
   - Left/Right arrow keys
   - Click on files in the list
   - Double-click to jump to specific image

## Requirements

- Python 3.x
- Pillow (PIL)
- tkinter (usually comes with Python)

Install requirements:
```
pip install -r requirements.txt
```

## Output

Labels are saved in `label_data.csv` in the selected folder with columns:
- Filename
- Task
- Intention Level

## Controls

- Arrow keys: Navigate images
- 1, 2, 3: Assign intention levels
- Double-click: Jump to image in list
- Single-click: Preview image

## Notes

- The program saves labels to `label_data.csv` in the selected folder
- The program auto-saves labels when navigating images
- The program supports .jpg, .jpeg, .png images
