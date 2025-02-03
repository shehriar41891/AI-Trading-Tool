import cv2
import os

def read_image(image_path):
    if not os.path.exists(image_path):
        print("Error: File not found.")
        return None
    
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Unable to read the image.")
        return None
    
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return image

# image_path = "./downloads/newplot.png"
# image = read_image(image_path)
