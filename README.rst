django-treeform
========================================

.. code:: python

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
