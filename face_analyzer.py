import cv2
import numpy as np
from PIL import Image
import io
import base64
from config import MAX_IMAGE_SIZE, SUPPORTED_FORMATS

class FaceAnalyzer:
    def __init__(self):
        # Initialize face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
    
    def validate_image(self, image_bytes: bytes) -> tuple[bool, str]:
        """Validate image format, size and quality"""
        try:
            # Check file size
            if len(image_bytes) > MAX_IMAGE_SIZE:
                return False, 'file_too_large'
            
            # Try to open and validate image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Check format
            if image.format not in SUPPORTED_FORMATS:
                return False, 'unsupported_format'
            
            # Check minimum dimensions
            if image.width < 100 or image.height < 100:
                return False, 'poor_quality'
            
            return True, 'valid'
            
        except Exception:
            return False, 'unsupported_format'
    
    def detect_faces(self, image_bytes: bytes) -> tuple[bool, str, dict]:
        """Detect faces in the image and extract basic features"""
        try:
            # Validate image first
            is_valid, error = self.validate_image(image_bytes)
            if not is_valid:
                return False, error, {}
            
            # Convert bytes to OpenCV image
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return False, 'processing_error', {}
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 50)
            )
            
            if len(faces) == 0:
                return False, 'no_face', {}
            
            if len(faces) > 1:
                return False, 'multiple_faces', {}
            
            # Extract features from the detected face
            face_features = self._extract_face_features(img, gray, faces[0])
            
            # Convert main image to base64 for OpenAI analysis
            _, buffer = cv2.imencode('.jpg', img)
            base64_image = base64.b64encode(buffer).decode('utf-8')
            
            return True, 'success', {
                'face_features': face_features,
                'base64_image': base64_image,
                'image_dimensions': (img.shape[1], img.shape[0])
            }
            
        except Exception as e:
            print(f"Face detection error: {e}")
            return False, 'processing_error', {}
    
    def _extract_face_features(self, img, gray, face_rect) -> dict:
        """Extract detailed facial features from detected face"""
        x, y, w, h = face_rect
        
        # Extract face region
        face_gray = gray[y:y+h, x:x+w]
        face_color = img[y:y+h, x:x+w]
        
        features = {
            'face_dimensions': (w, h),
            'face_position': (x, y),
            'face_area_ratio': (w * h) / (img.shape[0] * img.shape[1])
        }
        
        # Detect eyes within face region
        eyes = self.eye_cascade.detectMultiScale(face_gray, 1.1, 5)
        features['eye_count'] = len(eyes)
        
        if len(eyes) >= 2:
            # Calculate eye distance and symmetry
            eye_centers = []
            for (ex, ey, ew, eh) in eyes[:2]:
                center_x = ex + ew // 2
                center_y = ey + eh // 2
                eye_centers.append((center_x, center_y))
            
            if len(eye_centers) == 2:
                eye_distance = np.sqrt((eye_centers[0][0] - eye_centers[1][0])**2 + 
                                     (eye_centers[0][1] - eye_centers[1][1])**2)
                features['eye_distance'] = eye_distance
                features['eye_symmetry'] = abs(eye_centers[0][1] - eye_centers[1][1])
        
        # Detect smile
        smiles = self.smile_cascade.detectMultiScale(face_gray, 1.8, 20)
        features['smile_detected'] = len(smiles) > 0
        features['smile_intensity'] = len(smiles)
        
        # Calculate face proportions
        features['face_width_height_ratio'] = w / h if h > 0 else 0
        
        # Analyze brightness and contrast
        face_brightness = np.mean(face_gray)
        face_contrast = np.std(face_gray)
        features['brightness'] = face_brightness
        features['contrast'] = face_contrast
        
        # Calculate facial angles and symmetry
        features['face_center'] = (x + w//2, y + h//2)
        
        return features
