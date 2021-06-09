/**
 * Resize function for the boxes div. (Needed, that the boxes match the video on window resize)
 */
function resize_boxes() {
    const height = parseInt(video.clientHeight);
    const width = parseInt(video.clientWidth);
    let boxes_div = document.getElementById("boxes");
    if (width / height > video_width / video_height) {
        boxes_div.style.height = height.toString() + "px";
        boxes_div.style.top = "0px";
        const new_width = video_width / video_height * height;
        boxes_div.style.width = new_width.toString() + "px";
        boxes_div.style.left = ((width - new_width) / 2).toString() + "px";
    } else {
        boxes_div.style.width = width.toString() + "px";
        boxes_div.style.left = "0px";
        const new_height = video_height / video_width * width;
        boxes_div.style.height = new_height.toString() + "px";
        boxes_div.style.top = ((height - new_height) / 2).toString() + "px";
    }
    draw_boxes();
    set_box_colors();
}
/**
 * Draws the boxes (complete redraw => could be improved) Called on each new frame and on resize
 */
function draw_boxes() {
    const boxes_div = document.getElementById("boxes");
    boxes_div.innerHTML = '';
    const height = parseInt(document.getElementById("boxes").clientHeight);
    const width = parseInt(document.getElementById("boxes").clientWidth);
    for (let t = 0; t < trajectories.length; t++) {
        if (trajectories[t].positions_rotations_and_boxes[0] && trajectories[t].positions_rotations_and_boxes[0].box ) {
            for (let i = 0; i < trajectories[t].positions_rotations_and_boxes.length; i++) {
                if (trajectories[t].positions_rotations_and_boxes[i].frame == current_frame) {
                    const box_coords = trajectories[t].positions_rotations_and_boxes[i].box;
                    const rect = document.createElement("div");
                    rect.id = "id" + trajectories[t].id + "box";
                    rect.style.position = "absolute";
                    rect.style.left = (width / video_width * ((box_coords[0] < video_width) ? ((box_coords[0] < 0) ? 0 : box_coords[0]) : video_width)).toString() + "px";
                    rect.style.top = (height / video_height * ((box_coords[1] < video_height) ? ((box_coords[1] < 0) ? 0 : box_coords[1]) : video_height)).toString() + "px";
                    rect.style.width = ((width / video_width) * (((box_coords[2] - box_coords[0]) < video_width) ? (((box_coords[2] - box_coords[0]) < 0) ? 0 : (box_coords[2] - box_coords[0])) : video_width)).toString() + "px";
                    rect.style.height = ((height / video_height) * (((box_coords[3] - box_coords[1]) < video_height) ? (((box_coords[3] - box_coords[1]) < 0) ? 0 : (box_coords[3] - box_coords[1])) : video_height)).toString() + "px";
                    rect.style.border = (trajectories[t].positions_rotations_and_boxes[i].is_interpolated)? "3px dashed rgb(59, 173, 227)" : "3px solid rgb(59, 173, 227)";
                    rect.style.backgroundColor = "rgba(59, 173, 227,0.5)";
                    rect.style.backdropFilter = "contrast(1.5)";
                    rect.style.color = "rgb(59, 173, 227)";
                    try {
                        rect.innerText = trajectories[t].positions_rotations_and_boxes[i].confidence.toFixed(2);
                    } catch {
                        rect.innerText = "";
                    }
                    rect.addEventListener("mouseenter", handle_mouseenter_box);
                    rect.addEventListener("mouseleave", handle_mouseleave_element);
                    rect.addEventListener("click", handle_click_element);
                    boxes_div.appendChild(rect);
                }
            }
        }
    }
}

/**
 * Resets interpolated bounding_boxes to the original ones
 */
function uninterpolate_boxes(){
    for (let t = 0; t < trajectories.length; t++) {
        const index = original_boxes.findIndex((element) => element.id == trajectories[t].id);
        if (index >= 0){
            for (let i = 0; i < trajectories[t].positions_rotations_and_boxes.length; i++) {
                if (trajectories[t].positions_rotations_and_boxes[i].is_interpolated){
                    const index2 = original_boxes[index].boxes.findIndex((element) => element.frame == trajectories[t].positions_rotations_and_boxes[i].frame);
                    if (index2 >= 0){
                        trajectories[t].positions_rotations_and_boxes[i].box = original_boxes[index].boxes[index2].box;
                    }
                }
            }
        }
    }
}