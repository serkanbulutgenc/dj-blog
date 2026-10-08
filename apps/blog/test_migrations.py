import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


@pytest.mark.django_db(transaction=True)
def test_existing_posts_survive_owner_migration_without_an_owner():
    executor = MigrationExecutor(connection)
    latest_migrations = executor.loader.graph.leaf_nodes()
    migration_before_owner = ("blog", "0004_tag_post_tags")

    try:
        executor.migrate([migration_before_owner])
        old_apps = executor.loader.project_state([migration_before_owner]).apps
        legacy_post = old_apps.get_model("blog", "Post").objects.create(
            title="Legacy post",
            slug="legacy-post",
            content="Created before posts had owners.",
        )
        MigrationExecutor(connection).migrate([("blog", "0006_alter_post_owner")])

        migrated_apps = (
            MigrationExecutor(connection)
            .loader.project_state(
                latest_migrations,
            )
            .apps
        )
        migrated_post = migrated_apps.get_model("blog", "Post").objects.get(
            pk=legacy_post.pk,
        )
        assert migrated_post.owner_id is None
    finally:
        MigrationExecutor(connection).migrate(latest_migrations)


@pytest.mark.django_db(transaction=True)
def test_existing_posts_survive_like_migration():
    executor = MigrationExecutor(connection)
    latest_migrations = executor.loader.graph.leaf_nodes()
    migration_before_likes = ("blog", "0006_alter_post_owner")
    before_likes_targets = [
        migration_before_likes if app == "blog" else (app, migration)
        for app, migration in latest_migrations
    ]

    try:
        executor.migrate(before_likes_targets)
        old_apps = executor.loader.project_state(before_likes_targets).apps
        user = old_apps.get_model("users", "User").objects.create(
            username="legacy-like-owner",
        )
        legacy_post = old_apps.get_model("blog", "Post").objects.create(
            title="Post before likes",
            slug="post-before-likes",
            content="Existing content.",
            owner_id=user.pk,
        )
        executor = MigrationExecutor(connection)
        executor.migrate(latest_migrations)
        migrated_apps = executor.loader.project_state(latest_migrations).apps
        migrated_post = migrated_apps.get_model("blog", "Post").objects.get(
            pk=legacy_post.pk,
        )
        assert migrated_post.content == legacy_post.content
        assert migrated_post.owner_id == user.pk
        assert migrated_post.likes.count() == 0
    finally:
        MigrationExecutor(connection).migrate(latest_migrations)
