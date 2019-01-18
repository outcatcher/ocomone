# -*- coding=utf-8 -*-
"""Library for wiring widget class to file with locators"""

import os
from copy import copy
from typing import Any, Callable, Dict, Tuple, Type, Union

import wrapt
from ocomone import Resources
from selene import browser
from selene.bys import by_css, by_link_text, by_name, by_partial_text, by_text
from selene.elements import SeleneCollection, SeleneElement

from .bys import by_id, by_label

_SetterFnc = Callable[[Any, Any], None]  # self, value, field_name
_InnerSetter = Callable[[Any, Any, str], None]


class _RegisteredMixin:
    """Mixin for registrable element"""
    __set_value__: Callable[["_RegisteredMixin", Any], None]


class Wireable(_RegisteredMixin):
    """Base class defining methods and field required for valid usage with @wired(...) decorator"""

    _strategies: Dict[str, "By"]
    _locators: Dict[str, "GetLocator"]

    def elements(self, locator) -> SeleneCollection:
        """Return SeleneCollection (multiple elements) by locator"""
        raise NotImplementedError

    def element(self, locator) -> SeleneElement:
        """Return single SeleneElement by locator"""
        raise NotImplementedError

    def register_strategy(self, name: str, strategy: "By"):
        """Register new search strategy only for this object"""
        self._strategies.update({name: strategy})


_GetterFnc = Callable[[Wireable], _RegisteredMixin]


def __do_nothing(*_):
    pass


def register_setter(cls: Type[_RegisteredMixin], method: _SetterFnc):
    """Set new `__set_value__` method for class

    :param cls: class that will be used for bindings
    :param method: function used for setting field value

    Example: ``register_setter(SeleneElement, SeleneElement.set)``
    """

    def _real_setter(self: cls, value):
        if value is None:
            return __do_nothing
        return method(self, value)

    cls.__set_value__ = _real_setter


def register_without_setter(cls: Type[_RegisteredMixin]):
    """Register new class binding without setter"""

    def _read_only(*_) -> None:
        raise RuntimeWarning(f"Can't assign to field of class {cls}")

    register_setter(cls, _read_only)


# Standard setters
register_setter(SeleneElement, SeleneElement.set)
register_without_setter(SeleneCollection)

GetLocator = Callable[[Wireable], Tuple[str, str]]


def __convert_entity(cls, *cls_args):
    element = cls_args[0]
    if not isinstance(element, cls):  # if need to convert SeleneElement to some other
        try:
            # noinspection PyArgumentList
            element = cls(*cls_args)  # cls.__init__ must accept SeleneElement as lone argument
        except TypeError:  # this class has inappropriate __init__
            try:
                element = cls()
            except TypeError:
                raise TypeError(f"Impossible to wrap element with {cls}, __init__ won't accept {element}")
    return element


def __is_subclass(cls: type, sup_cls):
    if not isinstance(sup_cls, tuple):
        sup_cls = (sup_cls,)
    for sup in sup_cls:
        if sup in cls.__mro__:
            return True


def _wired_getter(cls: Type[Wireable], locator_getter: Callable[[_RegisteredMixin], Tuple[str, str]],
                  *field_class_args):
    if __is_subclass(cls, (SeleneCollection, list, tuple)):  # return multiple elements if attribute is iterable
        def __getter(self: cls) -> SeleneCollection:
            f_elements = self.elements if hasattr(self, "elements") else browser.elements
            elements = f_elements(locator_getter(self))
            elements = __convert_entity(cls, elements, *field_class_args)
            return elements
    else:
        def __getter(self: Wireable) -> SeleneElement:
            f_elements = self.element if hasattr(self, "element") else browser.element
            element = f_elements(locator_getter(self))
            element = __convert_entity(cls, element, *field_class_args)
            return element
    return __getter


By = Callable[[str], SeleneElement]


class _StrategyDict(Dict[str, By]):

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
        _method = self._strategies[strategy.strip()]
        _by, _selector = _method(locator.strip())
        return _by, _selector

    return _convert


def _to_property(field_cls: Type[_RegisteredMixin], getter: _GetterFnc):
    """Convert field to property.

    Setter is taken from registry: use ``register()`` to add new binding

    Getter is defined by class of field, basically returning `field_cls(actual_element)`,
    where locator of actual element is defined in wired file
    """

    if not hasattr(field_cls, "__set_value__"):
        raise RuntimeError(f"Can't convert {field_cls} to property: method `__set_value__` is missing")

    def _property_setter(instance: Wireable, value):
        return getter(instance).__set_value__(value)

    prop = property(getter, _property_setter)
    return prop


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

    Property ``setter`` will work depending on class __set__. Setters are already set for
        - SeleneElement: SeleneElement.set
        - Select: Select.select_by_value

    To set new setter use ``register_setter`` function

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
            if isinstance(entry, str):
                strategy, selector = entry.split(":")
            else:
                strategy, selector = list(entry.items())[0]  # we use just first locator
            return _convert_locator(strategy, selector)

        with open(self.resources[locator_file]) as input_file:
            mappings = yaml.load(input_file)
        locators = {item: _parse_yml_entry(locator) for item, locator in mappings.items()}

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
                    return  # already wired
                wrapped._strategies = copy(_STRATEGIES)
                wrapped._locators = copy(locators)  # store loaded locators inside of class
                annotations = wrapped.__annotations__
                for attr in annotations:  # through all annotated attributes
                    if not hasattr(wrapped, attr):  # only not assigned attributes
                        attr_cls = annotations[attr]
                        try:
                            locator_getter = locators[attr]
                        except KeyError:
                            raise KeyError(f"Missing `{attr}` in file `{locator_file}`")
                        getter = _wired_getter(attr_cls, locator_getter)
                        getter = _cached_getter(getter, attr)  # Selene handles reload of elements, so we can cache it
                        new_property = _to_property(attr_cls, getter)
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


def get_custom_element(bind_obj: Wireable, field_name, field_class=SeleneElement, *field_class_args):
    """Get field with given name for wired class"""
    getter = _wired_getter(field_class, bind_obj._locators[field_name], *field_class_args)
    element = getter(bind_obj)
    return element
