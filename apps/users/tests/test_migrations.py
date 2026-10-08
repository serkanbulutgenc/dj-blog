import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


@pytest.mark.django_db(transaction=True)
def test_removing_user_name_preserves_it_in_profile_info():
    executor = MigrationExecutor(connection)
    latest_migrations = executor.loader.graph.leaf_nodes()
    migration_before_name_removal = ("users", "0002_profile")

    try:
        executor.migrate([migration_before_name_removal])
        old_apps = executor.loader.project_state([migration_before_name_removal]).apps
        legacy_user = old_apps.get_model("users", "User").objects.create_user(
            username="legacy-name-user",
            name="Legacy Full Name",
        )
        old_apps.get_model("users", "Profile").objects.create(
            user_id=legacy_user.pk,
            info={"bio": "Existing profile data"},
        )
        old_apps.get_model("users", "User").objects.create_user(
            username="legacy-user-without-name",
        )
        MigrationExecutor(connection).migrate(latest_migrations)

        migrated_apps = (
            MigrationExecutor(connection)
            .loader.project_state(
                latest_migrations,
            )
            .apps
        )
        profile = migrated_apps.get_model("users", "Profile").objects.get(
            user__username="legacy-name-user",
        )
        assert profile.info == {
            "bio": "Existing profile data",
            "name": "Legacy Full Name",
        }
        assert (
            migrated_apps.get_model("users", "Profile")
            .objects.filter(
                user__username="legacy-user-without-name",
            )
            .exists()
        )
    finally:
        MigrationExecutor(connection).migrate(latest_migrations)
