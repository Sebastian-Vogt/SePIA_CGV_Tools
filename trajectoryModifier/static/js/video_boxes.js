/**
 * Resize function for the boxes div. (Needed, that the boxes match the video on window resize)
 */
function rescale_boxes() {
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

                    const tl_handle = document.createElement("div");
                    tl_handle.id = "id" + trajectories[t].id + "box_tl_handle";
                    tl_handle.classList.add("resizer");
                    tl_handle.classList.add("top_left_resizer");
                    tl_handle.addEventListener('mousedown', function(e){
                        handle_resizer_click(e, rect, t, i);
                    });
                    const tr_handle = document.createElement("div");
                    tr_handle.id = "id" + trajectories[t].id + "box_tr_handle";
                    tr_handle.classList.add("resizer");
                    tr_handle.classList.add("top_right_resizer");
                    tr_handle.addEventListener('mousedown', function(e){
                        handle_resizer_click(e, rect, t, i);
                    });
                    const bl_handle = document.createElement("div");
                    bl_handle.id = "id" + trajectories[t].id + "box_bl_handle";
                    bl_handle.classList.add("resizer");
                    bl_handle.classList.add("bottom_left_resizer");
                    bl_handle.addEventListener('mousedown', function(e){
                        handle_resizer_click(e, rect, t, i);
                    });
                    const br_handle = document.createElement("div");
                    br_handle.id = "id" + trajectories[t].id + "box_br_handle";
                    br_handle.classList.add("resizer");
                    br_handle.classList.add("bottom_right_resizer");
                    br_handle.addEventListener('mousedown', function(e){
                        handle_resizer_click(e, rect, t, i);
                    });

                    rect.appendChild(tl_handle);
                    rect.appendChild(tr_handle);
                    rect.appendChild(bl_handle);
                    rect.appendChild(br_handle);
                    boxes_div.appendChild(rect);
                }
            }
        }
    }
}

// TODO add resize bbxes
function handle_resizer_click(e, rect, t, i){

    e.target.classList.add("active_resizer");

    let original_x = parseFloat(rect.style.left.replace('px', ''));
    let original_y = parseFloat(rect.style.top.replace('px', ''));
    let original_width = parseFloat(rect.style.width.replace('px', ''));
    let original_height = parseFloat(rect.style.height.replace('px', ''));
    let original_mouse_x = e.pageX;
    let original_mouse_y = e.pageY;

    const boxes_div_height = parseInt(document.getElementById("boxes").clientHeight);
    const boxes_div_width = parseInt(document.getElementById("boxes").clientWidth);

    let x0 = original_x;
    let y0 = original_y;
    let x1 = original_x + original_width;
    let y1 = original_y + original_height;

    function move(eve) {
        x0 = original_x;
        y0 = original_y;
        x1 = original_x + original_width;
        y1 = original_y + original_height;
        let width = 0;
        let height = 0;
        if(e.target.classList.contains('top_left_resizer')){
            width = original_width - (eve.pageX - original_mouse_x);
            height = original_height - (eve.pageY - original_mouse_y);
            if(width < 0){
                width = -width;
                x0 = x1;
                x1 = x0 + width;
            }else{
                x0 = x0 + (eve.pageX - original_mouse_x);
            }
            if(height < 0){
                height = -height;
                y0 = y1;
                y1 = y0 + height;
            }else{
                y0 = y0 + (eve.pageY - original_mouse_y);
            }
        }else if(e.target.classList.contains('top_right_resizer')){
            width = original_width + (eve.pageX - original_mouse_x);
            height = original_height - (eve.pageY - original_mouse_y);
            if (width < 0){
                width = -width;
                x1 = x0;
                x0 = x1 - width;
            }else{
                x1 = x1 + (eve.pageX - original_mouse_x);
            }
            if (height < 0){
                height = -height;
                y0 = y1;
                y1 = y0 + height;
            }else{
                y0 = y0 + (eve.pageY - original_mouse_y);
            }
        }else if(e.target.classList.contains('bottom_left_resizer')){
            height = original_height + (eve.pageY - original_mouse_y);
            width = original_width - (eve.pageX - original_mouse_x);
            if (width < 0){
                width = -width;
                x0 = x1;
                x1 = x0 + width;
            }else{
                x0 = x0 + (eve.pageX - original_mouse_x);
            }
            if (height < 0){
                height = -height;
                y1 = y0;
                y0 = y0 - height;
            }else{
                y1 = y1 + (eve.pageY - original_mouse_y);
            }
        }else if(e.target.classList.contains('bottom_right_resizer')){
            width = original_width + (eve.pageX - original_mouse_x);
            height = original_height + (eve.pageY - original_mouse_y);
            if (width < 0){
                width = -width;
                x1 = x0;
                x0 = x1 - width;
            }else{
                x1 = x1 + (eve.pageX - original_mouse_x);
            }
            if (height < 0){
                height = -height;
                y1 = y0;
                y0 = y0 - height;
            }else{
                y1 = y1 + (eve.pageY - original_mouse_y);
            }
        }else
            return;


        // clamping
        if (x0 < 0){
            x0 = 0;
            width = x1-x0;
        }
        if (y0 < 0){
            y0 = 0;
            height = y1-y0;
        }
        if (x1 > boxes_div_width){
            x1 = boxes_div_width;
            width = x1-x0;
        }
        if (y1 > boxes_div_height){
            y1 = boxes_div_height;
            height = y1-y0;
        }

        rect.style.left = x0+'px';
        rect.style.top = y0+'px';
        rect.style.width = width+'px';
        rect.style.height = height+'px';

    };
    function up(eve) {

        trajectories[t].positions_rotations_and_boxes[i].box = [
            x0/boxes_div_width*video_width,
            y0/boxes_div_height*video_height,
            x1/boxes_div_width*video_width,
            y1/boxes_div_height*video_height
        ];

        e.target.removeEventListener('mousemove', move);
        e.target.removeEventListener('mouseup', up);
        e.target.removeEventListener('mouseleave', up);
        trajectories[t].positions_rotations_and_boxes[i].specified = true;
        e.target.classList.remove("active_resizer");

        interpolateTrajectory(t, function() {
            draw_boxes();
            // update save button
            if (!changes) {
                changes = true;
                updateSaveButton();
            }
        });
    };

    e.target.addEventListener('mousemove', move);
    e.target.addEventListener('mouseup', up);
    e.target.addEventListener('mouseleave', up);
}

