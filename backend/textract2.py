import cv2
import boto3

# Init Textract
textract = boto3.client("textract", region_name="us-east-1")

# Open webcam
cap = cv2.VideoCapture(0)

print("Press 's' to scan, 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Live Scanner", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("s"):
        # Save frame to memory and send to Textract
        _, buffer = cv2.imencode(".jpg", frame)
        image_bytes = buffer.tobytes()

        response = textract.analyze_document(
            Document={"Bytes": image_bytes},
            FeatureTypes=["QUERIES"],
            QueriesConfig={
                "Queries": [
                    {"Text": "What is the student's name on the ID card?", "Alias": "StudentName"},
                    {"Text": "What is the roll number?", "Alias": "RollNumber"},
                    {"Text": "What is the branch?", "Alias": "Branch"},
                ]
            }
        )

        print("----- Scan Result -----")
        for block in response["Blocks"]:
            if block["BlockType"] == "QUERY_RESULT":
                query_info = block.get("Query", {})
                alias = query_info.get("Alias", "Unknown")
                text = block.get("Text", "")
                print(f"{alias}: {text}")
        print("-----------------------")

    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
