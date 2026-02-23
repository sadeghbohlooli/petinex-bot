"""
core/states.py
Conversation states used across all handlers and flows.
"""

MAIN_MENU = 0
ANSWERING = 1
MULTI_SELECT = 2
OTHER_TEXT = 3       # New state: waiting for free-text after "_other" option
