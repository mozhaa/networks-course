def format_units(value, step, names, precision=1):
    for i, x in enumerate(names):
        if value < step or i == len(names) - 1:
            return f"{{:.{precision}f}} {{}}".format(value, x)
        value /= step


def format_speed(value):
    return format_units(value, 1000, ["B/s", "KB/s", "MB/s", "GB/s", "TB/s"])


def format_size(value):
    return format_units(value, 1000, ["B", "KB", "MB", "GB", "TB"])
