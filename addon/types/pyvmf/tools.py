def num(s: str):
    """
    Tries to turn string into int or float

    :param s: The string to parse
    :type s: :obj:`str`
    :return: If unable to convert returns the input
    :rtype: :obj:`int` or :obj:`float` or :obj:`str`
    """
    s = str(s)
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return str(s)
