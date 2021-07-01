
/**
 * Goes over all points and sets the correct colors and opacities for them. (highlight/current/self/opponent)
 */
function set_circle_colors() {

    try{
        for (let l = 0; l < points.length; l++) {
            for (let p = 0; p < points[l].length; p++) {
                let point_color = "rgb(255,255,255)";
                let point_opacity = 1.0;
                if (selection.filter(el => el[0] == l && el[1] == p).length > 0 && highlight.length == 0 || highlight.filter(el => el[0] == l && el[1] == p).length > 0) {
                    point_opacity = 1.0;
                    try {
                        if (trajectories[l].positions_rotations_and_boxes[p].detected || trajectories[l].positions_rotations_and_boxes[p].specified){
                            point_color = 'rgb(61, 227, 105)';
                        }
                        else {
                            point_color = 'rgb(41, 153, 71)';
                        }
                    }
                    catch (e){
                        point_color = 'rgb(41, 153, 71)';
                    }
                    if (current_frame < trajectories[l].positions_rotations_and_boxes[p].frame) {
                        point_opacity = 0.2;
                    }
                } else if (trajectories[l].id === 0) {

                    point_opacity = 1.0;
                    if (current_frame == trajectories[l].positions_rotations_and_boxes[p].frame) {
                        try {
                            if (trajectories[l].positions_rotations_and_boxes[p].detected || trajectories[l].positions_rotations_and_boxes[p].specified) {
                                point_color = 'rgb(255, 251, 20)';
                            } else {
                                point_color = 'rgb(204, 201, 16)';
                            }
                        }
                        catch (e){
                            point_color = 'rgb(204, 201, 16)';
                        }
                    } else if (current_frame > trajectories[l].positions_rotations_and_boxes[p].frame) {
                        point_opacity = 1.0;
                        try {
                            if (trajectories[l].positions_rotations_and_boxes[p].detected || trajectories[l].positions_rotations_and_boxes[p].specified) {
                                point_color = 'rgb(247, 76, 67)';
                            } else {
                                point_color = 'rgb(173, 53, 47)';
                            }
                        }
                        catch (e){
                            point_color = 'rgb(173, 53, 47)';
                        }
                    } else {
                        point_opacity = 0.2;
                        try {
                            if (trajectories[l].positions_rotations_and_boxes[p].detected || trajectories[l].positions_rotations_and_boxes[p].specified) {
                                point_color = 'rgb(247, 76, 67)';
                            } else {
                                point_color = 'rgb(173, 53, 47)';
                            }
                        }
                        catch (e){
                            point_color = 'rgb(173, 53, 47)';
                        }
                    }
                } else {
                    if (current_frame == trajectories[l].positions_rotations_and_boxes[p].frame) {
                        point_opacity = 1.0;
                        try {
                            if (trajectories[l].positions_rotations_and_boxes[p].detected || trajectories[l].positions_rotations_and_boxes[p].specified) {
                                point_color = 'rgb(255, 251, 20)';
                            } else {
                                point_color = 'rgb(204, 201, 16)';
                            }
                        }
                        catch (e){
                            point_color = 'rgb(204, 201, 16)';
                        }
                    } else if (current_frame > trajectories[l].positions_rotations_and_boxes[p].frame) {
                        point_opacity = 1.0;
                        try {
                            if (trajectories[l].positions_rotations_and_boxes[p].detected || trajectories[l].positions_rotations_and_boxes[p].specified) {
                                point_color = 'rgb(59, 173, 227)';
                            } else {
                                point_color = 'rgb(27, 78, 102)';
                            }
                        }
                        catch (e){
                            point_color = 'rgb(27, 78, 102)';
                        }
                    } else {
                        point_opacity = 0.2;
                        try {
                            if (trajectories[l].positions_rotations_and_boxes[p].detected || trajectories[l].positions_rotations_and_boxes[p].specified) {
                                point_color = 'rgb(59, 173, 227)';
                            } else {
                                point_color = 'rgb(27, 78, 102)';
                            }
                        }
                        catch (e){
                            point_color = 'rgb(27, 78, 102)';
                        }
                    }
                }
                points[l][p].setStyle({color: point_color, opacity: point_opacity});
            }
        }
    } catch (error) {

    }
}

/**
 * Goes over all lines and sets their correct color (self/opponent).
 */
function set_line_colors() {
    try{
        for (let t = 0; t < trajectories.length; t++) {
            if (trajectories[t].id === 0) {
                lines[t].setStyle({color: 'rgb(247, 76, 67)', opacity: 0.3});
            } else {
                lines[t].setStyle({color: 'rgb(59, 173, 227)', opacity: 0.3});
            }
        }
    } catch (error) {

    }
}

/**
 * Goes over all boxes and sets their colors (highlight/self/opponent).
 * If box has been inter-/extrapolated, the border gets dashed.
 */
function set_box_colors() {

    try{
        for (let t = 0; t < trajectories.length; t++) {
            let box = document.getElementById("id"+trajectories[t].id + "box");
            if (box) {

                // get index in trajectory of current frame
                let pbr_index = 0;
                for (let p = 0; p < trajectories[t].positions_rotations_and_boxes.length; p++) {
                    if (trajectories[t].positions_rotations_and_boxes[p].frame == current_frame) {
                        pbr_index = p;
                        break;
                    }
                }
                let box_color;
                let line_type = (trajectories[t].positions_rotations_and_boxes[pbr_index].detected || trajectories[t].positions_rotations_and_boxes[pbr_index].specified) ? '3px solid': '2px dashed';

                // main stuff
                if ((selection.filter(el => el[0] == t).length > 0 && highlight.length == 0 && selection.filter(el => el[0] == t).map(el => trajectories[el[0]].positions_rotations_and_boxes[el[1]].frame).includes(current_frame))
                    || (highlight.filter(el => el[0] == t).length > 0 && highlight.filter(el => el[0] == t).map(el => trajectories[el[0]].positions_rotations_and_boxes[el[1]].frame).includes(current_frame))) {

                    box_color = (trajectories[t].positions_rotations_and_boxes[pbr_index].detected || trajectories[t].positions_rotations_and_boxes[pbr_index].specified) ? 'rgb(61, 227, 105)' : 'rgb(41, 153, 71)';
                    box.style.backgroundColor = (trajectories[t].positions_rotations_and_boxes[pbr_index].detected || trajectories[t].positions_rotations_and_boxes[pbr_index].specified) ? 'rgba(61, 227, 105, 0.3)' : 'rgba(41, 153, 71, 0.3)';

                } else if (trajectories[t].id === 0) {

                    box_color = (trajectories[t].positions_rotations_and_boxes[pbr_index].detected || trajectories[t].positions_rotations_and_boxes[pbr_index].specified) ? 'rgb(247, 76, 67)' : 'rgb(173, 53, 47)';
                    box.style.backgroundColor = (trajectories[t].positions_rotations_and_boxes[pbr_index].detected || trajectories[t].positions_rotations_and_boxes[pbr_index].specified) ? 'rgba(247, 76, 67, 0.3)' : 'rgba(173, 53, 47, 0.3)';

                } else {

                    box_color = (trajectories[t].positions_rotations_and_boxes[pbr_index].detected || trajectories[t].positions_rotations_and_boxes[pbr_index].specified) ? 'rgb(59, 173, 227)' : 'rgb(40, 117, 153)';
                    box.style.backgroundColor = (trajectories[t].positions_rotations_and_boxes[pbr_index].detected || trajectories[t].positions_rotations_and_boxes[pbr_index].specified) ? 'rgba(59, 173, 227, 0.3)' : 'rgba(40, 117, 153, 0.3)';

                }

                box.style.border = line_type + " " + box_color;
                box.style.color = box_color;
            }
        }
    } catch (error) {

    }
}

/**
 * Goes over all element descriptors in the element selector and set their colors.
 * Classes must be used here => colors can be propagated to children (svg and text).
 */
function set_element_colors() {
    try {
        for (let t = 0; t < trajectories.length; t++) {
            const element = document.getElementById("id"+trajectories[t].id);
            if (trajectories[t].positions_rotations_and_boxes.length == 0) {
                element.classList.remove("active-element");
                element.classList.remove("self-element");
                element.classList.remove("some-element");
                element.classList.add("empty-element");
            } else if ((selection.filter(el => el[0] == t).length > 0 && highlight.length == 0 && selection.filter(el => el[0] == t).map(el => trajectories[el[0]].positions_rotations_and_boxes[el[1]].frame).includes(current_frame))
                || (highlight.filter(el => el[0] == t).length > 0 && highlight.filter(el => el[0] == t).map(el => trajectories[el[0]].positions_rotations_and_boxes[el[1]].frame).includes(current_frame))) {
                element.classList.add("active-element");
                element.classList.remove("self-element");
                element.classList.remove("some-element");
                element.classList.remove("empty-element");
            } else if (trajectories[t].id === 0) {
                element.classList.remove("active-element");
                element.classList.add("self-element");
                element.classList.remove("some-element");
                element.classList.remove("empty-element");
            } else {
                element.classList.remove("active-element");
                element.classList.remove("self-element");
                element.classList.add("some-element");
                element.classList.remove("empty-element");
            }
        }
    } catch (error) {

    }
}


function handle_mouseenter_descriptor(event) {
    handle_mouseenter_element(event.target.id);
}


function handle_mouseenter_box(event) {
    handle_mouseenter_element(event.target.id.replace("box", ""));
}


/**
 * Handles what happens when mouse enters either a box or an element descriptor. (Set selection / highlight + corrects colors)
 * @param id
 */
function handle_mouseenter_element(id) {

    const line_index = trajectories.findIndex((trajectory) => "id"+trajectory.id === id);
    if (trajectories[line_index].positions_rotations_and_boxes.length > 0) {
        switch (selection_mode) {
            case "point":
                const point_index = trajectories[line_index].positions_rotations_and_boxes.findIndex((pos_rot_box) => pos_rot_box.frame == current_frame);
                selection = [[line_index, point_index]];
                if (map.hasLayer(center_marker)) {
                    map.removeLayer(center_marker);
                }
                break;
            case "line":
                selection = [];

                //correct selection + center marker
                var lat = 0;
                var long = 0;
                for (let i = 0; i < points[line_index].length; i++) {
                    selection.push([line_index, i]);
                    lat += trajectories[line_index].positions_rotations_and_boxes[i].position[0];
                    long += trajectories[line_index].positions_rotations_and_boxes[i].position[1];
                }
                lat /= points[line_index].length;
                long /= points[line_index].length;
                if (map.hasLayer(center_marker)) {
                    map.removeLayer(center_marker);
                }
                center_marker.setLatLng(new L.LatLng(lat, long));
                if (action_mode != "move") {
                    center_marker.addTo(map);
                }
                break;
            case "all":
                selection = [];
                //correct selection + center marker
                var lat = 0;
                var long = 0;
                for (let l = 0; l < points.length; l++) {
                    for (let p = 0; p < points[l].length; p++) {
                        selection.push([l, p]);
                        lat += trajectories[l].positions_rotations_and_boxes[p].position[0];
                        long += trajectories[l].positions_rotations_and_boxes[p].position[1];
                    }
                }
                lat /= selection.length;
                long /= selection.length;
                if (map.hasLayer(center_marker)) {
                    map.removeLayer(center_marker);
                }
                center_marker.setLatLng(new L.LatLng(lat, long));
                if (action_mode != "move") {
                    center_marker.addTo(map);
                }
                break;
            case "selection":
                highlight = [];
                //only highlight the part of the selection of the element the mouse is over + correct centermarker
                var lat = 0;
                var long = 0;
                for (let selection_index = 0; selection_index < selection.length; selection_index++) {
                    if (selection[selection_index][0] == line_index) {
                        highlight.push(selection[selection_index]);
                        lat += trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position[0];
                        long += trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position[1];
                    }
                }
                if(highlight.length > 0){
                    lat /= highlight.length;
                    long /= highlight.length;
                    if (map.hasLayer(center_marker)) {
                        map.removeLayer(center_marker);
                    }
                    center_marker.setLatLng(new L.LatLng(lat, long));
                    if (action_mode != "move") {
                        center_marker.addTo(map);
                    }
                }
                break;
            default:
                break;
        }
    }

    set_element_colors();
    set_circle_colors();
    set_line_colors();
    set_box_colors();
}

/**
 * Handles what happens, when the mouse is leaving the box/element descriptor (reset selection + colors)
 */
function handle_mouseleave_element() {
    if (selection_mode != "selection") {
        selection = [];
        if (map.hasLayer(center_marker)) {
            map.removeLayer(center_marker);
        }
    } else {
        highlight = [];

        // update centermarker
        var lat = 0;
        var long = 0;
        for (let selection_index = 0; selection_index < selection.length; selection_index++) {
            lat += trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position[0];
            long += trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position[1];
        }
        if(highlight.length > 0) {
            lat /= selection.length;
            long /= selection.length;
            if (map.hasLayer(center_marker)) {
                map.removeLayer(center_marker);
            }
            center_marker.setLatLng(new L.LatLng(lat, long));
            if (action_mode != "move") {
                center_marker.addTo(map);
            }
        }
    }

    set_element_colors();
    set_circle_colors();
    set_line_colors();
    set_box_colors();
}


/**
 * Handles what happens if a box/element descriptor gets clicked (Only points of this object are still in the selection)
 */
function handle_click_element() {
    if (selection_mode == "selection") {
        selection = [...highlight];
    }
}

/**
 * Handles what happens when mouse enters a line. (Set selection + corrects colors + centermarker)
 */
function handle_mouseenter_line(event) {
    if (mouse_down == 0) {
        switch (selection_mode) {
            case "point":
                const point_index = closest_point_on_line(event.latlng, event.target.line_index);
                selection = [[event.target.line_index, point_index]];
                if (map.hasLayer(center_marker)) {
                    map.removeLayer(center_marker);
                }
                break;
            case "line":
                selection = [];
                var lat = 0;
                var long = 0;
                for (let i = 0; i < points[event.target.line_index].length; i++) {
                    selection.push([event.target.line_index, i]);
                    lat += trajectories[event.target.line_index].positions_rotations_and_boxes[i].position[0];
                    long += trajectories[event.target.line_index].positions_rotations_and_boxes[i].position[1];
                }
                lat /= points[event.target.line_index].length;
                long /= points[event.target.line_index].length;
                if (map.hasLayer(center_marker)) {
                    map.removeLayer(center_marker);
                }
                center_marker.setLatLng(new L.LatLng(lat, long));
                if (action_mode != "move") {
                    center_marker.addTo(map);
                }
                break;
            case "all":
                selection = [];
                var lat = 0;
                var long = 0;
                for (let l = 0; l < points.length; l++) {
                    for (let p = 0; p < points[l].length; p++) {
                        selection.push([l, p]);
                        lat += trajectories[l].positions_rotations_and_boxes[p].position[0];
                        long += trajectories[l].positions_rotations_and_boxes[p].position[1];
                    }
                }
                lat /= selection.length;
                long /= selection.length;
                if (map.hasLayer(center_marker)) {
                    map.removeLayer(center_marker);
                }
                center_marker.setLatLng(new L.LatLng(lat, long));
                if (action_mode != "move") {
                    center_marker.addTo(map);
                }
                break;
            default:
                break;
        }

        set_element_colors();
        set_circle_colors();
        set_line_colors();
        set_box_colors();
    }
}

/**
 * Handles what happens when mouse leaves a line. (Reset selection + corrects colors + centermarker)
 */
function handle_mouseleave_line(event) {
    if (selection_mode != "selection" && mouse_down == 0) { // mousedown needed for fast movements -> only leave when mouse is up
        selection = [];
        if (map.hasLayer(center_marker)) {
            map.removeLayer(center_marker);
        }
        set_element_colors();
        set_circle_colors();
        set_line_colors();
        set_box_colors();
    }
}

/**
 * Handles what happens when mouse enters a point. (Set selection + corrects colors + centermarker)
 */
function handle_mouseenter_point(event) {
    if (mouse_down == 0) {
        switch (selection_mode) {
            case "point":
                selection = [[event.target.line_index, event.target.point_index]];
                if (map.hasLayer(center_marker)) {
                    map.removeLayer(center_marker);
                }
                break;
            case "line":
                selection = [];
                var lat = 0;
                var long = 0;
                for (let i = 0; i < points[event.target.line_index].length; i++) {
                    selection.push([event.target.line_index, i]);
                    lat += trajectories[event.target.line_index].positions_rotations_and_boxes[i].position[0];
                    long += trajectories[event.target.line_index].positions_rotations_and_boxes[i].position[1];
                }
                lat /= points[event.target.line_index].length;
                long /= points[event.target.line_index].length;
                if (map.hasLayer(center_marker)) {
                    map.removeLayer(center_marker);
                }
                center_marker.setLatLng(new L.LatLng(lat, long));
                if (action_mode != "move") {
                    center_marker.addTo(map);
                }
                break;
            case "all":
                selection = [];
                var lat = 0;
                var long = 0;
                for (let l = 0; l < points.length; l++) {
                    for (let p = 0; p < points[l].length; p++) {
                        selection.push([l, p]);
                        lat += trajectories[l].positions_rotations_and_boxes[p].position[0];
                        long += trajectories[l].positions_rotations_and_boxes[p].position[1];
                    }
                }
                lat /= selection.length;
                long /= selection.length;
                if (map.hasLayer(center_marker)) {
                    map.removeLayer(center_marker);
                }
                center_marker.setLatLng(new L.LatLng(lat, long));
                if (action_mode != "move") {
                    center_marker.addTo(map);
                }
                break;
            default:
                break;
        }

        set_element_colors();
        set_circle_colors();
        set_line_colors();
        set_box_colors();
    }
}

/**
 * Handles what happens when mouse leaves a point. (Reset selection + corrects colors + centermarker)
 */
function handle_mouseleave_point(event) {
    if (selection_mode != "selection" && mouse_down == 0) {
        selection = [];
        if (map.hasLayer(center_marker)) {
            map.removeLayer(center_marker);
        }
        set_element_colors();
        set_circle_colors();
        set_line_colors();
        set_box_colors();
    }
}