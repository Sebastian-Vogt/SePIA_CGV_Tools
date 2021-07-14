/**
 * Searches the closest point on a line next to a clicked location (Needed for the line callback in point mode to gt the point to manipulate)
 */
function closest_point_on_line(point, line_index) {
    let min_dist = 90 * 90 + 360 * 360;
    let point_index = null;
    for (let p = 0; p < points[line_index].length; p++) {
        const test_point = points[line_index][p]._latlng;
        const dist = Math.pow(test_point.lat - point.lat, 2) + Math.pow(test_point.lng - point.lng, 2);
        if (dist < min_dist) {
            min_dist = dist;
            point_index = p
        }
    }
    return point_index;
}

/**
 * Updates line and point position information (given the index of the line to update)
 */
function update_line(index) {
    lines[index].setLatLngs(trajectories[index].positions_rotations_and_boxes.map(pos_rot_box => pos_rot_box.position));

    for (let p = 0; p < trajectories[index].positions_rotations_and_boxes.length; p++) {
        points[index][p].setLatLng(trajectories[index].positions_rotations_and_boxes[p].position);
    }
}


/**
 * Updates the position information of all lines (but NOT the points)
 */
function correct_lines() {
    for (let l = 0; l < trajectories.length; l++) {
        lines[l].setLatLngs(trajectories[l].positions_rotations_and_boxes.map(pos_rot_box => pos_rot_box.position));
    }
}

function delete_all_lines_and_points(){
    for (let l = 0; l < lines.length; l++) {
        map.removeLayer(lines[l]);
        for (let p = 0; p < points[l].length; p++) {
            map.removeLayer(points[l][p]);
        }
    }
}

function initialize_points_and_lines(){
    // initialize lines and points
    lines = trajectories.map(trajectory => L.polyline(trajectory.positions_rotations_and_boxes.map(position_rotation_and_box => position_rotation_and_box.position), {
        color: ((trajectory.id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)'),
        opacity: 0.3
    }).addTo(map));
    points = trajectories.map(trajectory => trajectory.positions_rotations_and_boxes.sort(
        function (a, b) {
            return parseInt(a) - parseInt(b)
        }
    ).map(position_rotation_and_box => L.circle(position_rotation_and_box.position, {
        radius: 0.5,
        color: 'rgb(247, 76, 67)'
    }).addTo(map)));

    // initialize mouse handlers
    for (let l = 0; l < lines.length; l++) {
        lines[l].trajectory_id = trajectories[l].id;
        lines[l].line_index = l;
        lines[l].addEventListener("mousedown", line_mousedown_function);
        lines[l].addEventListener("mouseover", handle_mouseenter_line);
        lines[l].addEventListener("mouseout", handle_mouseleave_line);
        for (let p = 0; p < points[l].length; p++) {
            points[l][p].trajectory_id = trajectories[l].id;
            points[l][p].line_index = l;
            points[l][p].point_index = p;
            points[l][p].addEventListener("mousedown", point_mousedown_function);
            points[l][p].addEventListener("mouseover", handle_mouseenter_point);
            points[l][p].addEventListener("mouseout", handle_mouseleave_point);
        }
    }

    set_circle_colors();
}

/**
 * Handles mouse down on point. (Set selection according to selection mode -> pass to handle action)
 */
function point_mousedown_function(e) {
    map.dragging.disable();

    switch (selection_mode) {
        case "point":
            selection = [[e.target.line_index, e.target.point_index]];
            break;
        case "line":
            selection = [];
            for (let i = 0; i < points[e.target.line_index].length; i++) {
                selection.push([e.target.line_index, i]);
            }
            break;
        case "all":
            selection = [];
            for (let l = 0; l < points.length; l++) {
                for (let p = 0; p < points[l].length; p++) {
                    selection.push([l, p]);
                }
            }
            break;
        default:
            break;
    }

    handle_action(e);
}

/**
 * Handles mouse down on line. (Set selection according to selection mode -> pass to handle action)
 */
function line_mousedown_function(e) {
    map.dragging.disable();

    switch (selection_mode) {
        case "point":
            const point_index = closest_point_on_line(e.latlng, e.target.line_index);
            selection = [[e.target.line_index, point_index]];
            break;
        case "line":
            selection = [];
            for (let i = 0; i < points[e.target.line_index].length; i++) {
                selection.push([e.target.line_index, i]);
            }
            break;
        case "all":
            selection = [];
            for (let l = 0; l < points.length; l++) {
                for (let p = 0; p < points[l].length; p++) {
                    selection.push([l, p]);
                }
            }
            break;
        default:
            break;
    }

    handle_action(e);
}

/**
 * Passes to handle function of active action
 */
function handle_action(e) {

    switch (action_mode) {
        case "move":
            handle_move(e);
            break;
        case "scale":
            handle_scale(e);
            break;
        case "rotate":
            handle_rotate(e);
            break;
        case "collapse":
            handle_collapse(e);
            break;
        case "remove":
            handle_remove(e);
            break;
    }

}

/**
 * Handles the move action of a selection
 */
function handle_move(e) {

    // position of the mouse on movement start
    const old_pos = e.latlng;

    // copies old position to be able to generate relative movement
    const old_trajectories = [];
    for (let t = 0; t < trajectories.length; t++) {
        old_trajectories.push(trajectories[t].positions_rotations_and_boxes.map(a => ({...a})));
    }

    map.on('mousemove', function (f) {
        // current mouse position
        const new_pos = f.latlng;

        //calculate relative movement
        const diff = [new_pos.lat - old_pos.lat, new_pos.lng - old_pos.lng];

        let lat = 0;
        let long = 0;

        // only update position information on lines that have changed
        let last_line_index = -1;
        for (let selection_index = 0; selection_index < selection.length; selection_index++) {
            if (selection[selection_index][0] != last_line_index && last_line_index >= 0) {
                update_line(last_line_index);
            }
            trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position = [old_trajectories[selection[selection_index][0]][selection[selection_index][1]].position[0] + diff[0], old_trajectories[selection[selection_index][0]][selection[selection_index][1]].position[1] + diff[1]];

            // to update center marker
            lat += trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position[0];
            long += trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position[1];

            last_line_index = selection[selection_index][0];
        }
        update_line(selection[selection.length - 1][0]);


        // update center marker
        lat /= selection.length;
        long /= selection.length;
        if (map.hasLayer(center_marker)) {
            map.removeLayer(center_marker);
        }
        center_marker.setLatLng(new L.LatLng(lat, long));
        if (action_mode != "move") {
            center_marker.addTo(map);
        }

        // update object outlines
        calculate_directions();
        redraw_object_map_object_outlines();
        // and button visibility (i.e. set direction button)
        button_visibility();
    });
    map.on('mouseup', function (e) {

        for (let selection_index = 0; selection_index < selection.length; selection_index++) {
            trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].specified = true;
        }

        to_be_interpolated_trajectories = Array.from(new Set(selection.map(x => x[0])))
        for (let index = 0; index < to_be_interpolated_trajectories.length; index++) {
            if(selection_mode == "point" || selection_mode == "selection"){
                if(selection_mode == "selection" && selection.filter(s => s[0] == to_be_interpolated_trajectories[index]).length == trajectories[to_be_interpolated_trajectories[index]].positions_rotations_and_boxes.length){
                    continue;
                }
                interpolateTrajectory(to_be_interpolated_trajectories[index], function(){
                    button_visibility();
                    redraw_object_map_object_outlines();
                    set_circle_colors();
                    draw_boxes();}
                );
            }
        }

        button_visibility();
        redraw_object_map_object_outlines();
        set_circle_colors();
        draw_boxes();

        // remove eventlistener otherwise they would stack
        map.removeEventListener('mousemove');
        map.removeEventListener('mouseup');

        map.dragging.enable();
        // update save button
        if (!changes) {
            changes = true;
            updateSaveButton();
        }
    });
}

/**
 * Handles the rotation of a selection
 */
function handle_rotate(e) {

    // not defined for points
    if (selection_mode == "point") {
        return;
    }

    // rotation center == center of mass
    const center = center_marker.getLatLng();
    const meter_center = degree2meter.forward([center.lng, center.lat]);    // needs to be in metric system
    const meter_start_pos = degree2meter.forward([e.latlng.lng, e.latlng.lat])  // position of mouse on mousedown
    const rel_start_y = meter_start_pos[1] - meter_center[1];
    const rel_start_x = meter_start_pos[0] - meter_center[0];

    // copies old position to be able to apply relative position
    const start_trajectories = [];
    for (let t = 0; t < trajectories.length; t++) {
        start_trajectories.push(trajectories[t].positions_rotations_and_boxes.map(a => ({...a})));
    }

    map.on('mousemove', function (f) {
        const new_pos = f.latlng;   //current mouse position
        const meter_new = degree2meter.forward([new_pos.lng, new_pos.lat]);
        const rel_new_y = meter_new[1] - meter_center[1];
        const rel_new_x = meter_new[0] - meter_center[0];

        // calculate angle between starting and end point and center of mass (scalar product + direction of angle by cross product)
        const scalar_product = (rel_new_y * rel_start_y + rel_start_x * rel_new_x) / (Math.sqrt(Math.pow(rel_start_y, 2) + Math.pow(rel_start_x, 2)) * Math.sqrt(Math.pow(rel_new_y, 2) + Math.pow(rel_new_x, 2)));
        const cross_prod_z = rel_new_y * rel_start_x - rel_new_x * rel_start_y;
        const rad = Math.sign(-cross_prod_z) * Math.acos(scalar_product);
        const sin_rad = Math.sin(rad);
        const cos_rad = Math.cos(rad);

        // update only lines that changed
        let last_line_index = -1;
        for (let selection_index = 0; selection_index < selection.length; selection_index++) {
            if (selection[selection_index][0] != last_line_index && last_line_index >= 0) {
                update_line(last_line_index);
            }
            const current_xy = degree2meter.forward([start_trajectories[selection[selection_index][0]][selection[selection_index][1]].position[1], start_trajectories[selection[selection_index][0]][selection[selection_index][1]].position[0]]);

            const rel_y = current_xy[1] - meter_center[1];
            const rel_x = current_xy[0] - meter_center[0];

            const res_rel_y = cos_rad * rel_y - sin_rad * rel_x;
            const res_rel_x = sin_rad * rel_y + cos_rad * rel_x;

            const res_y = meter_center[1] + res_rel_y;
            const res_x = meter_center[0] + res_rel_x;

            const new_pos = degree2meter.inverse([res_x, res_y]);

            trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position = [new_pos[1], new_pos[0]];
            last_line_index = selection[selection_index][0];
        }
        update_line(selection[selection.length - 1][0]);

        // update object outlines
        calculate_directions();
        redraw_object_map_object_outlines();
        // and button visibility (i.e. set direction button)
        button_visibility();

    });
    map.on('mouseup', function (e) {

        for (let selection_index = 0; selection_index < selection.length; selection_index++) {
            trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].specified = true;
        }

        to_be_interpolated_trajectories = Array.from(new Set(selection.map(x => x[0])))
        for (let index = 0; index < to_be_interpolated_trajectories.length; index++) {
            if(selection_mode == "point" || selection_mode == "selection"){
                if(selection_mode == "selection" && selection.filter(s => s[0] == to_be_interpolated_trajectories[index]).length == trajectories[to_be_interpolated_trajectories[index]].positions_rotations_and_boxes.length){
                    continue;
                }
                interpolateTrajectory(to_be_interpolated_trajectories[index], function(){
                    button_visibility();
                    redraw_object_map_object_outlines();
                    set_circle_colors();
                    draw_boxes();}
                );
            }
        }

        button_visibility();
        redraw_object_map_object_outlines();
        set_circle_colors();
        draw_boxes();

        // remove eventlistener otherwise they would stack
        map.removeEventListener('mousemove');
        map.removeEventListener('mouseup');

        map.dragging.enable();

        // update save button
        if (!changes) {
            changes = true;
            updateSaveButton();
        }
    });
}

/**
 * Handles scaling of a selection
 */
function handle_scale(e) {

    // not defined for points
    if (selection_mode == "point") {
        return;
    }

    // scale center == center of mass
    const center = center_marker.getLatLng();
    const start_pos = e.latlng; // position of mouse on mousedown
    const rel_start_lat = start_pos.lat - center.lat;
    const rel_start_long = start_pos.lng - center.lng;

    // copies old position to be able to apply relative position
    const start_trajectories = [];
    for (let t = 0; t < trajectories.length; t++) {
        start_trajectories.push(trajectories[t].positions_rotations_and_boxes.map(a => ({...a})));
    }

    map.on('mousemove', function (f) {
        // current position of mouse
        const new_pos = f.latlng;
        const rel_new_lat = new_pos.lat - center.lat;
        const rel_new_long = new_pos.lng - center.lng;

        // scale factors for each direction
        const lat_scale_factor = rel_new_lat / rel_start_lat;
        const long_scale_factor = rel_new_long / rel_start_long;

        // only update lines that have changed
        let last_line_index = -1;
        for (let selection_index = 0; selection_index < selection.length; selection_index++) {
            if (selection[selection_index][0] != last_line_index && last_line_index >= 0) {
                update_line(last_line_index);
            }

            const lat = start_trajectories[selection[selection_index][0]][selection[selection_index][1]].position[0] - center.lat;
            const long = start_trajectories[selection[selection_index][0]][selection[selection_index][1]].position[1] - center.lng;

            const res_lat = lat_scale_factor * lat;
            const res_long = long_scale_factor * long;

            trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position = [res_lat + center.lat, res_long + center.lng];
            last_line_index = selection[selection_index][0];
        }
        update_line(selection[selection.length - 1][0]);

        // update object outlines
        calculate_directions();
        redraw_object_map_object_outlines();
        // and button visibility (i.e. set direction button)
        button_visibility();
    });
    map.on('mouseup', function (e) {

        for (let selection_index = 0; selection_index < selection.length; selection_index++) {
            trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].specified = true;
        }

        to_be_interpolated_trajectories = Array.from(new Set(selection.map(x => x[0])))
        for (let index = 0; index < to_be_interpolated_trajectories.length; index++) {
            if(selection_mode == "point" || selection_mode == "selection"){
                if(selection_mode == "selection" && selection.filter(s => s[0] == to_be_interpolated_trajectories[index]).length == trajectories[to_be_interpolated_trajectories[index]].positions_rotations_and_boxes.length){
                    continue;
                }
                interpolateTrajectory(to_be_interpolated_trajectories[index], function(){
                    button_visibility();
                    redraw_object_map_object_outlines();
                    set_circle_colors();
                    draw_boxes();}
                );
            }
        }

        button_visibility();
        redraw_object_map_object_outlines();
        set_circle_colors();
        draw_boxes();

        // remove eventlistener otherwise they would stack
        map.removeEventListener('mousemove');
        map.removeEventListener('mouseup');

        map.dragging.enable();

        // update save button
        if (!changes) {
            changes = true;
            updateSaveButton();
        }
    });
}

/**
 * Handles collapse of a selection
 */
function handle_collapse(e) {
    // not defined for points
    if (selection_mode == "point") {
        return;
    }

    // all points are set to center of mass
    const center = center_marker.getLatLng();

    // only update lines that have changed
    let last_line_index = -1;
    for (let selection_index = 0; selection_index < selection.length; selection_index++) {
        if (selection[selection_index][0] != last_line_index && last_line_index >= 0) {
            update_line(last_line_index);
        }

        trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position = [center.lat, center.lng];
        last_line_index = selection[selection_index][0];
    }
    update_line(selection[selection.length - 1][0]);

    // update object outlines
    calculate_directions();
    redraw_object_map_object_outlines();
    // and button visibility (i.e. set direction button)
    button_visibility();

    map.on('mouseup', function (e) {

        for (let selection_index = 0; selection_index < selection.length; selection_index++) {
            trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].specified = true;
        }

        to_be_interpolated_trajectories = Array.from(new Set(selection.map(x => x[0])))
        for (let index = 0; index < to_be_interpolated_trajectories.length; index++) {
            interpolateTrajectory(to_be_interpolated_trajectories[index], function(){
                button_visibility();
                redraw_object_map_object_outlines();
                set_circle_colors();
                draw_boxes();
            });
        }

        // remove eventlistener otherwise they would stack
        map.removeEventListener('mouseup');

        map.dragging.enable();

        // update save button
        if (!changes) {
            changes = true;
            updateSaveButton();
        }
    });

}

/**
 * Handles collapse of a selection
 */
function handle_remove(e) {
    map.on('mouseup', function (e) {

        let current_line_index = -1;
        let index_offset = 0;   // when deleting one point all following points are moved by one index -> this variable deals with this offset
        let line_indicies = [];
        // for each point in the selection: remove from map and trajectory + store changed line indices
        for (let selection_index = 0; selection_index < selection.length; selection_index++) {
            if (current_line_index != selection[selection_index][0]) {
                current_line_index = selection[selection_index][0];
                line_indicies.push(current_line_index);
                index_offset = 0;
            }
            trajectories[selection[selection_index][0]].positions_rotations_and_boxes.splice(selection[selection_index][1] - index_offset, 1);
            map.removeLayer(points[selection[selection_index][0]][selection[selection_index][1] - index_offset]);
            points[selection[selection_index][0]].splice(selection[selection_index][1] - index_offset, 1);
            index_offset += 1;
        }

        // update changed lines
        for (let line_index = 0; line_index < line_indicies.length; line_index++) {
            const l = line_indicies[line_index];
            map.removeLayer(lines[l]);

            lines[l] = L.polyline(trajectories[l].positions_rotations_and_boxes.map(position_rotation_and_box => position_rotation_and_box.position), {
                color: ((trajectories[l].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)'),
                opacity: 0.3
            }).addTo(map);

            lines[l].trajectory_id = trajectories[l].id;
            lines[l].line_index = l;
            lines[l].addEventListener("mousedown", line_mousedown_function);
            lines[l].addEventListener("mouseover", handle_mouseenter_line);
            lines[l].addEventListener("mouseout", handle_mouseleave_line);

            // update point indexes in those lines points (Because the whole object does not get deleted, the lines are still there, but empty when completely deleted. Therefore the line indices stay correct)
            for (let p = 0; p < points[l].length; p++) {
                points[l][p].point_index = p;
            }

        }

        selection = [];
        map.removeEventListener('mouseup');

        calculate_directions();
        redraw_object_map_object_outlines();

        button_visibility();

        map.dragging.enable();

        // update save button
        if (!changes) {
            changes = true;
            updateSaveButton();
        }
    });
}


/**
 * Packs successive list elements of the same value into a list.
 * I.e: [1,1,1,2,2,3,2,4] => [[1,1,1],[2,2],[3],[2],[4]]
 *
 * @param unpacked_list (list to pack)
 * @param compare_lambda (function used to compare two list elements. Needs to take the 2 arguments to compare and to return true if they are equal and false otherwise)
 * @param element_lambda (function to specify output. I.e. instead of element them self give out index in input list. I.e: [1,1,1,2,2,3,2,4] => [[0,1,2],[3,4],[5],[6],[7]]. Needs to take element and list index and return the output value of some arbitrary type.)
 * @returns [[]]
 */
function pack(unpacked_list, compare_lambda, element_lambda) {
    if (unpacked_list.length == 0)
        return [];
    let packed_list = [];
    let current_package = [element_lambda(unpacked_list, 0)];
    let previous_element = unpacked_list[0];
    for (let i = 1; i < unpacked_list.length; i++) {
        if (compare_lambda(previous_element, unpacked_list[i])) {
            current_package.push(element_lambda(unpacked_list, i));
        } else {
            packed_list.push(current_package);
            current_package = [element_lambda(unpacked_list, i)];
        }
        previous_element = unpacked_list[i];
    }
    packed_list.push(current_package);
    return packed_list
}

/**
 * Calculates the directions for all the points in all trajectories (and updates them in the trajectories).
 * Uses central difference if possible.
 * When multiple successive elements share the same position -> calculate central difference with the next points who dont share the same position
 * Direction is measured in ° from north direction.
 */
function calculate_directions() {
    for (let t = 0; t < trajectories.length; t++) {
        let packed_indices = pack(// this makes further processing much easier
            trajectories[t].positions_rotations_and_boxes,
            ((a, b) => a.position[0] == b.position[0] && a.position[1] == b.position[1]), // compare by position
            ((l, i) => i) // give out index
        );
        let previous_index, next_index;
        for (let current_index = 0; current_index < packed_indices.length; current_index++) {
            previous_index = current_index;
            let temp_pos = trajectories[t].positions_rotations_and_boxes[packed_indices[previous_index][0]].position;
            let previous_pos = degree2meter.forward([temp_pos[1], temp_pos[0]]);
            temp_pos = trajectories[t].positions_rotations_and_boxes[packed_indices[current_index][0]].position;
            let current_pos = degree2meter.forward([temp_pos[1], temp_pos[0]]);
            while(Math.sqrt(Math.pow(previous_pos[0]-current_pos[0],2)+Math.pow(previous_pos[1]-current_pos[1], 2)) < 0.2 && previous_index>0){
                previous_index -= 1;
                let temp_pos = trajectories[t].positions_rotations_and_boxes[packed_indices[previous_index][0]].position;
                previous_pos = degree2meter.forward([temp_pos[1], temp_pos[0]]);
            }
            next_index = current_index
            temp_pos = trajectories[t].positions_rotations_and_boxes[packed_indices[next_index][0]].position
            let next_pos = degree2meter.forward([temp_pos[1], temp_pos[0]]);
            while(Math.sqrt(Math.pow(next_pos[0]-current_pos[0],2)+Math.pow(next_pos[1]-current_pos[1], 2)) < 0.2 && next_index < packed_indices.length - 1){
                next_index += 1;
                let temp_pos = trajectories[t].positions_rotations_and_boxes[packed_indices[next_index][0]].position;
                next_pos = degree2meter.forward([temp_pos[1], temp_pos[0]]);
            }

            let direction;

            if (previous_pos[0] == next_pos[0] && previous_pos[1] == next_pos[1]) {// if previous and next position are the same
                if (previous_pos[0] == current_pos[0] && previous_pos[1] == current_pos[1]) {// and current position is the same too -> no gradient can be calculated
                    window.console.log("previous_position == current_position == next_position => no gradient calculatable.");

                    let flag = true;
                    let first = trajectories[t].positions_rotations_and_boxes[packed_indices[current_index][0]].rotation;
                    for (let i = 1; i < packed_indices[current_index].length; i++) {
                        if (trajectories[t].positions_rotations_and_boxes[packed_indices[current_index][i]].rotation != first) {
                            flag = false;
                            break;
                        }
                    }
                    if (flag) {
                        continue;
                    }
                    for (let i = 0; i < packed_indices[current_index].length; i++) {
                        trajectories[t].positions_rotations_and_boxes[packed_indices[current_index][i]].rotation = 0;
                    }
                    continue;
                } else {// if current position is unequal -> forward + 180°turn + back to start -> direction to forward + 90° turn => snapshot on  half turn
                    direction = [current_pos[0] - previous_pos[0], current_pos[1] - previous_pos[1]];
                    direction = [-direction[1], direction[0]]; // inverse reciprocal <= + 90°
                }
            } else {
                direction = [next_pos[0] - previous_pos[0], next_pos[1] - previous_pos[1]];
            }

            // simple 2d rotation by angle
            const scalar_product = (direction[1] * 1 + direction[0] * 0) / (Math.sqrt(Math.pow(direction[1], 2) + Math.pow(direction[0], 2)));
            const cross_prod_z = direction[1] * 0 - direction[0] * 1; // zdimension of the cross product. In the end just direction[0] but for better understanding...
            const rad = Math.sign(cross_prod_z) * Math.acos(scalar_product);
            const degrees = rad / Math.PI * 180;

            for (let i = 0; i < packed_indices[current_index].length; i++) {
                trajectories[t].positions_rotations_and_boxes[packed_indices[current_index][i]].rotation = degrees;
            }

        }
    }
}

/**
 * Draws top projection outline polygons of objects (complete redraw on any change => could be improved)
 */
function redraw_object_map_object_outlines() {
    // removes old ones
    for (let o = 0; o < map_object_outlines.length; o++) {
        map.removeLayer(map_object_outlines[o]);
    }
    map_object_outlines = [];
    // drawes new ones
    for (let t = 0; t < trajectories.length; t++) {
        if ("dimensions" in trajectories[t]) {

            for (let p = 0; p < trajectories[t].positions_rotations_and_boxes.length; p++) {
                if (trajectories[t].positions_rotations_and_boxes[p].frame == current_frame && "rotation" in trajectories[t].positions_rotations_and_boxes[p]) {
                    const position_wgs84 = trajectories[t].positions_rotations_and_boxes[p].position;
                    const center = degree2meter.forward([position_wgs84[1], position_wgs84[0]]);
                    const rad = -trajectories[t].positions_rotations_and_boxes[p].rotation / 180 * Math.PI;
                    const sin_rad = Math.sin(rad);
                    const cos_rad = Math.cos(rad);

                    let left_front, right_front, left_back, right_back;

                    if (trajectories[t].id === 0 && "camera_position" in trajectories[t]) {    // for self object find correct camera location -> point in polygon should match camera position
                        left_front = [-trajectories[t].camera_position[0], trajectories[t].camera_position[1]];                                                                       //  left_front ---- north/y ---- right_front
                        right_front = [-trajectories[t].camera_position[0] + trajectories[t].dimensions[0], trajectories[t].camera_position[1]];                                      //      |                               |
                        left_back = [-trajectories[t].camera_position[0], trajectories[t].camera_position[1] - trajectories[t].dimensions[1]];                                        //      |             0              east/x
                        right_back = [-trajectories[t].camera_position[0] + trajectories[t].dimensions[0], trajectories[t].camera_position[1] - trajectories[t].dimensions[1]];       //      |                               |
                                                                                                                                                                                      //  left_back ------------------ right_back
                    } else {
                        left_front = [-0.5 * trajectories[t].dimensions[0], 0.5 * trajectories[t].dimensions[1]];     //  left_front ---- north/y ---- right_front
                        right_front = [0.5 * trajectories[t].dimensions[0], 0.5 * trajectories[t].dimensions[1]];     //      |                               |
                        left_back = [-0.5 * trajectories[t].dimensions[0], -0.5 * trajectories[t].dimensions[1]];     //      |             0              east/x
                        right_back = [0.5 * trajectories[t].dimensions[0], -0.5 * trajectories[t].dimensions[1]];     //      |                               |
                                                                                                                      //  left_back ------------------ right_back
                    }

                    // basic 2d rotation:
                    // x = sin(a) * y + cos(a) * x
                    // y = cos(a) * y - sin(a) * x
                    const rotated_left_front = [sin_rad * left_front[1] + cos_rad * left_front[0], cos_rad * left_front[1] - sin_rad * left_front[0]];
                    const rotated_right_front = [sin_rad * right_front[1] + cos_rad * right_front[0], cos_rad * right_front[1] - sin_rad * right_front[0]];
                    const rotated_left_back = [sin_rad * left_back[1] + cos_rad * left_back[0], cos_rad * left_back[1] - sin_rad * left_back[0]];
                    const rotated_right_back = [sin_rad * right_back[1] + cos_rad * right_back[0], cos_rad * right_back[1] - sin_rad * right_back[0]];

                    // before relative to 0,0 -> relative to center
                    left_front[0] = rotated_left_front[0] + center[0];
                    left_front[1] = rotated_left_front[1] + center[1];
                    right_front[0] = rotated_right_front[0] + center[0];
                    right_front[1] = rotated_right_front[1] + center[1];
                    left_back[0] = rotated_left_back[0] + center[0];
                    left_back[1] = rotated_left_back[1] + center[1];
                    right_back[0] = rotated_right_back[0] + center[0];
                    right_back[1] = rotated_right_back[1] + center[1];

                    const left_front_wgs84 = degree2meter.inverse(left_front);
                    const right_front_wgs84 = degree2meter.inverse(right_front);
                    const left_back_wgs84 = degree2meter.inverse(left_back);
                    const right_back_wgs84 = degree2meter.inverse(right_back);

                    map_object_outlines.push(L.polygon([[left_front_wgs84[1], left_front_wgs84[0]], [right_front_wgs84[1], right_front_wgs84[0]], [right_back_wgs84[1], right_back_wgs84[0]], [left_back_wgs84[1], left_back_wgs84[0]]], {color: '#fffb14'}).addTo(map));

                    break;  // dont search other frames behind current one
                }
            }
        }
    }
    // this is to pass mouse events to underlying points
    for (let m = 0; m < map_object_outlines.length; m++) {
        map_object_outlines[m]._path.classList.add("objectOutline");
    }
}

function smooth_trajectory(index) {

    let lats = [];
    let longs = [];
    for (let p = 0; p < trajectories[index].positions_rotations_and_boxes.length; p++) {
        lats.push(trajectories[index].positions_rotations_and_boxes[p].position[0]);
        longs.push(trajectories[index].positions_rotations_and_boxes[p].position[1]);
    }

    let kernel = gaussianKernel1d(9, 1.0);
    let first_lats = Array(4).fill(lats[0]);
    let last_lats = Array(4).fill(lats[lats.length-1]);
    let first_longs = Array(4).fill(longs[0]);
    let last_longs = Array(4).fill(longs[longs.length-1]);

    let temp_lats = first_lats.concat(lats.concat(last_lats));
    let temp_longs = first_longs.concat(longs.concat(last_longs));

    for(let i = 0; i < lats.length; i++){
        lats[i] = 0;
        longs[i] = 0;
        for(let k = 0; k < kernel.length; k++){
            lats[i] += kernel[k] * temp_lats[i+k];
            longs[i] += kernel[k] * temp_longs[i+k];
        }
    }

    for (let p = 0; p < trajectories[index].positions_rotations_and_boxes.length; p++) {
        trajectories[index].positions_rotations_and_boxes[p].position[0] = lats[p];
        trajectories[index].positions_rotations_and_boxes[p].position[1] = longs[p];
    }

    update_line(index);
    calculate_directions();

}

function gaussianKernel1d(size, sigma) {
    var sqr2pi = Math.sqrt(2 * Math.PI);

    // ensure size is even and prepare variables
    var width = (size / 2) | 0,
        kernel = new Array(width * 2 + 1),
        norm = 1.0 / (sqr2pi * sigma),
        coefficient = 2 * sigma * sigma,
        total = 0,
        x;

    // set values and increment total
    for (x = -width; x <= width; x++) {
        total += kernel[width + x] = norm * Math.exp(-x * x / coefficient);
    }

    // divide by total to make sure the sum of all the values is equal to 1
    for (x = 0; x < kernel.length; x++) {
        kernel[x] /= total;
    }

    return kernel;
}

function interpolateTrajectory(index, callback_f){

    const xhr = new XMLHttpRequest();
    const theUrl = "/interpolate";
    xhr.open("POST", theUrl);
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {

            const json_resp = JSON.parse(xhr.responseText);
            trajectories[index] = json_resp;

            // remove old line and replace it with the new one + setting callbacks

            map.removeLayer(lines[index]);

            lines[index] = L.polyline(trajectories[index].positions_rotations_and_boxes.map(position_rotation_and_box => position_rotation_and_box.position), {
                color: ((trajectories[index].id === 0) ? 'rgb(247, 76, 67)' : 'rgb(59, 173, 227)'),
                opacity: 0.3
            }).addTo(map);

            lines[index].trajectory_id = trajectories[index].id;
            lines[index].line_index = index;
            lines[index].addEventListener("mousedown", line_mousedown_function);
            lines[index].addEventListener("mouseover", handle_mouseenter_line);
            lines[index].addEventListener("mouseout", handle_mouseleave_line);

            // remove old points of interpolated trajectory and replace it with the new one + setting callbacks

            for (let p = 0; p < trajectories[index].positions_rotations_and_boxes.length; p++) {
                if (p >= points[index].length) {
                    points[index].push(L.circle(
                        new L.LatLng(trajectories[index].positions_rotations_and_boxes[p].position[0],
                            trajectories[index].positions_rotations_and_boxes[p].position[1]),
                        {
                            radius: 0.5,
                            color: 'rgb(59, 173, 227)'
                        }
                    ).addTo(map));
                } else {
                    map.removeLayer(points[index][p]);
                    points[index][p] = L.circle(
                        new L.LatLng(trajectories[index].positions_rotations_and_boxes[p].position[0],
                            trajectories[index].positions_rotations_and_boxes[p].position[1]),
                        {
                            radius: 0.5,
                            color: 'rgb(59, 173, 227)'
                        }
                    ).addTo(map);
                }

                points[index][p].line_index = index;
                points[index][p].point_index = p;
                points[index][p].addEventListener("mousedown", point_mousedown_function);
                points[index][p].addEventListener("mouseover", handle_mouseenter_point);
                points[index][p].addEventListener("mouseout", handle_mouseleave_point);
            }
            callback_f();
        }

    };
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(trajectories[index]));


}