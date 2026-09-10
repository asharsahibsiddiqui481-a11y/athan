# Athan Clock

Prayer times, Qibla direction, a daily prayer goal tracker, and **Qari Sahib** —
a Quran reading and recitation-practice companion.

Two pages:

- `/` — Athan Clock: live prayer times, countdown to the next prayer, Qibla
  direction, and a daily "complete all 5 prayers" goal with a streak.
- `/quran.html` — Qari Sahib: browse surahs, read a Mushaf-style page, practice
  reciting an ayah (scoring 75% unlocks the next one), a Learn to Pray
  walkthrough, and a dua library.

## Running it locally

```bash
pip install -r requirements.txt
python server.py
```

Then open http://localhost:3000

## Notes

- Prayer times come from the Aladhan API; Quran text and audio from Al Quran Cloud.
- Accounts are stored in `users.json` (git-ignored) with hashed passwords.
- Set `SECRET_KEY` in a `.env` file so sessions survive a restart.
