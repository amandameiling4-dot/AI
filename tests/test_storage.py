from backend.storage import AppStore


def test_store_persists_thoughts_apps_and_builds(tmp_path):
    db_path = tmp_path / "app_store.sqlite3"
    store = AppStore(db_path=str(db_path))

    store.add_connected_app("notes-app", "app-1")
    store.add_thought("hello world", "user")
    store.add_generated_app(
        project_name="hello-world",
        description="build a landing page",
        app_type="website",
        generated_files=["index.html"],
        security_checks=["prompt scan"],
    )

    thoughts = store.list_thoughts()
    connected_apps = store.list_connected_apps()
    builds = store.list_generated_apps()

    assert len(thoughts) == 1
    assert thoughts[0]["content"] == "hello world"
    assert len(connected_apps) == 1
    assert connected_apps[0]["app_id"] == "app-1"
    assert len(builds) == 1
    assert builds[0]["project_name"] == "hello-world"
