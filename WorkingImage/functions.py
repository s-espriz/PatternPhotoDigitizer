import cv2 
import numpy as np 
from rdp import rdp
import ezdxf
from ezdxf.addons.drawing import Frontend, RenderContext, layout , pymupdf, config

def pairwise_distances(points):
    # Compute pairwise distances using Euclidean distance formula
    dist = np.sqrt(np.sum((points[:, np.newaxis] - points) ** 2, axis=-1))
    return dist

def euclidean_distance(point1, point2):
    return np.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)







def find_most_distant_points(points):
    # Compute pairwise distances
    distances = pairwise_distances(points)
    
    # Find the indices of the maximum distance
    idx_max = np.unravel_index(np.argmax(distances), distances.shape)
    
    # Extract the coordinates of the two points
    point1 = points[idx_max[0]]
    point2 = points[idx_max[1]]
    points = np.array([point1,point1])
    distance = euclidean_distance(point1, point2)

    return points,distance

def create_dxf_doc(image , blur_size = 9,  threshold_percentage = 60 ,arz = 122.2 , tool = 89.7, epsilon = 9, grid_size_cm = 10.0, small_things = 3 , spline = False , degree_treshold = 150, scale = False , methods_spline = "normal"):
    # bluring image
    blur_size_transformed = blur_size * 2 - 1 
    blured = cv2.GaussianBlur(image, (blur_size_transformed, blur_size_transformed), 0) 
    # making gray scale image
    gray = cv2.cvtColor(blured, cv2.COLOR_BGR2GRAY)

    # Creating tresholded image
    darkest_pixel = np.min(gray)
    
    # Calculate the threshold value
    threshold_percentage = int(threshold_percentage)
    threshold_value = darkest_pixel + (255 - darkest_pixel) * threshold_percentage / 100

    # Apply thresholding
    _, thresholded_img = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    cv2.imwrite("thresholded_img.jpg", thresholded_img)
    # canny edge detection 
    canny = cv2.Canny(thresholded_img, 255, 255)

    #getting countours
    contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)


    # remove amall junks from the surface 
    mod_contours = []

    for i in range(len(contours)):
        contour = np.squeeze(contours[i], axis=1)
        points , dist = find_most_distant_points(contour)
        if dist > max(gray.shape)* small_things / 100:
            mod_contours.append(contours[i])



    # creating_initial_dxf 
    doc = ezdxf.new(dxfversion='R2000')
    msp = doc.modelspace()
    # msp.add_lwpolyline(frame)
    scaling_array = np.array([(arz/image.shape[1]),(tool/image.shape[0])])

    for contour in mod_contours:
        contour = np.squeeze(contour, axis=1)
        # Explicitly close the polyline by connecting the last and first points
        # print(contour.shape)
        # break
        contour = np.vstack((contour, contour[0]))
        new_lines = rdp(contour ,epsilon=epsilon)
        new_lines = np.array(new_lines)
        current_spline = []
        total_splines = []
        new_lines = np.vstack((new_lines, new_lines[0]))
        if scale : 
            new_lines = new_lines * scaling_array
        # adding group for gemini object detection
        group = doc.groups.new()
        if spline : 
            for i in range(len(new_lines)):
                if len(current_spline) > 1:
                    # print(len(current_spline))
                    v1 = np.array([current_spline[-2][0] - current_spline[-1][0]  , current_spline[-2][1] - current_spline[-1][1] ])
                    v2 = np.array([-current_spline[-1][0] + new_lines[i][0]  , -current_spline[-1][1] + new_lines[i][1]])
                    dot_product = v1 @ v2.T
                    cosa = dot_product / (np.linalg.norm(v1) * np.linalg.norm(v2) )
                    theta = np.arccos(cosa)
                    theta_degree = theta * 180 / np.pi 
                    # break
                    if theta_degree >= degree_treshold : 
                        current_spline.append(new_lines[i])
                    else : 
                        with group.edit_data() as g :
                            if len(current_spline) == 2 :
                                g.append(msp.add_lwpolyline(current_spline, dxfattribs={"color": 6}))
                            if len(current_spline) == 3 : 
                                g.append(msp.add_lwpolyline(current_spline , dxfattribs = {"color": 5}))
                            if len(current_spline) > 3 : 
                                if methods_spline == "normal" : 
                                    g.append(msp.add_spline(current_spline , dxfattribs = {"color": 4}))
                                elif methods_spline == "centripetal" :
                                    g.append(msp.add_spline_control_frame(current_spline, method='centripetal', dxfattribs={'color': 8}))
                                elif methods_spline == "chord" :
                                    g.append(msp.add_spline_control_frame(current_spline, method='chord', dxfattribs={'color': 8}))

                        total_splines.append(current_spline)
                        current_spline = []
                        current_spline.append(new_lines[i-1])
                if len(current_spline) <= 1 : 
                    current_spline.append(new_lines[i])
        else : 
        # scaled_lines = new_lines * scaling_array
            msp.add_lwpolyline(new_lines, dxfattribs={"color": 6})
    return doc


def create_cheching_image(image , blur_size = 9,  threshold_percentage = 60 ,arz = 122.2 , tool = 89.7, epsilon = 9, grid_size_cm = 10.0, small_things = 3 , spline = False , degree_treshold = 150, spline_method = "normal") -> bool :
    
    frame  = [(0,0),(image.shape[1],0),(image.shape[1],image.shape[0]),(0,image.shape[0]),(0,0)]
    doc = create_dxf_doc(image, blur_size,threshold_percentage,arz,tool,epsilon,grid_size_cm,small_things,spline,degree_treshold, methods_spline = spline_method)
    msp = doc.modelspace()
    msp.add_lwpolyline(frame)
    # scaled_frame = np.array(frame) * scaling_array 
    # print(frame)




    # creating_initial_dxf 
    context = RenderContext(doc)
    # 2. create the backend
    backend = pymupdf.PyMuPdfBackend()
    # 3. create the frontend
    cfg = config.Configuration(
            background_policy=config.BackgroundPolicy.OFF,
            lineweight_scaling = 3
            # color_policy=config.ColorPolicy.COLOR,
        )

    frontend = Frontend(context, backend, config=cfg)
    # 4. draw the modelspace
    frontend.draw_layout(msp)
    # 5. create an A4 page layout
    page = layout.Page(image.shape[1]+1, image.shape[0]+1, layout.Units.px, margins=layout.Margins.all(0))
    # 6. get the PDF rendering as bytes
    png_bytes = backend.get_pixmap_bytes(page, fmt="png", dpi=96)
    with open("png_export.png", "wb") as fp:
        fp.write(png_bytes)
    # print(png_bytes)




    # blening with the source image
    # Load the JPEG image (background)
    background = image
    # print(background.shape)
    
    # Load the PNG image
    foreground = cv2.imread('png_export.png')
    # print(foreground.shape)
    # return 
    foreground_flipped = cv2.flip(foreground, 0)

    # Resize the foreground image to match the background image's dimensions
    # foreground_resized = cv2.resize(foreground, (background.shape[1], background.shape[0]))

    # Blend the images
    blended = cv2.addWeighted(background, 0.5, foreground_flipped,0.5, 0)  # Adjust blending ratio as needed



    # Gridding Final image
    # Save the blended image
    cv2.imwrite('blended_image.jpg', blended)

    maxdim = max(tool, arz)
    maxpixelsize = max(image.shape[0],image.shape[1])
    # Define grid parameters
    rows, cols, _ = blended.shape

    grid_size = int(grid_size_cm * (maxpixelsize / maxdim))  # adjust as needed
    color = (0, 255, 0)  # grid color (in BGR format)
    thickness = 1  # grid line thickness

    # Create a blank image to draw the grid
    grid_image = np.copy(blended)

    # Draw horizontal grid lines
    for i in range(0, rows, grid_size):
        cv2.line(grid_image, (0, i), (cols, i), color, thickness)

    # Draw vertical grid lines
    for j in range(0, cols, grid_size):
        cv2.line(grid_image, (j, 0), (j, rows), color, thickness)

    # Modify color and opacity of the grid image
    alpha = 1  # adjust opacity (0-1, 0 is fully transparent, 1 is fully opaque)
    beta = (1.0 - alpha)
    grid_with_opacity = cv2.addWeighted(grid_image, alpha, image, beta, 0)

    # Save or display the grid image

    return grid_with_opacity


def create_final_image(image , blur_size = 9,  threshold_percentage = 60 ,arz = 122.2 , tool = 89.7, epsilon = 9,small_things = 3 , spline = False , degree_treshold = 150 ,spline_method = "normal"):
    doc = create_dxf_doc(image, blur_size,threshold_percentage,arz,tool,epsilon, small_things=small_things , spline= spline , degree_treshold=degree_treshold, scale=True , methods_spline = spline_method)
    return doc
