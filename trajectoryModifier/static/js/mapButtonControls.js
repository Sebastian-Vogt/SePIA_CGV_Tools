
/**
 * Handles the click on the "all" selection type button
 */
function on_all_selection_mode_button_click() {
    selection_mode = "all";
    selection = [];
    const svgAll = document.getElementById("svgAll");
    const svgLine = document.getElementById("svgLine");
    const svgPoint = document.getElementById("svgPoint");
    const svgSelection = document.getElementById("svgSelection");
    svgPoint.classList.add("hidden");
    svgLine.classList.add("hidden");
    svgAll.classList.remove("hidden");
    svgSelection.classList.add("hidden");

    const collapseActionButton = document.getElementById("collapseActionButton");
    const rotateActionButton = document.getElementById("rotateActionButton");
    const scaleActionButton = document.getElementById("scaleActionButton");
    collapseActionButton.classList.remove("hidden");
    rotateActionButton.classList.remove("hidden");
    scaleActionButton.classList.remove("hidden");

    lasso.disable();

    map.on('mouseup', function (e) {
        map.removeEventListener('mousemove');
    })
}

/**
 * Handles the click on the "line" selection type button
 */
function on_line_selection_mode_button_click() {
    selection_mode = "line";
    selection = [];
    const svgAll = document.getElementById("svgAll");
    const svgLine = document.getElementById("svgLine");
    const svgPoint = document.getElementById("svgPoint");
    const svgSelection = document.getElementById("svgSelection");
    svgPoint.classList.add("hidden");
    svgLine.classList.remove("hidden");
    svgAll.classList.add("hidden");
    svgSelection.classList.add("hidden");

    const collapseActionButton = document.getElementById("collapseActionButton");
    const rotateActionButton = document.getElementById("rotateActionButton");
    const scaleActionButton = document.getElementById("scaleActionButton");
    collapseActionButton.classList.remove("hidden");
    rotateActionButton.classList.remove("hidden");
    scaleActionButton.classList.remove("hidden");

    lasso.disable();

    map.on('mouseup', function (e) {
        map.removeEventListener('mousemove');
    })
}
/**
 * Handles the click on the "point" selection type button
 */
function on_point_selection_mode_button_click() {
    selection_mode = "point";
    selection = [];
    const svgAll = document.getElementById("svgAll");
    const svgLine = document.getElementById("svgLine");
    const svgPoint = document.getElementById("svgPoint");
    const svgSelection = document.getElementById("svgSelection");
    svgPoint.classList.remove("hidden");
    svgLine.classList.add("hidden");
    svgAll.classList.add("hidden");
    svgSelection.classList.add("hidden");

    const collapseActionButton = document.getElementById("collapseActionButton");
    const rotateActionButton = document.getElementById("rotateActionButton");
    const scaleActionButton = document.getElementById("scaleActionButton");
    collapseActionButton.classList.add("hidden");
    rotateActionButton.classList.add("hidden");
    scaleActionButton.classList.add("hidden");

    lasso.disable();

    map.on('mouseup', function (e) {
        map.removeEventListener('mousemove');
    })
}

/**
 * Handles the click on the "selection" (lasso) selection type button
 */
function on_selection_selection_mode_button_click() {
    selection_mode = "selection";
    selection = [];
    const svgAll = document.getElementById("svgAll");
    const svgLine = document.getElementById("svgLine");
    const svgPoint = document.getElementById("svgPoint");
    const svgSelection = document.getElementById("svgSelection");
    svgPoint.classList.add("hidden");
    svgLine.classList.add("hidden");
    svgAll.classList.add("hidden");
    svgSelection.classList.remove("hidden");

    const collapseActionButton = document.getElementById("collapseActionButton");
    const rotateActionButton = document.getElementById("rotateActionButton");
    const scaleActionButton = document.getElementById("scaleActionButton");
    collapseActionButton.classList.remove("hidden");
    rotateActionButton.classList.remove("hidden");
    scaleActionButton.classList.remove("hidden");

    lasso.enable();
}

/**
 * Handles the click on the "move" action type button
 */
function on_move_action_button_click() {
    action_mode = "move";
    const svgMove = document.getElementById("svgMove");
    const svgScale = document.getElementById("svgScale");
    const svgRotate = document.getElementById("svgRotate");
    const svgCollapse = document.getElementById("svgCollapse");
    const svgRemove = document.getElementById("svgRemove");
    svgMove.classList.remove("hidden");
    svgScale.classList.add("hidden");
    svgRotate.classList.add("hidden");
    svgCollapse.classList.add("hidden");
    svgRemove.classList.add("hidden");

    const svgAllButton = document.getElementById("allSelectionButton");
    const svgLineButton = document.getElementById("lineSelectionButton");
    const svgPointButton = document.getElementById("pointSelectionButton");
    const svgSelectionButton = document.getElementById("selectionSelectionButton");
    svgAllButton.classList.remove("hidden");
    svgLineButton.classList.remove("hidden");
    svgPointButton.classList.remove("hidden");
    svgSelectionButton.classList.remove("hidden");

    if (map.hasLayer(center_marker)) {
        map.removeLayer(center_marker);
    }
}

/**
 * Handles the click on the "scale" action type button
 */
function on_scale_action_button_click() {
    action_mode = "scale";
    const svgMove = document.getElementById("svgMove");
    const svgScale = document.getElementById("svgScale");
    const svgRotate = document.getElementById("svgRotate");
    const svgCollapse = document.getElementById("svgCollapse");
    const svgRemove = document.getElementById("svgRemove");
    svgMove.classList.add("hidden");
    svgScale.classList.remove("hidden");
    svgRotate.classList.add("hidden");
    svgCollapse.classList.add("hidden");
    svgRemove.classList.add("hidden");

    const svgAllButton = document.getElementById("allSelectionButton");
    const svgLineButton = document.getElementById("lineSelectionButton");
    const svgPointButton = document.getElementById("pointSelectionButton");
    const svgSelectionButton = document.getElementById("selectionSelectionButton");
    svgAllButton.classList.remove("hidden");
    svgLineButton.classList.remove("hidden");
    svgPointButton.classList.add("hidden");
    svgSelectionButton.classList.remove("hidden");

    let lat = 0;
    let long = 0;
    for (let selection_index = 0; selection_index < selection.length; selection_index++) {
        lat += trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position[0];
        long += trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position[1];
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
}
/**
 * Handles the click on the "rotate" action type button
 */
function on_rotate_action_button_click() {
    action_mode = "rotate";
    const svgMove = document.getElementById("svgMove");
    const svgScale = document.getElementById("svgScale");
    const svgRotate = document.getElementById("svgRotate");
    const svgCollapse = document.getElementById("svgCollapse");
    const svgRemove = document.getElementById("svgRemove");
    svgMove.classList.add("hidden");
    svgScale.classList.add("hidden");
    svgRotate.classList.remove("hidden");
    svgCollapse.classList.add("hidden");
    svgRemove.classList.add("hidden");

    const svgAllButton = document.getElementById("allSelectionButton");
    const svgLineButton = document.getElementById("lineSelectionButton");
    const svgPointButton = document.getElementById("pointSelectionButton");
    const svgSelectionButton = document.getElementById("selectionSelectionButton");
    svgAllButton.classList.remove("hidden");
    svgLineButton.classList.remove("hidden");
    svgPointButton.classList.add("hidden");
    svgSelectionButton.classList.remove("hidden");

    let lat = 0;
    let long = 0;
    for (let selection_index = 0; selection_index < selection.length; selection_index++) {
        lat += trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position[0];
        long += trajectories[selection[selection_index][0]].positions_rotations_and_boxes[selection[selection_index][1]].position[1];
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
}
/**
 * Handles the click on the "collapse" action type button
 */
function on_collapse_action_button_click() {
    action_mode = "collapse";
    const svgMove = document.getElementById("svgMove");
    const svgScale = document.getElementById("svgScale");
    const svgRotate = document.getElementById("svgRotate");
    const svgCollapse = document.getElementById("svgCollapse");
    const svgRemove = document.getElementById("svgRemove");
    svgMove.classList.add("hidden");
    svgScale.classList.add("hidden");
    svgRotate.classList.add("hidden");
    svgCollapse.classList.remove("hidden");
    svgRemove.classList.add("hidden");

    const svgAllButton = document.getElementById("allSelectionButton");
    const svgLineButton = document.getElementById("lineSelectionButton");
    const svgPointButton = document.getElementById("pointSelectionButton");
    const svgSelectionButton = document.getElementById("selectionSelectionButton");
    svgAllButton.classList.remove("hidden");
    svgLineButton.classList.remove("hidden");
    svgPointButton.classList.add("hidden");
    svgSelectionButton.classList.remove("hidden");
}
/**
 * Handles the click on the "remove" action type button
 */
function on_remove_action_button_click() {
    action_mode = "remove";
    const svgMove = document.getElementById("svgMove");
    const svgScale = document.getElementById("svgScale");
    const svgRotate = document.getElementById("svgRotate");
    const svgCollapse = document.getElementById("svgCollapse");
    const svgRemove = document.getElementById("svgRemove");
    svgMove.classList.add("hidden");
    svgScale.classList.add("hidden");
    svgRotate.classList.add("hidden");
    svgCollapse.classList.add("hidden");
    svgRemove.classList.remove("hidden");

    const svgAllButton = document.getElementById("allSelectionButton");
    const svgLineButton = document.getElementById("lineSelectionButton");
    const svgPointButton = document.getElementById("pointSelectionButton");
    const svgSelectionButton = document.getElementById("selectionSelectionButton");
    svgAllButton.classList.remove("hidden");
    svgLineButton.classList.remove("hidden");
    svgPointButton.classList.remove("hidden");
    svgSelectionButton.classList.remove("hidden");
}
/**
 * Callback for Leaflet lasso function -> sets selection, updates the colors and centermarker
 */
function selection_finished(event) {
    selection = [];
    let lat = 0;
    let long = 0;
    for (let i = 0; i < event.layers.length; i++) {
        if ("point_index" in event.layers[i]) {
            selection.push([event.layers[i].line_index, event.layers[i].point_index]);
            lat += trajectories[event.layers[i].line_index].positions_rotations_and_boxes[event.layers[i].point_index].position[0];
            long += trajectories[event.layers[i].line_index].positions_rotations_and_boxes[event.layers[i].point_index].position[1];
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
    set_element_colors();
    set_circle_colors();
    set_line_colors();
    set_box_colors();
}