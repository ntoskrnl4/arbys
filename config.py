# Configuration file for the bot, settings such as logging options, whatever

# log settings, required for use. levels go in order of increasing verbosity
# Absolutely nothing (disable logging there): -1
# Fatal: 0
# Critical: 1
# Error: 2
# Warning: 3
# Info: 4
# Debug: 5

terminal_loglevel = 5
exc_to_stderr = True  # log warnings and above to stderr instead of stdout

file_loglevel = 5
logfile = "bot.log"  # log file names will have the year and month prepended to them, for example: 2018-06-bot.log
logfile_encoding = "UTF-8"  # UTF-8 recommended because emojis

# Bot's default online status when it logs in. Should usually be dnd to indicate it is online but still loading.
# Valid values are "online", "idle", "dnd" (default) or "do_not_disturb", and "invisible".
boot_status = "dnd"
