from plone.app.content.browser.vocabulary import SourceView


class SourceView(SourceView):
    """ Patch Plone SourceView's get_context() method 
        since context of the subform is a dictionary (which is correct)
    """

    def get_context(self):
        #Get form object
        form = self.context.form
        try:
            parent_form = form.__parent__.form
        except:
            parent_form = None
        if parent_form:
            return parent_form.context
        else:
            return form.context