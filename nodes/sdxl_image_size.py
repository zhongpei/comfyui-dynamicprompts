import math

RESOLUTIONS_W = [
    # SDXL Base resolution
    {"width": 1024, "height": 1024},
    # SDXL Resolutions, widescreen
    {"width": 2048, "height": 512},
    {"width": 1984, "height": 512},
    {"width": 1920, "height": 512},
    {"width": 1856, "height": 512},
    {"width": 1792, "height": 576},
    {"width": 1728, "height": 576},
    {"width": 1664, "height": 576},
    {"width": 1600, "height": 640},
    {"width": 1536, "height": 640},
    {"width": 1472, "height": 704},
    {"width": 1408, "height": 704},
    {"width": 1344, "height": 704},
    {"width": 1344, "height": 768},
    {"width": 1280, "height": 768},
    {"width": 1216, "height": 832},
    {"width": 1152, "height": 832},
    {"width": 1152, "height": 896},
    {"width": 1088, "height": 896},
    {"width": 1088, "height": 960},
    {"width": 1024, "height": 960},
]
RESOLUTIONS_H = [
    # SDXL Resolutions, portrait
    {"width": 960, "height": 1024},
    {"width": 960, "height": 1088},
    {"width": 896, "height": 1088},
    {"width": 896, "height": 1152},
    {"width": 832, "height": 1152},
    {"width": 832, "height": 1216},
    {"width": 768, "height": 1280},
    {"width": 768, "height": 1344},
    {"width": 704, "height": 1408},
    {"width": 704, "height": 1472},
    {"width": 640, "height": 1536},
    {"width": 640, "height": 1600},
    {"width": 576, "height": 1664},
    {"width": 576, "height": 1728},
    {"width": 576, "height": 1792},
    {"width": 512, "height": 1856},
    {"width": 512, "height": 1920},
    {"width": 512, "height": 1984},
    {"width": 512, "height": 2048},
]
MIN_RESOLUTION = 950272
BASE_RESOLUTION = 1024 * 1024


class SDXLImageSize:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "max": 4096, "min": 64, "step": 1}),
                "height": ("INT", {"default": 1024, "max": 4096, "min": 64, "step": 1}),
                "scale_by": ("FLOAT", {"default": 1.0, "max": 2.0, "min": 0.5, "step": 0.1})

            }
        }

    RETURN_TYPES = ("INT", "INT", "FLOAT")
    RETURN_NAMES = ("WIDTH", "HEIGHT", "SCALE_BY")
    FUNCTION = "get_image_size"
    OUTPUT_NODE = True
    CATEGORY = "fofo/image"

    def get_image_size(self, width: int, height: int, scale_by: float) -> tuple[int, int, float]:
        best_resolution = None
        min_difference = float('inf')

        scale = (width * height) / MIN_RESOLUTION

        scale = math.sqrt(scale)

        scale_by_out = 1 / math.sqrt((width * height) / BASE_RESOLUTION)
        scale_by_out = scale_by_out * scale_by
        scale_by_out = scale_by_out * width // 64 * 64 / width
        scale_by_out = scale_by_out * height // 64 * 64 / height

        print(f"Min resolution: {MIN_RESOLUTION}")
        print(f"Scale: {scale} width: {width} height: {height},scale_by:{scale_by_out}")
        width = int(width / scale)
        height = int(height / scale)
        print(f"Scale: {scale} width: {width} height: {height}")
        if width >= height:
            resolutions = RESOLUTIONS_W
        else:
            resolutions = RESOLUTIONS_H
        for resolution in resolutions:
            width_diff = abs(resolution["width"] - width)
            height_diff = abs(resolution["height"] - height)

            total_diff = width_diff + height_diff
            if total_diff < min_difference:
                min_difference = total_diff
                best_resolution = resolution

        output_width = best_resolution["width"]
        output_height = best_resolution["height"]
        if scale_by != 1.0:
            output_height = int(output_height * scale_by) // 64 * 64
            output_width = int(output_width * scale_by) // 64 * 64
        print(
            f"Closest resolution: {best_resolution} width: {output_width} height: {output_height}"
        )
        return output_width, output_height, scale_by_out
