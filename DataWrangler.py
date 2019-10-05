import sublime
import sublime_plugin
from collections import defaultdict
from math import log10, floor, ceil
import threading
from subprocess import check_output
import re


# pass in a variable name and an optional default value
# to get what that value is set to in settings
def settings(name, default=None):
    return sublime.load_settings("DataWrangler.sublime-settings").get(name, default)


def detect_num_columns(self, sep=None):
    if sep is None:
        sep = detect_separations(self)

    # read and split the first line
    r = sublime.Region(0, self.view.size())
    first_line_region = self.view.lines(r)[0]
    first_line = self.view.substr(first_line_region)
    return len(first_line.split(sep))


def detect_separations(self, first_line=None):
    if first_line is None:
        # read and split the first line
        r = sublime.Region(0, self.view.size())
        first_line_region = self.view.lines(r)[0]
        first_line = self.view.substr(first_line_region)

    # hacky solution that should be improved in the future
    if '\t' in first_line:
        return '\t'
    elif ', ' in first_line:
        return ', '
    elif ',' in first_line:
        return ','
    else:
        ' '


def detect_col_widths(self, sep=None, num_columns=None, lines=None):
    if sep is None:
        sep = detect_separations(self)
    if num_columns is None:
        num_columns = detect_num_columns(self, sep)

    if lines is None:
        # collect the line strings
        r = sublime.Region(0, self.view.size())
        line_regions = self.view.lines(r)
        lines = (self.view.substr(x) for x in line_regions)
        lines = [x for x in lines if x != '']

    column_widths = [0]*num_columns
    for line in lines:
        split_line = line.split(sep)
        for i, cell_string in enumerate(split_line):
            column_widths[i] = max(len(cell_string), column_widths[i])

    return column_widths


'''
Description
-----------
Count the number of times each line occurs, then display that info in a new tab
'''
class LineFreqCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message('Data Wrangler: Counting line frequencies')

        # collect settings
        ignore_case_when_merging_lines = settings("ignore_case_when_merging_lines", False)

        # collect the line strings
        r = sublime.Region(0, self.view.size())
        line_regions = self.view.lines(r)
        lines = (self.view.substr(x) for x in line_regions)
        lines = [x for x in lines if x != '']

        # count the unique lines
        counts = defaultdict(int)
        for line in lines:
            if ignore_case_when_merging_lines:
                line = line.lower()
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
            if not (line.startswith('\t') or line.startswith(' ')):
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


'''
Description
-----------
Before:
AAA    BBB
AAA    CCC

After:
AAA
    BBB
    CCC
'''
class GroupListOfListsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message('Data Wrangler: Grouping list column')

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
            heading, subheading = line.split('\t')
            if heading == current_heading:
                new_lines.append('\t'+subheading)
            else:
                current_heading = heading
                new_lines.append(current_heading)

        new_everything_string = "\n".join(new_lines) + "\n"

        # open new file
        new_view = sublime.active_window().new_file()
        # insert selected text into the new file
        new_view.insert(edit, 0, new_everything_string)

        # self.view.replace(edit, everything_region, new_everything_string)
        # self.view.sel().clear()
        # self.view.run_command("go_to_line", {'line':'0'})


'''
Description
-----------
Before:
aaaa bb ccc
dd eeeeee ff

After:
aaaa bb     ccc
dd   eeeeee ff
'''
class AlignColumnsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message('Data Wrangler: Aligning columns')

        # collect the line strings
        r = sublime.Region(0, self.view.size())
        line_regions = self.view.lines(r)
        lines = (self.view.substr(x) for x in line_regions)
        lines = [x for x in lines if x != '']

        # compute the max width of each column
        sep = detect_separations(self)
        num_columns = detect_num_columns(self, sep)
        column_widths = detect_col_widths(self, sep, num_columns)

        # re-format all the columns
        format_string = "  ".join(("{: >"+str(width)+"}" for width in column_widths))
        out_strings = []
        for line in lines:
            cells = line.split(sep)
            resized_line = format_string.format(*cells)
            out_strings.append(resized_line)

        # initialize array to hold output lines
        output_string = '\n'.join(out_strings) + '\n'

        # write frequencies to new tab
        new_view = sublime.active_window().new_file()
        new_view.insert(edit, 0, output_string)


'''
Description
-----------
Delete every column that has a cursor in it
'''
class DeleteColumnsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message('Data Wrangler: Deleting columns')

        # indices of data columns that will be removed
        data_columns_to_delete = set()

        # for each cursor, find which data column that cursor is in
        for cursor_region in self.view.sel():
            line_region = self.view.line(cursor_region.a)
            tabs_region = sublime.Region(line_region.a, cursor_region.a)
            num_tabs_before_cursor = self.view.substr(tabs_region).count('\t')

            # the data column index is equal to the number of tabs before the cursor
            data_column = num_tabs_before_cursor
            data_columns_to_delete.add( data_column )

        # collect the line strings
        r = sublime.Region(0, self.view.size())
        line_regions = self.view.lines(r)
        lines = (self.view.substr(x) for x in line_regions)
        lines = [x for x in lines if x != '']

        # delete unwanted columns
        sep = detect_separations(self)
        out_strings = []
        for line in lines:
            columns = line.split(sep)
            filtered_columns = [y for (x,y) in enumerate(columns) if x not in data_columns_to_delete]
            filtered_line = sep.join(filtered_columns)
            out_strings.append(filtered_line)

        # initialize array to hold output lines
        output_string = '\n'.join(out_strings) + '\n'

        # write frequencies to new tab
        new_view = sublime.active_window().new_file()
        new_view.insert(edit, 0, output_string)


'''
Description
-----------
Separate each word onto its own line
'''
class WordSplitCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message('Data Wrangler: Counting line frequencies')

        # collect the line strings
        r = sublime.Region(0, self.view.size())
        line_regions = self.view.lines(r)
        lines = (self.view.substr(x) for x in line_regions)
        lines = [x for x in lines if x != '']

        # initialize array to hold output lines
        out_strings = []

        for line in lines:
            re.split(r"\W+", line)
            for word in line.split():
                out_strings += [word]

        output_string = '\n'.join(out_strings) + '\n'

        # write frequencies to new tab
        new_view = sublime.active_window().new_file()
        new_view.insert(edit, 0, output_string)
