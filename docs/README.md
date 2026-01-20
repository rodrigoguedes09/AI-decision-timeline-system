# AI Decision Timeline Demo

This directory contains demonstration assets for the AI Decision Timeline system.

## Screenshot/GIF Placeholder

To complete the README, please add a demo GIF or screenshot showing:
1. The timeline view with decision cards
2. The replay mode in action
3. The filtering and statistics features

### How to Create the Demo

1. **Start the system**:
   ```bash
   # Backend
   cd backend
   python scripts/load_demo_data.py
   uvicorn app.main:app --reload
   
   # Frontend
   cd frontend
   npm run dev
   ```

2. **Record a demo**:
   - Open http://localhost:3000
   - Use a screen recording tool (OBS, Loom, etc.)
   - Show:
     - Timeline scrolling
     - Clicking a decision card
     - Replay mode playing through steps
     - Filtering decisions
   - Export as GIF (< 10MB for GitHub)

3. **Add to project**:
   ```bash
   # Save as demo.gif in this directory
   git add docs/demo.gif
   ```

### Recommended Tools

- **Windows**: ShareX, ScreenToGif
- **macOS**: Kap, Gifski
- **Linux**: Peek, SimpleScreenRecorder + ffmpeg

### Alternative: Screenshots

If you prefer static images:
- `timeline-view.png` - Full timeline view
- `replay-mode.png` - Replay modal open
- `stats-dashboard.png` - Statistics cards

Then update README.md to reference the images.
