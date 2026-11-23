from aqt import mw, gui_hooks

def on_profile_opened():
    _load_config() 

    try:
        _db_open()
    except Exception:
        pass

    if LANG_PROFILE == "auto":
        try:
            lang = _guess_lang_from_sources()
            if lang:
                globals()["LANG_PROFILE"] = lang
        except Exception:
            pass

    if not DB_MODE:
        _load_sources()
        _reload_all_sources()

    _start_server()
    _nuke(mw.web)
    build_yomi_menu()

    from aqt.qt import QTimer
    QTimer.singleShot(1200, _show_whats_new)

    gui_hooks.reviewer_did_show_question.append(_on_q)
    gui_hooks.reviewer_did_show_answer.append(_on_a)
    gui_hooks.state_did_change.append(_on_state_change)

def _run_on_profile_opened():
    mw.taskman.run_on_main(on_profile_opened)

gui_hooks.profile_did_open.append(_run_on_profile_opened)


if mw and mw.app:
    try:
        mw.app.aboutToQuit.connect(cleanup_on_exit)
    except Exception:
        pass

# Hook AddonManager cleanup points to release database file locks on Windows when deleting/updating.
try:
    from aqt.addons import AddonManager
    _addon_dir_name = os.path.basename(ADDON_DIR)

    if not hasattr(AddonManager, "_old_backupUserFiles_yomilens") and hasattr(AddonManager, "backupUserFiles"):
        AddonManager._old_backupUserFiles_yomilens = AddonManager.backupUserFiles

        def _yomilens_backup_user_files(self, *args, **kwargs):
            target = str(args[0]) if args else ""
            if target == _addon_dir_name or os.path.basename(target) == _addon_dir_name:
                cleanup_on_exit()
            return self._old_backupUserFiles_yomilens(*args, **kwargs)

        AddonManager.backupUserFiles = _yomilens_backup_user_files

    if not hasattr(AddonManager, "_old_deleteAddon_hanzi_popup"):
        AddonManager._old_deleteAddon_hanzi_popup = AddonManager.deleteAddon

        def _my_delete_addon(self, dir_name):
            if dir_name == _addon_dir_name:
                cleanup_on_exit()
            return self._old_deleteAddon_hanzi_popup(dir_name)

        AddonManager.deleteAddon = _my_delete_addon
except Exception:
    pass