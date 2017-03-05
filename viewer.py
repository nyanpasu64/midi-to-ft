#!/usr/bin/env python3

# TODO: (geometry)
# Retain geometry after reload
# Retain maximization, minimization after reload

import sys

from tkinter import *
from tkinter import ttk

from midi_convert import *


class Viewer(object):
    # def yview(self, *args):
    # for scroll in self.scrolls:
    # scroll.yview(*args)

    # SCROLLING

    COLOR_GRAY = '#CCC'
    COLOR_DARK_GRAY = '#AAA'
    COLOR_PIANO_BLACK = '#F8F0F0'

    def xview(self, *args):
        for scroll in self.xscrolls:
            scroll.xview(*args)

    def yview(self, *args):
        for scroll in self.yscrolls:
            scroll.yview(*args)

    # WHEEL
    def _on_mousewheel(self, event):
        # up down
        for scroll in self.yscrolls:
            scroll.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def _on_shift_mousewheel(self, event):
        # left right
        for scroll in self.xscrolls:
            scroll.xview_scroll(int(-1 * (event.delta / 120)), 'units')

    # PAGEUP PAGEDOWN
    def _on_pageup(self, event):
        # up
        for scroll in self.yscrolls:
            scroll.yview_scroll(-1, 'pages')

    def _on_pagedown(self, event):
        # down
        for scroll in self.yscrolls:
            scroll.yview_scroll(1, 'pages')

    def _on_shift_pageup(self, event):
        # left
        for scroll in self.xscrolls:
            scroll.xview_scroll(-1, 'pages')

    def _on_shift_pagedown(self, event):
        # right
        for scroll in self.xscrolls:
            scroll.xview_scroll(1, 'pages')

    # HOME END
    def _on_home(self, event):
        # left
        for scroll in self.xscrolls:
            scroll.xview_moveto(0)

    def _on_end(self, event):
        # right
        for scroll in self.xscrolls:
            # WIDTH = x
            visible = scroll.winfo_width()
            total = int(scroll.cget('width'))
            scroll.xview_moveto((total - visible) / total)

    def _on_shift_home(self, event):
        # up
        for scroll in self.yscrolls:
            scroll.yview_moveto(0)

    def _on_shift_end(self, event):
        # down
        for scroll in self.yscrolls:
            # HEIGHT
            visible = scroll.winfo_height()
            total = int(scroll.cget('height'))
            scroll.yview_moveto((total - visible) / total)

    # ARROW KEYS
    def _on_arrow_up(self, event):
        for scroll in self.yscrolls:
            scroll.yview_scroll(-1, 'units')

    def _on_arrow_down(self, event):
        for scroll in self.yscrolls:
            scroll.yview_scroll(1, 'units')

    def _on_arrow_left(self, event):
        for scroll in self.xscrolls:
            scroll.xview_scroll(-1, 'units')

    def _on_arrow_right(self, event):
        for scroll in self.xscrolls:
            scroll.xview_scroll(1, 'units')

    # DRAWING
    @staticmethod
    def calc_y(note):
        return 16 * (127 - note)

    def calc_x(self, time):
        # Converts from time to width.
        # Ticks / (ticks/note) * (pixels/note) = pixels
        return round(time * self.qnote_width / self.tickrate + 0.000001)

    def pitch_calc_y(self, cents):
        pitch_height = int(self.pitch_canvas.cget('height'))
        pixel_range = pitch_height // 2
        # Scales pitch_range to pixel_range
        scaled_cents = cents * pixel_range // self.pitch_range

        # Because positive pitch is negative pixels
        return pixel_range - scaled_cents


    def draw_vline(self, x, **kwargs):
        for canvas in self.xscrolls:
            height_str = canvas.cget('height')
            height = int(height_str)
            canvas.create_line(x, 0, x, height, **kwargs)

    @staticmethod
    def draw_single_vline(canvas, x, **kwargs):
        height_str = canvas.cget('height')
        height = int(height_str)
        canvas.create_line(x, 0, x, height, **kwargs)

    def draw_hline(self, y, **kwargs):
        for canvas in self.yscrolls:
            # Drawing a horizontal line, you must calculate the width of the canvas.
            width_str = canvas.cget('width')
            width = int(width_str)
            canvas.create_line(0, y, width, y, **kwargs)

    @staticmethod
    def draw_single_hline(canvas, y, **kwargs):
        # Drawing a horizontal line, you must calculate the width of the canvas.
        width_str = canvas.cget('width')
        width = int(width_str)
        canvas.create_line(0, y, width, y, **kwargs)


    @staticmethod
    def draw_text(canvas, x, y, text, **kwargs):
        canvas.create_text(x, y, anchor='w', font='fakefont 10', text=text, **kwargs)

    # UTILITY
    def create_canvas(self, width, height):
        canvas = Canvas(self.frame, bg='#FFF', scrollregion=(0, 0, width, height),
                        width=width, height=height, bd=0, highlightthickness=0, relief='ridge')
        return canvas

    @staticmethod
    def note2sci(note):
        note2letter = ['C', 'C#', 'D', 'D#', 'E', 'F',
                       'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = note // 12 - 1
        letter = note2letter[note % 12]
        return letter + str(octave)

    # etc.
    def _on_list_selected(self, event):
        # Add 1 to the track, as the thing only shows tracks [1:]
        self.new_tracknum = self.track_box.current() + 1
        self.root.destroy()

    def __init__(self, file_name, track_list, curr_num, track, tickrate, qnote_width, pitch_range):
        # Initialize the arrays
        self.xscrolls = []
        self.yscrolls = []

        # Dummy out the list box
        self.track_box = None

        # Convert the track.
        self.tracknum = curr_num
        self.new_tracknum = -1
        note_out, pitch_out, vibrato_out, maxtick = convert_track(track)
        self.note_out = note_out
        self.pitch_out = pitch_out
        self.vibrato_out = vibrato_out
        # maxtick = 1000

        # Configure the canvas.
        self.tickrate = tickrate
        self.qnote_width = qnote_width

        self.maxtick = maxtick
        width = self.calc_x(maxtick)    # Depends on qnote_width
        self.width = width

        self.pitch_range = pitch_range


        # self.:
        # root, frame, canvas, labels, time_canvas, pitch_canvas, vibrato_canvas

        # Prepare Tkinter.
        root = Tk()
        self.root = root
        root.title('Port-a-Potty - ' + file_name)
        root.geometry("640x480")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Main frame
        frame = ttk.Frame(root, padding=(0, 0, 0, 0))
        self.frame = frame
        frame.grid(column=0, row=0, sticky=(N, W, E, S))
        # Column 1 contains score. Row 2 contains scrollable note section.
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

        # Primary canvas
        canvas = self.create_canvas(width, 16 * 128)
        self.canvas = canvas
        canvas.grid(column=1, row=2, sticky=(N, W, E, S), padx=1, pady=1)
        self.xscrolls.append(canvas)
        self.yscrolls.append(canvas)

        # Note labels
        labels = self.create_canvas(64, 16 * 128)
        self.labels = labels
        labels.grid(column=0, row=2, sticky=(N, W, E, S), padx=1, pady=1)
        self.yscrolls.append(labels)

        # Time canvas
        time_canvas = self.create_canvas(width, 16)
        self.time_canvas = time_canvas
        time_canvas.grid(column=1, row=1, sticky=(N, W, E, S), padx=1, pady=1)
        self.xscrolls.append(time_canvas)

        # Pitch canvas
        pitch_canvas = self.create_canvas(width, 128)
        self.pitch_canvas = pitch_canvas
        pitch_canvas.grid(column=1, row=3, sticky=(N, W, E, S), padx=1, pady=1)
        self.xscrolls.append(pitch_canvas)

        # Vibrato canvas
        vibrato_canvas = self.create_canvas(width, 32)
        self.vibrato_canvas = vibrato_canvas
        vibrato_canvas.grid(column=1, row=4, sticky=(N, W, E, S), padx=1, pady=1)
        self.xscrolls.append(vibrato_canvas)

        self.setup_list(track_list)
        self.setup_scrolls()
        self.setup_background()
        self.setup_measures()
        self.draw()

    def setup_list(self, track_list):
        # Initialized with track list, excluding dummy track.
        self.track_box = track_box = ttk.Combobox(self.frame, state='readonly', values=track_list[1:])
        track_box.grid(column=0, row=0, sticky=(N, S, E, W), columnspan=3)

        track_box.current(self.tracknum - 1)

        # Bind events to select next track.
        track_box.bind('<<ComboboxSelected>>', self._on_list_selected)
        pass

    def setup_scrolls(self):
        root = self.root
        # Vertical scrollbar
        self.vbar = vbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.yview)
        vbar.grid(column=2, row=2, sticky=(N, W, E, S))
        self.canvas.configure(yscrollcommand=vbar.set)

        # Horizontal scrollbar
        self.hbar = hbar = ttk.Scrollbar(self.frame, orient=HORIZONTAL, command=self.xview)
        hbar.grid(column=1, row=100, sticky=(N, W, E, S))
        self.canvas.configure(xscrollcommand=hbar.set)

        # Not scrollbars, but the best place to put them.
        root.bind('<Shift-MouseWheel>', self._on_shift_mousewheel)
        root.bind('<MouseWheel>', self._on_mousewheel)
        root.bind('<Button-4>', self._on_mousewheel)
        root.bind('<Button-5>', self._on_mousewheel)

        root.bind('<Prior>', self._on_pageup)
        root.bind('<Next>', self._on_pagedown)
        root.bind('<Shift-Prior>', self._on_shift_pageup)
        root.bind('<Shift-Next>', self._on_shift_pagedown)

        root.bind('<Home>', self._on_home)
        root.bind('<End>', self._on_end)
        root.bind('<Shift-Home>', self._on_shift_home)
        root.bind('<Shift-End>', self._on_shift_end)

        root.bind('<Up>', self._on_arrow_up)
        root.bind('<Down>', self._on_arrow_down)
        root.bind('<Left>', self._on_arrow_left)
        root.bind('<Right>', self._on_arrow_right)

    def setup_background(self):
        canvas = self.canvas
        pitch_canvas = self.pitch_canvas
        width = self.width

        # Draw note lines
        for note in range(128):
            if note % 12 in [1,3,6,8,10]:
                y = self.calc_y(note)
                canvas.create_rectangle(0, y, width, y+16, width=0, fill=self.COLOR_PIANO_BLACK)
        for note in range(128):
            y = self.calc_y(note)
            self.draw_hline(y)
            if note % 12 == 0:
                self.draw_hline(y + 15)

        # Draw note labels
        for y in range(128):
            self.labels.create_text(29, self.calc_y(y) + 8, anchor='e', font='fakefont 10',
                                    text=str(y))
            self.labels.create_text(62, self.calc_y(y) + 8, anchor='e', font='fakefont 10',
                                    text=self.note2sci(y))

        # Draw the pitch canvas lines
        # Zero marking
        self.draw_single_hline(pitch_canvas, self.pitch_calc_y(0), width=3)

        for y in range(100, self.pitch_range, 100):
            upper = self.pitch_calc_y(y)
            lower = self.pitch_calc_y(-y)

            # Even markings are darker
            if y // 100 % 2 == 0:
                color = '#000'
            else:
                color = self.COLOR_GRAY
            self.draw_single_hline(pitch_canvas, upper, fill=color)
            self.draw_single_hline(pitch_canvas, lower, fill=color)

        # draw dividing line
        self.draw_single_vline(self.labels, 31)

    def setup_measures(self):
        # The multiplier converts ticks to pixels.
        tickrate = self.tickrate
        maxtick = self.maxtick

        # draw measure lines
        for measure_tick in range(0, maxtick, 4 * tickrate):  # fsck me right? Always assuming 4:4 songs... RIGHT?
            # Convert the measure tick into pixels, then draw the line.
            measure_num = measure_tick // (4 * tickrate)
            measure_x = self.calc_x(measure_tick)
            measure_x -= 1  # Create a double-thickness line. Not for the first, though.
                            # Doesn't really matter, but inconsistent.
            self.draw_text(self.time_canvas, measure_x + 4, 8, str(measure_num))
            self.draw_vline(measure_x)

        # Draw note lines
        for note_tick in range(0, maxtick, tickrate):
            note_x = self.calc_x(note_tick)
            self.draw_vline(note_x)

        # Draw 16th notes (quarter note * divide_factor=4) = 16
        divide_factor = 4
        # There are maxtick ticks.
        # Each increment advances (tickrate/divide_factor) ticks.
        # There are maxtick/(increment_size) increments total.
        increment_size = tickrate / divide_factor
        for i in range(int(maxtick / increment_size)):
            if i % 4 == 0:
                continue
            time = tickrate * i // divide_factor
            x = self.calc_x(time)
            self.draw_vline(x, fill=self.COLOR_GRAY)

    def draw(self):
        canvas = self.canvas
        pitch_canvas = self.pitch_canvas

        # draw notes
        for pitch, pitch_dict in enumerate(self.note_out):
            for time, note_tuple in pitch_dict.items():
                note_pitch = note_tuple[0]
                volume = note_tuple[1]
                end_time = note_tuple[2]
                if pitch != note_pitch:
                    print('ERROR INCORRECT PITCH IN NOTE!')
                    print(pitch)
                    print(note_pitch)
                    raise Exception
                # Calculate the note's position, and draw it.
                note_x = self.calc_x(time)
                note_y = self.calc_y(pitch)
                note_end = self.calc_x(end_time)

                # Fill color is blue for note extensions
                if volume < 0:
                    fill = '#BBF'
                else:
                    fill = '#FBB'

                volume = abs(volume)

                amount_filled = volume * 16 / 128   # Convert 128-volume to 16-pixels.

                canvas.create_rectangle(note_x, note_y,
                                        note_end, note_y + 16, fill=self.COLOR_GRAY)
                canvas.create_rectangle(note_x, note_y + 16 - amount_filled,
                                        note_end, note_y + 16, fill=fill)
                self.draw_text(canvas, note_x + 2, note_y + 8, str(abs(volume)))
                # DEBUGGING
                # self.draw_text(canvas, note_x + 32, note_y + 8, str(time))
                # self.draw_text(canvas, note_x + 64, note_y + 8, str(end_time))

        # Draw pitch bends.
        prev_x = 0
        prev_y = 32
        for time, pitch in sorted(self.pitch_out.items()):
            curr_x = self.calc_x(time)
            curr_y = self.pitch_calc_y(pitch)

            # Draw previous crossbar.
            pitch_canvas.create_line(prev_x, prev_y, curr_x, prev_y, width=3, fill='#F00')
            # Draw previous vertical bar.
            pitch_canvas.create_line(curr_x, prev_y, curr_x, curr_y, fill='#F00')

            # Remove text for clarity.
            # self.draw_text(pitch_canvas, curr_x + 2, curr_y, str(pitch))
            prev_x = curr_x
            prev_y = curr_y


# main
file_name = sys.argv[1]
with open(file_name, 'rb') as file:
# with open('test.mid', 'rb') as file:
    score = MIDI.midi2score(file.read())

tick_rate = score[0]
tracks = score[1:]

curr_num = 1
track_names = ['']
for index, track in enumerate(tracks[1:]):
    # print(index, track)
    name = get_name(track)
    if name is None:
        track_names.append('Unnamed Track ' + str(index + 1))
    else:
        track_names.append(name)


while curr_num != -1:
    track = tracks[curr_num]
    # print('Tick rate', tick_rate)
    viewer = Viewer(file_name, track_names, curr_num, track, tickrate=tick_rate, qnote_width=48, pitch_range=1200)
    # All pitch bends are calculated in cents

    viewer.root.mainloop()
    curr_num = viewer.new_tracknum
    del viewer