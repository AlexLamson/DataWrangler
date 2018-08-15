# DataWrangler - Sublime Plugin
Clean and analyze text data more easily

!["Screenshot"](https://raw.github.com/AlexLamson/DataWrangler/master/screenshots/demo.gif "Screenshot")


## Motivation
While cleaning data from a large survey, I wanted to ask questions about the data so I could clean it better.
For example, many people would type what city they were from, but some would misspell it. By looking at the most common responses, I could quickly find the mispelled words and fix them.

## Installation
Install via Package Control by searching for `DataWrangler`.

If you don't have Package Control, you can install it [here](https://packagecontrol.io/installation).


## Usage
To run a command, open the command palette (ctrl+shift+P on Windows) and type the name of the function you want.

If a command expects data to be formatted in rows and columns of data, tabs are the preferred separator (it also tries to be clever if you are using another separator, ex. commas). This was chosen because it makes it very compatible with copy-pasting from Google Sheets and Excel spreadsheets.


## Commands
All commands are non-destructive, and the results will appear in a new tab.
 * Line/word frequency
 * Flatten a list of lists
 * Vertically align all columns
 * Delete each column that contains a cursor
