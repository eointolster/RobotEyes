import cv2
import numpy as np
import argparse
import torch
from PIL import Image
from moondream import detect_device, LATEST_REVISION
from transformers import AutoTokenizer, AutoModelForCausalLM
import csv
import os

def initialize_csv(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['View', 'Right', 'Right Center', 'Center', 'Left Center', 'Left'])  # Column headers

def update_csv(file_path, counter, descriptions):
    # Read existing data
    with open(file_path, newline='') as file:
        reader = list(csv.reader(file))
        if len(reader) < 6:  # If we have less than 6 rows including headers, add a new one
            reader.append([counter] + descriptions)
        else:  # If we have 6 rows, update the second one
            reader[1] = [counter] + descriptions
            reader = reader[:1] + reader[2:] + reader[1:2]  # Move the updated row to the bottom

    # Write updated data
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(reader)
        
# Argument parser for CPU mode
parser = argparse.ArgumentParser()
parser.add_argument("--cpu", action="store_true")
args = parser.parse_args()

# Device detection
device = torch.device("cpu") if args.cpu else torch.device("cuda" if torch.cuda.is_available() else "cpu")
dtype = torch.float32

print("Using device:", device)
if device != torch.device("cpu"):
    print("If you run into issues, pass the `--cpu` flag to this script.")

# Moondream model initialization
model_id = "vikhyatk/moondream2"
tokenizer = AutoTokenizer.from_pretrained(model_id, revision=LATEST_REVISION)
moondream = AutoModelForCausalLM.from_pretrained(
    model_id, trust_remote_code=True, revision=LATEST_REVISION
).to(device=device, dtype=dtype)
moondream.eval()

# Function to get a description from the moondream model
def answer_question(img, prompt):
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    image_embeds = moondream.encode_image(img_pil)
    description = moondream.answer_question(
        image_embeds=image_embeds,
        question=prompt,
        tokenizer=tokenizer
    )
    return description

def put_text_on_image(cv_img, text, position, max_width, font_scale=0.5, color=(255, 255, 255), thickness=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    wrapped_text = []
    words = text.split(' ')

    # Pre-calculate the height of a single line of text to use for line spacing
    sample_text = "Sample"  # Use any sample text to measure text size
    text_size, _ = cv2.getTextSize(sample_text, font, font_scale, thickness)

    # Create wrapped text to fit the specified maximum width
    while words:
        line = ''
        while words and cv2.getTextSize(line + words[0], font, font_scale, thickness)[0][0] < max_width:
            line += words.pop(0) + ' '
        wrapped_text.append(line)

    # Draw each line on the image, adjusting the vertical position
    y = position[1]
    for line in wrapped_text:
        cv2.putText(cv_img, line.strip(), (position[0], y), font, font_scale, color, thickness)
        y += text_size[1] + 5  # Adjust the y position based on the height of the text and add a small gap

# Initialize CSV file
file_path = 'descriptions.csv'  # Change to your desired file path
initialize_csv(file_path)
counter = 0  # Initialize the counter

# Initialize the camera
cap = cv2.VideoCapture(0)
persistent_descriptions = [""] * 5  # Only five descriptions as we are only processing the center row
current_segment = 0  # Start with the first segment

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    grid_h = h // 3  # We maintain three rows
    grid_w = w // 5  # Now five columns in the center row

    key = cv2.waitKey(1) & 0xFF

    # Processing only the middle row
    top_row = frame[0:grid_h, :]  # Not processed, but will be displayed
    bottom_row = frame[2*grid_h:h, :]  # Not processed, but will be displayed
    center_row = frame[grid_h:2*grid_h, :]  # The row that is processed

    # Process only the current segment in the center row
    section = center_row[:, current_segment*grid_w:(current_segment+1)*grid_w]
    description = answer_question(section, "Give a concise image description as few words as possible")
    persistent_descriptions[current_segment] = description

    # Update and display text for all segments
    for i in range(5):
        text_position = (i*grid_w + 5, grid_h + 25)
        segment_width = grid_w - 10
        put_text_on_image(frame, persistent_descriptions[i], text_position, segment_width)

    persistent_descriptions[current_segment] = description
    counter += 1  # Increment the counter every time we go through all segments
    if current_segment == 3:  # Check if we have completed a full cycle through segments
        update_csv(file_path, counter, persistent_descriptions)


    # Resize frame before display to enlarge it
    scale_factor = 3  # Change this factor to your desired scale
    enlarged_frame = cv2.resize(frame, (int(w * scale_factor), int(h * scale_factor)))

    # Display the unprocessed rows visually without modifying
    cv2.imshow('Frame', enlarged_frame)

    # Move to the next segment
    current_segment = (current_segment + 1) % 5  # Cycle through segments

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
