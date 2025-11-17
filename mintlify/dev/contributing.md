# Contributing to Delight

Thank you for your interest in contributing to Delight! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and considerate in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/magk/delight/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Environment details (OS, Node version, etc.)

### Suggesting Features

1. Check if the feature has been suggested in [Issues](https://github.com/magk/delight/issues)
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Development Process

1. **Fork the repository**

2. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**

   - Follow the coding style (see below)
   - Write/update tests
   - Update documentation

4. **Test your changes**

   ```bash
   pnpm test
   pnpm lint
   ```

5. **Commit your changes**

   ```bash
   git commit -m "feat: add new feature"
   ```

   Use [Conventional Commits](https://www.conventionalcommits.org/):

   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Adding/updating tests
   - `chore:` - Maintenance tasks

6. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear title and description
   - Reference any related issues
   - Ensure CI checks pass

## Coding Standards

### TypeScript

- Use strict TypeScript configuration
- Prefer explicit types over `any`
- Use meaningful variable and function names
- Document complex logic with comments

### Code Style

- Use Prettier for formatting (configured in `.prettierrc`)
- Use ESLint rules (configured in `.eslintrc`)
- Run `pnpm format` before committing

### Testing

- Write unit tests for new features
- Maintain >80% code coverage
- Use descriptive test names

```typescript
describe("QuestGenerator", () => {
  it("should generate a quest with narrative for a task", async () => {
    // Test implementation
  });
});
```

### Documentation

- Update README.md if adding user-facing features
- Document complex functions with JSDoc comments
- Update relevant docs in `/docs` folder

```typescript
/**
 * Generates a quest narrative from a task using AI.
 *
 * @param task - The task to convert into a quest
 * @param preferences - User's game preferences
 * @returns Generated quest with narrative
 */
async function generateQuestNarrative(
  task: Task,
  preferences: UserPreferences
): Promise<Quest> {
  // Implementation
}
```

## Project-Specific Guidelines

### Working with AI Components

- Always handle AI API failures gracefully
- Implement retries with exponential backoff
- Cache AI responses when appropriate
- Log AI interactions for debugging

### Memory Management

- Use appropriate memory tiers (Personal/Project/Task)
- Clean up task memory after sessions
- Implement deduplication for stored facts
- Tag all memories with metadata

### Gamification

- Balance XP rewards carefully
- Test quest generation thoroughly
- Ensure social features respect privacy
- Make game elements optional/customizable

### Frontend

- Use React hooks and functional components
- Implement proper error boundaries
- Optimize for performance (lazy loading, memoization)
- Ensure accessibility (ARIA labels, keyboard navigation)

### Backend

- Validate all inputs with Zod schemas
- Use transactions for multi-step database operations
- Implement proper error handling
- Rate limit API endpoints

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass (`pnpm test`)
- [ ] Linting passes (`pnpm lint`)
- [ ] Documentation is updated
- [ ] Commit messages follow Conventional Commits
- [ ] PR description clearly explains changes
- [ ] Related issues are referenced

## Review Process

1. Maintainers will review your PR within 3-5 business days
2. Address any requested changes
3. Once approved, a maintainer will merge your PR

## Development Setup

See [GETTING_STARTED.md](./GETTING_STARTED.md) for detailed setup instructions.

## Questions?

Feel free to open an issue or reach out to the maintainers if you have questions about contributing.

---

Thank you for contributing to Delight! 🎉
