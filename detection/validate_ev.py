from ultralytics import YOLO
import cv2, os

model = YOLO('models/ev_best.pt')
print(model.names)
def test_on_folder(image_folder, conf=0.10):
    results_log = []
    for img_file in os.listdir(image_folder):
        if not img_file.endswith(('.jpg','.png','.jpeg')):
            continue
        path = os.path.join(image_folder, img_file)
        results = model(path, conf=conf, verbose=False)
        detections = len(results[0].boxes)
        if detections > 0:
            for box in results[0].boxes:
                cls = model.names[int(box.cls[0])]
                conf_val = float(box.conf[0])
                results_log.append(f"{img_file}: {cls} ({conf_val:.1%})")
                print(len(results[0].boxes))
    return results_log

# Test on ambulance images (should detect them all)
print("Testing ambulance detection:")
hits = test_on_folder("data/ev_dataset/test_ambulances/")
for h in hits:
    print(" ", h)

# Test on negative images (should detect NOTHING)
print("\nTesting false positives (should be empty):")
fp = test_on_folder("data/ev_dataset/test_negatives/")
for f in fp:
    print(" FALSE ALARM:", f)
