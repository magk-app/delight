# Developer Quick Reference Card

**Print this or keep it open while coding!**

---

## 🎯 **The 6-Stage Story Workflow**

```
SELECT → PREPARE → DEVELOP → TEST → REVIEW → COMPLETE
```

---

## 📋 **Stage Checklist**

### **1. SELECT**

- [ ] Check `docs/sprint-status.yaml` for next backlog story
- [ ] Read story in `docs/epics.md`
- [ ] Verify prerequisites are "done"

### **2. PREPARE**

- [ ] Optional: Run `@bmad/bmm/workflows/story-context`
- [ ] Update `sprint-status.yaml` to "in-progress"
- [ ] Verify Supabase connection (DATABASE_URL in .env)
- [ ] Create branch: `git checkout -b story/X-Y-short-name`

### **3. DEVELOP**

- [ ] Create implementation checklist
- [ ] Start backend & frontend servers
- [ ] Implement features
- [ ] Test manually as you go
- [ ] Run linters before testing

### **4. TEST**

- [ ] Manual test ALL acceptance criteria
- [ ] Write unit tests (backend + frontend)
- [ ] Write integration tests (if needed)
- [ ] All tests passing

### **5. REVIEW**

- [ ] Complete self-review checklist
- [ ] Optional: Run `@bmad/bmm/workflows/code-review`
- [ ] Update `sprint-status.yaml` to "review" or "done"

### **6. COMPLETE**

- [ ] Create story summary
- [ ] Update `.cursor-changes`
- [ ] Commit with detailed message
- [ ] Merge to main
- [ ] Clean up branch
- [ ] Celebrate! 🎉

---

## ⌨️ **Common Commands**

### **Start Development**

```bash
# No Docker needed for database! Just Supabase connection string.

# Backend (Terminal 1)
cd packages/backend
poetry run uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd packages/frontend
npm run dev

# Optional: Redis (Terminal 3) - only if using local Redis
docker run -d -p 6379:6379 redis:7
# OR use Upstash (serverless, free tier)
```

### **Testing**

```bash
# Backend tests
cd packages/backend
poetry run pytest -v --cov=app

# Frontend tests
cd packages/frontend
npm test -- --coverage --watchAll=false

# E2E tests
cd packages/frontend
npm run test:e2e
```

### **Code Quality**

```bash
# Backend
poetry run black .
poetry run ruff check .
poetry run mypy app

# Frontend
npm run lint
npm run type-check
```

### **Git Workflow**

```bash
# Create branch
git checkout -b story/1-3-short-name

# Commit
git add .
git commit -m "Story X.Y: Title

Details here"

# Merge
git checkout main
git merge story/1-3-short-name
git push origin main
```

---

## 📝 **Files to Update**

### **During Development**

- Code files (obviously!)
- Tests (`tests/` or `__tests__/`)

### **Before Commit**

- `docs/sprint-status.yaml` → Update status
- `docs/stories/story-X.Y-summary.md` → Create summary
- `.cursor-changes` → Log changes
- `README.md` → If new setup/env vars

---

## ✅ **Pre-Commit Checklist**

```markdown
Code:

- [ ] All acceptance criteria met
- [ ] No console.log or TODO comments
- [ ] Error handling implemented
- [ ] Types added (TS) / Type hints (Python)

Testing:

- [ ] Manual tests pass
- [ ] Unit tests written & passing
- [ ] Integration tests (if needed)
- [ ] Coverage targets met (≥70% BE, ≥60% FE)

Quality:

- [ ] Linting clean
- [ ] Formatting applied
- [ ] No hardcoded values
- [ ] Comments for complex logic

Docs:

- [ ] Story summary created
- [ ] Change log updated
- [ ] README updated (if needed)
- [ ] sprint-status.yaml updated to "done"
```

---

## 🆘 **Quick Troubleshooting**

### **Tests Failing**

```bash
poetry install && npm install
docker-compose restart
rm -rf .next __pycache__
```

### **Port Already in Use**

```bash
# Windows
netstat -ano | findstr :8000

# Mac/Linux
lsof -i :8000
```

### **Database Issues**

```bash
# Supabase: Check connection
echo $DATABASE_URL

# Re-run migrations
cd packages/backend
poetry run alembic upgrade head

# If using local Redis:
docker restart redis
```

### **Git Conflicts**

```bash
git checkout main
git pull
git checkout your-branch
git rebase main
# Fix conflicts, then:
git add .
git rebase --continue
```

---

## 🎮 **BMAD Workflows**

```bash
# Before coding
@bmad/bmm/workflows/story-context

# During coding
@bmad/bmm/agents/dev

# Before commit
@bmad/bmm/workflows/code-review

# After testing
@bmad/bmm/workflows/story-done
```

---

## 📊 **Story Status Values**

- `backlog` → Not started yet
- `in-progress` → Currently working on it
- `review` → Ready for team review
- `done` → Completed and merged
- `deferred` → Postponed to later

---

## 🎯 **Testing Pyramid**

```
    E2E (Few)
   Integration (Some)
  Unit (Many)
```

**Test every acceptance criterion at minimum!**

---

## 💡 **Pro Tips**

1. ✅ **Read the story twice** before coding
2. ✅ **Test as you build**, don't wait
3. ✅ **Commit frequently** (small commits)
4. ✅ **Write tests first** (TDD when possible)
5. ✅ **Take breaks** during self-review
6. ✅ **Ask questions** early and often
7. ✅ **Celebrate wins** (even small ones!)

---

## 📖 **Key Documents**

- **Full Guide:** `docs/dev/BMAD-DEVELOPER-GUIDE.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Stories:** `docs/epics.md`
- **Sprint Status:** `docs/sprint-status.yaml`

---

**Remember: Systems beat willpower. Follow the process!**

---

**Version:** 1.0.0 | **Updated:** 2025-11-10
