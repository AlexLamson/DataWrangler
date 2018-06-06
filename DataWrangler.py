import sublime
import sublime_plugin
from collections import defaultdict
from math import log10, floor, ceil


def detect_num_columns(self, sep=None):
    if sep is None:
        sep = detect_separations(self)

    # collect the line strings
    r = sublime.Region(0, self.view.size())
    first_line_region = self.view.lines(r)[0]
    first_line = self.view.substr(first_line_region)
    return len(first_line.split(sep))


def detect_separations(self):
    # remember that you only need to read the first couple lines to first this out
    # realistically, you only need one line

    # # collect the line strings
    # r = sublime.Region(0, self.view.size())
    # line_regions = self.view.lines(r)
    # lines = (self.view.substr(x) for x in line_regions)
    # lines = [x for x in lines if x != '']

    # this is a temp solution for now
    return "\t"


'''
Description
-----------
Count the number of times each line occurs, then display that info in a new tab
'''
class LineFreqCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message('Data Wrangler: Counting line frequencies')

        # collect the line strings
        r = sublime.Region(0, self.view.size())
        line_regions = self.view.lines(r)
        lines = (self.view.substr(x) for x in line_regions)
        lines = [x for x in lines if x != '']

        # count the unique lines
        counts = defaultdict(int)
        for line in lines:
            counts[line] += 1
        total_num_words = sum((counts[x] for x in counts))

        # sort by word count then alphabetically
        count_tuples = ((counts[word], word) for word in counts)
        count_tuples = sorted(count_tuples, key=lambda x: (-x[0], x[1]))

        # make all the line counts line up
        max_count_characters = floor(log10( max((counts[x] for x in counts)) ))+1

        # add more decimal places to the percentages as needed
        smallest_percent = min((counts[x]/total_num_words for x in counts))
        num_decimal_places = 0
        if -(log10(smallest_percent)+2) > 0:
            num_decimal_places = ceil(-(log10(smallest_percent)+2))
            num_leading_chars_in_percentage = num_decimal_places+4
        else:
            num_leading_chars_in_percentage = 3  # special case when all percentages are whole numbers

        # initialize array to hold output lines
        out_strings = []

        # add a title to the beginning
        header_string = 'Frequencies of unique lines'
        out_strings.append(header_string)
        out_strings.append('='*len(header_string))

        # format each lines percentage, count, and line string
        percentage_format_specifier = '{: >' + str(num_leading_chars_in_percentage) + '.' + str(num_decimal_places) + '%}'
        count_format_specifier = '{: >' + str(max_count_characters) + 'd}'
        for (count, word) in count_tuples:
            percentage = count/total_num_words
            count_string = (percentage_format_specifier+'  '+count_format_specifier+'  {}').format(percentage, count, word)
            out_strings.append(count_string)

        # add in a grand total at the end
        out_strings.append('='*len(header_string))
        out_strings.append(str(total_num_words)+'  Total')

        output_string = '\n'.join(out_strings) + '\n'

        # write frequencies to new tab
        new_view = sublime.active_window().new_file()
        new_view.insert(edit, 0, output_string)


'''
Description
-----------
Before:
AAA
    BBB
    CCC

After:
AAA    BBB
AAA    CCC
'''
class FlattenListOfListsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message('Data Wrangler: Flattening list column')

        # collect all the lines from the documents as a list of strings
        self.view.run_command('select_all')
        everything_region = self.view.sel()[0]
        everything_string = self.view.substr(everything_region)
        self.view.sel().clear()
        lines = everything_string.split('\n')

        # discard the last line if it is blank
        if lines[-1] == '':
            del lines[-1]

        # flatten the list of lists
        new_lines = list()
        current_heading = ""
        for i, line in enumerate(lines):
            if not line.startswith('\t'):
                current_heading = line
            else:
                new_lines.append(current_heading + line)

        new_everything_string = "\n".join(new_lines) + "\n"

        # open new file
        new_view = sublime.active_window().new_file()
        # insert selected text into the new file
        new_view.insert(edit, 0, new_everything_string)

        # self.view.replace(edit, everything_region, new_everything_string)
        # self.view.sel().clear()
        # self.view.run_command("go_to_line", {'line':'0'})
