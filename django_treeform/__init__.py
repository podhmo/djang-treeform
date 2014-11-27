# -*- coding:utf-8 -*-
from functools import partial
from django.utils.functional import cached_property
from django import forms


class _Node(object):
    def __init__(self, formclass, keyname, params, clean=None):
        self.formclass = formclass
        self.keyname = keyname
        self.form = formclass(params[keyname])
        self._clean = clean
        self.configured = False
        self._self_errors = []

    def is_valid(self):
        status = self.form.is_valid()
        self.configured = True
        try:
            self.clean()
        except forms.ValidationError as e:
            self._self_errors.append(e.args[0])
            status = False
        return status

    def clean(self):
        if self._clean is None:
            return
        self._clean(self)

    @property
    def errors(self):
        if not self.configured:
            raise RuntimeError("is_valid() is not called")
        errors = self.form.errors

        if bool(self._self_errors):
            if "__all__" in errors:
                errors["__all__"].extend(self._self_errors)
            else:
                errors["__all__"] = self._self_errors
        if hasattr(self.form, "non_form_errors") and bool(self.form.non_form_errors):
            if "__all__" in errors:
                errors["__all__"].extend(self.form.non_form_errors)
            else:
                errors["__all__"] = self.form.non_form_errors
        return errors

    @cached_property
    def cleaned_data(self):
        if not self.configured:
            raise RuntimeError("is_valid() is not called")
        return self.form.cleaned_data

    def has_error(self):
        if hasattr(self.formclass, "has_error"):
            return self.form.has_error() or bool(self.non_form_errors)
        else:
            return any(self.errors.values())


class _Sequence(object):
    def __init__(self, formclass, list_of_params, clean=None):
        self.formclass = formclass
        self.forms = [formclass(params) for params in list_of_params]
        self._clean = clean
        self.non_form_errors = []
        self.configured = False

    def is_valid(self):
        status = all([form.is_valid() for form in self.forms])
        self.configured = True
        try:
            self.clean()
        except forms.ValidationError as e:
            self.non_form_errors.append(e.args[0])
            status = False
        return status

    def clean(self):
        if self._clean is None:
            return
        self._clean(self)

    @cached_property
    def errors(self):
        if not self.configured:
            raise RuntimeError("is_valid() is not called")
        return [form.errors for form in self.forms]

    @cached_property
    def cleaned_data(self):
        if not self.configured:
            raise RuntimeError("is_valid() is not called")
        return [form.cleaned_data for form in self.forms]

    def has_error(self):
        if hasattr(self.formclass, "has_error"):
            return any(f.has_error() for f in self.forms) or bool(self.non_form_errors)
        else:
            return any(self.errors)


class PartialWrapper(object):
    def __init__(self, cls, formclass, clean=None):
        self.cls = cls
        self.formclass = formclass
        self.clean = clean

    def __call__(self, keyname):
        return partial(self.cls, self.formclass, keyname, clean=self.clean)


class TreeFormMeta(type):
    def __new__(self, name, bases, attrs):
        cls = super(TreeFormMeta, self).__new__(self, name, bases, attrs)
        if "factories" not in cls.__dict__:
            cls.factories = set()

        for k, v in cls.__dict__.items():
            if isinstance(v, PartialWrapper):
                cls.factories.add(v(k))
            elif isinstance(v, TreeFormMeta):
                cls.factories.add(Node(v)(v.__name__))
        return cls


class _TreeForm(object):
    def __init__(self, params):
        self.nodes = [f(params) for f in self.factories]
        self.non_form_errors = []
        self.configured = False

    def is_valid(self):
        status = all([node.is_valid() for node in self.nodes])
        self.configured = True
        try:
            self.clean()
        except forms.ValidationError as e:
            self.non_form_errors.append(e.args[0])
            status = False
        return status

    def clean(self):
        pass

    @cached_property
    def errors(self):
        if not self.configured:
            raise RuntimeError("is_valid() is not called")
        errors = {}
        for node in self.nodes:
            errors.update({node.keyname: node.errors})
        if bool(self.non_form_errors):
            if "__all__" not in errors:
                errors["__all__"] = []
            errors["__all__"].extend(self.non_form_errors)
        return errors

    @cached_property
    def cleaned_data(self):
        if not self.configured:
            raise RuntimeError("is_valid() is not called")
        cleaned_data = {}
        for node in self.nodes:
                cleaned_data.update({node.keyname: node.cleaned_data})
        return cleaned_data

    def has_error(self):
        return any(node.has_error() for node in self.nodes)


TreeForm = TreeFormMeta("TreeForm", (_TreeForm, ), {})


def Sequence(formclass, clean=None):
    return partial(_Sequence, formclass, clean=clean)


def Node(formclass, clean=None):
    return PartialWrapper(_Node, formclass, clean=clean)


def SequenceNode(formclass):
    return Node(Sequence(formclass))


'''
class PointForm(Form):
  x = forms.IntegerField()
  y = forms.IntegerField()

PointsForm = Sequence(PointForm)

class PointPairForm(TreeForm):
    """receive: {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": "20"}}"""
    left = Node(PointForm)
    right = Node(PointForm)

class PointListForm(TreeForm):
    """receive: {"points": [{"x": 10, "y": 20}, {"x": 20, "y": "20"}]}"""
    points = Node(Sequence(PointForm))
'''
