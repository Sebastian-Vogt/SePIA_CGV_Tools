import numpy as np
import math
from itertools import product
from scipy.spatial.transform import Rotation as R


class PositionEstimator:

    def __init__(self, own_position_extractor, geo_handler, camera_car_rotation, camera_height, polynomial_coefficients,
                 distortion_center, stretch_matrix, image_size, scale_factor=1):
        try:
            if len(polynomial_coefficients) == 4:
                self.polynomial_coefficients = polynomial_coefficients
            else:
                raise TypeError()
        except TypeError:
            raise TypeError(
                "TypeError: Polynomial_coefficients parameter needs to be list of floats with length 4. It is " + str(
                    type(polynomial_coefficients)))

        if type(distortion_center) is np.ndarray:
            if distortion_center.shape == (2, 1):
                self.distortion_center = distortion_center
            else:
                raise TypeError("Distortion_center parameter should have shape (2, 1). It has shape " + str(
                    distortion_center.shape))
        else:
            raise TypeError(
                "TypeError: Distortion_center parameter needs to be an np.array of shape (2, 1). It is " + str(
                    type(distortion_center)))

        if type(stretch_matrix) is np.ndarray:
            if stretch_matrix.shape == (2, 2):
                self.stretch_matrix = stretch_matrix
                try:
                    self.inv_stretch_matrix = np.linalg.inv(stretch_matrix)
                except np.linalg.LinAlgError:
                    raise ValueError("Stretch_matrix is either not square or on another way not invertible.")
            else:
                raise TypeError(
                    "Stretch_matrix parameter should have shape (2, 2). It has shape " + str(stretch_matrix.shape))
        else:
            raise TypeError("Stretch_matrix parameter needs to be an np.array of shape (2, 2). It is " + str(
                type(stretch_matrix)))
        self.scale_factor = scale_factor
        #self.distance_direction_array = self.collect_norms(image_size)
        self.own_position_extractor = own_position_extractor
        self.camera_car_rotation = camera_car_rotation
        self.camera_height = camera_height
        self.geo = geo_handler

    def get_camera_ray(self, u, v):
        uv = np.array([[u], [v]])
        uv = np.subtract(uv, self.distortion_center)
        uv = np.dot(self.inv_stretch_matrix, uv)
        rho = math.sqrt(uv[0][0] ** 2 + uv[1][0] ** 2)
        matlab_xyz = self.scale_factor * np.array([[uv[0][0]],
                                                   [uv[1][0]],
                                                   [self.polynomial_coefficients[0] + self.polynomial_coefficients[
                                                       1] * (rho ** 2) + self.polynomial_coefficients[2] * (rho ** 3) +
                                                    self.polynomial_coefficients[3] * (rho ** 4)]])
        camera_xyz = matlab_xyz / np.linalg.norm(matlab_xyz)
        return camera_xyz

    def get_image_coords_to_3d_position(self, global_pos):
        global_pos = global_pos / np.linalg.norm(global_pos)
        global_pos = global_pos.flatten()

        cosang_array = np.tensordot(self.distance_direction_array, global_pos, axes=((2), (0)))
        cosang_array = cosang_array.flatten()
        # direction_vector_array = np.reshape(self.distance_direction_array, (self.distance_direction_array.shape[0]*self.distance_direction_array.shape[1], 3))
        pos_vector_array = np.full(self.distance_direction_array.shape, global_pos)
        cross_array = np.cross(self.distance_direction_array, pos_vector_array)
        sinang_array = np.linalg.norm(cross_array, axis=-1)
        sinang_array = sinang_array.flatten()
        angle_array = np.absolute(np.arctan2(sinang_array, cosang_array))
        min_index = np.argmin(angle_array)
        u, v = divmod(min_index, self.distance_direction_array.shape[1])
        return u, v

    def collect_norms(self, image_size):
        array = np.zeros(shape=(image_size[1], image_size[0], 3))
        for pos in product(range(image_size[1]), range(image_size[0])):
            ray = self.get_camera_ray(pos[0], pos[1])
            array[pos] = np.array([ray[0][0], ray[1][0], ray[2][0]])
        return array

    def estimate_positions_for_track(self, track):
        boxes = {}
        for frame in range(0, track.last_detected_frame):
            box = track.get_box(frame)
            if box is None:
                continue
            boxes[frame] = [int(round(x)) for x in box]

        self.own_position_extractor.init_yaw_matrix()

        positions = {}
        relative_pos = {}
        if len(boxes) > 0:
            for frame, box in boxes.items():
                camera_xyz = self.get_camera_ray(u=(box[2] + box[0]) / 2, v=box[3])
                car_xyz = self.camera_car_rotation.apply(camera_xyz.flatten())
                car_xyz = car_xyz / np.linalg.norm(car_xyz)
                pitch_matrix, yaw_matrix, roll_matrix = self.own_position_extractor.rotation(frame)

                car_xyz = np.array([[car_xyz[0]],[car_xyz[1]],[car_xyz[2]]])
                roll_pitch_matrix = np.dot(pitch_matrix, roll_matrix)
                world_xyz = np.dot(roll_pitch_matrix, car_xyz).flatten()

                t = self.camera_height / world_xyz[1]
                x = world_xyz[0] * t
                y = world_xyz[2] * t
                rel_car_pos_world = [[x], [y], [0]]
                if (y > 0) and (y < 75) and (x > -50) and (x < 50):
                    relative_pos[frame] = [[x], [y], [0]]

                    rel_world_xyz = np.dot(yaw_matrix, rel_car_pos_world)
                    own_position = self.own_position_extractor.position(frame)

                    x = rel_world_xyz[0][0] + own_position[0][0]
                    y = rel_world_xyz[1][0] + own_position[1][0]

                    lat, long = self.geo.meter_to_lat_long(x, y)
                    try:
                        elevation = self.geo.get_elevation(lat=lat, long=long)
                    except UserWarning:
                        elevation = 0
                    positions[frame] = [[x], [y], [elevation]]

        return positions, relative_pos
