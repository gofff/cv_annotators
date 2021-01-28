import sys
import os

from cv_annotators.circle_center import CircleCenterAnnotator


if __name__ == '__main__':

    cca = CircleCenterAnnotator()
    cca.annotate_path(sys.argv[1], sys.argv[2], False)