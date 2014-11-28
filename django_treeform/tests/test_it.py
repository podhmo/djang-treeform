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
            if self.has_error():
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
            if self.has_error():
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

    def test_with_custom_validation__failure__multiple(self):
        def clean(self):
            if self.has_error():
                return
            if len(self.cleaned_data) < 2:
                raise forms.ValidationError("oops")

        FormLikeClass = self._makeOne(PointForm, clean=clean)
        params = [{"x": "10", "y": "20"}]
        formlike = FormLikeClass(params)

        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
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
        self.assertEqual(formlike.cleaned_data, {"x": 10, "y": 20})
        self.assertEqual(formlike.errors, {})

    def test_it_failure(self):
        FormLikeClass = self._makeOne(PointForm)("left")
        params = {"left": {"x": "aaa", "y": "20"}}
        formlike = FormLikeClass(params)

        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"y": 20})
        self.assertNotEqual(formlike.errors, {})

    def test_it_missing(self):
        FormLikeClass = self._makeOne(PointForm)("left")
        params = {"left": {"y": "20"}}
        formlike = FormLikeClass(params)

        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"y": 20})
        self.assertNotEqual(formlike.errors, {})

    def test_with_custom_validation__success(self):
        def clean(self):
            if self.has_error():
                return
            if self.cleaned_data["x"] > 20:
                raise forms.ValidationError("oops")

        FormLikeClass = self._makeOne(PointForm, clean=clean)("left")
        params = {"left": {"x": "10", "y": "20"}}
        formlike = FormLikeClass(params)

        self.assertTrue(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"x": 10, "y": 20})
        self.assertEqual(formlike.errors, {})

    def test_with_custom_validation__failure(self):
        def clean(self):
            if self.has_error():
                return
            if self.cleaned_data["x"] < 20:
                raise forms.ValidationError("oops")

        FormLikeClass = self._makeOne(PointForm, clean=clean)("left")
        params = {"left": {"x": "10", "y": "20"}}
        formlike = FormLikeClass(params)

        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"x": 10, "y": 20})
        self.assertEqual(formlike.errors, {"__all__": ["oops"]})

    def test_with_custom_validation__failure__multiple(self):
        def clean(self):
            if self.has_error():
                return
            if self.cleaned_data["x"] < 20:
                raise forms.ValidationError("oops")

        FormLikeClass = self._makeOne(PointForm, clean=clean)("left")
        params = {"left": {"x": "10", "y": "20"}}
        formlike = FormLikeClass(params)

        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"x": 10, "y": 20})
        self.assertEqual(formlike.errors, {"__all__": ["oops"]})


class NodeTests2(unittest.TestCase):
    def _getTarget(self):
        from django_treeform import Node
        return Node

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        target = self._makeOne(self._makeOne(PointForm)("Y"))("X")
        params = {"X": {"Y": {"x": "20", "y": "20"}}}
        formlike = target(params)
        self.assertTrue(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {'x': 20, 'y': 20})
        self.assertEqual(formlike.errors, {})


class FormTests(unittest.TestCase):
    def _getTarget(self):
        from django_treeform import TreeForm
        return TreeForm

    def _makeOne(self, params):
        class ItemForm(self._getTarget()):
            age = forms.IntegerField(required=False)
        return ItemForm(params)

    def test_it_success(self):
        params = {"age": "10"}
        formlike = self._makeOne(params)

        self.assertTrue(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"age": 10})
        self.assertEqual(formlike.errors, {"age": []})

    def test_it_success2(self):
        params = {}
        formlike = self._makeOne(params)

        self.assertTrue(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"age": None})
        self.assertEqual(formlike.errors, {"age": []})

    def test_it_failure(self):
        params = {"age": object()}
        formlike = self._makeOne(params)

        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.cleaned_data, {"age": None})
        self.assertNotEqual(formlike.errors, {"age": []})


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

    def test_with_custom_validation__success(self):
        from django_treeform import Node

        class PointPairForm(self._getTarget()):
            left = Node(PointForm)
            right = Node(PointForm)

            def clean(self):
                if self.has_error():
                    return
                if self.cleaned_data["left"]["x"] > self.cleaned_data["right"]["x"]:
                    raise forms.ValidationError("oops")

        params = {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": "20"}}
        formlike = PointPairForm(params)
        self.assertTrue(formlike.is_valid())
        self.assertEqual(formlike.errors, {"left": {}, "right": {}})
        self.assertEqual(formlike.cleaned_data, {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": 20}})

    def test_with_custom_validation__failure(self):
        from django_treeform import Node

        class PointPairForm(self._getTarget()):
            left = Node(PointForm)
            right = Node(PointForm)

            def clean(self):
                if self.has_error():
                    return
                if self.cleaned_data["left"]["x"] < self.cleaned_data["right"]["x"]:
                    raise forms.ValidationError("oops")

        params = {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": "20"}}
        formlike = PointPairForm(params)
        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.errors, {"left": {}, "right": {}, "__all__": ["oops"]})
        self.assertEqual(formlike.cleaned_data, {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": 20}})

    def test_with_custom_validation__failure2(self):
        from django_treeform import Node

        def clean(self):
            if self.has_error():
                return
            if self.cleaned_data["x"] >= self.cleaned_data["y"]:
                raise forms.ValidationError("oops")

        class PointPairForm(self._getTarget()):
            left = Node(PointForm, clean=clean)
            right = Node(PointForm, clean=clean)

        params = {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": "20"}}
        formlike = PointPairForm(params)
        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.errors, {"left": {}, "right": {"__all__": ["oops"]}})
        self.assertEqual(formlike.cleaned_data, {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": 20}})

    def test_with_custom_validation__failure__multiple(self):
        from django_treeform import Node

        def clean(self):
            if self.has_error():
                return
            if self.cleaned_data["x"] >= self.cleaned_data["y"]:
                raise forms.ValidationError("oops")

        class PointPairForm(self._getTarget()):
            left = Node(PointForm, clean=clean)
            right = Node(PointForm, clean=clean)

        params = {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": "20"}}
        formlike = PointPairForm(params)
        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
        self.assertFalse(formlike.is_valid())
        self.assertEqual(formlike.errors, {"left": {}, "right": {"__all__": ["oops"]}})
        self.assertEqual(formlike.cleaned_data, {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": 20}})


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


class TreeFormTests5(unittest.TestCase):
    def test_it(self):
        from django_treeform import TreeForm, SequenceNode, Sequence

        class CharacteristicForm(TreeForm):
            id = forms.IntegerField()
            name = forms.CharField()
            rating = forms.CharField()

        class PersonForm(TreeForm):
            id = forms.IntegerField()
            name = forms.CharField()
            phone = forms.CharField()
            Charecteristics = SequenceNode(CharacteristicForm)

        params = [{
            "id": 1,
            "name": "abc",
            "phone": "12345",
            "Charecteristics": [
                {
                    "id": 1,
                    "name": "Good Looking",
                    "rating": "Average",
                },
                {
                    "id": 2,
                    "name": "Smart",
                    "rating": "Excellent",
                }
            ]
        },
        {
            "id": 2,
            "name": "abc",
            "phone": "12345",
            "Charecteristics": [
                {
                    "id": 1,
                    "name": "Good Looking",
                    "rating": "Average",
                },
                {
                    "id": 2,
                    "name": "Smart",
                    "rating": "Excellent",
                }
            ]
        }]
        form = Sequence(PersonForm)(params)
        self.assertTrue(form.is_valid())
