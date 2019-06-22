from unittest import TestCase, skip

from dirty_models import BaseModel, IntegerField


class TestModel(BaseModel):
    inner_doc_field = IntegerField(doc='Inner doc')

    post_doc_field = IntegerField()
    """Post doc"""

    #: Pre doc
    pre_doc_field = IntegerField()

    titled_field = IntegerField(title='Titled field')


class DocStringTests(TestCase):

    def test_inner_docstring(self):
        self.assertEquals(TestModel.inner_doc_field.__doc__, 'Inner doc')

    @skip('No way')
    def test_post_docstring(self):
        self.assertEquals(TestModel().post_doc_field.__doc__, 'Post doc', TestModel().post_doc_field.__doc__)

    @skip('No way')
    def test_pre_docstring(self):
        self.assertEquals(TestModel().pre_doc_field.__doc__, 'Pre doc', TestModel().pre_doc_field.__doc__)

    def test_title(self):
        self.assertEquals(TestModel.titled_field.title, 'Titled field')
