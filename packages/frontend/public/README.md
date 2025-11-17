# Public Assets Directory

This directory contains static assets served directly by Next.js.

## Structure

```
public/
├── favicon.ico              # Site favicon
├── apple-touch-icon.png     # iOS home screen icon (optional)
├── images/                  # Static images
│   └── .gitkeep
└── README.md                # This file
```

## Favicon

Place favicon files in the root of this directory:

- `favicon.ico` - Main favicon
- `apple-touch-icon.png` - iOS icon (180x180px recommended)
- `favicon.svg` - Modern SVG favicon (optional)

The favicon is configured in `src/app/layout.tsx` metadata.

## Images

Place all static images in `images/` subdirectory.

Reference them using:

- Public path: `/images/your-image.png`
- Or import: `import image from '@/public/images/your-image.png'`

For optimized images, use Next.js `Image` component:

```tsx
import Image from "next/image";
import logo from "@/public/images/logo.png";

<Image src={logo} alt="Logo" width={200} height={200} />;
```

## Notes

- Files in `public/` are served from the root URL (`/`)
- Use descriptive filenames
- Optimize images before adding them
- Keep file sizes reasonable
