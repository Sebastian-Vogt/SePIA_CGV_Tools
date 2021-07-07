/**
 * Hides and shows element descriptors when they are seen/ not seen in the video
 */
function hide_and_show_elements() {
    for (let t = 0; t < trajectories.length; t++) {
        const element_div = document.getElementById("id"+trajectories[t].id);
        let flag = false;
        for (let p = 0; p < trajectories[t].positions_rotations_and_boxes.length; p++) {
            if (current_frame == trajectories[t].positions_rotations_and_boxes[p].frame) {
                element_div.classList.remove("hidden");
                flag = true;
                break;
            }
        }
        if (!flag)
            element_div.classList.add("hidden");
        if (trajectories[t].positions_rotations_and_boxes.length == 0) {
            element_div.classList.remove("hidden");
        }
    }
    sortElementsByHidden();
}
/**
 * Hides and shows element descriptors buttons
 */
function button_visibility() {
    for (let t = 0; t < trajectories.length; t++) {
        // when there are no points
        if (trajectories[t].positions_rotations_and_boxes.length == 0) {
            let button = document.getElementById("id"+trajectories[t].id).querySelector('.addButton');   // extrapolation possible
            if (button) {
                button.classList.remove("hidden");
            }
            button = document.getElementById("id"+trajectories[t].id).querySelector('.interpolateButton'); // interpolation not possible
            if (button) {
                button.classList.add("hidden");
            }
            button = document.getElementById("id"+trajectories[t].id).querySelector('.orientationButton');   // orientation not possible
            if (button) {
                button.classList.add("hidden");
            }
            button = document.getElementById("id"+trajectories[t].id).querySelector('.smoothButton');   // smoothing not possible
            if (button) {
                button.classList.add("hidden");
            }
            continue;
        }
        // if there are no "free" frames on the start and end
        if (trajectories[t].positions_rotations_and_boxes[0].frame == 0 && trajectories[t].positions_rotations_and_boxes[trajectories[t].positions_rotations_and_boxes.length - 1].frame == nr_frames - 1) {
            const button = document.getElementById("id"+trajectories[t].id).querySelector('.addButton'); // extrapolation not possible
            if (button) {
                button.classList.add("hidden");
            }
        } else {    // otherwise
            const button = document.getElementById("id"+trajectories[t].id).querySelector('.addButton'); // extrapolation possible
            if (button) {
                button.classList.remove("hidden");
            }
        }

        let continuity_flag = true; // indicated that there are no "free" frames between other frames
        let constancy_flag = true;  // indicates that all positions are the same
        let prev_frame = trajectories[t].positions_rotations_and_boxes[0].frame - 1;
        let lat = trajectories[t].positions_rotations_and_boxes[0].position[0].toFixed(10);
        let long = trajectories[t].positions_rotations_and_boxes[0].position[1].toFixed(10);
        // correctly calculate continuity and constancy flags
        for (let p = 0; p < trajectories[t].positions_rotations_and_boxes.length; p++) {
            if (prev_frame + 1 != trajectories[t].positions_rotations_and_boxes[p].frame) {
                continuity_flag = false;
            }
            if (lat != trajectories[t].positions_rotations_and_boxes[p].position[0].toFixed(10) || long != trajectories[t].positions_rotations_and_boxes[p].position[1].toFixed(10)) {
                constancy_flag = false;
            }
            prev_frame = trajectories[t].positions_rotations_and_boxes[p].frame;
        }


        if (continuity_flag) {  // if continuous
            const button = document.getElementById("id"+trajectories[t].id).querySelector('.interpolateButton'); // no interpolation possible
            if (button) {
                button.classList.add("hidden");
            }
        } else { // otherwise it is
            const button = document.getElementById("id"+trajectories[t].id).querySelector('.interpolateButton');
            if (button) {
                button.classList.remove("hidden");
            }
        }

        if (constancy_flag) { // if constant
            const button = document.getElementById("id"+trajectories[t].id).querySelector('.orientationButton'); // orientation is possible
            if (button) {
                button.classList.remove("hidden");
            }
        } else {    // otherwise not
            const button = document.getElementById("id"+trajectories[t].id).querySelector('.orientationButton');
            if (button) {
                button.classList.add("hidden");
            }
        }
    }
}