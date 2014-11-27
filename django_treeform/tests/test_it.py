# -*- coding:utf-8 -*-
import unittest
from django import forms


class PointForm(forms.Form):
    x = forms.IntegerField()
    y = forms.IntegerField()


class SequenceTests(unittest.TestCase):
    def _getTarget(self):
        from django_treeform import Sequence
        return Sequence

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it_success(self):
        FormLikeClass = self._makeOne(PointForm)
        params = [{"x": "10", "y": "20"}]
        formlike = FormLikeClass(params)

        self.assertTrue(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, [{"x": 10, "y": 20}])
        self.assertEqual(formlike.errors, [{}])

    def test_it_failure(self):
        FormLikeClass = self._makeOne(PointForm)
        params = [{"x": "aaaa", "y": "20"}]
        formlike = FormLikeClass(params)

        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, [{"y": 20}])
        self.assertNotEqual(formlike.errors, [{}])

    def test_it_missing(self):
        FormLikeClass = self._makeOne(PointForm)
        params = [{"y": "20"}]
        formlike = FormLikeClass(params)

        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, [{"y": 20}])
        self.assertNotEqual(formlike.errors, [{}])

    def test_with_custom_validation__success(self):
        def clean(self):
            if any(self.errors):
                return
            if len(self.cleaned_data) > 2:
                raise forms.ValidationError("oops")

        FormLikeClass = self._makeOne(PointForm, clean=clean)
        params = [{"x": "10", "y": "20"}]
        formlike = FormLikeClass(params)

        self.assertTrue(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, [{"x": 10, "y": 20}])
        self.assertEqual(formlike.errors, [{}])

    def test_with_custom_validation__failure(self):
        def clean(self):
            if any(self.errors):
                return
            if len(self.cleaned_data) < 2:
                raise forms.ValidationError("oops")

        FormLikeClass = self._makeOne(PointForm, clean=clean)
        params = [{"x": "10", "y": "20"}]
        formlike = FormLikeClass(params)

        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, [{"x": 10, "y": 20}])
        self.assertEqual(formlike.errors, [{}])
        self.assertEqual(formlike.non_form_errors, ["oops"])


class NodeTests(unittest.TestCase):
    def _getTarget(self):
        from django_treeform import Node
        return Node

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it_success(self):
        FormLikeClass = self._makeOne(PointForm)("left")
        params = {"left": {"x": "10", "y": "20"}}
        formlike = FormLikeClass(params)

        self.assertTrue(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"left": {"x": 10, "y": 20}})
        self.assertEqual(formlike.errors, {"left": {}})

    def test_it_failure(self):
        FormLikeClass = self._makeOne(PointForm)("left")
        params = {"left": {"x": "aaa", "y": "20"}}
        formlike = FormLikeClass(params)

        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"left": {"y": 20}})
        self.assertNotEqual(formlike.errors, {"left": {}})

    def test_it_missing(self):
        FormLikeClass = self._makeOne(PointForm)("left")
        params = {"left": {"y": "20"}}
        formlike = FormLikeClass(params)

        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"left": {"y": 20}})
        self.assertNotEqual(formlike.errors, {"left": {}})


class TreeFormTests(unittest.TestCase):
    def _getTarget(self):
        from django_treeform import TreeForm
        return TreeForm

    def _makeOne(self, params):
        from django_treeform import Node

        class PointPairForm(self._getTarget()):
            left = Node(PointForm)
            right = Node(PointForm)
        return PointPairForm(params)

    def test_it_success(self):
        params = {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": "20"}}
        formlike = self._makeOne(params)

        self.assertTrue(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": 20}})
        self.assertEqual(formlike.errors, {"left": {}, "right": {}})

    def test_it_failure(self):
        params = {"left": {"x": 10, "y": "aaa"}, "right": {"x": 20, "y": "20"}}
        formlike = self._makeOne(params)

        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"left": {"x": 10}, "right": {"x": 20, "y": 20}})
        self.assertNotEqual(formlike.errors, {"left": {}, "right": {}})


class TreeFormTests2(unittest.TestCase):
    def _getTarget(self):
        from django_treeform import TreeForm
        return TreeForm

    def _makeOne(self, params):
        from django_treeform import Sequence, Node

        class PointListForm(self._getTarget()):
            points = Node(Sequence(PointForm))
        return PointListForm(params)

    def test_it_success(self):
        params = {"points": [{"x": 10, "y": 20}, {"x": 20, "y": "20"}]}
        formlike = self._makeOne(params)

        self.assertTrue(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"points": [{"x": 10, "y": 20}, {"x": 20, "y": 20}]})
        self.assertEqual(formlike.errors, {"points": [{}, {}]})


class TreeFormTests3(unittest.TestCase):
    def _getTarget(self):
        from django_treeform import TreeForm
        return TreeForm

    def _makeOne(self, params):
        from django_treeform import Node, SequenceNode

        class ItemForm(forms.Form):
            name = forms.CharField()

        class NestedForm(self._getTarget()):
            class pair(self._getTarget()):
                left = Node(PointForm)
                right = Node(PointForm)
            items = SequenceNode(ItemForm)
        return NestedForm(params)

    def test_it_success(self):
        params = {
            "pair": {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": "20"}},
            "items": [{"name": "A"}, {"name": "B"}]
        }
        formlike = self._makeOne(params)

        self.assertTrue(formlike.is_valid())
        expected = {'items': [{'name': 'A'}, {'name': 'B'}],
                    'pair': {'left': {'x': 10, 'y': 20}, 'right': {'x': 20, 'y': 20}}}
        self.assertEqual(formlike.cleaned_data, expected)
        self.assertEqual(formlike.errors, {"items": [{}, {}], "pair": {"left": {}, "right": {}}})


class TreeFormTests4(unittest.TestCase):
    def _getTarget(self):
        from django_treeform import TreeForm
        return TreeForm

    def _makeOne(self, params):
        from django_treeform import SequenceNode

        class ItemForm(forms.Form):
            name = forms.CharField()

        class NestedForm(self._getTarget()):
            class a(self._getTarget()):
                class b(self._getTarget()):
                    class c(self._getTarget()):
                        class d(self._getTarget()):
                            class e(self._getTarget()):
                                items = SequenceNode(ItemForm)
        return NestedForm(params)

    def test_it_success(self):
        params = {
            "a": {"b": {"c": {"d": {"e": {"items": [{"name": "A"}, {"name": "B"}]}}}}}
        }
        formlike = self._makeOne(params)

        self.assertTrue(formlike.is_valid())
        expected = {'a': {'b': {'c': {'d': {'e': {'items': [{'name': 'A'}, {'name': 'B'}]}}}}}}
        self.assertEqual(formlike.cleaned_data, expected)
        self.assertEqual(formlike.errors, {'a': {'b': {'c': {'d': {'e': {'items': [{}, {}]}}}}}})
