

def check_func_args(args, keys, arg_types):
    # checks dictionary keys and types
    ind = 0

    for key in keys:
        if key not in args or not isinstance(args[key], arg_types[ind]):
            return False
        ind += 1

    return True
