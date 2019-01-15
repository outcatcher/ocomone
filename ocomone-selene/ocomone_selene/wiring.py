# -*- coding=utf-8 -*-
"""Library for wiring widget class to file with locators"""

import os
from copy import copy
from typing import Any, Callable, Dict, Iterable, List, Tuple, Type, Union

import wrapt
from ocomone import Resources
from selene.bys import by_css, by_link_text, by_name, by_partial_text, by_text
from selene.elements import SeleneCollection, SeleneElement

from .bys import by_id, by_label

_GetterFnc = Callable[[Any], Any]
_SetterFnc = Callable[[Any, Any], None]  # self, value, field_name
_InnerSetter = Callable[[Any, Any, str], None]

__WIRED_CLASS_SETTERS: Dict[type, _InnerSetter] = {}

__WIRED_CLASS_ORDER: List[type] = []


class Wireable:
    """Base class defining methods and field required for valid usage with @wired(...) decorator"""

    strategies: "_StrategyDict"

    def elements(self, locator) -> SeleneCollection:
        """Return SeleneCollection (multiple elements) by locator"""
        raise NotImplementedError

    def element(self, locator) -> SeleneElement:
        """Return single SeleneElement by locator"""
        raise NotImplementedError

    def register_strategy(self, name: str, strategy: "GetLocator"):
        """Register new search strategy only for this object"""
        self.strategies.update({name: strategy})


def _is_subclass(cls, types: Union[type, Tuple[type]]):
    """Strange behaviour for issubclass() (m.b. https://bugs.python.org/issue33018)"""
    try:
        return issubclass(cls, types)
    except TypeError:
        pass
    if not isinstance(types, tuple):
        types = (types,)
    for typ in types:
        if typ in cls.__mro__:
            return True
    return False


def __sort_classes():
    def _is_sorted(classes: List[type]):
        """Most precise class should be the first"""
        prev_cls = type
        for _cls in classes:
            if _is_subclass(_cls, prev_cls):
                return False
            prev_cls = _cls
        return True

    length = len(__WIRED_CLASS_ORDER)
    while not _is_sorted(__WIRED_CLASS_ORDER):
        __wc = __WIRED_CLASS_ORDER
        for index in range(length - 1):
            # noinspection PyTypeHints
            if issubclass(__wc[index + 1], __wc[index]):
                __wc[index + 1], __wc[index] = __wc[index], __wc[index + 1]  #


def _register_class(cls, setter: _InnerSetter):
    """Insert new class into wired classes registry"""
    __sort_classes()
    __wco = __WIRED_CLASS_ORDER

    if cls in __WIRED_CLASS_ORDER:
        return

    __WIRED_CLASS_SETTERS.update({cls: setter})

    # if not subclass of any existing class, put to back
    if not _is_subclass(cls, tuple(__wco)):
        __wco.append(cls)
        return

    # or put before any superclass
    for existing_cls in __wco:  # pylint: disable=consider-using-enumerate
        # noinspection PyTypeHints
        if _is_subclass(cls, existing_cls):
            __wco.insert(__wco.index(existing_cls), cls)
            return


def __do_nothing(*_):
    pass


def register_setter(cls: type, method: _SetterFnc):
    """Register new setter binding.

    :param cls: class that will be used for bindings
    :param method: function used for setting field value

    Example: ``register_setter(SeleneElement, SeleneElement.set)``
    """
    if isinstance(method, property):
        method: _SetterFnc = method.__set__

    def _real_setter(self: Wireable, value, field_name):
        if value is None:
            return __do_nothing
        field: cls = getattr(self, field_name)
        return method(field, value)

    _register_class(cls, _real_setter)


def register_without_setter(cls: type):
    """Register new class binding without setter"""

    def _read_only(*_) -> None:
        raise RuntimeWarning(f"Can't assign to field of class {cls}")

    register_setter(cls, _read_only)


# Standard setters
register_setter(SeleneElement, SeleneElement.set)
register_without_setter(SeleneCollection)

GetLocator = Callable[[str], Tuple[str, str]]


def __convert_entity(element, cls):
    if not isinstance(element, cls):  # if need to convert SeleneElement to some other
        try:
            # noinspection PyArgumentList
            element = cls(element)  # cls.__init__ must accept SeleneElement as lone argument
        except TypeError:  # this class has inappropriate __init__
            raise TypeError(f"Impossible to wrap element with {cls}, __init__ won't accept {element}")
    return element


def _wired_getter(cls: Type[Wireable], getter: Callable[[Any], Tuple[str, str]]):
    if _is_subclass(cls, Iterable):  # return multiple elements if attribute is iterable
        def __getter(self: cls) -> cls:
            elements = self.elements(getter(self))
            elements = __convert_entity(elements, cls)
            return elements
    else:
        def __getter(self: Wireable) -> cls:
            element = self.element(getter(self))
            element = __convert_entity(element, cls)
            return element
    return __getter


class _StrategyDict(Dict[str, GetLocator]):

    # pylint: disable=no-member

    def __getitem__(self, item) -> GetLocator:
        def __impossible(_):
            raise NotImplementedError(f"`{item}` strategy is not defined")

        try:
            result = super().__getitem__(item)
        except KeyError:
            return __impossible

        if result is None:  # if strategy has no binding,
            return __impossible
        return result


_STRATEGIES = _StrategyDict({  # _STRATEGIES is used for locating elements further
    "id": by_id,
    "name": by_name,
    "label": None,
    "text": by_text,
    "partial": by_partial_text,
    "link": by_link_text,
    "css": by_css,
})


def register_strategy(name, strategy: GetLocator):
    """Register new location strategy

    New strategy should be a callable accepting locator string and returning pair: ``by, selector``

    ----

    Default strategies are:
        - ``id: by_id``
        - ``name: by_name``
        - ``text: by_text``
        - ``partial: by_partial_text``
        - ``link: by_link_text``
        - ``css: by_css``
    """
    _STRATEGIES.update({name, strategy})  # pylint: disable=no-member


def _convert_locator(strategy: str, locator: str):
    """Returning method, converting locator from short presentation to full"""

    def _convert(self: Wireable):
        _method = self.strategies[strategy]
        _by, _selector = _method(locator)
        return _by, _selector

    return _convert


def _to_property(field_name, field_cls, getter):
    """Convert field to property.

    Setter is taken from registry: use ``register()`` to add new binding

    Getter is defined by class of field, basically returning `field_cls(actual_element)`,
    where locator of actual element is defined in wired file
    """

    def __property_setter(_cls):
        def __inner(self: Wireable, value):
            _set = __WIRED_CLASS_SETTERS[_cls]
            return _set(self, value, field_name)

        return __inner

    for cls in __WIRED_CLASS_ORDER:
        if _is_subclass(field_cls, cls):
            return property(getter, __property_setter(cls))
    return None


def _cached_getter(getter: _GetterFnc, field_name):
    """Cache getter results to internal attribute"""
    internal_attr = f"__cached_{field_name}"

    def __real_getter(self):
        if not hasattr(self, internal_attr):
            setattr(self, internal_attr, getter(self))
        return getattr(self, internal_attr)

    return __real_getter


class WiredDecorator:
    """Convert annotated attributes of applied classes to properties

    Works only for not assigned attributes, e.g.

    ``username: SeleneElement`` will be converted

    but

    ``username: SeleneElement = element("#username")`` will be not

    ----

    Property ``getter`` will return SeleneElement, defined by locator in wired file

    Property ``setter`` will work depending on registered setters. Default setters are:
        - SeleneElement: SeleneElement.set
        - Select: Select.select_by_value

    To register new binding use ``register_setter`` function

    """

    def __init__(self, resources: Union[str, Resources]):
        """Bind to given resources, either as instance of :class:`Resources` or path to resources directory"""
        if isinstance(resources, str):
            path = os.path.abspath(resources)
            resources = Resources(path, "")
        self.resources = resources

    def __parse_csv(self, locator_file) -> Dict[str, GetLocator]:
        import csv
        with open(self.resources[locator_file]) as input_file:
            mappings = csv.reader(input_file, delimiter=":")
            # element:strategy:selector -> element: (strategy, selector)
            locators: Dict[str, GetLocator] = {mapping[0]: _convert_locator(*mapping[1:]) for mapping in mappings}
        return locators

    def __parse_yml(self, locator_file) -> Dict[str, GetLocator]:
        import yaml

        def _parse_yml_entry(entry: dict):
            return list(entry.items())[0]  # we use just first locator

        with open(self.resources[locator_file]) as input_file:
            mappings = yaml.load(input_file)
        locators = {item: _parse_yml_entry(locator) for item, locator in mappings.items}

        return locators

    def __call__(self, locator_file: str):
        """Returning decorator to be used for wiring class"""

        if not isinstance(locator_file, str):
            raise TypeError("@wired argument should be string")

        if locator_file.endswith(".csv"):
            locators = self.__parse_csv(locator_file)
        elif locator_file.endswith(".yml") or locator_file.endswith(".yaml"):
            locators = self.__parse_yml(locator_file)
        else:
            raise RuntimeError(f"Invalid locator file: {locator_file}")

        @wrapt.decorator
        def _wired(wrapped: Type[Wireable], _instance=None, args=(), kwargs=None) -> Wireable:

            def _wire_cls():
                if hasattr(wrapped, "__wired__") and (wrapped.__wired__ == wrapped.__name__):
                    print("not misregistered")
                    return  # already wired
                wrapped.strategies = copy(_STRATEGIES)
                annotations = wrapped.__annotations__
                for attr in annotations:  # through all annotated attributes
                    if not hasattr(wrapped, attr):  # only not assigned attributes
                        attr_cls = annotations[attr]
                        try:
                            locator = locators[attr]
                        except KeyError:
                            raise KeyError(f"Missing `{attr}` in file `{locator_file}`")
                        getter = _wired_getter(attr_cls, locator)
                        getter = _cached_getter(getter, attr)  # Selene handles reload of elements, so we can cache it
                        new_property = _to_property(attr, attr_cls, getter)
                        setattr(wrapped, attr, new_property)  # assign property to attribute
                wrapped.__wired__ = wrapped.__name__

            _wire_cls()

            # noinspection PyArgumentList
            _instance = wrapped(*args, **kwargs)

            # label strategy is context-dependent
            root_element = _instance.root_element if hasattr(_instance, "root_element") else None
            _instance.register_strategy("label", lambda text: by_label(text, root_element))
            return _instance

        return _wired


DEFAULT_WIRED = WiredDecorator(Resources(os.getcwd(), resources_dir="resources/locators"))


def wired(locator_file):
    """Wire decorator with resources path ``./resources/locators``

    See :class:`Wired` documentation
    """
    return DEFAULT_WIRED(locator_file)
