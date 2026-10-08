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
