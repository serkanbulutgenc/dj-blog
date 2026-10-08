# `apps/` Code Review Checklist

Findings from the review of the current changes under `apps/`. Check an item once its fix and regression coverage are verified.

## Critical — data loss risks, crashes

- [x] **Existing posts may prevent the owner migration from applying.** [apps/blog/migrations/0005_post_owner.py:19](./apps/blog/migrations/0005_post_owner.py) now adds a nullable owner foreign key so legacy posts without an attributable owner remain valid; the model and follow-up migration preserve nullability. Covered by a migration regression test.
- [x] **Removing `User.name` loses existing names.** [apps/users/migrations/0003_remove_user_name.py:13](./apps/users/migrations/0003_remove_user_name.py) now copies existing names to `Profile.info["name"]` and creates profiles for all existing users before removing the field. Covered by a migration regression test.
- [x] **Profile updates can crash when `user.profile` does not exist.** [apps/users/api/views.py:55](./apps/users/api/views.py) now creates a missing profile before applying submitted data. The signup signal is registered at app startup, and the data migration creates profiles for existing users.
- [x] **Partial profile updates discard existing JSON data.** [apps/users/api/views.py:56](./apps/users/api/views.py) now merges submitted profile keys recursively, preserving stored fields not included in the partial request. Covered by API regression tests.

## High — bugs, incorrect behaviour

- [x] **`/me/` accepts profile data but does not save it.** [apps/users/api/schema.py:38](./apps/users/api/schema.py) accepts a `profile` payload, and `update_current_user` now persists it and returns the updated profile. Covered by an API regression test.

## Medium — performance, maintainability

No findings.

## Low — style, minor improvement

No findings.
