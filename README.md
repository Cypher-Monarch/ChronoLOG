# ChronoLOG

> **In-Development:** ChronoLOG is a PySide6-based desktop study planner and productivity tool, designed to help students organize tasks, schedule study sessions, track progress, and take notes effectively.

---

## Overview
ChronoLOG integrates **task management, scheduling, progress tracking, and note-taking** into a modern, themeable interface. It is user-centric, with all data stored per user ID for personalization and security.

---

## Core Architecture

### Main Components
- **MainWindow.StudyPlanner** – Primary application window managing core functionality.
- **CollapsibleSidebar** – Modern navigation sidebar with expand/collapse animations.
- **Content Tabs** – Home, Subjects, Tasks, Schedule, Progress, Notes.
- **NotesTab** – Rich text editor with **Text-to-Speech (TTS)**.
- **Study Mode** – Fullscreen focused study timer with **AFK detection**.

---

## Key Features

### 1. User Interface
- Responsive collapsible sidebar with smooth animations.
- Dark/light theme system with consistent styling.
- Tab-based navigation for Home, Subjects, Tasks, Schedule, Progress, Notes.
- Status bar with real-time updates and notifications.

### 2. Data Management
- **MySQL Database** via `DBManager` for persistent storage.
- Notes stored in `Documents/ChronoLOG-Notes`.
- All data tied to specific user IDs.

### 3. Core Functionality

#### Home Screen
- Stats cards: pending tasks, today’s sessions, streaks, and progress.
- Recent activity feed.
- Quick access to study mode.

#### Subjects Management
- Create, edit, delete subjects.
- Priority system: High, Medium, Low.
- Safety checks to prevent accidental deletion.

#### Task System
- Task creation with subjects, due dates, priorities.
- Completion tracking and scheduling.
- Context menus for quick actions.

#### Scheduling
- Visual calendar of study sessions.
- Filters: All, Today, Upcoming, Completed.
- Session tracking: Pending, In Progress, Completed, Overdue.
- AFK detection during study sessions.

#### Progress Tracking
- Subject-wise and task-wise statistics.
- Time tracking and study streak system.
- Visual progress indicators.

#### Notes System
- Rich text editor: bold, italic, underline formatting.
- Text-to-Speech with voice and speed control.
- MP3 export.
- Word and character counting.
- File management: save, load, rename, delete.

### 4. Advanced Features
- AFK detection: 20-minute check-ins with 2-minute response timeout.
- Fullscreen study mode with **UltimateStudyTimer**.
- Recurring tasks support: daily, weekly, monthly.
- Task dependencies for relationship management between tasks.

---

## Technical Implementation
- **PySide6** – Modern Qt-based GUI framework.
- **pyttsx3** – Text-to-speech engine.
- **pydub** – Audio processing for MP3 export.
- Logging system with daily log files.
- MySQL database for persistent storage.
- Smooth animations for UI transitions.

---

## Workflow
1. Create subjects to organize study topics.
2. Add tasks with due dates and priorities.
3. Schedule study sessions.
4. Track progress with statistics and streaks.
5. Enter study mode with AFK monitoring.
6. Manage notes with TTS and file operations.

---

## Theme System
ChronoLOG supports consistent dark/light mode styling for:
- Buttons and controls
- Tree and list widgets
- Text input fields
- Progress indicators
- Navigation elements

---

## Error Handling
- User-friendly error messages.
- Logging of all exceptions.
- Safety checks before destructive operations.
- Database integrity protection.

---

## Notes
- ChronoLOG is currently **in development**.
- Features may be added, refined, or removed during the development process.

