

def underline2hump(name:str):
    """
    下划线转驼峰
    :param name:
    :return:
    """
    return ''.join([v[0].upper()+v[1:] for v in name.split('_')])
