from django.shortcuts import render
import numpy as np 
from deepface import DeepFace 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

def analyze_faces(image_path_1, image_path_2):
    try:
        analysis_1 = DeepFace.analysis(img_path = image_path_1, actions=['landmark'], enforce_detection=False)
        analysis_2 = DeepFace.analysis(img_path = image_path_2, actions=['landmark'], enforce_detection=False)

        return analysis_1["landmark"], analysis_2["landmark"]
    except Exception as e:
        return None, None, str(e)
# Function to calculate similarity score based on landmarks
def calculate_similarity(landmarks_1, landmarks_2):
    scores = {}
    total_score = 0

    try:
        for key in ["left_eye", "right_eye","nose","mouth_left","mouth_right"]:
            point1 = np.array(landmarks_1[key])
            point2 = np.array(landmarks_2[key])

            distance = np.linalg.norm(point1 - point2)

            normalized_score = 100 - min(distance, 100)

            scores[key] = round(normalized_score, 2)
            total_score += normalized_score

        # Calculate overall similarity
        overall_score = total_score / len(scores)
        scores['overall_similarity'] = round(overall_score, 2)
        return scores

    except Exception as e:
        return {"error": str(e)}

def annotate_images(image_path_1, image_path_2, landmarks_1, landmarks_2):
    annotate_images_1 = cv2.imread(image_path_1)
    annotate_images_2 = cv2.imread(image_path_2)

    for key, color in zip(["left_eye", "right_eye", "nose", "mouth_left", "mouth_right"], [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255)]):
        point1 = tuple(map(int, landmarks_1[key]))
        point2 = tuple(map(int, landmarks_2[key]))

        cv2.circle(annotate_images_1, point1, 5, color, -1)
        cv2.circle(annotate_images_2, point2, 5, color, -1)
    
    output_path_1 = "output_1.jpg"
    output_path_2 = "output_2.jpg"

    cv2.imwrite(output_path_1, annotate_images_1)
    cv2.imwrite(output_path_2, annotate_images_2)

    return output_path_1, output_path_2

#Django view to handle comparison request
@csrf_exempt
def compare_faces(request):
    if request.method == 'POST' and request.FILES:
        try:
            image_1 = request.FILES["image1"]
            image_2 = request.FILES["image2"]

            image_path_1 = f"media/{image_1.name}"
            image_path_2 = f"media/{image_2.name}"

            with open(image_path_1, 'wb+') as destination:
                for chunk in image_1.chunks():
                    destination.write(chunk)
            with open(image_path_2, 'wb+') as destination:
                for chunk in image_2.chunks():
                    destination.write(chunk)

            # Detect and analyze features
            landmarks_1, landmarks_2 = analyze_faces(image_path_1, image_path_2)

            if not landmark_1 or not landmarks_2:
                return JsonResponse({"error":"Face detection failed."})

            # Compute similarity
            similarity_scores = compute_similarity(landmark_1, landmarks_2)

            # Annotate images
            annotate_image_path_1, annotate_image_path_22 = annotate_images(image_path_1, image_path_2, landmark_1, landmarks_2)

            response = {
                "similarity_scores": similarity_scores,
                "annotated_images": {
                    "image1": annotate_image_path_1,
                    "image2": annotate_image_path_2
                }
            }

            return render(request, 'index.html', context)
        except Exception as e:
            return render(request, 'index.html', {"error":str(e)})

    return render(request, 'index.html')