from nebriosmodels import NebriOSField, NebriOSModel

class TemplateCard(NebriOSModel):

    card_id = NebriOSField(required=True)
    custom_send = NebriOSField()
    # card_items = NebriOSField(required=True)