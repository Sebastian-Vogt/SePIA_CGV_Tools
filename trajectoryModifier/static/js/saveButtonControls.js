/**
 * Handles the click on the save button. (If there are changes -> send them, Correct button appearance)
 */
function save_button_click(e) {
    if (changes) {
        const saving_button = document.getElementById("savingButton");
        saving_button.classList.toggle("hidden");
        const changes_button = document.getElementById("changesButton");
        changes_button.classList.toggle("hidden");
        const xhr = new XMLHttpRequest();   // new HttpRequest instance
        const theUrl = "/trajectories";
        xhr.open("POST", theUrl);
        xhr.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                changes = false;
                const saved_button = document.getElementById("savedButton");
                saved_button.classList.toggle("hidden");
                saving_button.classList.toggle("hidden");

                const xhr1 = new XMLHttpRequest();   // http request for trajectories
                const theUrl1 = "/trajectories";
                xhr1.onreadystatechange = function () {
                    if (this.readyState == 4 && this.status == 200) {
                        trajectories = JSON.parse(xhr1.responseText);

                        uninterpolate_boxes();

                        delete_all_lines_and_points();
                        initialize_points_and_lines();
                        draw_boxes();
                        hide_and_show_elements();
                        set_element_colors();
                        set_circle_colors();
                        set_line_colors();
                        set_box_colors();
                        button_visibility();
                        calculate_directions();
                        redraw_object_map_object_outlines();
                    }
                }
                xhr1.open("GET", theUrl1);
                xhr1.send();

            }
        };
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.send(JSON.stringify(trajectories));
    }
}


function recalibrate(e) {
    const xhr = new XMLHttpRequest();   // new HttpRequest instance
    const theUrl = "/recalibrate";
    xhr.open("POST", theUrl);
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            window.alert("Recalibration finished!");
        }
    };
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.send(JSON.stringify(trajectories));
}
