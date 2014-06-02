import sys

def on(*guards):
    def decorator(func):
        mod = sys.modules[func.__module__]
        if not hasattr(mod, '_matchete'):
            mod._matchete = {}
        if func.__name__ not in mod._matchete:
            mod._matchete[func.__name__] = []
        mod._matchete[func.__name__].append((guards, func))
        return call_overload(func.__name__)
    return decorator

def call_overload(name):    
    def match_guard(guard, arg):
        print(guard, arg)
        if isinstance(guard, str) and len(guard) > 0:
            if guard[0] == '.':
                return hasattr(arg, guard[1:])
            elif guard[0] == '#':
                return hasattr(arg, guard[1:]) and callable(getattr(arg, guard[1:]))
            else:
                return guard == arg
        elif isinstance(guard, type):
            print arg, guard, isinstance(arg, guard)
            return isinstance(arg, guard)
        elif callable(guard):
            return guard(arg)         
        else:
            return guard == arg

    def wrapper(self, *args, **kwargs):
        if hasattr(sys.modules[self.__module__], '_matchete'):
            self.__class__._matchete = sys.modules[self.__module__]._matchete
            delattr(sys.modules[self.__module__], '_matchete')
        # find method
        for guards, function in self.__class__._matchete[name]:
            if len(guards) <= len(args) and all([match_guard(guard, arg) for guard, arg in zip(guards, args)]):
                return function(self, *args, **kwargs)
        raise NotImplementedError("%s with %s not matching" % (name, str(args)))

    return wrapper

def extract_expected(obj, attribute):
    if attribute[0] == '.':
        if hasattr(obj, attribute[1:]):
            return getattr(obj, attribute[1:])
    elif attribute[0] == '#':
        if hasattr(obj, attribute[1:]) and callable(obj, attribute[1:]):
            return getattr(obj, attribute[1:])()
        
    
def eq(attribute, value):
    def wrapper(arg):
        return value == extract_expected(arg, attribute)
    return wrapper

def is_in(attribute, collection):
    def wrapper(arg):
        return extract_expected(arg, attribute) in collection
    return wrapper

def not_eq(attribute, value):
    def wrapper(arg):
        return value != extract_expected(arg, attribute)
    return wrapper

def contains(collection, value):
    def wrapper(arg):
        return any(select(lambda a: a == value, map(lambda a: extract_expected(arg, a), collection)))
    return wrapper

def Any(arg):
    return True
