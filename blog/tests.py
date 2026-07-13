from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from blog.models import Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@test.com", password="pass1234"
        )

    def test_post_str(self):
        post = Post.objects.create(
            title="Test Post",
            content="Content with more than 10 chars",
            author=self.user,
        )
        self.assertEqual(str(post), "Test Post")

    def test_slug_generated_from_title(self):
        post = Post.objects.create(
            title="Hello World",
            content="Content with more than 10 chars",
            author=self.user,
        )
        self.assertEqual(post.slug, "hello-world")

    def test_slug_unique_with_counter(self):
        Post.objects.create(
            title="Same Title",
            content="Content with more than 10 chars",
            author=self.user,
        )
        post2 = Post.objects.create(
            title="Same Title",
            content="Content with more than 10 chars",
            author=self.user,
        )
        self.assertEqual(post2.slug, "same-title-1")

    def test_published_at_set_on_publish(self):
        post = Post.objects.create(
            title="Draft Post",
            content="Content with more than 10 chars",
            author=self.user,
            status=Post.Status.DRAFT,
        )
        self.assertIsNone(post.published_at)
        post.status = Post.Status.PUBLISHED
        post.save()
        self.assertIsNotNone(post.published_at)

    def test_published_at_not_overwritten(self):
        post = Post.objects.create(
            title="Published Post",
            content="Content with more than 10 chars",
            author=self.user,
            status=Post.Status.PUBLISHED,
        )
        first_published = post.published_at
        post.title = "Updated Title"
        post.save()
        self.assertEqual(post.published_at, first_published)

    def test_default_status_is_draft(self):
        post = Post.objects.create(
            title="Post",
            content="Content with more than 10 chars",
            author=self.user,
        )
        self.assertEqual(post.status, Post.Status.DRAFT)

    def test_ordering_by_created_at_desc(self):
        p1 = Post.objects.create(
            title="First",
            content="Content with more than 10 chars",
            author=self.user,
        )
        p2 = Post.objects.create(
            title="Second",
            content="Content with more than 10 chars",
            author=self.user,
        )
        posts = list(Post.objects.all())
        self.assertEqual(posts[0], p2)
        self.assertEqual(posts[1], p1)


class PostViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="author@test.com", password="pass1234"
        )
        cls.other_user = User.objects.create_user(
            email="other@test.com", password="pass1234"
        )
        cls.client = Client()

    def test_home_shows_only_published(self):
        Post.objects.create(
            title="Published",
            content="Content with more than 10 chars",
            author=self.user,
            status=Post.Status.PUBLISHED,
        )
        Post.objects.create(
            title="Draft",
            content="Content with more than 10 chars",
            author=self.user,
            status=Post.Status.DRAFT,
        )
        response = self.client.get("/")
        self.assertContains(response, "Published")
        self.assertNotContains(response, "Draft")

    def test_home_pagination(self):
        for i in range(7):
            Post.objects.create(
                title=f"Post {i}",
                content="Content with more than 10 chars",
                author=self.user,
                status=Post.Status.PUBLISHED,
            )
        response = self.client.get("/")
        self.assertContains(response, "Post 6")
        self.assertNotContains(response, "Post 0")

    def test_post_detail_published(self):
        post = Post.objects.create(
            title="Visible Post",
            content="Content with more than 10 chars",
            author=self.user,
            status=Post.Status.PUBLISHED,
        )
        response = self.client.get(f"/post/{post.slug}/")
        self.assertEqual(response.status_code, 200)

    def test_post_detail_draft_hidden_from_guest(self):
        post = Post.objects.create(
            title="Hidden Draft",
            content="Content with more than 10 chars",
            author=self.user,
            status=Post.Status.DRAFT,
        )
        response = self.client.get(f"/post/{post.slug}/")
        self.assertEqual(response.status_code, 404)

    def test_post_detail_draft_visible_to_author(self):
        post = Post.objects.create(
            title="My Draft",
            content="Content with more than 10 chars",
            author=self.user,
            status=Post.Status.DRAFT,
        )
        self.client.login(email="author@test.com", password="pass1234")
        response = self.client.get(f"/post/{post.slug}/")
        self.assertEqual(response.status_code, 200)

    def test_post_create_requires_login(self):
        response = self.client.get("/post/new/")
        self.assertEqual(response.status_code, 302)

    def test_post_create_success(self):
        self.client.login(email="author@test.com", password="pass1234")
        response = self.client.post("/post/new/", {
            "title": "New Post",
            "content": "Content with more than 10 chars",
            "status": "draft",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title="New Post").exists())

    def test_post_edit_forbidden_for_other_user(self):
        post = Post.objects.create(
            title="Someone Post",
            content="Content with more than 10 chars",
            author=self.user,
        )
        self.client.login(email="other@test.com", password="pass1234")
        response = self.client.get(f"/post/{post.slug}/edit/")
        self.assertEqual(response.status_code, 403)

    def test_post_edit_by_author(self):
        post = Post.objects.create(
            title="My Post",
            content="Content with more than 10 chars",
            author=self.user,
        )
        self.client.login(email="author@test.com", password="pass1234")
        response = self.client.post(f"/post/{post.slug}/edit/", {
            "title": "Edited Post",
            "content": "Content with more than 10 chars",
            "status": "draft",
        })
        self.assertEqual(response.status_code, 302)
        post.refresh_from_db()
        self.assertEqual(post.title, "Edited Post")

    def test_post_delete_forbidden_for_other_user(self):
        post = Post.objects.create(
            title="Someone Post",
            content="Content with more than 10 chars",
            author=self.user,
        )
        self.client.login(email="other@test.com", password="pass1234")
        response = self.client.post(f"/post/{post.slug}/delete/")
        self.assertEqual(response.status_code, 403)

    def test_post_delete_by_author(self):
        post = Post.objects.create(
            title="My Post",
            content="Content with more than 10 chars",
            author=self.user,
        )
        self.client.login(email="author@test.com", password="pass1234")
        response = self.client.post(f"/post/{post.slug}/delete/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(slug=post.slug).exists())

    def test_my_posts_shows_drafts(self):
        Post.objects.create(
            title="My Draft",
            content="Content with more than 10 chars",
            author=self.user,
            status=Post.Status.DRAFT,
        )
        self.client.login(email="author@test.com", password="pass1234")
        response = self.client.get("/my-posts/")
        self.assertContains(response, "My Draft")

    def test_my_posts_requires_login(self):
        response = self.client.get("/my-posts/")
        self.assertEqual(response.status_code, 302)


class PostFormValidationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@test.com", password="pass1234"
        )

    def test_empty_title_invalid(self):
        self.client = Client()
        self.client.login(email="test@test.com", password="pass1234")
        response = self.client.post("/post/new/", {
            "title": "",
            "content": "Valid content here that is long",
            "status": "draft",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(title="").exists())

    def test_short_content_invalid(self):
        self.client = Client()
        self.client.login(email="test@test.com", password="pass1234")
        response = self.client.post("/post/new/", {
            "title": "Valid Title",
            "content": "short",
            "status": "draft",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(title="Valid Title").exists())
