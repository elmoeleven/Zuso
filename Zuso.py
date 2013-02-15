import sublime
from sublime_plugin import EventListener, TextCommand
import re
from threading import Thread

# Sublime Version
sublime_version = 2

# Initial support for Sublime Text 3
if not sublime.version() or int(sublime.version()) > 3000:
    sublime_version = 3

# Regexes
HEX_REGEX = re.compile(r'#(([0-9a-fA-F]{3})([0-9a-fA-F]{3})?){1}$')
RGBA_REGEX = re.compile(r'rgba\(\s*(?:(\d{1,3})\s*,?\s*){3}(([0](.\d*)?)|[1])\)$')
RGB_REGEX = re.compile(r'rgb\(\s*(?:(\d{1,3})\s*,?\s*){2}(\d{1,3})\)$')
FILE_REGEX = re.compile('.*\.(css|sass|scss)\Z(?ms)')

# Import Settings
settings = sublime.load_settings('Zuso.sublime-settings')
active = settings.get('active')
uppercase = settings.get('uppercase')
inline_comments = settings.get('inline_comments')
three_hex = settings.get('three_hex')
rgb = settings.get('rgb')
_opacity = settings.get('opacity')


def error(err):
    sublime.status_message(err)


def check_opacity():
    '''
        check_opacity()
        function to check opacity value from SublimeHex settings
    '''
    if _opacity <= 1 and _opacity >= 0:
        opacity = _opacity
    else:
        opacity = 1
    return opacity


def is_valid_file(filename):
    '''
        is_valid_file(filename)
        verify either css or sass files
    '''
    if FILE_REGEX.match(filename):
        return True
    return False


def check_hex(string):
    '''
        check_hex(self)
        verify if string is a proper hex value
    '''
    if HEX_REGEX.match(string):
        return True
    return False


def check_if_rgba(i, string):
    '''
        check_if_rgba(self)
        verify if string is a proper rgba value
    '''
    if i == 0:
        regex = RGB_REGEX
    elif i == 1:
        regex = RGBA_REGEX

    if regex.match(string):
        return True
    return False


def initiate(view, sels, **kwargs):
    sels = sels
    typeof = False

    for sel in sels:
        string = view.substr(sel)

        if check_hex(string):
            output = 'rgba'
            typeof = 'hex'
        if check_if_rgba(0, string):
            output = 'hex'
            typeof = 'rgb'
        if check_if_rgba(1, string):
            output = 'hex'
            typeof = 'rgba'

        if typeof:
            _cvtr = Converter(
                        sel=sel,
                        string=string,
                        original=string,
                        uppercase=uppercase,
                        inline_comments=inline_comments,
                        three_hex=three_hex,
                        opacity=check_opacity(),
                        typeof=typeof,
                        output=output,
                    )
            _cvtr.convert()
            return _cvtr
    return None


class ZusoListener(EventListener):
    def on_selection_modified(self, view):
        '''
            on_selection_modified(self, view)
            define action to be taken on each select event
        '''
        self.view = view
        self.filename = self.view.file_name()

        if not is_valid_file(self.filename):
            return

        if not active:
            sels = self.view.sel()
            self.cvtr = initiate(view, sels)

            if self.cvtr:
                self.show_auto_complete()

    def on_query_completions(self, view, prefix, locations):
        '''
            on_query_completions(self, view, prefix, locations)
            define actions to be taken when a check for possible
            completions is done
        '''
        if not active:
            return self.get_completions()

    def get_completions(self):
        '''
            get_completions(self)
            retrieve possible completions
        '''
        if not active:
            completions = []
            if self.cvtr:
                completions.append((self.cvtr.result + '\t' + self.cvtr.props['output'], self.cvtr.result))
                return completions
            return []

    def show_auto_complete(self):
        '''
            show_auto_complete(self)
            display auto complete window
        '''
        if not active:
            self.view.run_command(
                'auto_complete', {
                    'disable_auto_insert': True,
                    'api_completions_only': True,
                    'next_completion_if_showing': False
                }
            )


class ZusoCommand(TextCommand):
    def __init__(self, view):
        self.view = view
        self.sels = self.view.sel()
        self.filename = self.view.file_name()

    def run(self, edit):
        if active:
            threads = []
            thread = initiate(self.view, self.sels)
            threads.append(thread)

            # Clear the selections we're going to set
            self.view.sel().clear()

            edit = self.view.begin_edit('zuso')
            self.handle_threads(edit, threads)

    def handle_threads(self, edit, threads, offset=0, i=0, dir=1):
        next_threads = []
        for thread in threads:
            if thread.is_alive():
                next_threads.append(thread)
                continue
            if thread.result == False:
                continue
            offset = self.replace(edit, thread, offset)
        threads = next_threads

        if len(threads):
            # This animates a little activity indicator in the status area
            before = i % 8
            after = (7) - before
            if not after:
                dir = -1
            if not before:
                dir = 1
            i += dir
            self.view.set_status('zuso', 'Zuso [%s=%s]' % \
                (' ' * before, ' ' * after))

            sublime.set_timeout(lambda: self.handle_threads(edit, threads,
                offset, i, dir), 100)
            return

        self.view.end_edit(edit)

        self.view.erase_status('zuso')
        selections = len(self.view.sel())
        sublime.status_message('Zuso successfully run on %s selection%s' %
            (selections, '' if selections == 1 else 's'))

    def replace(self, edit, thread, offset):
        sel = thread.props['sel']
        original = thread.props['original']
        result = thread.result

        # Recalibrate our selections
        if offset:
            print(offset)
            sel = sublime.Region(sel.begin() + offset,
                sel.end() + offset)

        # Replace text
        self.view.replace(edit, sel, result)

        # Add the end of the new text to the selection
        end_point = sel.begin() + len(result)
        self.view.sel().add(sublime.Region(end_point, end_point))

        return offset + len(result) - len(original)


class Converter(Thread):
    def __init__(self, **kwargs):
        '''
            __init__(self, **kwargs)
            set properties, result, type, hex sequence and call run()
        '''
        self.props = kwargs
        self.result = None
        self.type = None
        self.hex_seq = '0123456789ABCDEF' if self.props['uppercase'] else '0123456789abcdef'
        if active:
            Thread.__init__(self)

    def convert(self):
        '''
            run(self)
            check if string is a hex2rgba or rgba2hex conversion
        '''
        if self.props['typeof'] is 'hex':
            self.result = self.convert_hex()
            return
        if self.props['typeof'] is 'rgb':
            self.result = self.convert_rgba()
            return
        if self.props['typeof'] is 'rgba':
            self.type = 'hex'
            self.result = self.convert_rgba()
            return
        self.result = False

    def hex2rgba(self):
        '''
            hex2rgba(self)
            convert hex to rgba
        '''
        if len(self.props['string']) == 3:
            s = ''
            for i in self.props['string']:
                s += i * 2
            self.props['string'] = s
        return int(self.props['string'][0:2], 16), int(self.props['string'][2:4], 16), int(self.props['string'][4:6], 16), self.props['opacity']

    def rgba2hex(self, i):
        '''
            rgba2hex(self, i)
            convert rbga to hex
        '''
        s = self.props['string'][i]
        s = max(0, min(s, 255))
        mod = int(s % 16)
        calc = int((s - mod) / 16)
        return self.hex_seq[calc] + self.hex_seq[mod]

    def convert_hex(self):
        '''
            convert_hex(self)
            initiate conversion to hex
        '''
        self.props['string'] = self.props['string'].lstrip('#')

        if rgb:
            val = self.hex2rgba()
            return 'rgb(%s,%s,%s)' % val[0: len(val) - 1]
            # return 'rgba{}'.format(val[0: len(val) - 1])

        return 'rgba(%s,%s,%s,%s)' % self.hex2rgba()
        # return 'rgba{}'.format(self.hex2rgba())

    def convert_rgba(self):
        '''
            convert_rgba(self)
            initiate conversion to rgba
        '''
        self.props['string'] = tuple(int(v, 10) for v in re.findall("[0-9]+", self.props['string'].lstrip('rgba')))

        for i, val in enumerate(self.props['string']):
            if val > 255:
                error("The value %s is not within the range 0-255" % val)
                # error("The value {} is not within the range 0-255".format(i))
                return False

        a = self.rgba2hex(0)
        b = self.rgba2hex(1)
        c = self.rgba2hex(2)

        if self.props['three_hex']:
            temp = ''
            for i in (a, b, c):
                if i[0] == i[1]:
                    i = i[1:]
                    temp += i
                else:
                    return ('#' + a + b + c)
            return('#' + temp)
        return ('#' + a + b + c)
