var trajectories;   // list of trajectories
var original_boxes; // list of uninterpolated bounding boxes

var map;    // leaflet map
var lasso;  // leaflet lasso for selection

var crosshairIcon;  // crosshair icon for the center marker
var center_marker;  // leaflet marker for the center of a selection

var lines = []; // list of leaflet lines ~ trajectories
var points; // list of list of leaflet circles ~ trajectory positions at frames
var map_object_outlines = [];   // list of leaflet polygons ~ object top down projection outlines

var video;  // html 5 video object
var current_frame;  // current video frame
var nr_frames;  // number of frames of th video
var fps;    // video frames per seconds
var video_height;   // height of the video in px
var video_width;    //width of the video in px
var loop;   // boolean flag if the loop button is activated
var is_playing; // boolean flag whether the video is playing
var interval;   // interval function to use when video is playing to proceed in the video
var range;  // html slider object (video slider)
var timeline_style_tag; // style tag needed for the video slider to set the color adaptively
const colorTable = [[59, 173, 227], [87, 111, 230]];    // colors to use for the video slider interpolation

var changes;    // boolean flag if there have been changes made since the last save/load

var selection = []; // current selected points (list of list [[line_index, point_index]...])
var highlight = []; // if there is a selection, but there needs something to be highlighted more importantly (same type as selection)
var selection_mode = "point";   // either "point", "line, "all" or "selection" (lasso)
var action_mode = "move";   // action to perform on selection. Either "move", "rotate", "scale", "remove" or "collapse"

var mouse_down = 0; // 0 = mouse is not pressed,  1 = mouse is pressed (needed for fast movements with pressed mouse to not trigger the leave function)

var index_to_edit;  // trajectory index that will be edited (inter-/extrapolated ...) (needed to know the index after the forms)

proj4.defs("EPSG:32633","+proj=utm +zone=33 +datum=WGS84 +units=m +no_defs");   // define proj4 projection of EPSG:32633
const wgs84 = 'WGS84';
const epsg32633 = 'EPSG:32633';
const degree2meter = proj4(wgs84,epsg32633);    // defined degree to meter projection
