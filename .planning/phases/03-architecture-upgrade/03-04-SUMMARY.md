# Plan 03-04: Migrate Raw SQL to Django ORM — Summary

**Date:** 2026-08-08
**Status:** ✅ Complete

## Overview

Successfully migrated all raw SQL queries (`g_database.select()` and `g_database.execute()`) to Django ORM across 6 files.

## Files Modified

### 1. `app/views/StreamView.py` — 12 raw SQL → ORM
- **Line 34:** `SELECT ... WHERE pull_stream_type=1` → `StreamModel.objects.filter(pull_stream_type=1).order_by('-id').values()[:1]`
- **Line 212:** SQL injection (`WHERE code='%s'`) → `StreamModel.objects.filter(code=stream_code).values().first()`
- **Line 253:** SQL injection (`WHERE app='%s' AND name='%s'`) → `StreamModel.objects.filter(app=app, name=name).values().first()`
- **Line 526:** `UPDATE av_stream SET forward_state=0` → `StreamModel.objects.update(forward_state=0)`
- **Line 540:** `UPDATE ... WHERE id=%d` → `StreamModel.objects.filter(id=d_id).update(forward_state=1)`
- **Line 543:** `UPDATE ... WHERE id=%d` → `StreamModel.objects.filter(id=d_id).update(forward_state=0)`
- **Lines 562-579:** Dynamic SQL with string formatting → ORM queryset with `Q` objects for search/filter
- **Line 1083:** `SELECT id,app,name,code,nickname` → `StreamModel.objects.values('id', 'app', 'name', 'code', 'nickname')`
- **Line 1136:** `SELECT app,name` → `StreamModel.objects.values('app', 'name')`

### 2. `app/views/ViewsBase.py` — 1 raw SQL → ORM
- **Line 132:** `f_dbReadStreamData()` → `StreamModel.objects.order_by('-id').values()`

### 3. `app/utils/GlobalUtils.py` — 2 raw SQL → ORM
- **Line 150:** `UPDATE av_stream SET forward_state=0` → `StreamModel.objects.update(forward_state=0)`
- **Line 212:** `UPDATE av_stream SET forward_state=0` → `StreamModel.objects.update(forward_state=0)`

### 4. `app/views/LLMView.py` — 2 raw SQL → ORM
- **Line 32:** `SELECT count(id) as count FROM av_llm` → `LLMModel.objects.count()`
- **Lines 36-37:** `SELECT * ... LIMIT %d,%d` → `LLMModel.objects.order_by('-id').values()[skip:skip+page_size]`

### 5. `app/views/UserView.py` — 2 raw SQL → ORM
- **Lines 119-126:** `SELECT count(id) ... FROM auth_user` + `SELECT * ... LIMIT %d,%d` → `User.objects.count()` + `User.objects.order_by('-id').values()[skip:skip+page_size]`
- **Lines 284-286:** SQL injection (`WHERE id!=%d AND username='%s'`) → `User.objects.filter(username=username).exclude(id=user_id).count()`

### 6. `app/views/SystemView.py` — 1 raw SQL → ORM
- **Line 286:** `SELECT * FROM av_log ORDER BY id DESC LIMIT 100` → `LogModel.objects.order_by('-id')[:100].values()`

## Security Improvements

- **Fixed 3 SQL injection vulnerabilities** in StreamView.py (lines 212, 253) and UserView.py (line 284)
  - All user-provided values now use parameterized ORM queries instead of string formatting

## Verification Results

```powershell
# All view files: zero g_database. calls
Select-String -Path "app\views\StreamView.py" -Pattern "g_database\." -Quiet    # False ✓
Select-String -Path "app\views\ViewsBase.py" -Pattern "g_database\." -Quiet     # False ✓
Select-String -Path "app\views\LLMView.py" -Pattern "g_database\." -Quiet      # False ✓
Select-String -Path "app\views\UserView.py" -Pattern "g_database\." -Quiet     # False ✓
Select-String -Path "app\views\SystemView.py" -Pattern "g_database\." -Quiet   # False ✓

# GlobalUtils.py: zero g_database. calls
Select-String -Path "app\utils\GlobalUtils.py" -Pattern "g_database\." -Quiet  # False ✓
```

## Notes

- The `g_database` instance in `GlobalUtils.py:48` is retained for backward compatibility (other modules may still reference it)
- Added `from django.db.models import Q` import to StreamView.py for complex search filtering
- All ORM queries preserve existing behavior (search, pagination, filtering, ordering)
- `values()` returns dictionaries, maintaining API compatibility with frontend templates
