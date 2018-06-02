import sublime
import sublime_plugin
from collections import defaultdict
from math import log10, floor

'''
Potential future functions to add:
 * use fancy NLP to extract words (more clever than str.split(' '), get rid of commas and stuff)

'''


'''
Potential future improvements to word freq command:
 * ignore case when merging lines
 * Make first line of input document be title of output summary
    * maybe like only if the first line only occurs once do this automatically
'''
class WordFreqCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message('Word Freq: Counting unique lines')

        # collect all the lines from the documents as a list of strings
        self.view.run_command('select_all')
        everything_region = self.view.sel()[0]
        everything_string = self.view.substr(everything_region)
        self.view.sel().clear()
        lines = everything_string.split('\n')

        # discard the last line if it is blank
        if lines[-1] == '':
            del lines[-1]

        # count the unique lines
        counts = defaultdict(int)
        for line in lines:
            counts[line] += 1
        total_num_words = sum((counts[x] for x in counts))

        # sort by word count then alphabetically
        count_tuples = ((counts[word], word) for word in counts)
        count_tuples = sorted(count_tuples, key=lambda x: (-x[0], x[1]))

        max_count_characters = floor(log10( max((counts[x] for x in counts)) ))+1

        '''
        Finish later
        (the idea is to make the percentages adaptively longer if they are very small)
        '''
        # smallest_percent = min((100.0*counts[x]/total_num_words for x in counts))
        # if smallest_percent >= 1.0:
        #     max_percent_characters = pass
        # max_percent_characters = floor(log10( smallest_percent ))+1

        count_strings = [('{: >4.1f}%  {: >'+str(max_count_characters)+'d}  {}').format(100.0*count/total_num_words, count, word) for (count, word) in count_tuples]

        # add a title to the beginning
        header_string = 'Frequencies of unique lines'
        header_string = header_string + '\n' + '='*len(header_string) + '\n'

        # add in a grand total at the end
        total_count_string = '{}  {}'.format(total_num_words, 'Total unique lines')
        count_strings.append('='*len(total_count_string))
        count_strings.append(total_count_string)

        new_everything_string = header_string + '\n'.join(count_strings) + '\n'

        # open new file
        new_view = sublime.active_window().new_file()
        # insert selected text into the new file
        new_view.insert(edit, 0, new_everything_string)

        # self.view.replace(edit, everything_region, new_everything_string)
        # self.view.sel().clear()
