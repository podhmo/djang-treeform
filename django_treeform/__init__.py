# -*- coding:utf-8 -*-
from functools import partial
from django.utils.functional import cached_property
from django import forms


class _Node(object):
    def __init__(self, formclass, keyname, params):
        self.formclass = formclass
        self.keyname = keyname
        self.form = formclass(params[keyname])

    def is_valid(self):
        return self.form.is_valid()

    @cached_property
    def errors(self):
        return {self.keyname: self.form.errors}

    @cached_property
    def cleaned_data(self):
        self.is_valid()
        return {self.keyname: self.form.cleaned_data}


class _Sequence(object):
    def __init__(self, formclass, list_of_params, clean=None):
        self.formclass = formclass
        self.forms = [formclass(params) for params in list_of_params]
        self._clean = clean
        self.non_form_errors = []

    def is_valid(self):
        status = all(form.is_valid() for form in self.forms)
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
        return [form.errors for form in self.forms]

    @cached_property
    def cleaned_data(self):
        return [form.cleaned_data for form in self.forms]


class PartialWrapper(object):
    def __init__(self, cls, formclass):
        self.cls = cls
        self.formclass = formclass

    def __call__(self, keyname):
        return partial(self.cls, self.formclass, keyname)


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

    def is_valid(self):
        return all(node.is_valid() for node in self.nodes)

    @cached_property
    def errors(self):
        errors = {}
        for node in self.nodes:
            errors.update(node.errors)
        return errors

    @cached_property
    def cleaned_data(self):
        cleaned_data = {}
        for node in self.nodes:
            cleaned_data.update(node.cleaned_data)
        return cleaned_data

TreeForm = TreeFormMeta("TreeForm", (_TreeForm, ), {})


def Sequence(formclass, clean=None):
    return partial(_Sequence, formclass, clean=clean)


def Node(formclass):
    return PartialWrapper(_Node, formclass)


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
