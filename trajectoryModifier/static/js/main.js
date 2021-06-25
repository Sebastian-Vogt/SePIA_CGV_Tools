// only works when everything is loaded
document.addEventListener("DOMContentLoaded", function () {

        // create style tag for the video slider
        timeline_style_tag = document.createElement('style');
        document.querySelector('head').appendChild(timeline_style_tag);

        // register functions for mouse down/up measurement
        document.body.onmousedown = function () {
            mouse_down = 1;
        }
        document.body.onmouseup = function () {
            mouse_down = 0;
        }

        // set center marker (url for icon is bypassed in the html document)
        crosshairIcon = L.icon({
            iconUrl: document.getElementById("centerUrlBypass").getAttribute('data-url'),
            iconSize: [21, 21],
            iconAnchor: [11, 11],
        });
        center_marker = new L.marker(new L.LatLng(0, 0), {icon: crosshairIcon, clickable: false});  // init at 0,0 -> init out of sight. Also not added to map yet

        // register right click handler for all existing object
        let smooth_Buttons = document.getElementsByClassName('smoothButton');
        for(let i = 0; i < smooth_Buttons.length; i++) {
            smooth_Buttons[i].addEventListener('contextmenu', function (ev) {
                ev.preventDefault();
                gauss_smooth_object(ev);
                return false;
            }, false);
        }

        const xhr = new XMLHttpRequest();   // http request to get video information (i.e. fps)
        const theUrl = "/videoinformation";
        xhr.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                video_info = JSON.parse(xhr.responseText);
                fps = video_info.fps;
                nr_frames = video_info.length;
                video_height = video_info.height;
                video_width = video_info.width;

                const xhr1 = new XMLHttpRequest();   // http request for trajectories
                const theUrl1 = "/trajectories";
                xhr1.onreadystatechange = function () {
                    if (this.readyState == 4 && this.status == 200) {
                        trajectories = JSON.parse(xhr1.responseText);
                        original_boxes = [];
                        for (let t = 0; t < trajectories.length; t++) {
                            const boxes_obj = { id: trajectories[t].id,
                                                boxes: []};
                            for (let i = 0; i < trajectories[t].positions_rotations_and_boxes.length; i++) {
                                const box = {  frame: trajectories[t].positions_rotations_and_boxes[i].frame,
                                               box: trajectories[t].positions_rotations_and_boxes[i].box};
                                 //if (! trajectories[t].positions_rotations_and_boxes[i].is_interpolated) {
                                boxes_obj.boxes.push(box);
                                 //}
                            }
                            original_boxes.push(boxes_obj);
                        }

                        // get min and max values of points -> adjust map view according to this
                        let min_lat = 90;
                        let min_long = 180;
                        let max_lat = -90;
                        let max_long = -180;
                        for (let t = 0; t < trajectories.length; t++) {
                            for (let i = 0; i < trajectories[t].positions_rotations_and_boxes.length; i++) {
                                if (trajectories[t].positions_rotations_and_boxes[i].position[0] < min_lat)
                                    min_lat = trajectories[t].positions_rotations_and_boxes[i].position[0];
                                if (trajectories[t].positions_rotations_and_boxes[i].position[1] < min_long)
                                    min_long = trajectories[t].positions_rotations_and_boxes[i].position[1];
                                if (trajectories[t].positions_rotations_and_boxes[i].position[0] > max_lat)
                                    max_lat = trajectories[t].positions_rotations_and_boxes[i].position[0];
                                if (trajectories[t].positions_rotations_and_boxes[i].position[1] > max_long)
                                    max_long = trajectories[t].positions_rotations_and_boxes[i].position[1];
                            }
                            document.getElementById("id" + trajectories[t].id + "size").innerHTML = ("dimensions" in trajectories[t]) ? trajectories[t].dimensions[0] + "m * " + trajectories[t].dimensions[1] + "m * " + trajectories[t].dimensions[2] + "m" : "no size given";
                        }

                        map = L.map('map').setView([(min_lat + max_lat) / 2, max_long], 18);
                        const osm = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png', {
                            maxZoom: 23,    // more zoom, than natively provided (linear)
                            maxNativeZoom: 20
                        }).addTo(map);

                        //lasso for "selection" selection mode
                        lasso = L.lasso(map);
                        map.on('lasso.finished', selection_finished);

                        initialize_points_and_lines();

                        // init video variables
                        video = document.getElementById("video");
                        loop = false;
                        current_frame = 0;
                        is_playing = false;
                        changes = false;

                        // set handlers for all buttons
                        const all_selection_button = document.getElementById("allSelectionButton");
                        all_selection_button.addEventListener("click", on_all_selection_mode_button_click);
                        document.addEventListener("keydown", function (e) {
                            if (e.keyCode == 65) {
                                on_all_selection_mode_button_click()
                            }
                        }, false);
                        const line_selection_button = document.getElementById("lineSelectionButton");
                        line_selection_button.addEventListener("click", on_line_selection_mode_button_click);
                        document.addEventListener("keydown", function (e) {
                            if (e.keyCode == 76) {
                                on_line_selection_mode_button_click()
                            }
                        }, false);
                        const point_selection_button = document.getElementById("pointSelectionButton");
                        point_selection_button.addEventListener("click", on_point_selection_mode_button_click);
                        document.addEventListener("keydown", function (e) {
                            if (e.keyCode == 80) {
                                on_point_selection_mode_button_click()
                            }
                        }, false);
                        const selection_selection_button = document.getElementById("selectionSelectionButton");
                        selection_selection_button.addEventListener("click", on_selection_selection_mode_button_click);
                        document.addEventListener("keydown", function (e) {
                            if (e.keyCode == 79) {
                                on_selection_selection_mode_button_click()
                            }
                        }, false);


                        const move_action_button = document.getElementById("moveActionButton");
                        move_action_button.addEventListener("click", on_move_action_button_click);
                        document.addEventListener("keydown", function (e) {
                            if (e.keyCode == 77) {
                                on_move_action_button_click()
                            }
                        }, false);
                        const scale_action_button = document.getElementById("scaleActionButton");
                        scale_action_button.addEventListener("click", on_scale_action_button_click);
                        document.addEventListener("keydown", function (e) {
                            if (e.keyCode == 83 && !(window.navigator.platform.match("Mac") ? e.metaKey : e.ctrlKey)) {
                                on_scale_action_button_click()
                            }
                        }, false);
                        const rotate_action_button = document.getElementById("rotateActionButton");
                        rotate_action_button.addEventListener("click", on_rotate_action_button_click);
                        document.addEventListener("keydown", function (e) {
                            if (e.keyCode == 82 && !(window.navigator.platform.match("Mac") ? e.metaKey : e.ctrlKey)) {
                                on_rotate_action_button_click()
                            }
                        }, false);
                        const collapse_action_button = document.getElementById("collapseActionButton");
                        collapse_action_button.addEventListener("click", on_collapse_action_button_click);
                        document.addEventListener("keydown", function (e) {
                            if (e.keyCode == 67) {
                                on_collapse_action_button_click()
                            }
                        }, false);
                        const remove_action_button = document.getElementById("removeActionButton");
                        remove_action_button.addEventListener("click", on_remove_action_button_click);
                        document.addEventListener("keydown", function (e) {
                            if (e.keyCode == 68) {
                                on_remove_action_button_click()
                            }
                        }, false);


                        const add_points_cancelation_button = document.getElementById("addFormAbortButton");
                        add_points_cancelation_button.addEventListener("click", cancel_add_points);
                        const number_of_new_points_input_field = document.getElementById("numberOfPoints")
                        number_of_new_points_input_field.addEventListener("input", numberOfPointsValidation);
                        const new_point_direction_switch = document.getElementById("newPointDirection");
                        new_point_direction_switch.addEventListener("change", numberOfPointsValidation);

                        const change_size_cancelation_button = document.getElementById("changeSizeAbortButton");
                        change_size_cancelation_button.addEventListener("click", cancel_change_size);
                        const width_input_field = document.getElementById("widthInput");
                        width_input_field.addEventListener("input", sizeValidation);
                        const length_input_field = document.getElementById("lengthInput");
                        length_input_field.addEventListener("input", sizeValidation);
                        const height_input_field = document.getElementById("heightInput");
                        height_input_field.addEventListener("input", sizeValidation);
                        const new_element_cancelation_button = document.getElementById("newElementAbortButton");
                        new_element_cancelation_button.addEventListener("click", cancel_add_new_element);
                        const new_width_input_field = document.getElementById("newWidthInput");
                        new_width_input_field.addEventListener("input", sizeValidation);
                        const new_length_input_field = document.getElementById("newLengthInput");
                        new_length_input_field.addEventListener("input", sizeValidation);
                        const new_height_input_field = document.getElementById("newHeightInput");
                        new_height_input_field.addEventListener("input", sizeValidation);
                        const frame_to_start_input_field = document.getElementById("frameToStartInput");
                        frame_to_start_input_field.addEventListener("input", validate_starting_frame);

                        const changes_button = document.getElementById("changesButton");
                        changes_button.addEventListener("click", save_button_click);
                        document.addEventListener("keydown", function (e) {
                            if ((window.navigator.platform.match("Mac") ? e.metaKey : e.ctrlKey) && e.keyCode == 83) {
                                e.preventDefault();
                                save_button_click(e);
                            }
                        }, false);

                        document.addEventListener("keydown", function (e) {
                            if ((window.navigator.platform.match("Mac") ? e.metaKey : e.ctrlKey) && e.keyCode == 82) {
                                e.preventDefault();
                                recalibrate(e);
                            }
                        }, false);

                        const loop_button = document.getElementById("loopButton");
                        loop_button.addEventListener("click", loop_button_pressed);

                        const play_button = document.getElementById("playButton");
                        const pause_button = document.getElementById("pauseButton");
                        const time_text_element = document.getElementById("rightTime");

                        play_button.addEventListener("click", function f() {
                            play_button_pressed(play_button, pause_button, time_text_element);
                        });
                        pause_button.addEventListener("click", function f() {
                            pause_button_pressed(play_button, pause_button);
                        });

                        // set range slider + init color
                        range = document.getElementById("timelineRange");
                        range.addEventListener("input", function f() {
                            on_slider(play_button, pause_button, time_text_element);
                            sliderColorCorrector(colorTable, range, timeline_style_tag);
                        });
                        range.addEventListener("change", function f() {
                            on_slider(play_button, pause_button, time_text_element);
                            sliderColorCorrector(colorTable, range, timeline_style_tag);
                        });
                        sliderColorCorrector(colorTable, range, timeline_style_tag);

                        // set resize callback for video + initialize size
                        window.addEventListener("resize", rescale_boxes);
                        rescale_boxes();

                        // correct colors etc.
                        draw_boxes();
                        hide_and_show_elements();
                        correct_lines();
                        set_element_colors();
                        set_circle_colors();
                        set_line_colors();
                        set_box_colors();
                        button_visibility();
                        calculate_directions();
                        redraw_object_map_object_outlines();

                        checkDraggablility();
                    } else {
                        return "something went wrong"
                    }
                }
                xhr1.open("GET", theUrl1);
                xhr1.send();
            }
        }
        xhr.open("GET", theUrl);
        xhr.send();

    }
);