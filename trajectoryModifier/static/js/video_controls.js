/**
 * Corrects the color of the video slider (linear interpolation between values in the color table)
 */
function sliderColorCorrector(colorTable, element, styleTag) {
    let r, g, b, i = 0;

    let value = parseInt(element.value);
    let min = parseInt(element.min);
    let max = parseInt(element.max);

    // find correct position in table
    for (; i < colorTable.length - 1; i++) {
        if ((value >= min + i * (max - min) / (colorTable.length - 1)) && (value <= min + (i + 1) * (max - min) / (colorTable.length - 1)))
            break;
    }

    // calculate linear interpolation coefficient
    let alpha;
    // catch NaN error
    if (value - min === 0) {
        alpha = 0;
    } else {
        alpha = (value - min - (i * (max - min) / (colorTable.length - 1))) / ((max - min) / (colorTable.length - 1));
    }

    // calculate color
    r = Math.round((1 - alpha) * colorTable[i][0] + alpha * colorTable[i + 1][0]);
    g = Math.round((1 - alpha) * colorTable[i][1] + alpha * colorTable[i + 1][1]);
    b = Math.round((1 - alpha) * colorTable[i][2] + alpha * colorTable[i + 1][2]);

    styleTag.innerHTML = "#" + element.id + "::-webkit-slider-thumb{   border-color: rgb(" + r + ", " + g + ", " + b + ")!important}\n#" + element.id + "::-moz-range-thumb {border-color: rgb(" + r + ", " + g + ", " + b + ")!important}";

}

/**
 * When playing, sets increases the video frame on the right time (also corrects the slider (incl. color) and the text values and the button values on the end if not in loop)
 */
function interval_function(play_button, pause_button, time_text_element) {
    if (is_playing) {
        current_frame = parseInt(current_frame) + 1;
        if (parseInt(current_frame) >= parseInt(nr_frames)) {
            if (loop) { // when in loop: begin again
                current_frame = 0;
            } else {    // otherwise: stop
                clearInterval(interval);
                is_playing = false;
                play_button.classList.toggle("hidden");
                pause_button.classList.toggle("hidden");
                return;
            }
        }
        time_text_element.innerHTML = Math.floor(parseInt(current_frame) / fps / 60).pad(2) + ":" + (Math.floor((parseInt(current_frame) / fps) % 60)).pad(2) + " / " + Math.floor(parseInt(current_frame) + 1).pad(3);
        range.value = current_frame;
        draw_boxes();
        set_box_colors();
        video.currentTime = current_frame / fps;
        sliderColorCorrector(colorTable, range, timeline_style_tag);
        hide_and_show_elements();
        set_element_colors();
        set_circle_colors();
        correct_lines();
        button_visibility();
        redraw_object_map_object_outlines();
    }
}
/**
 * Changes the video position according to the slider
 */
function on_slider(play_button, pause_button, time_text_element) {
    let was_playing = is_playing;
    if (is_playing) {
        is_playing = false;
        clearInterval(interval);
    }
    current_frame = parseInt(range.value);
    draw_boxes();
    set_box_colors();
    video.currentTime = parseInt(current_frame) / fps;
    hide_and_show_elements();
    set_element_colors();
    set_circle_colors();
    correct_lines();
    button_visibility();
    redraw_object_map_object_outlines();
    time_text_element.innerHTML = Math.floor(parseInt(current_frame) / fps / 60).pad(2) + ":" + (Math.floor((parseInt(current_frame) / fps) % 60)).pad(2) + " / " + Math.floor(parseInt(current_frame) + 1).pad(3);
    if (was_playing) {
        is_playing = was_playing;
        interval = setInterval(function f() {
            interval_function(play_button, pause_button, time_text_element);
        }, 1000 / fps);
    }
}
/**
 * Handles click on play button
 */
function play_button_pressed(play_button, pause_button, time_text_element) {
    is_playing = true;
    if (parseInt(current_frame) >= parseInt(nr_frames) - 1) {
        current_frame = 0;
        time_text_element.innerHTML = Math.floor(parseInt(current_frame) / fps / 60).pad(2) + ":" + (Math.floor((parseInt(current_frame) / fps) % 60)).pad(2) + " / " + Math.floor(parseInt(current_frame) + 1).pad(3);
    }
    interval = setInterval(function f() {
        interval_function(play_button, pause_button, time_text_element);
    }, 1000 / fps);
    play_button.classList.toggle("hidden");
    pause_button.classList.toggle("hidden");
}
/**
 * Handles click on pause button
 */
function pause_button_pressed(play_button, pause_button) {
    is_playing = false;
    clearInterval(interval);
    play_button.classList.toggle("hidden");
    pause_button.classList.toggle("hidden");
}
/**
 * Handles click on loop button
 */
function loop_button_pressed(e) {
    loop = !loop;
    document.getElementById("loopButton").classList.toggle("activatedLoop");
}

/**
 * Adds leading zeros to string numbers
 */
Number.prototype.pad = function (size) {
    var s = String(this);
    while (s.length < (size || 2)) {
        s = "0" + s;
    }
    return s;
}