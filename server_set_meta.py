SETTING_COLUMNS = {
    "reademoji":        ("is_reademoji", True),
    "readname":         ("is_readname", False),
    "skip_repeat_name": ("is_skip_repeat_name", True),
    "queue_speedup":    ("is_queue_speedup", True),
    "readurl":          ("is_readurl", True),
    "readjoinleave":    ("is_readjoin", False),
    "readsan":          ("is_readsan", False),
    "joinnotice":       ("is_joinnotice", True),
    "translate":        ("is_translate", False),
    "eew":              ("is_eew", True),
    "readforward":      ("is_readforward", True),
    "readmention":      ("is_readmention", True),
    "lang":             ("lang", "ja"),
    "join_text":        ("join_text", "&nameが入室したのだ、"),
    "leave_text":       ("leave_text", "&nameが退出したのだ、"),
}


def format_setting_value(value):
    """DB から読んだ値を、そのまま value として送れる文字列にする。"""
    if isinstance(value, bool):
        return "on" if value else "off"
    return str(value)


def drop_value(choices, value):
    """先頭に出す現在値と重複する候補を取り除く。"""
    return [c for c in choices if c != value]
