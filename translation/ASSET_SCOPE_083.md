# Translation source checkpoint 083

The identified linguistic assets have a complete first draft. This is not a claim of runtime correctness or exhaustive active-screen coverage.

- Main QuickDat: 13,430 translated drafts out of 16,550 records. The remaining 3,120 records are 2,912 blanks, 145 keyboard/font character records, 48 symbols/markup records, and 15 technical literals. No pending linguistic row remains in this extracted table.
- Save/load locale: 52 additional drafts in supplemental_text.tsv. The shipped kor_kr.loc was consulted; the English table is rebuilt with Korean wording and original substitution tokens.
- Intro brand caption: one translated sentence in movie_captions.json.
- All 3,374 textures decoded and reviewed through numbered contact sheets. Eight image/movie manifest entries are localized drafts, including three archive textures and five standalone resources. Other locales, hardware button labels, brand lockups, diagnostic codes and unreadable decorative microprint are preserved with explicit decisions.
- PSP shell TITLE is Korean. Disc identity, firmware update files and existing save data are preserved.
- The credits.txt file uses translated QuickDat section references and original contributor names. Names and musical licensing identities are intentionally retained.
- Simlish voices, ambient audio, animation/model identifiers and engine diagnostic strings are preserved. No dubbing was requested.

## Rebuild

Use Python 3.9+, Pillow from requirements.txt and FFmpeg on PATH with libx264 and drawtext. Configure original_iso and raster_font in config/project.json. The source handoff does not contain the original game ISO, local TTF or FFmpeg binary.

Run:

    .\run.ps1 -Mode Build -BuildId A_FRESH_UNIQUE_ID -VerifyPatch

Do not reapply old editorial batches over the canonical TSV.

New modules/builders:

- castaway/locale.py: LOCH/LOCL UTF-16 pointer tables.
- castaway/texture.py: original-palette indexed textures and linear BGR565 boot image.
- castaway/pmf.py: AVC access-unit groups written into original PMF packet slots; headers, timestamps and nonvideo packets retained.
- build_supplemental.py: save/load locale, shell title, boot and save icons.
- build_icon_movie.py: localized stationary lower title strip; original upper motion retained.
- build_brand_movie.py: Korean brand-identification caption.
- config/texture_replacements.json and supplemental_images.json: declarative asset mappings.

PMF format reference consulted: https://github.com/hrydgard/ppsspp/blob/master/Core/HLE/scePsmf.cpp

## Limits for the user review

No emulator was launched. All translations remain DRAFT. New glyphs use local Malgun Gothic; original font pixels are preserved. Readability, wrapping, missing characters, controller prompts and every game state need the user's review.

The 32-pixel newspaper masthead has little room for Hangul. The icon movie's title strip is stationary and uses heavier compression to fit the original video packet capacity. Other motion/audio packets are retained. Decorative microprint has no recoverable source sentence at its native resolution.

Underscore-bearing source variable tokens are preserved exactly; English-looking fragments inside those tokens are technical literals. Their runtime grammar was not changed.

Image generation used the built-in tool. Final project assets and exact prompts are in translation/images/TRANSLATION_082_PROMPTS.json and TRANSLATION_083_PROMPTS.json. Image resizing and palette encoding happen only during asset integration.
