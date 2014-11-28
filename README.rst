django-treeform
========================================

.. code:: python

    from django import forms
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
    print(form.is_valid()) # => True

more nested forms

.. code:: python

    from django import forms
    from django_treeform import SequenceNode, TreeForm

    class ItemForm(forms.Form):
        name = forms.CharField()


    class NestedForm(TreeForm):
        class a(TreeForm):
            class b(TreeForm):
                class c(TreeForm):
                    class d(TreeForm):
                        class e(TreeForm):
                            items = SequenceNode(ItemForm)

    params = {
        "a": {"b": {"c": {"d": {"e": {"items": [{"name": "A"}, {"name": "B"}]}}}}}
    }
    formlike = NestedForm(params)

    print(formlike.is_valid()) # => True
    expected = {'a': {'b': {'c': {'d': {'e': {'items': [{'name': 'A'}, {'name': 'B'}]}}}}}}
    assert formlike.cleaned_data == expected
    assert formlike.errors == {'a': {'b': {'c': {'d': {'e': {'items': [{}, {}]}}}}}}

custom validation

.. code:: python

    class PointForm(forms.Form):
        x = forms.IntegerField()
        y = forms.IntegerField()


    class PointPairForm(TreeForm):
        left = Node(PointForm)
        right = Node(PointForm)

        def clean(self):
            if self.has_error():
                return
            if self.cleaned_data["left"]["x"] < self.cleaned_data["right"]["x"]:
                raise forms.ValidationError("oops")

    params = {"left": {"x": 10, "y": 20}, "right": {"x": 20, "y": "20"}}
    formlike = PointPairForm(params)
    print(formlike.is_valid() # => False
    print(formlike.errors) # => {"left": {}, "right": {}, "__all__": ["oops"]}
