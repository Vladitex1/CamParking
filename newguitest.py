import dearpygui.dearpygui as dpg
import cv2
import numpy as np
import os

# Create context and viewport
dpg.create_context()
dpg.create_viewport(title='Region Editor', width=1200, height=800)

# Variables for data storage
current_tool = "rectangle"
brush_size = 20
image_data = None
current_image = None
texture_id = None
mask = None
drawing = False
start_pos = None
current_pos = None
rectangles = []
polygons = []
current_polygon = []


def load_and_display_image(filepath):
    global current_image, texture_id, image_data, mask

    # Load image with OpenCV
    image = cv2.imread(filepath)
    if image is None:
        print("Error: Could not load image")
        return

    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    current_image = image_rgb

    # Initialize mask
    height, width = image_rgb.shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)

    # Convert to format suitable for Dear PyGui
    image_data = image_rgb.flatten()
    image_data = np.asarray(image_data, dtype=np.float32) / 255.0

    # Create or update texture
    if texture_id is None:
        with dpg.texture_registry():
            texture_id = dpg.add_raw_texture(
                width=width,
                height=height,
                default_value=image_data,
                format=dpg.mvFormat_Float_rgb
            )
    else:
        dpg.set_value(texture_id, image_data)

    # Clear previous drawlist if it exists
    if dpg.does_item_exist("image_drawlist"):
        dpg.delete_item("image_drawlist")

    # Display image in the drawlist with proper positioning
    with dpg.drawlist(width=width, height=height, tag="image_drawlist", parent="image_area"):
        dpg.draw_image(
            texture_id,
            (0, 0),
            (width, height),
            uv_min=(0, 0),
            uv_max=(1, 1)
        )

    # Clear previous selections
    rectangles.clear()
    polygons.clear()
    current_polygon.clear()

    print(f"Image loaded: {filepath}")


def update_display():
    """Update the display with image and mask overlay"""
    if current_image is None:
        return

    height, width = current_image.shape[:2]

    # Create overlay image
    overlay = current_image.copy()

    # Apply mask as red overlay
    if mask is not None:
        red_overlay = np.zeros_like(overlay)
        red_overlay[mask > 0] = [255, 0, 0]  # Red color for mask
        overlay = cv2.addWeighted(overlay, 0.7, red_overlay, 0.3, 0)

    # Convert to Dear PyGui format
    overlay_data = overlay.flatten()
    overlay_data = np.asarray(overlay_data, dtype=np.float32) / 255.0

    # Update texture
    dpg.set_value(texture_id, overlay_data)

    # Clear previous drawlist if it exists
    if dpg.does_item_exist("image_drawlist"):
        dpg.delete_item("image_drawlist")

    # Create new drawlist
    with dpg.drawlist(width=width, height=height, tag="image_drawlist", parent="image_area"):
        dpg.draw_image(
            texture_id,
            (0, 0),
            (width, height),
            uv_min=(0, 0),
            uv_max=(1, 1)
        )

        # Draw all saved rectangles
        for rect in rectangles:
            dpg.draw_rectangle(
                (rect['x1'], rect['y1']),
                (rect['x2'], rect['y2']),
                color=(0, 255, 0, 255),
                thickness=2
            )

        # Draw all saved polygons
        for polygon in polygons:
            if len(polygon) >= 3:
                dpg.draw_polygon(polygon, color=(0, 255, 255, 255), thickness=2)

        # Draw current selection (rectangle in progress)
        if drawing and start_pos and current_pos:
            x1, y1 = start_pos
            x2, y2 = current_pos
            dpg.draw_rectangle(
                (min(x1, x2), min(y1, y2)),
                (max(x1, x2), max(y1, y2)),
                color=(255, 255, 0, 255),  # Yellow for current selection
                thickness=2
            )

        # Draw current polygon in progress
        if current_polygon:
            if len(current_polygon) > 1:
                dpg.draw_polyline(current_polygon, color=(255, 0, 255, 255), thickness=2)  # Magenta for current
            for point in current_polygon:
                dpg.draw_circle(point, 3, color=(255, 255, 0, 255), fill=(255, 255, 0, 255))


def mouse_click_handler(sender, app_data):
    """Handle mouse clicks for drawing"""
    global drawing, start_pos, current_pos

    if current_image is None:
        return

    # Get mouse position relative to the drawlist
    mouse_button = app_data
    mouse_pos = dpg.get_mouse_pos(local=False)  # Get global mouse position

    # Get drawlist position to calculate local coordinates
    drawlist_pos = dpg.get_item_pos("image_drawlist")
    x = int(mouse_pos[0] - drawlist_pos[0])
    y = int(mouse_pos[1] - drawlist_pos[1])

    height, width = current_image.shape[:2]

    # Check if click is within image bounds
    if 0 <= x < width and 0 <= y < height:
        if current_tool == "rectangle":
            if mouse_button == 0:  # Left mouse button
                drawing = True
                start_pos = (x, y)
                current_pos = (x, y)
                print(f"Rectangle started at: ({x}, {y})")

        elif current_tool == "polygon":
            if mouse_button == 0:  # Left click - add point
                current_polygon.append((x, y))
                print(f"Polygon point added: ({x}, {y}) - Total points: {len(current_polygon)}")
                update_display()
            elif mouse_button == 1:  # Right click - complete polygon
                if len(current_polygon) >= 3:
                    complete_polygon()

        elif current_tool == "brush":
            if mouse_button == 0:
                cv2.circle(mask, (x, y), brush_size, 255, -1)
                print(f"Brush at: ({x}, {y})")
                update_display()

        elif current_tool == "eraser":
            if mouse_button == 0:
                cv2.circle(mask, (x, y), brush_size, 0, -1)
                print(f"Eraser at: ({x}, {y})")
                update_display()


def mouse_drag_handler(sender, app_data):
    """Handle mouse dragging"""
    global current_pos

    if not drawing or current_image is None:
        return

    # Get mouse position relative to the drawlist
    mouse_pos = dpg.get_mouse_pos(local=False)
    drawlist_pos = dpg.get_item_pos("image_drawlist")
    x = int(mouse_pos[0] - drawlist_pos[0])
    y = int(mouse_pos[1] - drawlist_pos[1])

    height, width = current_image.shape[:2]

    if 0 <= x < width and 0 <= y < height:
        current_pos = (x, y)
        update_display()


def mouse_release_handler(sender, app_data):
    """Handle mouse release"""
    global drawing, start_pos, current_pos

    if not drawing or current_image is None:
        return

    mouse_button = app_data
    mouse_pos = dpg.get_mouse_pos()
    x, y = int(mouse_pos[0]), int(mouse_pos[1])
    height, width = current_image.shape[:2]

    if mouse_button == 0 and current_tool == "rectangle":  # Left mouse button release
        drawing = False
        if start_pos and current_pos:
            x1, y1 = start_pos
            x2, y2 = current_pos
            rect = {
                'x1': min(x1, x2),
                'y1': min(y1, y2),
                'x2': max(x1, x2),
                'y2': max(y1, y2)
            }
            rectangles.append(rect)

            # Update mask
            cv2.rectangle(mask, (rect['x1'], rect['y1']), (rect['x2'], rect['y2']), 255, -1)
            update_display()

        start_pos = None
        current_pos = None


def complete_polygon():
    """Complete the current polygon and add to mask"""
    global current_polygon

    if len(current_polygon) >= 3:
        # Convert points to numpy array
        points = np.array(current_polygon, dtype=np.int32)

        # Add to polygons list (store as separate object)
        polygons.append({
            'points': current_polygon.copy(),
            'type': 'polygon'
        })

        # Update mask
        cv2.fillPoly(mask, [points], 255)

        print(f"Polygon completed with {len(current_polygon)} points")
        current_polygon.clear()
        update_display()


def print_saved_regions():
    """Print all saved regions for debugging"""
    print("\n=== SAVED REGIONS ===")
    print(f"Rectangles: {len(rectangles)}")
    for i, rect in enumerate(rectangles):
        print(f"  Rectangle {i}: ({rect['x1']}, {rect['y1']}) to ({rect['x2']}, {rect['y2']})")

    print(f"Polygons: {len(polygons)}")
    for i, poly in enumerate(polygons):
        print(f"  Polygon {i}: {len(poly['points'])} points")

    print("=====================\n")


def key_press_handler(sender, app_data):
    """Handle key presses"""
    if app_data == dpg.mvKey_Return:  # Enter key
        if current_tool == "polygon" and current_polygon:
            complete_polygon()
    elif app_data == dpg.mvKey_Delete:  # Delete key
        clear_mask()


def clear_mask():
    """Clear all masks and selections"""
    global mask, rectangles, polygons, current_polygon

    if mask is not None:
        mask.fill(0)
    rectangles.clear()
    polygons.clear()
    current_polygon.clear()
    update_display()
    print("Mask cleared")


def save_mask():
    """Save the mask to file"""
    if mask is not None and np.any(mask > 0):
        cv2.imwrite("output_mask.png", mask)
        print("Mask saved as output_mask.png")

        # Also save overlay image
        if current_image is not None:
            overlay = current_image.copy()
            red_overlay = np.zeros_like(overlay)
            red_overlay[mask > 0] = [255, 0, 0]
            result = cv2.addWeighted(overlay, 0.7, red_overlay, 0.3, 0)
            cv2.imwrite("output_overlay.png", cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
            print("Overlay saved as output_overlay.png")
    else:
        print("No mask to save")


def tool_changed(sender, app_data):
    global current_tool
    # app_data - это выбранный текст, а не индекс
    tool_mapping = {
        "Rectangle": "rectangle",
        "Polygon": "polygon",
        "Brush": "brush",
        "Eraser": "eraser"
    }
    current_tool = tool_mapping.get(app_data, "rectangle")
    print(f"Selected tool: {current_tool}")


def brush_size_changed(sender, app_data):
    global brush_size
    brush_size = app_data
    print(f"Brush size: {brush_size}")


def load_image(sender, app_data):
    if app_data["file_path_name"]:
        load_and_display_image(app_data["file_path_name"])


def show_help(sender, app_data):
    dpg.configure_item("help_modal", show=True)


# Create main window
with dpg.window(label="Main Window", tag="main_window"):
    # Tools panel
    with dpg.group(horizontal=True):
        with dpg.child_window(width=300, height=600):
            dpg.add_text("Selection Tools")
            dpg.add_separator()

            # Radio buttons for tool selection
            dpg.add_radio_button(
                items=["Rectangle", "Polygon", "Brush", "Eraser"],
                callback=tool_changed,
                default_value="Rectangle"
            )

            dpg.add_spacer(height=20)

            # Brush size slider
            dpg.add_slider_int(
                label="Brush Size",
                min_value=1,
                max_value=100,
                default_value=brush_size,
                callback=brush_size_changed
            )

            dpg.add_spacer(height=20)

            # Action buttons
            dpg.add_button(label="Load Image", callback=lambda: dpg.show_item("file_dialog"))
            dpg.add_button(label="Clear Mask", callback=clear_mask)
            dpg.add_button(label="Save Mask", callback=save_mask)

            dpg.add_spacer(height=20)

            # Info
            dpg.add_text("Instructions:")
            dpg.add_text("Rectangle: Click and drag")
            dpg.add_text("Polygon: Click to add points")
            dpg.add_text("Enter: Complete polygon")
            dpg.add_text("Brush: Click to draw")
            dpg.add_text("Eraser: Click to erase")

            dpg.add_spacer(height=20)
            dpg.add_button(label="Help", callback=show_help)

        # Image area
        with dpg.child_window(width=800, tag="image_area"):
            dpg.add_text("Image Area - Load an image to start")
            dpg.add_separator()

            # Placeholder - will be replaced when image is loaded
            with dpg.drawlist(width=780, height=550):
                dpg.draw_rectangle((10, 10), (770, 540), color=(100, 100, 100, 255))
                dpg.draw_text((300, 250), "No image loaded", color=(255, 255, 255, 255))

# File selection dialog
with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=load_image,
        id="file_dialog",
        width=700,
        height=400
):
    dpg.add_file_extension("Images{.jpg,.jpeg,.png,.bmp,.tga}")
    dpg.add_file_extension("All files{.*}")

# Help modal window
with dpg.window(
        label="Help",
        modal=True,
        show=False,
        id="help_modal",
        no_title_bar=True,
        width=500,
        height=300
):
    dpg.add_text("Region Editor Help:")
    dpg.add_text("1. Load an image using 'Load Image' button")
    dpg.add_text("2. Select a tool from the left panel")
    dpg.add_text("3. Draw on the image:")
    dpg.add_text("   - Rectangle: Click and drag")
    dpg.add_text("   - Polygon: Click to add points, press Enter to finish")
    dpg.add_text("   - Brush: Click to draw freehand")
    dpg.add_text("   - Eraser: Click to erase areas")
    dpg.add_text("4. Use 'Save Mask' to export the result")
    dpg.add_spacer(height=20)
    dpg.add_button(label="Close", width=75, callback=lambda: dpg.configure_item("help_modal", show=False))

# Event handlers
with dpg.handler_registry():
    dpg.add_mouse_click_handler(callback=mouse_click_handler)
    dpg.add_mouse_drag_handler(callback=mouse_drag_handler)
    dpg.add_mouse_release_handler(callback=mouse_release_handler)
    dpg.add_key_press_handler(callback=key_press_handler)

# Create menu
with dpg.viewport_menu_bar():
    with dpg.menu(label="File"):
        dpg.add_menu_item(label="Open", callback=lambda: dpg.show_item("file_dialog"))
        dpg.add_menu_item(label="Clear Mask", callback=clear_mask)
        dpg.add_menu_item(label="Save Mask", callback=save_mask)
        dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

    with dpg.menu(label="Help"):
        dpg.add_menu_item(label="Help", callback=show_help)

# Setup and launch
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)

# Main loop
dpg.start_dearpygui()

# Cleanup
dpg.destroy_context()