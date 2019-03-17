from PIL import Image, ImageDraw, ImageFont


def text_wrap(text, font, max_width):
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(' ')
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = ''
            while i < len(words) and font.getsize(line +
                                                  words[i])[0] <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word,
            # add the line to the lines array
            lines.append(line)
    return lines


def hextorgb(hex: str):
    hex = hex[1:]
    return tuple(int(hex[i:i + 2], 16) for i in range(0, len(hex), 2))


def draw_round_rectangles(draw: ImageDraw.ImageDraw,
                          left_top,
                          right_bottom,
                          radius,
                          fill: str or tuple = 'black'):
    if fill[0] == '#':
        fill = hextorgb(fill)
    width = right_bottom[0] - left_top[0]
    height = right_bottom[1] - left_top[0]
    draw.rectangle(
        (tuple(p + radius
               for p in left_top), tuple(p - radius for p in right_bottom)),
        fill=fill)
    draw.rectangle(((left_top[0] + radius, left_top[1]),
                    (left_top[0] + width - radius, left_top[1] + radius)),
                   fill=fill)
    draw.rectangle(((left_top[0], left_top[1] + radius),
                    (left_top[0] + radius, right_bottom[1] - radius)),
                   fill=fill)
    draw.rectangle(((right_bottom[0] - radius, left_top[1] + radius),
                    (right_bottom[0], right_bottom[1] - radius)),
                   fill=fill)
    draw.rectangle(((left_top[0] + radius, right_bottom[1] - radius),
                    (right_bottom[0] - radius, right_bottom[1])),
                   fill=fill)
    draw.pieslice(
        (left_top, (left_top[0] + radius * 2, left_top[1] + radius * 2)),
        start=-180,
        end=-90,
        fill=fill,
    )
    draw.pieslice(
        ((right_bottom[0] - radius * 2, left_top[1]),
         (right_bottom[0], left_top[1] + radius * 2)),
        start=-90,
        end=-0,
        fill=fill,
    )
    draw.pieslice(
        ((left_top[0], right_bottom[1] - 2 * radius),
         (left_top[0] + 2 * radius, right_bottom[1])),
        start=90,
        end=180,
        fill=fill,
    )
    draw.pieslice(
        ((right_bottom[0] - radius * 2, right_bottom[1] - 2 * radius),
         right_bottom),
        start=0,
        end=90,
        fill=fill,
    )


# BACKGROUND = hextorgb('#040505')
# BLOCKS = hextorgb('#EEAF5A')
# TEXT = hextorgb('#514C18')
BACKGROUND = hextorgb('#F8F7F8')
BLOCKS = hextorgb('#020203')
BLOCK_BORDERS = hextorgb('#E0AE4D')
BLOCK_BINDINGS = hextorgb('#4E515E')
TEXT = hextorgb('#F8F7F8')

blocks_mode = (2, 2)
block_size = (600, 600)
margin = (40, 40)
padding = (60, 60)
block_radius = 80
block_binding_width = 30

font = ImageFont.truetype('consola.ttf', size=80, encoding='utf-8')
line_height = font.getsize('hg')[1]

img = Image.new(
    'RGB', (
        blocks_mode[0] * (block_size[0] + margin[0]) + margin[0],
        blocks_mode[1] * (block_size[1] + margin[1]) + margin[1],
    ),
    color=BACKGROUND)
draw = ImageDraw.Draw(img)

# Available fields
# - mode [text, image]
# - content [text, path]
# - bound_to_right [bool]
# - with_padding [bool]
# - with_mask [bool]
# -

contents = [
    # Write here data in dicts {}, {}, {}
]

index = -1
for y_index in range(blocks_mode[1]):
    block_y = y_index * (block_size[1] + margin[1])
    for x_index in range(blocks_mode[0]):
        index += 1
        block_x = x_index * (block_size[0] + margin[0])
        print((block_x + margin[0], block_y + margin[1]))
        if contents[index].get('bound_to_right'):
            draw.rectangle(
                ((block_x + margin[0] + block_size[0], block_y + margin[1] +
                  block_size[1] // 2 - block_binding_width // 2),
                 (block_x + margin[0] * 2 + block_size[0], block_y + margin[1]
                  + block_size[1] // 2 + block_binding_width // 2)),
                fill=BLOCK_BINDINGS)
        draw.rectangle(((block_x + margin[0], block_y + margin[1]),
                        (block_x + margin[0] + block_size[0],
                         block_y + margin[1] + block_size[1])),
                       fill=BLOCKS,
                       outline=None)

        if contents[index]['mode'] == 'text':
            lines = []
            for p in contents[index]['content'].split('\n'):
                lines += text_wrap(
                    p, font, block_size[0] -
                    (padding[0] if contents[index].get('with_padding') else 0)
                    * 2)
            x = block_x + margin[0] + (
                padding[0] if contents[index].get('with_padding') else 0)
            y = block_y + margin[1] + (
                padding[1] if contents[index].get('with_padding') else 0)
            for line in lines:
                draw.text((
                    x,
                    y,
                ), line, font=font, fill=TEXT)
                y += line_height
        elif contents[index]['mode'] == 'image':
            current_img = Image.open(contents[index]['content'])
            if contents[index].get('with_padding'):
                current_img.thumbnail((block_size[0] - padding[0] * 2,
                                       block_size[1] - padding[1] * 2))
                img.paste(current_img, (block_x + margin[0] + padding[0],
                                        block_y + margin[1] + padding[1]),
                          current_img if contents[index].get('with_mask') else None)
            else:
                current_img.thumbnail((block_size[0], block_size[1]))
                img.paste(current_img,
                          (block_x + margin[0], block_y + margin[1]),
                          current_img if contents[index].get('with_mask') else None)

img.save("Test.png")

if __name__ == '__main__':
    pass
