# import sys
# from pathlib import Path
#
# import ezdxf
# from ezdxf.math import Vec2, intersect_polylines_2d
# from ezdxf.path import make_path
#
#
# def inspect_file(file_path: Path) -> None:
#     document = ezdxf.readfile(file_path)
#     modelspace = document.modelspace()
#
#     print()
#     print("FILE:", file_path)
#     print()
#
#     entities = [
#         entity
#         for entity in modelspace
#         if entity.dxf.layer.lower() == "main"
#     ]
#
#     print(
#         "ENTITIES IN MAIN:",
#         len(entities),
#     )
#     print()
#
#     # Собираем данные обо всех замкнутых кривых.
#     paths_data = []
#
#     for entity in entities:
#         print(
#             entity.dxftype(),
#             "handle=",
#             entity.dxf.handle,
#         )
#
#         try:
#             path = make_path(entity)
#
#         except TypeError as error:
#             print(
#                 "  Path unsupported:",
#                 error,
#             )
#             print()
#             continue
#
#         print(
#             "  closed:",
#             path.is_closed,
#         )
#
#         # Для поиска main и stopper-кандидатов
#         # нас интересуют только замкнутые кривые.
#         if not path.is_closed:
#             print()
#             continue
#
#         bbox = path.bbox()
#
#         if not bbox.has_data:
#             print(
#                 "  bbox: no data"
#             )
#             print()
#             continue
#
#         width = (
#             bbox.extmax.x
#             - bbox.extmin.x
#         )
#
#         height = (
#             bbox.extmax.y
#             - bbox.extmin.y
#         )
#
#         bbox_area = width * height
#
#         print(
#             "  min:",
#             (
#                 round(bbox.extmin.x, 3),
#                 round(bbox.extmin.y, 3),
#             ),
#         )
#
#         print(
#             "  max:",
#             (
#                 round(bbox.extmax.x, 3),
#                 round(bbox.extmax.y, 3),
#             ),
#         )
#
#         print(
#             "  width:",
#             round(width, 3),
#         )
#
#         print(
#             "  height:",
#             round(height, 3),
#         )
#
#         print(
#             "  bbox area:",
#             round(bbox_area, 3),
#         )
#
#         paths_data.append(
#             {
#                 "entity": entity,
#                 "path": path,
#                 "width": width,
#                 "height": height,
#                 "bbox_area": bbox_area,
#             }
#         )
#
#         print()
#
#     # Если в main вообще нет замкнутых кривых,
#     # анализировать больше нечего.
#     if not paths_data:
#         print(
#             "No closed paths found in main"
#         )
#         return
#
#     # Самая большая замкнутая кривая по bbox
#     # считается основным контуром шаблона.
#     main_data = max(
#         paths_data,
#         key=lambda item: item["bbox_area"],
#     )
#
#     main_path = main_data["path"]
#
#     # Главный контур аппроксимируем один раз.
#     # Затем используем эти точки для проверки
#     # всех остальных замкнутых кривых.
#     main_points = [
#         Vec2(
#             point.x,
#             point.y,
#         )
#         for point in main_path.flattening(
#             distance=0.001
#         )
#     ]
#
#     print()
#     print("CLOSED PATH ANALYSIS:")
#     print()
#
#     for data in paths_data:
#         entity = data["entity"]
#         path = data["path"]
#
#         is_main = data is main_data
#
#         print(
#             entity.dxftype(),
#             "handle=",
#             entity.dxf.handle,
#         )
#
#         print(
#             "  width:",
#             round(
#                 data["width"],
#                 3,
#             ),
#         )
#
#         print(
#             "  height:",
#             round(
#                 data["height"],
#                 3,
#             ),
#         )
#
#         print(
#             "  bbox area:",
#             round(
#                 data["bbox_area"],
#                 3,
#             ),
#         )
#
#         print(
#             "  MAIN:",
#             is_main,
#         )
#
#         if not is_main:
#             candidate_points = [
#                 Vec2(
#                     point.x,
#                     point.y,
#                 )
#                 for point in path.flattening(
#                     distance=0.001
#                 )
#             ]
#
#             intersections = (
#                 intersect_polylines_2d(
#                     candidate_points,
#                     main_points,
#                     abs_tol=0.001,
#                 )
#             )
#
#             print(
#                 "  INTERSECTS MAIN:",
#                 bool(intersections),
#             )
#
#             print(
#                 "  INTERSECTION COUNT:",
#                 len(intersections),
#             )
#
#         print()
#
#
# def main() -> None:
#     if len(sys.argv) != 2:
#         print(
#             "Usage:"
#             " python -m scripts.inspect_main_geometry"
#             ' "path\\to\\file.dxf"'
#         )
#         return
#
#     file_path = Path(
#         sys.argv[1]
#     )
#
#     if not file_path.exists():
#         print(
#             "File not found:",
#             file_path,
#         )
#         return
#
#     inspect_file(
#         file_path
#     )
#
#
# if __name__ == "__main__":
#     main()



import sys
from pathlib import Path

import ezdxf

from services.stopper_detector import StopperDetector


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage:"
            " python -m scripts.test_stopper_detector"
            ' "path\\to\\file.dxf"'
        )
        return

    file_path = Path(
        sys.argv[1]
    )

    document = ezdxf.readfile(
        file_path
    )

    detector = StopperDetector()

    candidates = detector.find_candidates(
        document.modelspace()
    )

    print(
        "STOPPER CANDIDATES:",
        len(candidates),
    )

    for candidate in candidates:
        print(
            candidate.entity.dxftype(),
            "handle=",
            candidate.entity.dxf.handle,
            "width=",
            round(candidate.width, 3),
            "height=",
            round(candidate.height, 3),
        )


if __name__ == "__main__":
    main()