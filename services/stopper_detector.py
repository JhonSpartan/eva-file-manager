from ezdxf.layouts import Modelspace
from ezdxf.math import Vec2, intersect_polylines_2d
from ezdxf.path import Path, make_path

from models.stopper_candidate import StopperCandidate


class StopperDetector:

    FLATTENING_DISTANCE = 0.001
    INTERSECTION_TOLERANCE = 0.001

    def find_candidates(
            self,
            modelspace: Modelspace,
    ) -> list[StopperCandidate]:

        closed_paths = self._get_closed_paths(
            modelspace
        )

        if len(closed_paths) < 2:
            return []

        main_contour = max(
            closed_paths,
            key=lambda item: item.bbox_area,
        )

        main_points = self._flatten_path(
            main_contour.path
        )

        candidates = []

        for item in closed_paths:
            if item is main_contour:
                continue

            candidate_points = self._flatten_path(
                item.path
            )

            intersections = intersect_polylines_2d(
                candidate_points,
                main_points,
                abs_tol=self.INTERSECTION_TOLERANCE,
            )

            if intersections:
                continue

            candidates.append(item)

        return candidates

    def _get_closed_paths(
            self,
            modelspace: Modelspace,
    ) -> list[StopperCandidate]:

        result = []

        for entity in modelspace:
            if entity.dxf.layer.lower() != "main":
                continue

            try:
                path = make_path(entity)

            except TypeError:
                continue

            if not path.is_closed:
                continue

            bbox = path.bbox()

            if not bbox.has_data:
                continue

            width = (
                bbox.extmax.x
                - bbox.extmin.x
            )

            height = (
                bbox.extmax.y
                - bbox.extmin.y
            )

            result.append(
                StopperCandidate(
                    entity=entity,
                    path=path,
                    width=width,
                    height=height,
                    bbox_area=width * height,
                )
            )

        return result

    def _flatten_path(
            self,
            path: Path,
    ) -> list[Vec2]:

        return [
            Vec2(
                point.x,
                point.y,
            )
            for point in path.flattening(
                distance=self.FLATTENING_DISTANCE
            )
        ]