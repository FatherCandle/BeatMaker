from collections import defaultdict, namedtuple
from typing import List
from xmlrpc.client import boolean
import pygame
from pygame import Rect, mixer
from screeninfo import get_monitors

Point = namedtuple("Point", ["x", "y"])
BeatBox = namedtuple("BeatBox", ["rect", "cordinates"])
Instrument = namedtuple("Instrument", ["id", "text", "sound"])

pygame.init()
# primary_monitor = next(m for m in get_monitors() if m.is_primary)
WIDTH = 1400  # primary_monitor.width
HEIGHT = 800  # primary_monitor.height - 50


class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    GREEN = (0, 255, 0)
    GOLD = (212, 175, 55)
    BLUE = (0, 255, 255)


screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Beat Maker")

label_font = pygame.font.Font("freesansbold.ttf", 32)
fps = 144
timer = pygame.time.Clock()
beat_count = 8
boxes = []
clicked = defaultdict(boolean)
bpm = 240  # 240 = 4 beats per second
is_playing = True
current_beat_index = 0
current_beat_length = 0

# Sets the instruments labels and lines in the left tray
instruments = [
    Instrument(0, "Hi Hat", mixer.Sound(r"sounds\hi hat.wav")),
    Instrument(1, "Snare", mixer.Sound(r"sounds\snare.wav")),
    Instrument(2, "Bass drum", mixer.Sound(r"sounds\bass.wav")),
    Instrument(3, "Crash", mixer.Sound(r"sounds\crash.wav")),
    Instrument(4, "Clap", mixer.Sound(r"sounds\clap.wav")),
    Instrument(5, "Floor Tom", mixer.Sound(r"sounds\tom.wav")),
]
pygame.mixer.set_num_channels(len(instruments) * 3)


def play_notes(clicked, current_beat_index):
    for instrument in instruments:
        if clicked[(instrument.id, current_beat_index)]:
            instrument.sound.play()


def draw_grid(screen, clicked, current_beat_index) -> List[BeatBox]:
    ret_rects = defaultdict(None)
    instruments_count = len(instruments)
    LEFT_TRAY_WIDTH = 200
    BOT_TRAY_HEIGHT = 200
    INSTRUMENT_BOX_HEIGHT = (HEIGHT - BOT_TRAY_HEIGHT) // instruments_count
    BEAT_BOX_WIDTH = (WIDTH - LEFT_TRAY_WIDTH) // beat_count

    # Drawing the left panel with the instruments texts
    left_box = pygame.draw.rect(
        screen, Colors.GRAY, [0, 0, LEFT_TRAY_WIDTH, HEIGHT - BOT_TRAY_HEIGHT], 5
    )

    instruments_labels = []
    INSTRUMENT_LABEL_X = 30
    instrument_label_y = 30
    line_under_instrument_y = INSTRUMENT_BOX_HEIGHT
    for instrument in instruments:

        pygame.draw.line(
            screen,
            Colors.GRAY,
            (0, line_under_instrument_y),
            (LEFT_TRAY_WIDTH, line_under_instrument_y),
            3,
        )
        line_under_instrument_y += INSTRUMENT_BOX_HEIGHT

        instruments_labels.append(
            (
                label_font.render(instrument.text, True, Colors.WHITE),
                (INSTRUMENT_LABEL_X, instrument_label_y),
            )
        )
        instrument_label_y += INSTRUMENT_BOX_HEIGHT
    screen.blits(instruments_labels)

    # Darwing the bottom panel with the functionallity buttons
    bottom_box = pygame.draw.rect(
        screen, Colors.GRAY, [0, HEIGHT - BOT_TRAY_HEIGHT, WIDTH, BOT_TRAY_HEIGHT], 5
    )

    func_bottuns = []
    play_pause_rect = pygame.draw.rect(
        surface=screen,
        color=Colors.GRAY,
        rect=(
            INSTRUMENT_LABEL_X - 10,
            HEIGHT - BOT_TRAY_HEIGHT + 30,
            BEAT_BOX_WIDTH,
            INSTRUMENT_BOX_HEIGHT,
        ),
    )
    play_pause_label = (
        label_font.render("Pause" if is_playing else "Play", True, Colors.WHITE),
        (INSTRUMENT_LABEL_X + 10, HEIGHT - BOT_TRAY_HEIGHT + 60),
    )
    func_bottuns.append(play_pause_label)
    screen.blits(func_bottuns)
    ret_rects["play pause btn"] = play_pause_rect

    # Drawing the middle section with the beats
    boxes = []
    for instrument in instruments:
        for beat_index in range(beat_count):
            beat_box_rect = Rect(
                LEFT_TRAY_WIDTH + beat_index * BEAT_BOX_WIDTH,
                instrument.id * INSTRUMENT_BOX_HEIGHT,
                BEAT_BOX_WIDTH,
                INSTRUMENT_BOX_HEIGHT,
            )
            beat_box = pygame.draw.rect(
                surface=screen,
                color=Colors.GREEN
                if clicked[(instrument.id, beat_index)]
                else Colors.GRAY,
                rect=beat_box_rect,
                width=0,
                border_radius=5,
            )
            # Border of the beat box
            pygame.draw.rect(
                surface=screen,
                color=Colors.GOLD,
                rect=beat_box_rect,
                width=3,
                border_radius=5,
            )
            boxes.append(BeatBox(beat_box, Point(instrument.id, beat_index)))

    active_beat_rect = Rect(
        LEFT_TRAY_WIDTH + current_beat_index * BEAT_BOX_WIDTH,
        0,
        BEAT_BOX_WIDTH,
        INSTRUMENT_BOX_HEIGHT * instruments_count,
    )
    pygame.draw.rect(
        surface=screen,
        color=Colors.BLUE,
        rect=active_beat_rect,
        width=5,
        border_radius=5,
    )
    ret_rects["beat boxes"] = boxes
    return ret_rects


# Main game loop
run = True

while run:
    timer.tick(fps)
    screen.fill(Colors.BLACK)

    rect_objects = draw_grid(screen, clicked, current_beat_index)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for box in rect_objects["beat boxes"]:
                if box.rect.collidepoint(event.pos):
                    clicked[box.cordinates] = not clicked[box.cordinates]

            if rect_objects["play pause btn"].collidepoint(event.pos):
                is_playing = not is_playing

    beat_length = 60 * fps // bpm
    if is_playing:
        if current_beat_length == 0:
            current_beat_index = (current_beat_index + 1) % beat_count
            play_notes(clicked, current_beat_index)
        current_beat_length = (current_beat_length + 1) % beat_length

    pygame.display.flip()
pygame.quit()
