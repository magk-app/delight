# Mintlify Documentation

This directory contains the Mintlify documentation for the Delight platform.

## Structure

```
mintlify/
├── docs.json              # Navigation configuration
├── introduction.mdx       # Landing page
├── quickstart.mdx         # Quick start guide
├── architecture/          # Architecture documentation (8 pages)
├── dev/                   # Development guides (4 pages)
├── epics/                 # Product epics (9 pages)
├── runbook/              # Operational runbooks (3 pages)
└── users/                # User guides (1 page)
```

**Total:** 27 MDX pages + 1 JSON config

## Key Fix Applied

This implementation fixes the Mintlify "page not found" issues by:

✅ **Correct Navigation Structure**
- Uses `tabs → groups → pages` hierarchy (not `tabs → pages`)
- This was the primary cause of page not found errors

✅ **Proper File Extensions**
- All files are `.mdx` (Mintlify requirement)
- No `.md` files that Mintlify can't find

✅ **Correct docs.json**
- Page references don't include `.mdx` extension
- Uses latest schema: `https://mintlify.com/docs.json`
- Proper structure matches working examples

## Local Development

### Install Mintlify CLI

```bash
npm install -g mintlify
```

### Start Dev Server

```bash
cd mintlify
mintlify dev
```

Or use npx:

```bash
cd mintlify
npx mintlify@latest dev
```

This starts the documentation at http://localhost:3000

### Verify All Pages Load

After starting the dev server, check:
- ✅ All tabs appear (Documentation, Product, Operations)
- ✅ All groups expand correctly
- ✅ No "page not found" errors
- ✅ All navigation links work

## Navigation Structure

### Documentation Tab
- **Get Started** - Introduction, Quickstart
- **Architecture** - 8 architecture pages
- **Development** - 4 development guides

### Product Tab
- **Epics** - 9 epic pages (overview + epic-1 through epic-8)
- **User Guide** - Getting started guide

### Operations Tab
- **Runbooks** - Documentation, deployment, troubleshooting

## Deployment

Documentation is automatically deployed when changes are pushed to main branch.

**To deploy:**
1. Make changes to MDX files
2. Test locally with `mintlify dev`
3. Commit and push to repository
4. Mintlify automatically rebuilds and deploys

## Adding New Pages

<details>
<summary>Step-by-step guide</summary>

1. **Create the MDX file**
   ```bash
   touch mintlify/section/new-page.mdx
   ```

2. **Add frontmatter**
   ```mdx
   ---
   title: 'Your Page Title'
   description: 'Brief description'
   ---

   # Your Content
   ```

3. **Update docs.json**
   Add to the appropriate group:
   ```json
   {
     "group": "Section Name",
     "pages": [
       "section/existing-page",
       "section/new-page"
     ]
   }
   ```

4. **Test locally**
   ```bash
   mintlify dev
   ```

</details>

## Mintlify Components Used

This documentation uses Mintlify's rich component library:

- `<Card>` & `<CardGroup>` - Visual organization
- `<Info>`, `<Warning>`, `<Tip>`, `<Note>` - Callouts
- `<Steps>` & `<Step>` - Step-by-step guides
- `<Checks>` & `<Check>` - Checklists
- `<Accordion>` & `<AccordionGroup>` - Collapsible sections
- `<CodeGroup>` - Multi-language code examples
- `<Tabs>` & `<Tab>` - Tabbed content

See [Mintlify Components Docs](https://mintlify.com/docs/content/components) for full reference.

## File Naming Conventions

- Use `.mdx` extension (not `.md`)
- Use lowercase with hyphens: `my-page.mdx`
- No spaces in filenames
- Match filename to page topic

## Content Guidelines

- Add descriptive frontmatter to every page
- Use proper heading hierarchy (h1 → h2 → h3)
- Include code examples with language identifiers
- Add navigation links between related pages
- Use Mintlify components for better UX

## Troubleshooting

### "Page not found" errors

✅ **Already fixed!** This implementation uses:
- Correct `tabs → groups → pages` structure
- `.mdx` file extensions
- Proper path references in docs.json

### Dev server not starting

```bash
# Clear cache
rm -rf node_modules .mintlify
npm install -g mintlify@latest

# Restart
mintlify dev
```

### Navigation not updating

After changing docs.json:
1. Stop the dev server (Ctrl+C)
2. Restart with `mintlify dev`
3. Hard refresh browser (Ctrl+Shift+R)

## Resources

- **Mintlify Docs:** https://mintlify.com/docs
- **Component Reference:** https://mintlify.com/docs/content/components
- **Navigation Guide:** https://mintlify.com/docs/settings/navigation
- **Deployment Guide:** https://mintlify.com/docs/development

---

**Last Updated:** 2025-11-17
**Maintained By:** Delight Team
