/**
 * Handles the click on the interpolation button
 */
function interpolate_points(event) {
    const trajectory_id = event.target.closest(".elementButtonRegion").getAttribute("data-id");
    let trajectory_index = trajectories.findIndex(t => "id"+t.id === trajectory_id);

    const xhr = new XMLHttpRequest();
    const theUrl = "/interpolate";
    xhr.open("POST", theUrl);
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {

            const json_resp = JSON.parse(xhr.responseText);
            trajectories[trajectory_index] = json_resp;

            uninterpolate_boxes();

            // remove old line and replace it with the new one + setting callbacks

            map.removeLayer(lines[trajectory_index]);

            lines[trajectory_index] = L.polyline(trajectories[trajectory_index].positions_rotations_and_boxes.map(position_rotation_and_box => position_rotation_and_box.position), {
                color: ((trajectories[trajectory_index].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)'),
                opacity: 0.3
            }).addTo(map);

            lines[trajectory_index].trajectory_id = trajectories[trajectory_index].id;
            lines[trajectory_index].line_index = trajectory_index;
            lines[trajectory_index].addEventListener("mousedown", line_mousedown_function);
            lines[trajectory_index].addEventListener("mouseover", handle_mouseenter_line);
            lines[trajectory_index].addEventListener("mouseout", handle_mouseleave_line);

            // remove old points of interpolated trajectory and replace it with the new one + setting callbacks

            for (let p = 0; p < trajectories[trajectory_index].positions_rotations_and_boxes.length; p++) {
                if (p >= points[trajectory_index].length) {
                    points[trajectory_index].push(L.circle(
                        new L.LatLng(trajectories[trajectory_index].positions_rotations_and_boxes[p].position[0],
                            trajectories[trajectory_index].positions_rotations_and_boxes[p].position[1]),
                        {
                            radius: 0.5,
                            color: ((trajectories[trajectory_index].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)')
                        }
                    ).addTo(map));
                } else {
                    map.removeLayer(points[trajectory_index][p]);
                    points[trajectory_index][p] = L.circle(
                        new L.LatLng(trajectories[trajectory_index].positions_rotations_and_boxes[p].position[0],
                            trajectories[trajectory_index].positions_rotations_and_boxes[p].position[1]),
                        {
                            radius: 0.5,
                            color: ((trajectories[trajectory_index].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)')
                        }
                    ).addTo(map);
                }

                points[trajectory_index][p].line_index = trajectory_index;
                points[trajectory_index][p].point_index = p;
                points[trajectory_index][p].addEventListener("mousedown", point_mousedown_function);
                points[trajectory_index][p].addEventListener("mouseover", handle_mouseenter_point);
                points[trajectory_index][p].addEventListener("mouseout", handle_mouseleave_point);
            }

            button_visibility();
            redraw_object_map_object_outlines();
        }

    };
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(trajectories[trajectory_index]));
}

/**
 * Handles the click on the remove object button
 */
function remove_object(event) {
    const trajectory_id = event.target.closest(".elementButtonRegion").getAttribute("data-id");
    remove_object_by_ID(trajectory_id);
}

/**
 * Removes an object by id
 */
function remove_object_by_ID(trajectory_id) {
    let trajectory_index = trajectories.findIndex(t => "id"+t.id === trajectory_id);

    trajectories.splice(trajectory_index, 1);

    // remove points and line from map
    map.removeLayer(lines[trajectory_index]);
    for (let p = 0; p < points[trajectory_index].length; p++) {
        map.removeLayer(points[trajectory_index][p]);
    }
    //remove points and line from arrays
    lines.splice(trajectory_index, 1);
    points.splice(trajectory_index, 1);

    //correct indices of remaining points and lines
    for (let l = trajectory_index; l < lines.length; l++) {
        lines[l].line_index -= 1;
        for (let p = 0; p < points[l].length; p++) {
            points[l][p].line_index -= 1;
        }
    }

    document.getElementById("elementSelector").removeChild(document.getElementById(trajectory_id));
    document.getElementById("boxes").removeChild(document.getElementById(trajectory_id + "box"));

    const boxes_index = original_boxes.findIndex(e => e.id === trajectory_id);
    if (boxes_index >= 0){
        original_boxes.splice(boxes_index, 1);
    }

    set_element_colors();
    set_circle_colors();
    set_line_colors();
    set_box_colors();
    redraw_object_map_object_outlines();
}

/**
 * Merges two objects
 */
function merge_objects(trajectory_id1, trajectory_id2) {
    // ids will begin with an "id" -> do not match actual ids
    let trajectory_index1 = trajectories.findIndex(t => "id"+t.id === trajectory_id1);
    const trajectory_index2 = trajectories.findIndex(t => "id"+t.id === trajectory_id2);

    // add non existing frames (unsorted)
    for(let p = 0; p < trajectories[trajectory_index2].positions_rotations_and_boxes.length; p++){
        if(trajectories[trajectory_index1].positions_rotations_and_boxes.findIndex(e => e.frame === trajectories[trajectory_index2].positions_rotations_and_boxes[p].frame) == -1){
            trajectories[trajectory_index1].positions_rotations_and_boxes.push(trajectories[trajectory_index2].positions_rotations_and_boxes[p]);
        }
    }

    const boxes_index1 = original_boxes.findIndex(e => "id"+e.id === trajectory_id1);
    const boxes_index2 = original_boxes.findIndex(e => "id"+e.id === trajectory_id2);
    for(let bi = 0; bi < original_boxes[boxes_index2].boxes.length; bi++){
        if(original_boxes[boxes_index1].boxes.findIndex(e => e.frame === original_boxes[boxes_index2].boxes[bi].frame) == -1){
            original_boxes[boxes_index1].boxes.push(original_boxes[boxes_index2].boxes[bi]);
        }
    }
    // sort by frame
    trajectories[trajectory_index1].positions_rotations_and_boxes.sort(function (a, b) { return a.frame - b.frame;});
    original_boxes[boxes_index1].boxes.sort(function (a, b) { return a.frame - b.frame;});
    // remove old trajectory
    trajectories.splice(trajectory_index2, 1);
    original_boxes.splice(boxes_index2, 1);
    // indices might have changed
    trajectory_index1 = trajectories.findIndex(t => "id"+t.id === trajectory_id1);

    // remove old points and lines from map
    map.removeLayer(lines[trajectory_index1]);
    map.removeLayer(lines[trajectory_index2]);
    for (let p = 0; p < points[trajectory_index1].length; p++) {
        map.removeLayer(points[trajectory_index1][p]);
    }
    for (let p = 0; p < points[trajectory_index2].length; p++) {
        map.removeLayer(points[trajectory_index2][p]);
    }
    // remove only traj. 2 since traj. 1 will be refilled
    lines.splice(trajectory_index2, 1);
    points.splice(trajectory_index2, 1);
    points[trajectory_index1] = []

    const xhr = new XMLHttpRequest();
    const theUrl = "/interpolate";
    xhr.open("POST", theUrl);
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            const json_resp = JSON.parse(xhr.responseText);
            trajectories[trajectory_index1] = json_resp;

            uninterpolate_boxes();

            lines[trajectory_index1] = L.polyline(trajectories[trajectory_index1].positions_rotations_and_boxes.map(position_rotation_and_box => position_rotation_and_box.position), {
                color: ((trajectories[trajectory_index1].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)'),
                opacity: 0.3
            }).addTo(map);

            lines[trajectory_index1].trajectory_id = trajectories[trajectory_index1].id;
            lines[trajectory_index1].line_index = trajectory_index1;
            lines[trajectory_index1].addEventListener("mousedown", line_mousedown_function);
            lines[trajectory_index1].addEventListener("mouseover", handle_mouseenter_line);
            lines[trajectory_index1].addEventListener("mouseout", handle_mouseleave_line);

            for (let p = 0; p < trajectories[trajectory_index1].positions_rotations_and_boxes.length; p++) {
                points[trajectory_index1].push(L.circle(
                    new L.LatLng(trajectories[trajectory_index1].positions_rotations_and_boxes[p].position[0],
                        trajectories[trajectory_index1].positions_rotations_and_boxes[p].position[1]),
                    {
                        radius: 0.5,
                        color: ((trajectories[trajectory_index1].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)')
                    }
                ).addTo(map));
                points[trajectory_index1][p].line_index = trajectory_index1;
                points[trajectory_index1][p].point_index = p;
                points[trajectory_index1][p].addEventListener("mousedown", point_mousedown_function);
                points[trajectory_index1][p].addEventListener("mouseover", handle_mouseenter_point);
                points[trajectory_index1][p].addEventListener("mouseout", handle_mouseleave_point);
            }

            set_element_colors();
            set_circle_colors();
            set_line_colors();
            set_box_colors();
            button_visibility();
            redraw_object_map_object_outlines();
            draw_boxes();
        }
    };
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(trajectories[trajectory_index1]));

    document.getElementById("elementSelector").removeChild(document.getElementById(trajectory_id2));
    document.getElementById("boxes").removeChild(document.getElementById(trajectory_id2 + "box"));

}

/**
 * Handles the click on the extrapolate button
 */
function add_points_form_submitted() {
    const number_of_points = parseInt(document.getElementById("numberOfPoints").value);

    if (trajectories[index_to_edit].positions_rotations_and_boxes.length >= 2) {

        //create list of frame numbers to be extrapolated
        let frames_to_be_extrapolated = [];
        if (document.getElementById("newPointDirection").checked) {
            for (let i = 1; i <= number_of_points; i++) {
                frames_to_be_extrapolated.push(trajectories[index_to_edit].positions_rotations_and_boxes[trajectories[index_to_edit].positions_rotations_and_boxes.length - 1].frame + i);
            }
        } else {
            for (let i = trajectories[index_to_edit].positions_rotations_and_boxes[0].frame - number_of_points; i < trajectories[index_to_edit].positions_rotations_and_boxes[0].frame; i++) {
                frames_to_be_extrapolated.push(i);
            }
        }


        const xhr = new XMLHttpRequest();
        const theUrl = "/extrapolate";
        xhr.open("POST", theUrl);
        xhr.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {

                const json_resp = JSON.parse(xhr.responseText);
                trajectories[index_to_edit] = json_resp;

                uninterpolate_boxes();

                // remove old line and replace it with the new one + setting callbacks

                map.removeLayer(lines[index_to_edit]);

                lines[index_to_edit] = L.polyline(trajectories[index_to_edit].positions_rotations_and_boxes.map(position_rotation_and_box => position_rotation_and_box.position), {
                    color: ((trajectories[index_to_edit].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)'),
                    opacity: 0.3
                }).addTo(map);

                lines[index_to_edit].trajectory_id = trajectories[index_to_edit].id;
                lines[index_to_edit].line_index = index_to_edit;
                lines[index_to_edit].addEventListener("mousedown", line_mousedown_function);
                lines[index_to_edit].addEventListener("mouseover", handle_mouseenter_line);
                lines[index_to_edit].addEventListener("mouseout", handle_mouseleave_line);

                // remove old points of interpolated trajectory and replace it with the new one + setting callbacks

                for (let p = 0; p < trajectories[index_to_edit].positions_rotations_and_boxes.length; p++) {
                    if (p >= points[index_to_edit].length) {
                        points[index_to_edit].push(L.circle(
                            new L.LatLng(trajectories[index_to_edit].positions_rotations_and_boxes[p].position[0],
                                trajectories[index_to_edit].positions_rotations_and_boxes[p].position[1]),
                            {
                                radius: 0.5,
                                color: ((trajectories[index_to_edit].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)')
                            }
                        ).addTo(map));
                    } else {
                        map.removeLayer(points[index_to_edit][p]);
                        points[index_to_edit][p] = L.circle(
                            new L.LatLng(trajectories[index_to_edit].positions_rotations_and_boxes[p].position[0],
                                trajectories[index_to_edit].positions_rotations_and_boxes[p].position[1]),
                            {
                                radius: 0.5,
                                color: ((trajectories[index_to_edit].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)')
                            }
                        ).addTo(map);
                    }

                    points[index_to_edit][p].line_index = index_to_edit;
                    points[index_to_edit][p].point_index = p;
                    points[index_to_edit][p].addEventListener("mousedown", point_mousedown_function);
                    points[index_to_edit][p].addEventListener("mouseover", handle_mouseenter_point);
                    points[index_to_edit][p].addEventListener("mouseout", handle_mouseleave_point);
                }

                button_visibility();
                redraw_object_map_object_outlines();

                document.getElementById("numberOfPoints").value = 1;
                document.getElementById("newPointDirection").checked = true;
                document.getElementById("addPointsPopup").classList.add("hidden");
            }
        }
        ;
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        const json = {
            "trajectory": trajectories[index_to_edit],
            "frames": frames_to_be_extrapolated
        }
        xhr.send(JSON.stringify(json));
    } else if (trajectories[index_to_edit].positions_rotations_and_boxes.length == 1) {

        // when only one point exists: copy point n times

        for (let i = 1; i <= number_of_points; i++) {
            if (document.getElementById("newPointDirection").checked) {
                let pbr = {
                    "frame": trajectories[index_to_edit].positions_rotations_and_boxes[0] + i,
                    "position": [trajectories[index_to_edit].positions_rotations_and_boxes[0].position[0], trajectories[index_to_edit].positions_rotations_and_boxes[0].position[1]],
                    "is_interpolated": true
                }
                trajectories[index_to_edit].positions_rotations_and_boxes.push(pbr);
            } else {
                let pbr = {
                    "frame": trajectories[index_to_edit].positions_rotations_and_boxes[0] - i,
                    "position": [trajectories[index_to_edit].positions_rotations_and_boxes[0].position[0], trajectories[index_to_edit].positions_rotations_and_boxes[0].position[1]],
                    "is_interpolated": true
                }
                trajectories[index_to_edit].positions_rotations_and_boxes.unshift(pbr);
            }

        }

        update_lines_and_points_on_extrapolate();

        set_element_colors();
        set_circle_colors();
        set_line_colors();

        button_visibility();
        redraw_object_map_object_outlines();

        document.getElementById("numberOfPoints").value = 1;
        document.getElementById("newPointDirection").checked = true;
        document.getElementById("addPointsPopup").classList.add("hidden");

    } else {
        // if there is no point at all: create n ones at the center of the map view

        const starting_frame = parseInt(document.getElementById("frameToStartInput").value);
        const lat = map.getBounds().getSouth() + (map.getBounds().getNorth() - map.getBounds().getSouth()) / 2;
        const long = map.getBounds().getWest() + (map.getBounds().getEast() - map.getBounds().getWest()) * 3 / 10;

        for (let i = 0; i < number_of_points; i++) {
            let pbr = {
                "frame": starting_frame + i,
                "position": [lat, long],
                "is_interpolated": true
            }
            trajectories[index_to_edit].positions_rotations_and_boxes.push(pbr);
        }

        update_lines_and_points_on_extrapolate();

        set_element_colors();
        set_circle_colors();
        set_line_colors();

        button_visibility();
        redraw_object_map_object_outlines();

        document.getElementById("numberOfPoints").value = 1;
        document.getElementById("frameToStartInput").value = current_frame;
        document.getElementById("newPointDirection").checked = true;
        document.getElementById("addPointsPopup").classList.add("hidden");

    }


}

/**
 * Validates that the starting frame (extrapolate with no existing points) is between 0 and nr of frames
 */
function validate_starting_frame(event) {
    let value = parseInt(event.target.value);
    if (isNaN(value) || value < 0) {
        value = 0;
    } else if (value >= nr_frames) {
        value = nr_frames - 1;
    }

    event.target.value = value;
}

/**
 * Redrawes line and points of trajectory with on index index_to_edit (called from the extrapolate function)
 */
function update_lines_and_points_on_extrapolate() {
    map.removeLayer(lines[index_to_edit]);

    lines[index_to_edit] = L.polyline(trajectories[index_to_edit].positions_rotations_and_boxes.map(position_rotation_and_box => position_rotation_and_box.position), {
        color: ((trajectories[index_to_edit].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)'),
        opacity: 0.3
    }).addTo(map);

    lines[index_to_edit].trajectory_id = trajectories[index_to_edit].id;
    lines[index_to_edit].line_index = index_to_edit;
    lines[index_to_edit].addEventListener("mousedown", line_mousedown_function);
    lines[index_to_edit].addEventListener("mouseover", handle_mouseenter_line);
    lines[index_to_edit].addEventListener("mouseout", handle_mouseleave_line);

    if (document.getElementById("newPointDirection").checked) {
        const nr_points_before = points[index_to_edit].length;
        const number_of_points = parseInt(document.getElementById("numberOfPoints").value)
        for (let p = 0; p < number_of_points; p++) {
            points[index_to_edit].push(L.circle(
                new L.LatLng(trajectories[index_to_edit].positions_rotations_and_boxes[nr_points_before + p].position[0],
                    trajectories[index_to_edit].positions_rotations_and_boxes[nr_points_before + p].position[1]),
                {
                    radius: 0.5,
                    color: ((trajectories[index_to_edit].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)')
                }
            ).addTo(map));
            points[index_to_edit][nr_points_before + p].line_index = index_to_edit;
            points[index_to_edit][nr_points_before + p].point_index = nr_points_before + p;
            points[index_to_edit][nr_points_before + p].addEventListener("mousedown", point_mousedown_function);
            points[index_to_edit][nr_points_before + p].addEventListener("mouseover", handle_mouseenter_point);
            points[index_to_edit][nr_points_before + p].addEventListener("mouseout", handle_mouseleave_point);
        }
    } else {
        let new_points = [];
        for (let p = 0; p < number_of_points; p++) {
            new_points.push(L.circle(
                new L.LatLng(trajectories[index_to_edit].positions_rotations_and_boxes[p].position[0],
                    trajectories[index_to_edit].positions_rotations_and_boxes[p].position[1]),
                {
                    radius: 0.5,
                    color: ((trajectories[index_to_edit].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)')
                }
            ).addTo(map));
            new_points[p].line_index = index_to_edit;
            new_points[p].point_index = p;
            new_points[p].addEventListener("mousedown", point_mousedown_function);
            new_points[p].addEventListener("mouseover", handle_mouseenter_point);
            new_points[p].addEventListener("mouseout", handle_mouseleave_point);
        }
        points[index_to_edit].unshift(...new_points);
        for (let p = number_of_points; p < points[index_to_edit].length; p++) {
            points[index_to_edit][p].point_index = p;
        }
    }
}

/**
 * Handles click on cancel extraction button. (Hides form and resets values.)
 */
function cancel_add_points() {
    document.getElementById("numberOfPoints").value = 1;
    document.getElementById("newPointDirection").checked = true;
    document.getElementById("addPointsPopup").classList.add("hidden");
}

/**
 * Validates number of points to add. (Needs to be inside first to last frame)
 */
function numberOfPointsValidation() {
    let value = parseInt(document.getElementById("numberOfPoints").value);
    if (isNaN(value)) {
        value = 1;
    } else if (value < 1) {
        value = 1;
    } else if (document.getElementById("newPointDirection").checked && value + trajectories[index_to_edit].positions_rotations_and_boxes[trajectories[index_to_edit].positions_rotations_and_boxes.length - 1].frame >= nr_frames) {
        value = nr_frames - trajectories[index_to_edit].positions_rotations_and_boxes[trajectories[index_to_edit].positions_rotations_and_boxes.length - 1].frame;
    } else if (!document.getElementById("newPointDirection").checked && trajectories[index_to_edit].positions_rotations_and_boxes[0].frame - value < 0) {
        value = trajectories[index_to_edit].positions_rotations_and_boxes[0].frame;
    }

    document.getElementById("numberOfPoints").value = value;
}

/**
 * Handles click on extrapolate button in element descriptor. (Shows form + initialize values + also decides if switch or starting frame input will be shown)
 */
function add_point(event) {
    const trajectory_id = event.target.closest(".elementButtonRegion").getAttribute("data-id");

    let trajectory_index = 0;
    for (let t = 0; t < trajectories.length; t++) {
        if ("id"+trajectories[t].id === trajectory_id) {
            trajectory_index = t;
            break;
        }
    }

    index_to_edit = trajectory_index;

    if (trajectories[index_to_edit].positions_rotations_and_boxes.length == 0) {
        document.getElementById("switchContainer").classList.add("hidden");
        document.getElementById("frameToStart").classList.remove("hidden");
    } else {
        document.getElementById("switchContainer").classList.remove("hidden");
        document.getElementById("frameToStart").classList.add("hidden");
    }

    document.getElementById("numberOfPoints").value = 1;
    document.getElementById("newPointDirection").checked = true;
    document.getElementById("frameToStartInput").value = current_frame;
    document.getElementById("addPointsPopup").classList.remove("hidden");
}

/**
 * Handles click on abort button of the change size from.
 */
function cancel_change_size() {
    document.getElementById("widthInput").value = trajectories[index_to_edit].dimensions[0];
    document.getElementById("lengthInput").value = trajectories[index_to_edit].dimensions[1];
    document.getElementById("heightInput").value = trajectories[index_to_edit].dimensions[2];
    document.getElementById("changeSizePopup").classList.add("hidden");
}

/**
 * Validates size input is a number
 */
function sizeValidation(event) {
    let value = event.target.value;

    if (!/^([0-9]+(\.[0-9]*)?)$/.test(value)) {
        value = 0.0;
    }
    event.target.value = value;

}

/**
 * Handles click on set size button in the element descriptor (Shows form and initialize values)
 */
function set_size(event) {
    const trajectory_id = event.target.closest(".sizeButton").getAttribute("data-id");

    let trajectory_index = 0;
    for (let t = 0; t < trajectories.length; t++) {
        if ("id"+trajectories[t].id === trajectory_id) {
            trajectory_index = t;
            break;
        }
    }
    index_to_edit = trajectory_index;
    document.getElementById("widthInput").value = trajectories[index_to_edit].dimensions[0];
    document.getElementById("lengthInput").value = trajectories[index_to_edit].dimensions[1];
    document.getElementById("heightInput").value = trajectories[index_to_edit].dimensions[2];
    document.getElementById("changeSizePopup").classList.remove("hidden");
}

/**
 * Handles click on submit button of the change size form (applies values and hides form)
 */
function change_size_form_submit() {
    trajectories[index_to_edit].dimensions[0] = document.getElementById("widthInput").value;
    trajectories[index_to_edit].dimensions[1] = document.getElementById("lengthInput").value;
    trajectories[index_to_edit].dimensions[2] = document.getElementById("heightInput").value;
    document.getElementById("id"+trajectories[index_to_edit].id + "size").innerHTML = trajectories[index_to_edit].dimensions[0] + "m * " + trajectories[index_to_edit].dimensions[1] + "m * " + trajectories[index_to_edit].dimensions[2] + "m";
    document.getElementById("changeSizePopup").classList.add("hidden");

    redraw_object_map_object_outlines();
}

/**
 * Handles click on submit button of the create a new element form
 */
function add_new_element_form_submit() {

    /**
     * generates a uuid
     * @returns {string}
     */
    function create_UUID() {
        let dt = new Date().getTime();
        let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            let r = (dt + Math.random() * 16) % 16 | 0;
            dt = Math.floor(dt / 16);
            return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
        return uuid;
    }

    // create trajectory
    let trajectory = {
        "id": create_UUID(),
        "type": document.getElementById("elementType").value,
        "dimensions": [document.getElementById("newWidthInput").value,
            document.getElementById("newLengthInput").value,
            document.getElementById("newHeightInput").value],
        "positions_rotations_and_boxes": []
    }
    trajectories.push(trajectory);
    // push empty line and points to the array to have the indices persistent
    lines.push(L.polyline([], {color: 'rgb(59, 173, 227)', opacity: 0.3}).addTo(map));
    points.push([]);

    // creates the element descriptor
    const divElement = document.createElement("div");
    divElement.id = "id"+trajectory.id;
    divElement.classList.add("element");
    divElement.addEventListener("click", handle_click_element);
    divElement.addEventListener("mouseenter", handle_mouseenter_descriptor);
    divElement.addEventListener("mouseleave", handle_mouseleave_element);

    const elementSVGContainerDiv = document.createElement("div");
    elementSVGContainerDiv.classList.add("elementSVGContainer");
    divElement.appendChild(elementSVGContainerDiv);

    const elementSVGImage = document.createElement("img");
    elementSVGImage.classList.add("svgImg");
    elementSVGImage.src = document.getElementById("elementSelector").getAttribute("data-svg_base_url") + document.getElementById("elementType").value + ".svg";
    elementSVGContainerDiv.appendChild(elementSVGImage);
    SVGInject(elementSVGImage);

    const elementTextParagraph = document.createElement("p");
    elementTextParagraph.classList.add("elementText");
    let type_as_text;
    switch (parseInt(trajectory.type)) {
        case 1:
            type_as_text = "Car";
            break;
        case 2:
            type_as_text = "Truck";
            break;
        case 3:
            type_as_text = "Bus";
            break;
        case 4:
            type_as_text = "Bicycle";
            break;
        case 5:
            type_as_text = "Motorcycle";
            break;
        case 6:
            type_as_text = "Trailer";
            break;
        case 7:
            type_as_text = "Tram";
            break;
        case 8:
            type_as_text = "Train";
            break;
        case 9:
            type_as_text = "Caravan";
            break;
        case 10:
            type_as_text = "Agricultural vehicle";
            break;
        case 11:
            type_as_text = "Construction vehicle";
            break;
        case 12:
            type_as_text = "Emergency vehicle";
            break;
        case 13:
            type_as_text = "Passive vehicle";
            break;
        case 14:
            type_as_text = "Person";
            break;
        case 15:
            type_as_text = "Large animal";
            break;
        case 16:
            type_as_text = "Small animal";
            break;
        default:
            type_as_text = "User defined";
            break;
    }
    elementTextParagraph.innerHTML = type_as_text + "<br/>" + trajectory.id;
    divElement.appendChild(elementTextParagraph);

    const elementSizeSectionDiv = document.createElement("div");
    elementSizeSectionDiv.classList.add("elementSizeSection");
    divElement.appendChild(elementSizeSectionDiv);

    const elementSizeParagraph = document.createElement("p");
    elementSizeParagraph.id = "id"+trajectory.id + "size";
    elementSizeParagraph.classList.add("sizeText");
    elementSizeParagraph.innerHTML = trajectory.dimensions[0] + "m * " + trajectory.dimensions[1] + "m * " + trajectory.dimensions[2] + "m";
    elementSizeSectionDiv.appendChild(elementSizeParagraph);

    const sizeButtonAreaDiv = document.createElement("div");
    sizeButtonAreaDiv.classList.add("sizeButtonArea");
    sizeButtonAreaDiv.innerHTML = "<a type=\"button\" class=\"interactionButton sizeButton \" onclick=\"set_size(event)\">\n" +
        "                                <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 16 16\" fill=\"currentColor\">\n" +
        "                                    <path fill-rule=\"evenodd\"\n" +
        "                                          d=\"M1.464 10.536a.5.5 0 01.5.5v3h3a.5.5 0 010 1h-3.5a.5.5 0 01-.5-.5v-3.5a.5.5 0 01.5-.5z\"\n" +
        "                                          clip-rule=\"evenodd\"/>\n" +
        "                                    <path fill-rule=\"evenodd\"\n" +
        "                                          d=\"M5.964 10a.5.5 0 010 .707l-4.146 4.147a.5.5 0 01-.707-.708L5.257 10a.5.5 0 01.707 0zm8.854-8.854a.5.5 0 010 .708L10.672 6a.5.5 0 01-.708-.707l4.147-4.147a.5.5 0 01.707 0z\"\n" +
        "                                          clip-rule=\"evenodd\"/>\n" +
        "                                    <path fill-rule=\"evenodd\"\n" +
        "                                          d=\"M10.5 1.5A.5.5 0 0111 1h3.5a.5.5 0 01.5.5V5a.5.5 0 01-1 0V2h-3a.5.5 0 01-.5-.5zm4 9a.5.5 0 00-.5.5v3h-3a.5.5 0 000 1h3.5a.5.5 0 00.5-.5V11a.5.5 0 00-.5-.5z\"\n" +
        "                                          clip-rule=\"evenodd\"/>\n" +
        "                                    <path fill-rule=\"evenodd\"\n" +
        "                                          d=\"M10 9.964a.5.5 0 000 .708l4.146 4.146a.5.5 0 00.708-.707l-4.147-4.147a.5.5 0 00-.707 0zM1.182 1.146a.5.5 0 000 .708L5.328 6a.5.5 0 00.708-.707L1.889 1.146a.5.5 0 00-.707 0z\"\n" +
        "                                          clip-rule=\"evenodd\"/>\n" +
        "                                    <path fill-rule=\"evenodd\"\n" +
        "                                          d=\"M5.5 1.5A.5.5 0 005 1H1.5a.5.5 0 00-.5.5V5a.5.5 0 001 0V2h3a.5.5 0 00.5-.5z\"\n" +
        "                                          clip-rule=\"evenodd\"/>\n" +
        "                                </svg>\n" +
        "                            </a>"
    sizeButtonAreaDiv.children[0].setAttribute("data-id", "id"+trajectory.id);
    elementSizeSectionDiv.appendChild(sizeButtonAreaDiv);

    const elementButtonRegionDiv = document.createElement("div");
    elementButtonRegionDiv.classList.add("elementButtonRegion");
    elementButtonRegionDiv.setAttribute("data-id", "id"+trajectory.id);
    elementButtonRegionDiv.innerHTML = "<a type=\"button\" class=\"interactionButton elementButton interpolateButton\" onclick=\"interpolate_points(event)\">\n" +
        "                            <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 16 16\" fill=\"currentColor\">\n" +
        "                                <path fill-rule=\"evenodd\"\n" +
        "                                      d=\"M3.646 14.354a.5.5 0 00.708 0L8 10.707l3.646 3.647a.5.5 0 00.708-.708l-4-4a.5.5 0 00-.708 0l-4 4a.5.5 0 000 .708zm0-12.208a.5.5 0 01.708 0L8 5.793l3.646-3.647a.5.5 0 01.708.708l-4 4a.5.5 0 01-.708 0l-4-4a.5.5 0 010-.708z\"\n" +
        "                                      clip-rule=\"evenodd\"/>\n" +
        "                                <path fill-rule=\"evenodd\" d=\"M8 3a1 1 0 100-2 1 1 0 000 2z\" clip-rule=\"evenodd\"/>\n" +
        "                                <path fill-rule=\"evenodd\" d=\"M8 9.25a1 1 0 100-2 1 1 0 000 2z\" clip-rule=\"evenodd\"/>\n" +
        "                                <path fill-rule=\"evenodd\" d=\"M8 15a1 1 0 100-2 1 1 0 000 2z\" clip-rule=\"evenodd\"/>\n" +
        "                            </svg>\n" +
        "                        </a>\n" +
        "                        <a type=\"button\" class=\"interactionButton elementButton addButton\" onclick=\"add_point(event)\">\n" +
        "                            <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 16 16\" fill=\"currentColor\">\n" +
        "                                <path fill-rule=\"evenodd\" d=\"M3.5 8a.5.5 0 01.5-.5h8a.5.5 0 010 1h-8a.5.5 0 01-.5-.5z\"\n" +
        "                                      clip-rule=\"evenodd\"/>\n" +
        "                                <path fill-rule=\"evenodd\"\n" +
        "                                      d=\"M8 3.5a.5.5 0 01.5.5v4a.5.5 0 01-.5.5H4a.5.5 0 010-1h3.5V4a.5.5 0 01.5-.5z\"\n" +
        "                                      clip-rule=\"evenodd\"/>\n" +
        "                                <path fill-rule=\"evenodd\"\n" +
        "                                      d=\"M7.5 8a.5.5 0 01.5-.5h4a.5.5 0 010 1H8.5V12a.5.5 0 01-1 0V8z\"\n" +
        "                                      clip-rule=\"evenodd\"/>\n" +
        "                            </svg>\n" +
        "                        </a>\n" +
        "                        <a type=\"button\" class=\"interactionButton elementButton\" onclick=\"remove_object(event)\">\n" +
        "                            <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 16 16\" fill=\"currentColor\">\n" +
        "                                <path fill-rule=\"evenodd\"\n" +
        "                                      d=\"M2.5 1a1 1 0 00-1 1v1a1 1 0 001 1H3v9a2 2 0 002 2h6a2 2 0 002-2V4h.5a1 1 0 001-1V2a1 1 0 00-1-1H10a1 1 0 00-1-1H7a1 1 0 00-1 1H2.5zm3 4a.5.5 0 01.5.5v7a.5.5 0 01-1 0v-7a.5.5 0 01.5-.5zM8 5a.5.5 0 01.5.5v7a.5.5 0 01-1 0v-7A.5.5 0 018 5zm3 .5a.5.5 0 00-1 0v7a.5.5 0 001 0v-7z\"\n" +
        "                                      clip-rule=\"evenodd\"/>\n" +
        "                            </svg>\n" +
        "                        </a>\n" +
        "                        <a type=\"button\" class=\"interactionButton elementButton smoothButton\" onclick=\"smooth_object(event)\">\n" +
        "                            <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 16 16\" fill=\"currentColor\">\n" +
        "                                <path fill-rule=\"evenodd\" d=\"M14.39 4.312L10.041 9.75 7 6.707l-3.646 3.647-.708-.708L7 5.293 9.959 8.25l3.65-4.563.781.624z\"/>\n" +
        "                                <path fill-rule=\"evenodd\" d=\"M14.39 4.312L10.041 9.75 7 6.707l-3.646 3.647-.708-.708L7 5.293 9.959 8.25l3.65-4.563.781.624z\"/>\n" +
        "                            </svg>\n" +
        "                        </a>\n" +
        "                        <a type=\"button\" class=\"interactionButton elementButton orientationButton\" onclick=\"set_object_orientation(event)\">\n" +
        "                            <svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 16 16\" fill=\"currentColor\">\n" +
        "                                <path fill-rule=\"evenodd\" d=\"M4 13a1.5 1.5 0 100-3 1.5 1.5 0 000 3z\"\n" +
        "                                      clip-rule=\"evenodd\"/>\n" +
        "                                <path fill-rule=\"evenodd\"\n" +
        "                                      d=\"M6.146 4a.5.5 0 01.5-.5h5a.5.5 0 01.5.5v5a.5.5 0 01-1 0V4.5H6.646a.5.5 0 01-.5-.5z\"\n" +
        "                                      clip-rule=\"evenodd\"/>\n" +
        "                                <path fill-rule=\"evenodd\"\n" +
        "                                      d=\"M12 3.646a.5.5 0 010 .708l-6 6a.5.5 0 01-.708-.708l6-6a.5.5 0 01.708 0z\"\n" +
        "                                      clip-rule=\"evenodd\"/>\n" +
        "                            </svg>\n" +
        "                        </a>"
    let smooth_Button = elementButtonRegionDiv.getElementsByClassName('smoothButton')[0];
    smooth_Button.addEventListener('contextmenu', function(ev) {
        ev.preventDefault();
        gauss_smooth_object(ev);
        return false;
    }, false);
    divElement.appendChild(elementButtonRegionDiv);
    document.getElementById("elementSelector").insertBefore(divElement, document.getElementById("elementSelector").children[document.getElementById("elementSelector").children.length - 1]);

    set_element_colors();
    button_visibility();
    checkDraggablility();

    // hides form + resets values
    document.getElementById("elementType").value = 1;
    document.getElementById("newWidthInput").value = 0.0;
    document.getElementById("newLengthInput").value = 0.0;
    document.getElementById("newHeightInput").value = 0.0;
    document.getElementById("addNewElementPopup").classList.add("hidden");

}

/**
 * Handles click on add new object button in the element selector (Shows form and resets values)
 */
function add_new_object() {
    document.getElementById("elementType").value = 1;
    document.getElementById("newWidthInput").value = 0.0;
    document.getElementById("newLengthInput").value = 0.0;
    document.getElementById("newHeightInput").value = 0.0;
    document.getElementById("addNewElementPopup").classList.remove("hidden");
}

/**
 * Handles click on cancel button of the new object form
 */
function cancel_add_new_element() {
    document.getElementById("elementType").value = 1;
    document.getElementById("newWidthInput").value = 0.0;
    document.getElementById("newLengthInput").value = 0.0;
    document.getElementById("newHeightInput").value = 0.0;
    document.getElementById("addNewElementPopup").classList.add("hidden");
}

/**
 * Handles click on the set orientation button in the element descriptor (draws blue line from object to the mouse and on click calculates the direction)
 */
function set_object_orientation(event) {
    const trajectory_id = event.target.closest(".elementButtonRegion").getAttribute("data-id");
    let trajectory_index = trajectories.findIndex(t => "id"+t.id === trajectory_id);

    var position = trajectories[trajectory_index].positions_rotations_and_boxes[0].position;

    var line = null;
    var point = null;

    map.dragging.disable();
    map.on('mousemove', function (e_move) {

        if (line) {
            line.setLatLngs([position, e_move.latlng]);
            point.setLatLng(e_move.latlng);
        } else {
            line = L.polyline([position, e_move.latlng], {
                color: 'rgb(87, 111, 230)',
                opacity: 1
            }).addTo(map);
            point = L.circle(e_move.latlng, {
                radius: 0.5,
                color: 'rgb(87, 111, 230)'
            }).addTo(map);
        }
    });
    map.on('click', function (e_click) {

        const meter_pos = degree2meter.forward([position[1], position[0]]);
        const meter_click_pos = degree2meter.forward([e_click.latlng.lng, e_click.latlng.lat])

        const x_1 = meter_click_pos[0] - meter_pos[0];
        const y_1 = meter_click_pos[1] - meter_pos[1];

        const scalar_product = (y_1 * 1 + x_1 * 0) / (Math.sqrt(Math.pow(y_1, 2) + Math.pow(x_1, 2)));
        const cross_prod_z = y_1 * 0 - x_1 * 1; // in the end x_1 but for better understanding...
        const rad = Math.sign(cross_prod_z) * Math.acos(scalar_product);
        const degrees = rad / Math.PI * 180;

        for (let p = 0; p < trajectories[trajectory_index].positions_rotations_and_boxes.length; p++) {
            trajectories[trajectory_index].positions_rotations_and_boxes[p].rotation = degrees;
        }

        map.removeLayer(line);
        map.removeLayer(point);

        map.removeEventListener('mousemove');
        map.removeEventListener('click');

        redraw_object_map_object_outlines();
        map.dragging.enable();
    });
}

/**
 * Handles left click on smooth button
 * @param event
 */
function smooth_object(event) {
    const trajectory_id = event.target.closest(".elementButtonRegion").getAttribute("data-id");
    let trajectory_index = trajectories.findIndex(t => "id"+t.id === trajectory_id);

    const xhr = new XMLHttpRequest();
    const theUrl = "/smooth";
    xhr.open("POST", theUrl);
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {

            const json_resp = JSON.parse(xhr.responseText);
            trajectories[trajectory_index] = json_resp;

            update_line(trajectory_index);
            calculate_directions();
            redraw_object_map_object_outlines();
        }

    };
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(trajectories[trajectory_index]));
}

/**
 * Handles right click on smooth button
 * @param event
 */
function gauss_smooth_object(event) {
    const trajectory_id = event.target.closest(".elementButtonRegion").getAttribute("data-id");
    let trajectory_index = trajectories.findIndex(t => "id"+t.id === trajectory_id);

    smooth_trajectory(trajectory_index);
    redraw_object_map_object_outlines();

}

/**
 * Drag and drop stuff
 */
function checkDraggablility(){
    let activate = function(){
        for(let i = 0; i < elements.length; i++) {

            elements[i].removeEventListener("dragstart", dragElementDescriptorStart);
            elements[i].removeEventListener("dragenter", dragElementDescriptorEnter);
            elements[i].removeEventListener("dragleave", dragElementDescriptorLeave);
            //elements[i].addEventListener("dragend", dragEndElementDescriptor);
            elements[i].removeEventListener("dragover", dragoverElementDescriptor);
            elements[i].removeEventListener("drop", dropElementDescriptor);

            elements[i].draggable = true;
            elements[i].addEventListener("dragstart", dragElementDescriptorStart);
            elements[i].addEventListener("dragenter", dragElementDescriptorEnter);
            elements[i].addEventListener("dragleave", dragElementDescriptorLeave);
            //elements[i].addEventListener("dragend", dragEndElementDescriptor);
            elements[i].addEventListener("dragover", dragoverElementDescriptor);
            elements[i].addEventListener("drop", dropElementDescriptor);
        }
    };
    let deactivate = function(){
        for(let i = 0; i < elements.length; i++) {
            elements[i].draggable = false;
            elements[i].removeEventListener("dragstart", dragElementDescriptorStart);
            elements[i].removeEventListener("dragenter", dragElementDescriptorEnter);
            elements[i].removeEventListener("dragleave", dragElementDescriptorLeave);
            //elements[i].removeEventListener("dragend", dragEndElementDescriptor);
            elements[i].removeEventListener("dragover", dragoverElementDescriptor);
            elements[i].removeEventListener("drop", dropElementDescriptor);
        }
    };

    let elements = document.getElementsByClassName("some-element");
    activate();
    elements = document.getElementsByClassName("active-element");
    activate();
    elements = document.getElementsByClassName("empty-element");
    deactivate();
}

function sortElementsByHidden(){
    let selector = document.getElementById("elementSelector");
    [].slice.call(selector.children).sort((a,b) => {
        if(b.classList.contains("hidden")) return -1;
        if(!b.classList.contains("hidden") && a.classList.contains("hidden")) return 1;
        return 0;
    }).forEach(function(val, index) {
        selector.appendChild(val);
    });
    selector.appendChild(document.getElementById("addButtonWrapper"));
}

function dragElementDescriptorStart(ev) {
    //const id = ev.target.closest("div.some-element").id;
    ev.dataTransfer.setData("id", ev.target.id);
    // Timeout needed: https://stackoverflow.com/questions/14203734/dragend-dragenter-and-dragleave-firing-off-immediately-when-i-drag
    setTimeout(function(){
    let elements = document.getElementsByClassName("some-element");
    for (let i = 0; i < elements.length; i++){
        if(ev.target.id != elements[i].id) {
            elements[i].classList.remove("hidden");
            elements[i].classList.add("hint");
        }
    }
    ev.target.addEventListener("dragend", dragEndElementDescriptor);
    }, 1);
}

function dragElementDescriptorEnter(ev) {
    if (ev.target.id != ev.dataTransfer.getData("id")) {
        ev.target.classList.add("active");
        ev.target.classList.remove("hint");
    }
}

function dragElementDescriptorLeave(ev) {
    if (ev.target.id != ev.dataTransfer.getData("id")) {
        ev.target.classList.remove("active");
        ev.target.classList.add("hint");
    }else{
        ev.target.classList.remove("active");
    }
}

function dragEndElementDescriptor(ev){
    let fun = function () {
        for (let i = 0; i < elements.length; i++) {
            elements[i].classList.remove("hint");
            elements[i].classList.remove("active");

            const ti = trajectories.findIndex(t => "id" + t.id === elements[i].id);
            if (ti < 0) {
                continue;
            }
            if (trajectories[ti].positions_rotations_and_boxes.findIndex(prb => prb.frame === current_frame) === -1) {
                elements[i].classList.add("hidden");
            }

        }
    };

    let elements = document.getElementsByClassName("some-element");
    fun();
    elements = document.getElementsByClassName("active-element");
    fun();

    ev.target.removeEventListener("dragend", dragEndElementDescriptor);
    sortElementsByHidden();
}

function dragoverElementDescriptor(ev){
    ev.preventDefault();
}

function dropElementDescriptor(ev) {
    ev.preventDefault();
    const id2 = ev.dataTransfer.getData("id");
    //const id1 = ev.target.id;
    const el = ev.target.closest("div.some-element");
    if(el){
        const id1 = el.id;
        if(id1===id2) {
            return
        }
        if (confirm("You are going to merge object with id " + id2.replace("id","") + " into object with id " + id1.replace("id","") + ". Are you sure that you want to do this?") == true) {
            merge_objects(id1, id2);
        }
    }
    dragEndElementDescriptor();
}