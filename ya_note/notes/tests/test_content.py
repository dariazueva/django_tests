from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Брэд Пит'
        )
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст', author=cls.author)
        cls.reader = User.objects.create(username='Анон')

    def test_notes_list_for_different_users(self):
        users_note_in_list = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in users_note_in_list:
            self.client.force_login(user)
            with self.subTest(user=user):
                url = reverse('notes:list', None)
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, note_in_list)

    def test_create_note_page_contains_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_edit_note_page_contains_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)
