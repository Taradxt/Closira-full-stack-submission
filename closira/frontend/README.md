# Closira Frontend

Mobile dashboard for Closira — built as a single-file HTML/JS/CSS app that mimics a React Native mobile experience.

## How to Run

Just open `index.html` in any browser. No build step, no dependencies.

Or serve it:
```bash
npx serve .
```

## Screens

1. **Home** — Stats overview (leads, missed, escalations, follow-ups) + activity feed + quick actions
2. **Leads** — Searchable list with channel badges (WhatsApp/Email/Call) and status indicators
3. **Escalations** — Active alerts with urgency levels, resolve button per card
4. **Follow-ups** — Task cards with due times, mark-as-done action
5. **Conversation Detail** — Full message thread, SOP match label, AI summary, status timeline

## Design Decisions

- Dark theme — easier on eyes for business owners checking stats frequently
- Syne + DM Sans fonts — distinctive, not generic
- Mobile-first: max-width 430px, bottom tab navigation, touch-friendly tap targets
- Channel badges consistently coloured: WhatsApp (green), Email (blue), Call (amber)
- Status indicators: New (blue), Qualified (green), Escalated (red)
- Empty states on all list screens

## Styling Choice

Plain CSS with CSS variables — chosen over NativeWind because:
- This is a web prototype, not a native React Native build
- Zero dependencies = faster setup and easier review
- CSS variables give full design token control

## Mock Data

All data is hardcoded in `/mock` section of index.html, structured as proper JSON objects with field names matching what a real API would return (id, customer, channel, status, receivedAt, etc.)

## Known Limitations

- Not a native React Native app — this is a web prototype
- No real API calls — all data is mocked
- No authentication layer
- Conversation thread shows 2 messages only (inbound + auto-response)

## Built by
Tarika Dixit | tarikadixit2002@gmail.com
