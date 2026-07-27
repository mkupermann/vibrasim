# Hacker News Post Draft: "Building a Brain from First Principles – A Solo Research Project"

**Title:** Building a Brain from First Principles – A Solo Research Project  
**URL:** https://github.com/mkupermann/vibrasim  
**Tags:** `neuroscience`, `machine-learning`, `research`, `open-source`, `solo-project`  
**Target Subreddit:** [Hacker News](https://news.ycombinator.com/)  

---

## 📢 Post Content

### Title
**Building a Brain from First Principles – A Solo Research Project**

### Text
```
I've been working on a solo research project called **vibrasim** (https://github.com/mkupermann/vibrasim) for the past year, and I'd love to get feedback from the HN community. The goal is to explore **emergence in a 3D continuous substrate** where vibrations bind into higher-level structures (electrons → pairs → triads → atoms → molecules → bridges), inspired by ideas from neuroscience, physics, and complex systems.

### What's New (as of 2026-07-27)
After a recent pivot, the project now has:

1. **Flux as the Default Substrate**
   - A **thermodynamically grounded** approach where energy quanta flow through an open boundary, and structures emerge where they channel this flux more efficiently.
   - **F0-F1c are complete**: binding, decay, thermal dynamics, and bidirectional injection all work.
   - **T2 Bénard test now passes reliably** (previously 30% pass rate; fixed by disabling a misconfigured pressure-gradient force).

2. **Biological Network Topologies**
   - Added support for **Barabási-Albert (scale-free)**, **Watts-Strogatz (small-world)**, and **Erdős-Rényi (random)** topologies for Bridges.
   - Hypothesis: These may improve robustness of emergent structures compared to homogeneous grids.

3. **Autopilot v2: Encoder-Free Training**
   - A **fully automated, pre-registered** pipeline for running experiments with the Flux substrate.
   - Works with **raw audio** (no pre-trained encoders needed).
   - **50-60% success probability** (per internal metrics).
   - Tutorial: https://github.com/mkupermann/vibrasim/blob/main/docs/TUTORIAL_AUTOPILOT_V2.md

### Why This Matters
- **Reproducibility**: Every experiment is **pre-registered** with acceptance criteria (see `docs/marker_protocol.md`).
- **Transparency**: The **LOGBOOK.md** (42 KB) and **ANALYSIS.md** (22 KB) document every decision, failure, and lesson learned.
- **Practical Utility**: Autopilot v2 can be used **today** for automated experiments (e.g., replicating speech recognition papers).

### Honest Assessment
This is **not** "verified emergence" or a breakthrough in AI. It's a **sandbox to think against**—a disciplined, solo research project where I'm writing down what I actually do when none of my usual moves work. The **real deliverables** are:
1. The **process** (pre-registration, honest scope statements, detailed logging).
2. The **tools** (Flux substrate, Autopilot v2, biological topologies).
3. The **lessons learned** (e.g., "homogeneous substrates percolate; engineered compartments contain").

### What I'm Looking For
I'd love feedback on any of the following:
- **Does the Flux substrate design make sense?** (See `docs/superpowers/specs/2026-05-10-flux-substrate-design.md`)
- **Would you use Autopilot v2?** If not, what's missing?
- **Are the biological topologies a good idea?** Any suggestions for other topologies to try?
- **How can I improve outreach?** (This is my first HN post for the project.)

### How to Get Started
1. **Try Flux**: `python -m world run --duration 60.0` (Flux is now the default).
2. **Run Autopilot v2**: See the [tutorial](https://github.com/mkupermann/vibrasim/blob/main/docs/TUTORIAL_AUTOPILOT_V2.md).
3. **Open an Issue**: Use the [RFC template](https://github.com/mkupermann/vibrasim/issues/new?assignees=&labels=feedback%2Cdiscussion&template=request_for_comments.md).

### Metrics (as of 2026-07-27)
- **Code**: ~31,665 LOC (Python), 100+ test files.
- **Docs**: LOGBOOK.md (7,695 lines), ANALYSIS.md (22 KB), README.md (50 KB).
- **Tests**: T2 Bénard test **PASSES reliably** (previously 30% pass rate).
- **Community**: 0 stars, 0 forks (but that's why I'm posting here!).

### Final Thought
This project is **not** about hype or overclaims. It's about **honest, disciplined research** in a space where most projects fail silently. If you're a computational neuroscientist, ML engineer, or just curious about emergence, I'd love to hear your thoughts.

GitHub: https://github.com/mkupermann/vibrasim
Tutorial: https://github.com/mkupermann/vibrasim/blob/main/docs/TUTORIAL_AUTOPILOT_V2.md
LOGBOOK: https://github.com/mkupermann/vibrasim/blob/main/LOGBOOK.md
```

---

## 🎯 Posting Checklist

- [ ] **Title** is clear and engaging.
- [ ] **URL** is correct (https://github.com/mkupermann/vibrasim).
- [ ] **Tags** are relevant (`neuroscience`, `machine-learning`, `research`, `open-source`, `solo-project`).
- [ ] **Text** is concise (<500 words).
- [ ] **Links** are working (test before posting!).
- [ ] **Tone** is honest and transparent (no hype).

---

## 📅 Posting Schedule

| Date | Action | Status |
|------|--------|--------|
| 2026-07-27 | Draft post | ✅ |
| 2026-07-28 | Review with community (if any) | ⏳ |
| 2026-07-29 | **Post to Hacker News** | ⏳ |
| 2026-07-30 | Monitor comments & respond | ⏳ |

---

## 💬 Expected Outcomes

| Outcome | Probability | Action |
|---------|-------------|--------|
| **>10 upvotes** | 30% | Engage with commenters; update post with answers. |
| **5-10 upvotes** | 40% | Respond to all comments; consider cross-posting to lobste.rs. |
| **<5 upvotes** | 30% | Analyze why (timing? content?); try again in 1 month. |
| **Negative feedback** | 10% | Address critiques honestly; update docs/code as needed. |
| **Collaboration offers** | 5% | **High priority**: Follow up within 24 hours. |

---

## 📌 Notes

- **Do not post on weekends** (lower engagement).
- **Best time to post**: 9-11 AM EST (HN peak hours).
- **Avoid**: Self-promotion, hype, or vague claims.
- **Emphasize**: Honesty, transparency, and practical utility.

---

*Draft created: 2026-07-27*  
*Status: Ready for review*
