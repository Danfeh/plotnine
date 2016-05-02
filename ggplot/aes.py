from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import re
from copy import deepcopy

import six

from .utils import suppress

__all__ = ['aes']

all_aesthetics = {
    'alpha', 'angle', 'color', 'colour', 'fill', 'group',
    'hjust', 'label', 'linetype', 'lower', 'lwd', 'middle',
    'order', 'radius', 'sample', 'shape', 'size', 'stroke',
    'upper', 'vjust', 'weight', 'width', 'x', 'xend', 'xmax',
    'xmin', 'xintercept', 'y', 'yend', 'ymax', 'ymin',
    'yintercept', 'z'}


class aes(dict):
    """
    Creates a dictionary that is used to evaluate
    things you're plotting. Most typically, this will
    be a column in a pandas DataFrame.

    Parameters
    -----------
    x : x-axis value
        Can be used for continuous (point, line) charts and for
        discrete (bar, histogram) charts.
    y : y-axis value
        Can be used for continuous charts only
    color (colour) : color of a layer
        Can be continuous or discrete. If continuous, this will be
        given a color gradient between 2 colors.
    shape : shape of a point
        Can be used only with geom_point
    size : size of a point or line
        Used to give a relative size for a continuous value
    alpha : transparency level of a point
        Number between 0 and 1. Only supported for hard coded values.
    ymin : min value for a vertical line or a range of points
        See geom_area, geom_ribbon, geom_vline
    ymax : max value for a vertical line or a range of points
        See geom_area, geom_ribbon, geom_vline
    xmin : min value for a horizonal line
        Specific to geom_hline
    xmax : max value for a horizonal line
        Specific to geom_hline
    slope : slope of an abline
        Specific to geom_abline
    intercept : intercept of an abline
        Specific to geom_abline

    Examples
    --------
    >>> aes(x='x', y='y')
    >>> aes('x', 'y')
    >>> aes(x='weight', y='height', color='salary')
    """

    DEFAULT_ARGS = ['x', 'y', 'color']

    def __init__(self, *args, **kwargs):
        kwargs = rename_aesthetics(kwargs)
        if args:
            dict.__init__(self, zip(self.DEFAULT_ARGS, args))
        if kwargs:
            self.update(kwargs)

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the environment
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        # Just copy the keys and point to the env
        for key, item in self.items():
            result[key] = deepcopy(self[key], memo)

        return result


def rename_aesthetics(d):
    with suppress(KeyError):
        d['color'] = d.pop('colour')

    with suppress(KeyError):
        d['outlier_color'] = d.pop('outlier_colour')
    return d


def is_calculated_aes(aesthetics):
    """
    Return a list of the aesthetics that are calculated
    """
    pattern = "^\.\.([a-zA-Z._]+)\.\.$"
    calculated_aesthetics = []
    for k, v in aesthetics.items():
        if not isinstance(v, six.string_types):
            continue
        if re.match(pattern, v):
            calculated_aesthetics.append(k)
    return calculated_aesthetics


def strip_dots(ae):
    with suppress(AttributeError):
        ae = ae.strip('..')
    return ae


def aes_to_scale(var):
    """
    Look up the scale that should be used for a given aesthetic
    """
    if var in {'x', 'xmin', 'xmax', 'xend', 'xintercept'}:
        var = 'x'
    elif var in {'y', 'ymin', 'ymax', 'yend', 'yintercept'}:
        var = 'y'
    return var


def is_position_aes(vars_):
    """
    Figure out if an aesthetic is a position aesthetic or not
    """
    try:
        return all([aes_to_scale(v) in {'x', 'y'} for v in vars_])
    except TypeError:
        return aes_to_scale(vars_) in {'x', 'y'}


def make_labels(mapping):
    """
    Convert aesthetic mapping into text labels
    """
    labels = mapping.copy()
    for ae in labels:
        labels[ae] = strip_dots(labels[ae])
    return labels