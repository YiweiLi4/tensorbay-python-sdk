#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Box2D, Box3D.

:class:`Box2D` contains the information of a 2D bounding box, such as the coordinates,
width and height.
It provides :meth:`Box2D.iou` to calculate the intersection over union of two 2D boxes.

:class:`Box3D` contains the information of a 3D bounding box such as the transform,
translation, rotation and size.
It provides :meth:`Box3D.iou` to calculate the intersection over union of two 3D boxes.

"""

from typing import Dict, Iterable, Optional, Tuple, Type, TypeVar, Union

from ..utility import ReprMixin, ReprType, UserSequence, common_loads
from .quaternion import Quaternion
from .transform import Transform3D
from .vector import Vector2D, Vector3D

_T = TypeVar("_T", bound="Box3D")


class Box2D(UserSequence[float]):
    """This class defines the concept of Box2D.

    :class:`Box2D` contains the information of a 2D bounding box, such as the coordinates,
    width and height.
    It provides :meth:`Box2D.iou` to calculate the intersection over union of two 2D boxes.

    Arguments:
        args: Coordinates of a 2D bounding box:

            .. code:: python

                box = Box2D()
                box = Box2D(10, 20, 30, 40)
                box = Box2D([10, 20, 30, 40])

        x: X coordinate of the top left vertex of the box.
        y: Y coordinate of the top left vertex of the box.
        width: Length along the x axis.
        height: Length along the y axis.

    Raises:
        TypeError: If input parameters do not meet the requirement.

    """

    _T = TypeVar("_T", bound="Box2D")

    _repr_type = ReprType.INSTANCE

    _LENGTH = 4

    def __init__(
        self,
        *args: Union[None, float, Iterable[float]],
        x: Optional[float] = None,
        y: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> None:
        if x is not None or y is not None or width is not None or height is not None:
            try:
                xmin: float = x  # type: ignore[assignment]
                ymin: float = y  # type: ignore[assignment]
                xmax = x + width  # type: ignore[operator]
                ymax = y + height  # type: ignore[operator]
            except TypeError as error:
                raise TypeError(
                    "Require x, y, width, height keyword arguments to construct a 2D box."
                ) from error
        else:
            arg: Optional[Iterable[float]]
            arg = args[0] if len(args) == 1 else args  # type: ignore[assignment]
            if arg is None:
                self._data = (0.0,) * Box2D._LENGTH
                return

            try:
                xmin, ymin, xmax, ymax = arg
            except (ValueError, TypeError) as error:
                raise TypeError(
                    f"Require 4 dimensional data to construct {self.__class__.__name__}."
                ) from error

        if xmin >= xmax or ymin >= ymax:
            self._data = (0.0,) * Box2D._LENGTH
        else:
            self._data = (xmin, ymin, xmax, ymax)

    def __len__(self) -> int:
        return Box2D._LENGTH

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)
        return False

    def __and__(self, other: "Box2D") -> "Box2D":
        """Calculate the intersect box of two boxes.

        Arguments:
            other: The other box.

        Returns:
            The intersect box of the two boxes.

        """
        xmin = max(self._data[0], other._data[0])
        ymin = max(self._data[1], other._data[1])
        xmax = min(self._data[2], other._data[2])
        ymax = min(self._data[3], other._data[3])
        return Box2D(xmin, ymin, xmax, ymax)

    def _loads(self, contents: Dict[str, float]) -> None:
        self._data = (contents["xmin"], contents["ymin"], contents["xmax"], contents["ymax"])

    def _repr_head(self) -> str:
        """Return basic information of the Box2D.

        Returns:
            Basic information of the Box2D.

        """
        return f"{self.__class__.__name__}{self._data}"

    @staticmethod
    def iou(box1: "Box2D", box2: "Box2D") -> float:
        """Calculate the intersection over union of two 2D boxes.

        Arguments:
            box1: A 2D box.
            box2: A 2D box.

        Returns:
            The intersection over union between the two input boxes.

        """
        area1 = box1.area()
        area2 = box2.area()
        intersect_box = box1 & box2
        intersect = intersect_box.area()
        union = area1 + area2 - intersect
        return intersect / union

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, float]) -> _T:
        """Load a :class:`Box2D` from a dict containing coordinates of the 2D box.

        Arguments:
            contents: A dict containing coordinates of a 2D box::

                {
                    "xmin": ...
                    "ymin": ...
                    "xmax": ...
                    "ymax": ...
                }

        Returns:
            The loaded :class:`Box2D` object.

        """
        return common_loads(cls, contents)

    @property
    def xmin(self) -> float:
        """Return the minimum x coordinate.

        Returns:
            Minimum x coordinate.

        """
        return self._data[0]

    @property
    def ymin(self) -> float:
        """Return the minimum y coordinate.

        Returns:
            Minimum y coordinate.

        """
        return self._data[1]

    @property
    def xmax(self) -> float:
        """Return the maximum x coordinate.

        Returns:
            Maximum x coordinate.

        """
        return self._data[2]

    @property
    def ymax(self) -> float:
        """Return the maximum y coordinate.

        Returns:
            Maximum y coordinate.

        """
        return self._data[3]

    @property
    def tl(self) -> Vector2D:  # pylint: disable=invalid-name
        """Return the top left point.

        Returns:
            The top left point.

        """
        return Vector2D(self._data[:2])

    @property
    def br(self) -> Vector2D:  # pylint: disable=invalid-name
        """Return the bottom right point.

        Returns:
            The bottom right point.

        """
        return Vector2D(self._data[2:])

    @property
    def width(self) -> float:
        """Return the width of the 2D box.

        Returns:
            The width of the 2D box.

        """
        return self._data[2] - self._data[0]

    @property
    def height(self) -> float:
        """Return the height of the 2D box.

        Returns:
            The height of the 2D box.

        """
        return self._data[3] - self._data[1]

    def dumps(self) -> Dict[str, float]:
        """Dumps a 2D box into a dict.

        Returns:
            A dict containing vertex coordinates of the box.

        """
        return {
            "xmin": self._data[0],
            "ymin": self._data[1],
            "xmax": self._data[2],
            "ymax": self._data[3],
        }

    def area(self) -> float:
        """Return the area of the 2D box.

        Returns:
            The area of the 2D box.

        """
        return self.width * self.height


class Box3D(ReprMixin):
    """This class defines the concept of Box3D.

    :class:`Box3D` contains the information of a 3D bounding box such as the transform,
    translation, rotation and size.
    It provides :meth:`Box3D.iou` to calculate the intersection over union of two 3D boxes.

    Arguments:
        transform: A :class:`~tensorbay.geometry.transform.Transform3D` object
            or a 4x4 or 3x4 transform matrix.
        translation: Translation in a sequence of [x, y, z].
        rotation: Rotation in a sequence of [w, x, y, z] or a 3x3 rotation matrix
            or a :class:`~tensorbay.geometry.quaternion.Quaternion` object.
        size: Size in a sequence of [x, y, z].
        **kwargs: Other parameters to initialize rotation of the transform.
            See :class:`~tensorbay.geometry.quaternion.Quaternion` documents for details.

    """

    _repr_type = ReprType.INSTANCE
    _repr_attrs: Tuple[str, ...] = ("translation", "rotation", "size")

    def __init__(
        self,
        transform: Transform3D.TransformType = None,
        *,
        translation: Optional[Iterable[float]] = None,
        rotation: Quaternion.ArgsType = None,
        size: Optional[Iterable[float]] = None,
        **kwargs: Quaternion.KwargsType,
    ) -> None:
        self._transform = Transform3D(
            transform, translation=translation, rotation=rotation, **kwargs
        )
        self._size = Vector3D(size)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._size.__eq__(other._size) and self._transform.__eq__(other._transform)
        return False

    def __rmul__(self: _T, other: Transform3D) -> _T:
        if isinstance(other, Transform3D):
            box: _T = object.__new__(self.__class__)
            box._transform = other * self._transform
            box._size = self._size
            return box

        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    def _line_intersect(length1: float, length2: float, midpoint_distance: float) -> float:
        """Calculate the intersect length between two parallel lines.

        Arguments:
            length1: The length of line1.
            length2: the length of line2.
            midpoint_distance: The distance between midpoints of the two lines.

        Returns:
            The intersect length between line1 and line2.

        """
        line1_min = -length1 / 2
        line1_max = length1 / 2
        line2_min = -length2 / 2 + midpoint_distance
        line2_max = length2 / 2 + midpoint_distance
        intersect_length = min(line1_max, line2_max) - max(line1_min, line2_min)
        return intersect_length if intersect_length > 0 else 0

    def _loads(self, contents: Dict[str, Dict[str, float]]) -> None:
        self._size = Vector3D.loads(contents["size"])
        self._transform = Transform3D.loads(contents)

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Dict[str, float]]) -> _T:
        """Load a :class:`Box3D` from a dict containing the coordinates of the 3D box.

        Arguments:
            contents: A dict containing the coordinates of a 3D box::

                {
                    "size": {
                        "x": ...
                        "y": ...
                        "z": ...
                    },
                    "translation": {
                        "x": ...
                        "y": ...
                        "z": ...
                    },
                    "rotation": {
                        "w": ...
                        "x": ...
                        "y": ...
                        "z": ...
                    }
                }

        Returns:
            The loaded :class:`Box3D` object.

        """
        return common_loads(cls, contents)

    @classmethod
    def iou(cls, box1: "Box3D", box2: "Box3D", angle_threshold: float = 5) -> float:
        """Calculate the intersection over union between two 3D boxes.

        Arguments:
            box1: A 3D box.
            box2: A 3D box.
            angle_threshold: The threshold of the relative angles
                between two input 3d boxes in degree.

        Returns:
            The intersection over union of the two 3D boxes.

        """
        box2 = box1.transform.inverse() * box2
        if abs(box2.rotation.degrees) > angle_threshold:
            return 0

        intersect_size = [
            cls._line_intersect(*args) for args in zip(box1.size, box2.size, box2.translation)
        ]
        intersect = intersect_size[0] * intersect_size[1] * intersect_size[2]
        union = box1.volume() + box2.volume() - intersect
        return intersect / union

    @property
    def translation(self) -> Vector3D:
        """Return the translation of the 3D box.

        Returns:
            The translation of the 3D box.

        """
        return self._transform.translation

    @property
    def rotation(self) -> Quaternion:
        """Return the rotation of the 3D box.

        Returns:
            The rotation of the 3D box.

        """
        return self._transform.rotation

    @property
    def transform(self) -> Transform3D:
        """Return the transform of the 3D box.

        Returns:
            The transform of the 3D box.

        """
        return self._transform

    @property
    def size(self) -> Vector3D:
        """Return the size of the 3D box.

        Returns:
            The size of the 3D box.

        """
        return self._size

    def volume(self) -> float:
        """Return the volume of the 3D box.

        Returns:
            The volume of the 3D box.

        """
        return self.size.x * self.size.y * self.size.z

    def dumps(self) -> Dict[str, Dict[str, float]]:
        """Dumps the 3D box into a dict.

        Returns:
            A dict containing translation, rotation and size information.

        """
        contents = self._transform.dumps()
        contents["size"] = self.size.dumps()
        return contents
