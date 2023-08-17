from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionUpscalePipeline

import os
import click
from xformers.ops import MemoryEfficientAttentionFlashAttentionOp
import shutil


from PIL import Image
from diffusers import StableDiffusionUpscalePipeline
import torch
from split_image import split
import os
import random


def split_image(im, rows, cols, should_square, should_quiet=False):
    im_width, im_height = im.size
    row_width = int(im_width / cols)
    row_height = int(im_height / rows)
    name = "image"
    ext = ".png"
    name = os.path.basename(name)
    images = []
    if should_square:
        min_dimension = min(im_width, im_height)
        max_dimension = max(im_width, im_height)
        if not should_quiet:
            print("Resizing image to a square...")
            print("Determining background color...")
        bg_color = split.determine_bg_color(im)
        if not should_quiet:
            print("Background color is... " + str(bg_color))
        im_r = Image.new("RGBA" if ext == "png" else "RGB",
                         (max_dimension, max_dimension), bg_color)
        offset = int((max_dimension - min_dimension) / 2)
        if im_width > im_height:
            im_r.paste(im, (0, offset))
        else:
            im_r.paste(im, (offset, 0))
        im = im_r
        row_width = int(max_dimension / cols)
        row_height = int(max_dimension / rows)
    n = 0
    for i in range(0, rows):
        for j in range(0, cols):
            box = (j * row_width, i * row_height, j * row_width +
                   row_width, i * row_height + row_height)
            outp = im.crop(box)
            outp_path = name + "_" + str(n) + ext
            if not should_quiet:
                print("Exporting image tile: " + outp_path)
            images.append(outp)
            n += 1
    return [img for img in images]




# load model and scheduler
def load_pipe(lower_memory: bool = False):
    model_id = "stabilityai/stable-diffusion-x4-upscaler"
    pipeline = StableDiffusionUpscalePipeline.from_pretrained(
        model_id,
        revision="fp16",
        torch_dtype=torch.float16,
        scale_factor=0.08333,

    )
    pipeline.enable_xformers_memory_efficient_attention()
    if lower_memory:
        # pipeline.enable_xformers_memory_efficient_attention(attention_op=MemoryEfficientAttentionFlashAttentionOp)
        pipeline.enable_attention_slicing()
        pipeline.enable_model_cpu_offload()
        pipeline = pipeline.to("cpu")
    else:

        pipeline = pipeline.to("cuda")
    return pipeline


@torch.no_grad()
def upscale_image(
        pipeline,
        img,
        rows,
        cols,
        seed,
        prompt,
        negative_prompt="",
        enable_custom_sliders=False,
        guidance=7,
        iterations=50
):
    # img = Image.fromarray(img)
    # load model and scheduler
    if seed == -1:
        generator = torch.manual_seed(random.randint(0, 9999999))
    else:
        generator = torch.manual_seed(seed)

    original_width, original_height = img.size
    max_dimension = max(original_width, original_height)
    tiles = split_image(img, rows, cols, True, False)
    ups_tiles = []
    i = 0
    for x in tiles:
        i = i + 1
        if enable_custom_sliders:
            ups_tile = pipeline(prompt=prompt, negative_prompt=negative_prompt, guidance_scale=guidance,
                                num_inference_steps=iterations, image=x.convert("RGB"), generator=generator).images[0]
        else:
            ups_tile = pipeline(prompt=prompt, negative_prompt=negative_prompt, image=x.convert("RGB"),
                                generator=generator).images[0]
        ups_tiles.append(ups_tile)

    # Determine the size of the merged upscaled image
    total_width = 0
    total_height = 0
    side = 0
    for ups_tile in ups_tiles:
        side = ups_tile.width
        break
    for x in tiles:
        tsize = x.width
        break

    ups_times = abs(side / tsize)
    new_size = (max_dimension * ups_times, max_dimension * ups_times)
    total_width = cols * side
    total_height = rows * side

    # Create a blank image with the calculated size
    merged_image = Image.new("RGB", (total_width, total_height))

    # Paste each upscaled tile into the blank image
    current_width = 0
    current_height = 0
    maximum_width = cols * side
    for ups_tile in ups_tiles:
        merged_image.paste(ups_tile, (current_width, current_height))
        current_width += ups_tile.width
        if current_width >= maximum_width:
            current_width = 0
            current_height = current_height + side

    # Using the center of the image as pivot, crop the image to the original dimension times four
    crop_left = (new_size[0] - original_width * ups_times) // 2
    crop_upper = (new_size[1] - original_height * ups_times) // 2
    crop_right = crop_left + original_width * ups_times
    crop_lower = crop_upper + original_height * ups_times
    final_img = merged_image.crop((crop_left, crop_upper, crop_right, crop_lower))
    del merged_image
    del tiles
    # The resulting image should be identical to the original image in proportions / aspect ratio, with no loss of elements.
    # Save the merged image
    return final_img


@click.command(
    help="Upscale images using Stable Diffusion Upscaler"
)
@click.option("--input-dir", "-i", type=str, help="source directory", required=True)
@click.option("--output-dir", "-o", type=str, help="destination directory", required=True)
@click.option("--lower-memory", "-m", type=bool, default=False, help="lower memory usage")
@click.option("--skip-exist", "-s", type=bool, default=True, help="skip existing files")
@click.option("--sd-limit", "-l", type=int, default=262144, help="sd image size limit, sd1.5: 262144, sdxl: 950272")
@click.option("--guidance-scale", "-g", type=float, default=0.75, help="guidance scale")
@click.option("--onnx", "-x", type=bool, default=False, help="use onnx model")
def up_scale(
        input_dir: str,
        output_dir: str,
        lower_memory: bool = False,
        skip_exist: bool = True,
        sd_limit: int = 262144,
        guidance_scale: float = 0.75,
        onnx: bool = False
):
    if onnx:
        pipeline = load_onnx_pipe()
    else:
        pipeline = load_pipe(lower_memory)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    fns = get_image_files(input_dir)
    fns_map = {}
    for fn in fns:
        text_fn = f"{os.path.splitext(os.path.basename(fn))[0]}.txt"
        text_fn = os.path.join(os.path.dirname(fn), text_fn)
        if not os.path.exists(text_fn):
            print(f"ignore {text_fn}")
            continue
        fns_map[fn] = text_fn

    for image_fn, text_fn in fns_map.items():
        output_fn = os.path.join(output_dir, f"{os.path.basename(image_fn)}")
        if skip_exist and os.path.exists(output_fn):
            exist_image = Image.open(output_fn)  # .convert("RGB")
            hight, width = exist_image.size
            if hight * width > sd_limit:
                print(f"skip exist {output_fn},{hight}*{width}, size: {hight * width} > {sd_limit}")
                continue

            low_res_img = Image.open(output_fn)  # .convert("RGB")
        else:

            low_res_img = Image.open(image_fn)  # .convert("RGB")
        # low_res_img = low_res_img.resize((128, 128))
        hight, width = low_res_img.size
        if hight * width > sd_limit:
            print(f"copy org {output_fn}, size: {hight * width} > {sd_limit}")
            shutil.copy(image_fn, output_fn)
        prompt = open(text_fn, "r", encoding="utf-8").read()
        prompt = prompt.split(",")[0]

        upscaled_image = \
            upscale_image(pipeline=pipeline, img=low_res_img, rows=3, cols=3, seed=-1, prompt=prompt,
                          guidance=guidance_scale, iterations=50)

        up_high, up_width = upscaled_image.size

        if up_high * up_width < sd_limit:
            print(f"up scale *2 {output_fn},{up_high}*{up_width}, size: {up_high * up_width} < {sd_limit}")
            upscaled_image = \
                upscale_image(pipeline=pipeline, img=low_res_img, rows=3, cols=3, seed=-1, prompt=prompt,
                              guidance=guidance_scale, iterations=50)

        print(f"save {output_fn}")
        upscaled_image.save(output_fn)
        del upscaled_image
        del low_res_img


if __name__ == '__main__':
    up_scale()