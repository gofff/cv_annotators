from typing import Any, Tuple, List
from cv_annotators.custom_types import Circle_t, Point_t

import cv2 
import numpy as np
import os
import random
import math

from cv_annotators.constants import KeyCode


def draw_circle(img: np.ndarray, center: Point_t,
                radius: float, mode: int = 0) -> np.ndarray:

    center_color = (200, 200, 200)
    edge_color = (200, 200, 0)
    thikness = 1
    if mode:
        edge_color = (0, 0, 200)

    # Draw center point
    cv2.circle(img, center, 2, center_color, cv2.FILLED)

    # Draw circle edge
    cv2.circle(img, center, int(radius), edge_color, 1)

    return img
    

def redraw(image: np.ndarray, circles: Circle_t) -> np.ndarray:
    proc_img = np.copy(image)
    for circle in circles:
        draw_circle(proc_img, circle[0], int(circle[1]))
    return proc_img


def estimate_radius(center_coord: Point_t, 
                    edge_coord: Point_t) -> float:

    diff = [(c1 - c2)**2 
            for c1, c2 in zip(center_coord, edge_coord)]
    return math.sqrt(sum(diff))


def mouse_callback(event: int, x: int, y: int, 
                       flags: int, param: Any) -> None:
    
    if event == cv2.EVENT_LBUTTONDOWN:
    
        if param['have_center']:
            param['finished'] = True
            param['have_center'] = False
            param['radius'] = estimate_radius(param['center'], (x, y))
        else:
            param['have_center'] = True
            param['finished'] = False
            param['center'] = (x, y)
            param['radius'] = 0.

    elif param['have_center'] and event == cv2.EVENT_MOUSEMOVE:

        param['radius'] = estimate_radius(param['center'], (x, y))

    return


class CircleCenterAnnotator:

    WINDOW_NAME = 'CircleCenterAnnotator'

    def __init__(self) -> None:
        self.draw_params = {
            'center': (0, 0),
            'radius': 0.,
            'have_center': False,
            'finished': False
        }
        cv2.namedWindow(self.WINDOW_NAME, flags=cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.WINDOW_NAME, mouse_callback, 
                             param = self.draw_params)

        self.exit_flag = False
        return


    def annotate_image(self, image: np.ndarray) -> List[Circle_t]:

        circles = []
        proc_img = np.copy(image)
        while True:
            cv2.imshow(self.WINDOW_NAME, proc_img)

            is_finished = self.draw_params['finished']
            have_center = self.draw_params['have_center']
            if have_center:
                proc_img = redraw(image, circles)
                proc_img = draw_circle(proc_img, 
                                       self.draw_params['center'], 
                                       int(self.draw_params['radius']),
                                       mode = 1)
            if is_finished:
                circles.append((self.draw_params['center'],
                                self.draw_params['radius']))
                self.draw_params['finished'] = False

            pressed_key = cv2.waitKey(1)

            if pressed_key == KeyCode.UNDO and circles:
                if have_center:
                    self.draw_params['have_center'] = False
                else:
                    circles.pop()
                proc_img = redraw(image, circles)


            if pressed_key == KeyCode.ESC:
                self.exit_flag = True
                break

            if pressed_key == KeyCode.NEXT:
                break

        return circles


    def annotate_path(self, path: str, out_path: str, 
                      shuffle: bool = False) -> None:

        filename_iterator = os.listdir(path)
        if shuffle:
            filename_iterator = [f for f in os.listdir(path)]
            random.shuffle(filename_iterator)

        for filename in filename_iterator:
            print(filename)
            file_ext = os.path.splitext(filename)[-1]
            out_filename = filename.replace(file_ext, '.txt')
            out_filename = os.path.join(out_path, out_filename)
            if os.path.exists(out_filename):
                continue

            img = cv2.imread(os.path.join(path, filename))
            circles = self.annotate_image(img)

            if self.exit_flag:
                break
            
            with open(out_filename, 'w') as outf:
                for center, radius in circles:
                    outf.write(f'{center[0]},{center[1]},')
                    outf.write(f'{radius}' + '\n')
        return


    def __del__(self) -> None:

        cv2.destroyWindow(self.WINDOW_NAME)
