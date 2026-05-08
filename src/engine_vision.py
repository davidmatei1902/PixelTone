import numpy as np
from sklearn.cluster import KMeans

class VisionEngine:
    def __init__(self):
        pass

    def apply_kmeans(self, image_matrix, k=4):
        print(f"applying k-means clustering with k={k}...")
        
        # flatten the 2d matrix into a 1d column of pixels
        pixels = image_matrix.reshape((-1, 1))
        
        # train the model and map pixels
        kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto")
        kmeans.fit(pixels)
        quantized_pixels = kmeans.cluster_centers_[kmeans.labels_]
        
        # reshape back to the original 2d image dimensions
        quantized_image = quantized_pixels.reshape(image_matrix.shape)
        
        return quantized_image.astype(np.uint8)