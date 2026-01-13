# Manual Test Cases for simFocus Frontend

## Test Environment Setup
- **Browsers**: Chrome 120+, Firefox 120+, Safari 17+, Edge 120+
- **Devices**: Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)
- **Test Data**: Prepare test user accounts, sample topics, character templates

---

## Module 1: User Authentication

### TC-AUTH-001: User Registration - Valid Input
**Priority**: High
**Test Type**: Functional

**Steps**:
1. Navigate to `/register`
2. Enter valid email: `test@example.com`
3. Enter strong password: `SecurePass123`
4. Confirm password: `SecurePass123`
5. Click "Create Account"

**Expected Result**:
- Form submits successfully
- Redirects to email verification page or dashboard
- Success message displayed

**Actual Result**: _______________

---

### TC-AUTH-002: User Registration - Password Validation
**Priority**: High
**Test Type**: Validation

**Steps**:
1. Navigate to `/register`
2. Enter email: `test@example.com`
3. Enter weak password: `weak`
4. Attempt to submit

**Expected Result**:
- Password strength indicator shows weak password
- Error messages displayed for:
  - Minimum 8 characters
  - At least one lowercase letter
  - At least one uppercase letter
  - At least one number

**Actual Result**: _______________

---

### TC-AUTH-003: User Registration - Password Mismatch
**Priority**: Medium
**Test Type**: Validation

**Steps**:
1. Navigate to `/register`
2. Enter email: `test@example.com`
3. Password: `SecurePass123`
4. Confirm Password: `DifferentPass123`
5. Click "Create Account"

**Expected Result**:
- Error: "Passwords do not match"

**Actual Result**: _______________

---

### TC-AUTH-004: User Login - Valid Credentials
**Priority**: Critical
**Test Type**: Functional

**Steps**:
1. Navigate to `/login`
2. Enter registered email
3. Enter correct password
4. (Optional) Check "Remember me"
5. Click "Sign In"

**Expected Result**:
- Successful authentication
- Redirects to dashboard
- User info displayed in header
- Session token stored in localStorage

**Actual Result**: _______________

---

### TC-AUTH-005: User Login - Invalid Credentials
**Priority**: High
**Test Type**: Error Handling

**Steps**:
1. Navigate to `/login`
2. Enter email: `test@example.com`
3. Enter wrong password: `WrongPassword123`
4. Click "Sign In"

**Expected Result**:
- Error message: "Invalid email or password"
- Remains on login page
- Form fields preserved for re-entry

**Actual Result**: _______________

---

### TC-AUTH-006: Social Login - Google
**Priority**: Medium
**Test Type**: Integration

**Steps**:
1. Navigate to `/login`
2. Click "Continue with Google"
3. Complete OAuth flow in popup

**Expected Result**:
- Redirects to Google OAuth page
- After authentication, returns to app
- User logged in successfully

**Actual Result**: _______________

---

### TC-AUTH-007: Password Recovery
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. Navigate to `/login`
2. Click "Forgot password?"
3. Enter registered email
4. Submit form

**Expected Result**:
- Success message: "Password reset email sent"
- Email received with reset link

**Actual Result**: _______________

---

### TC-AUTH-008: Logout
**Priority**: High
**Test Type**: Functional

**Steps**:
1. Login to application
2. Click user avatar in header
3. Click "Logout"

**Expected Result**:
- Redirects to home page
- localStorage cleared
- Session token removed
- Cannot access protected routes without re-login

**Actual Result**: _______________

---

### TC-AUTH-009: Route Protection
**Priority**: High
**Test Type**: Security

**Steps**:
1. Logout (clear session)
2. Navigate directly to `/dashboard`

**Expected Result**:
- Redirects to `/login?redirect=/dashboard`
- Original URL saved for post-login redirect

**Actual Result**: _______________

---

## Module 2: Topic Management

### TC-TOPIC-001: Create Topic - Valid Input
**Priority**: Critical
**Test Type**: Functional

**Steps**:
1. Login and navigate to `/topics/create`
2. Enter title: "Discussion about AI Ethics" (10-200 chars)
3. Enter description: "Explore ethical implications..." (0-2000 chars)
4. Select 3-7 characters from library
5. Select discussion mode: "Free Discussion"
6. Set max rounds: 15
7. Click "Create Discussion"

**Expected Result**:
- Topic created successfully
- Redirects to discussion room
- Topic appears in topic list

**Actual Result**: _______________

---

### TC-TOPIC-002: Create Topic - Title Validation
**Priority**: High
**Test Type**: Validation

**Test Data**:
| Title | Length | Expected |
|-------|--------|----------|
| Short | 5 chars | Error: "At least 10 characters" |
| Too Long | 201 chars | Error: "No more than 200 characters" |
| Empty | 0 chars | Error: "Title is required" |
| Valid | 50 chars | Success |

**Actual Result**: _______________

---

### TC-TOPIC-003: Character Selection - Minimum
**Priority**: High
**Test Type**: Validation

**Steps**:
1. Navigate to `/topics/create`
2. Fill in valid title and description
3. Select only 1 character
4. Click "Create Discussion"

**Expected Result**:
- Error: "Select at least 3 characters"

**Actual Result**: _______________

---

### TC-TOPIC-004: Character Selection - Maximum
**Priority**: Medium
**Test Type**: Validation

**Steps**:
1. Navigate to `/topics/create`
2. Attempt to select more than 7 characters

**Expected Result**:
- Cannot select more than 7 characters
- Visual feedback showing limit reached

**Actual Result**: _______________

---

### TC-TOPIC-005: Discussion Mode Selection
**Priority**: Medium
**Test Type**: Functional

**Test Data**:
| Mode | Description |
|------|-------------|
| Free Discussion | Unrestricted conversation |
| Structured Debate | Pro/con/neutral teams |
| Creative Brainstorm | "Yes, and" approach |
| Consensus Building | Find common ground |

**Steps**: Verify each mode has appropriate description and icon

**Actual Result**: _______________

---

### TC-TOPIC-006: Use Topic Template
**Priority**: Low
**Test Type**: Functional

**Steps**:
1. Navigate to `/topics/create`
2. Click "Use Template"
3. Browse template library
4. Select a template (e.g., "Product Feature Validation")
5. Modify if needed
6. Create discussion

**Expected Result**:
- Form pre-filled with template content
- Can modify before creating
- Characters pre-selected based on template

**Actual Result**: _______________

---

### TC-TOPIC-007: Topic List - Filtering
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. Navigate to `/topics`
2. Test status filters: Draft, Ready, In Discussion, Completed
3. Test search by title
4. Test sort by: Newest, Oldest, Most Used

**Expected Result**:
- Filters work correctly
- Results update in real-time
- Filter indicators visible

**Actual Result**: _______________

---

### TC-TOPIC-008: Edit Topic
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. Navigate to `/topics`
2. Click "Edit" on a draft topic
3. Modify title, description
4. Save changes

**Expected Result**:
- Changes saved successfully
- Updated topic visible in list
- Success message displayed

**Actual Result**: _______________

---

### TC-TOPIC-009: Delete Topic
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. Navigate to `/topics`
2. Click "Delete" on a topic
3. Confirm deletion in dialog

**Expected Result**:
- Confirmation dialog shown
- After confirm, topic removed from list
- Success message displayed
- Action cannot be undone

**Actual Result**: _______________

---

## Module 3: Character System

### TC-CHAR-001: Browse Character Library
**Priority**: High
**Test Type**: Functional

**Steps**:
1. Navigate to character library
2. Browse available characters
3. Filter by category
4. Search by name or trait

**Expected Result**:
- Characters displayed with:
  - Avatar
  - Name
  - Role/Profession
  - Key traits
  - Usage count
  - Rating

**Actual Result**: _______________

---

### TC-CHAR-002: Create Custom Character
**Priority**: High
**Test Type**: Functional

**Steps**:
1. Click "Create Character"
2. Fill in basic info:
   - Name: "Dr. Smith"
   - Age: 45
   - Gender: Prefer not to say
   - Profession: AI Researcher
3. Configure personality traits (1-10 scale):
   - Openness: 8
   - Rigor: 7
   - Critical Thinking: 9
   - Optimism: 5
4. Set knowledge fields: ["AI Ethics", "Machine Learning"]
5. Set experience years: 15
6. Select stance: Neutral
7. Select expression style: Formal
8. Select behavior pattern: Balanced
9. Click "Create"

**Expected Result**:
- Character created successfully
- Added to library
- Can be selected for discussions

**Actual Result**: _______________

---

### TC-CHAR-003: Character Preview
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. Click on a character card
2. View character detail modal

**Expected Result**:
- Display all character attributes
- Show usage statistics
- Show sample dialogue
- Show related characters

**Actual Result**: _______________

---

### TC-CHAR-004: Intelligent Character Recommendation
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. Create a new topic
2. Click "Get Recommendations"
3. Review suggested characters

**Expected Result**:
- AI suggests 3-5 relevant characters
- Recommendations match topic context
- Can select suggested characters directly

**Actual Result**: _______________

---

## Module 4: Discussion Engine

### TC-DISC-001: Start Discussion
**Priority**: Critical
**Test Type**: Functional

**Steps**:
1. Navigate to discussion room
2. Verify all participants listed
3. Click "Start Discussion"

**Expected Result**:
- Discussion status changes to "Running"
- Progress bar initializes
- Phase indicator shows "Opening"
- First character begins responding
- Messages appear in real-time

**Actual Result**: _______________

---

### TC-DISC-002: Pause Discussion
**Priority**: High
**Test Type**: Functional

**Steps**:
1. Start a discussion
2. Wait for 2-3 messages
3. Click "Pause"

**Expected Result**:
- Status changes to "Paused"
- Message generation stops
- Current message completes
- Can resume with "Resume" button

**Actual Result**: _______________

---

### TC-DISC-003: Resume Discussion
**Priority**: High
**Test Type**: Functional

**Steps**:
1. Pause a running discussion
2. Click "Resume"

**Expected Result**:
- Status changes to "Running"
- Next character begins responding
- Progress continues from pause point

**Actual Result**: _______________

---

### TC-DISC-004: Stop Discussion
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. Start a discussion
2. Click "Stop"
3. Confirm in dialog

**Expected Result**:
- Discussion ends
- Status changes to "Completed"
- Final statistics shown
- Report generation begins

**Actual Result**: _______________

---

### TC-DISC-005: Inject Question
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. During discussion, click "Inject Question"
2. Enter question: "What about the environmental impact?"
3. Submit

**Expected Result**:
- Question appears in message stream
- Marked as "injected question"
- Characters respond to question
- Discussion flows naturally

**Actual Result**: _______________

---

### TC-DISC-006: Adjust Playback Speed
**Priority**: Low
**Test Type**: Functional

**Test Data**: 1.0x, 1.5x, 2.0x, 3.0x

**Steps**:
1. Start discussion
2. Change speed to 2.0x
3. Observe message generation rate

**Expected Result**:
- Messages generate faster at higher speeds
- Smooth acceleration without errors

**Actual Result**: _______________

---

### TC-DISC-007: Phase Progression
**Priority**: High
**Test Type**: Functional

**Steps**:
1. Start discussion
2. Observe phase indicator through discussion

**Expected Result**:
- Phases progress: Opening → Development → Debate → Closing
- Each phase shows appropriate label
- Round counter increments
- Phase transitions are smooth

**Actual Result**: _______________

---

### TC-DISC-008: Character Speaking Indicators
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. Start discussion
2. Watch character panel

**Expected Result**:
- Current speaker highlighted
- Typing indicator shows when character is "speaking"
- Message count updates
- Visual feedback for each message

**Actual Result**: _______________

---

### TC-DISC-009: Message Display
**Priority**: High
**Test Type**: Functional

**Steps**:
1. During discussion, observe message list

**Expected Result**:
- Each message shows:
  - Character avatar
  - Character name
  - Phase badge
  - Round number
  - Message content
  - Timestamp
- Messages auto-scroll to latest
- User can manually scroll to view history

**Actual Result**: _______________

---

### TC-DISC-010: Auto-Scroll Toggle
**Priority**: Low
**Test Type**: Functional

**Steps**:
1. During discussion, scroll up manually
2. Verify auto-scroll pauses
3. Scroll to bottom
4. Verify auto-scroll resumes

**Expected Result**:
- Auto-scroll indicator shows state
- Manual scroll disables auto-scroll
- Scroll to bottom re-enables auto-scroll

**Actual Result**: _______________

---

## Module 5: Report Generation

### TC-REP-001: View Discussion Report
**Priority**: High
**Test Type**: Functional

**Steps**:
1. Complete a discussion
2. Navigate to report
3. Review all sections

**Expected Result**:
- Report contains:
  - Summary of discussion
  - All participants' final positions
  - Key insights
  - Areas of consensus
  - Points of disagreement
  - Actionable recommendations

**Actual Result**: _______________

---

### TC-REP-002: Opinion Distribution Visualization
**Priority**: Medium
**Test Type**: Visual

**Steps**:
1. View discussion report
2. Check opinion distribution chart

**Expected Result**:
- ECharts visualization displays
- Each character's stance shown
- Interactive tooltips
- Clear legend

**Actual Result**: _______________

---

### TC-REP-003: Export Report as PDF
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. View discussion report
2. Click "Export as PDF"

**Expected Result**:
- PDF generated successfully
- Download starts automatically
- PDF contains all report sections
- Formatting is clean and readable

**Actual Result**: _______________

---

### TC-REP-004: Export Report as Markdown
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. View discussion report
2. Click "Export as Markdown"

**Expected Result**:
- Markdown file downloaded
- Contains structured content
- Can be opened in markdown editor
- Renders correctly in GitHub/docs

**Actual Result**: _______________

---

### TC-REP-005: Export Report as JSON
**Priority**: Low
**Test Type**: Functional

**Steps**:
1. View discussion report
2. Click "Export as JSON"

**Expected Result**:
- JSON file downloaded
- Contains all discussion data
- Valid JSON format
- Includes metadata

**Actual Result**: _______________

---

### TC-REP-006: Share Discussion Report
**Priority**: Medium
**Test Type**: Functional

**Steps**:
1. View discussion report
2. Click "Share"
3. Configure sharing options:
   - Public/Private
   - Expiration date
   - Allow comments
4. Generate link
5. Copy link

**Expected Result**:
- Shareable link generated
- Link accessible to recipients
- Privacy settings respected

**Actual Result**: _______________

---

## Module 6: API Key Management

### TC-API-001: Add OpenAI API Key
**Priority**: Critical
**Test Type**: Functional

**Steps**:
1. Navigate to `/settings/api-keys`
2. Click "Add API Key"
3. Select provider: OpenAI
4. Enter key: `sk-test-...`
5. Click "Save"

**Expected Result**:
- Key saved successfully
- Encrypted in storage (verify in DevTools)
- Shows as "Connected"
- Masked display: `sk-test••••••••`

**Actual Result**: _______________

---

### TC-API-002: Add Anthropic API Key
**Priority**: High
**Test Type**: Functional

**Steps**:
1. Navigate to `/settings/api-keys`
2. Click "Add API Key"
3. Select provider: Anthropic
4. Enter key
5. Save

**Expected Result**:
- Key saved
- Provider icon displayed
- Ready to use

**Actual Result**: _______________

---

### TC-API-003: Delete API Key
**Priority**: High
**Test Type**: Functional

**Steps**:
1. Navigate to `/settings/api-keys`
2. Click "Delete" on a key
3. Confirm deletion

**Expected Result**:
- Key removed from storage
- Cannot be recovered
- Success message shown

**Actual Result**: _______________

---

### TC-API-004: API Key Validation
**Priority**: Medium
**Test Type**: Validation

**Test Data**:
| Input | Expected |
|-------|----------|
| Empty | Error: "API key required" |
| Invalid format | Error: "Invalid key format" |
| Valid format | Success |

**Actual Result**: _______________

---

## UI/UX Test Cases

### TC-UI-001: Responsive Design - Desktop
**Priority**: High
**Test Type**: UI/UX

**Viewports**:
- 1920x1080 (Full HD)
- 1440x900 (Laptop)
- 1366x768 (Small Laptop)

**Checks**:
- All elements visible and aligned
- No horizontal scroll
- Text readable without zoom
- Buttons clickable
- Forms usable

**Actual Result**: _______________

---

### TC-UI-002: Responsive Design - Tablet
**Priority**: High
**Test Type**: UI/UX

**Viewports**:
- 768x1024 (iPad Portrait)
- 1024x768 (iPad Landscape)

**Checks**:
- Side panels collapse
- Navigation adapts
- Touch targets ≥ 44x44px
- No horizontal scroll
- Content readable

**Actual Result**: _______________

---

### TC-UI-003: Responsive Design - Mobile
**Priority**: High
**Test Type**: UI/UX

**Viewports**:
- 375x667 (iPhone SE)
- 390x844 (iPhone 12)
- 414x896 (iPhone 11)

**Checks**:
- Single column layout
- Hamburger menu
- Full-width buttons
- Readable text (≥16px)
- No tiny touch targets
- No horizontal scroll

**Actual Result**: _______________

---

### TC-UI-004: Dark Mode
**Priority**: Medium
**Test Type**: UI/UX

**Steps**:
1. Toggle dark mode in settings
2. Navigate through app
3. Check all pages

**Expected Result**:
- Consistent dark theme
- Sufficient contrast ratios (WCAG AA)
- All components styled
- No eye strain
- Colors harmonious

**Actual Result**: _______________

---

### TC-UI-005: Loading States
**Priority**: High
**Test Type**: UI/UX

**Scenarios**:
- Page load
- Form submission
- API calls
- Discussion generation

**Expected Result**:
- Loading indicator (skeleton or spinner)
- Prevents duplicate submissions
- Clear when action completes
- Smooth transitions

**Actual Result**: _______________

---

### TC-UI-006: Error States
**Priority**: High
**Test Type**: UI/UX

**Scenarios**:
- Network error
- API error
- Validation error
- 404 page
- 500 server error

**Expected Result**:
- Clear error message
- Human-readable explanation
- Action to resolve
- Maintains user context
- No data loss

**Actual Result**: _______________

---

### TC-UI-007: Empty States
**Priority**: Medium
**Test Type**: UI/UX

**Scenarios**:
- No topics
- No discussions
- No characters
- No messages

**Expected Result**:
- Friendly illustration
- Clear explanation
- Call-to-action button
- Helpful, not frustrating

**Actual Result**: _______________

---

## Security Test Cases

### TC-SEC-001: XSS Prevention
**Priority**: Critical
**Test Type**: Security

**Steps**:
1. Enter `<script>alert('XSS')</script>` in:
   - Topic title
   - Topic description
   - Character name
   - Discussion messages (if possible)
2. Submit form

**Expected Result**:
- Script does NOT execute
- Input sanitized or escaped
- HTML entities displayed as text

**Actual Result**: _______________

---

### TC-SEC-002: API Key Storage
**Priority**: Critical
**Test Type**: Security

**Steps**:
1. Add API key in settings
2. Open DevTools → Application → Local Storage
3. Find stored key

**Expected Result**:
- Key is encrypted (not plaintext)
- Cannot extract usable key
- Only server can decrypt

**Actual Result**: _______________

---

### TC-SEC-003: Session Management
**Priority**: High
**Test Type**: Security

**Steps**:
1. Login to application
2. Copy session token from localStorage
3. Logout
4. Paste token back to localStorage
5. Refresh page

**Expected Result**:
- Session invalid on server
- Redirected to login
- Token rejected

**Actual Result**: _______________

---

### TC-SEC-004: CSRF Token
**Priority**: High
**Test Type**: Security

**Steps**:
1. Open DevTools → Network
2. Submit a form
3. Check request headers

**Expected Result**:
- CSRF token included
- Token validated server-side
- Unique per session

**Actual Result**: _______________

---

### TC-SEC-005: HTTPS Enforcement
**Priority**: Critical
**Test Type**: Security

**Steps**:
1. Try accessing via HTTP (if possible)

**Expected Result**:
- Redirect to HTTPS
- Mixed content warnings resolved
- All resources via HTTPS

**Actual Result**: _______________

---

## Performance Test Cases

### TC-PERF-001: Initial Page Load
**Priority**: High
**Test Type**: Performance

**Metrics**:
- Time to First Byte (TTFB): < 200ms
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s

**Steps**: Load home page with cleared cache

**Actual Result**: _______________

---

### TC-PERF-002: Discussion Message Rendering
**Priority**: High
**Test Type**: Performance

**Steps**:
1. Create discussion with 50+ messages
2. Scroll through message list

**Expected Result**:
- Smooth scrolling (60fps)
- No jank or lag
- Virtual scrolling works for large lists

**Actual Result**: _______________

---

### TC-PERF-003: Real-time Updates
**Priority**: High
**Test Type**: Performance

**Steps**:
1. Start a discussion
2. Monitor message delivery latency

**Expected Result**:
- New messages appear within 1-2 seconds
- No dropped messages
- WebSocket stays connected

**Actual Result**: _______________

---

### TC-PERF-004: Bundle Size
**Priority**: Medium
**Test Type**: Performance

**Metrics**:
- Initial bundle: < 200KB gzipped
- Each route chunk: < 100KB gzipped
- Total JS: < 500KB gzipped

**Steps**: Run build and analyze dist/

**Actual Result**: _______________

---

## Accessibility Test Cases

### TC-A11Y-001: Keyboard Navigation
**Priority**: High
**Test Type**: Accessibility

**Steps**:
1. Navigate app using only Tab, Enter, Esc
2. Verify focus order is logical
3. Verify all interactive elements reachable

**Expected Result**:
- Visible focus indicators
- Logical tab order
- No keyboard traps
- Skip links available

**Actual Result**: _______________

---

### TC-A11Y-002: Screen Reader Compatibility
**Priority**: High
**Test Type**: Accessibility

**Steps**:
1. Enable screen reader (NVDA/VoiceOver)
2. Navigate app
3. Verify labels and announcements

**Expected Result**:
- All images have alt text
- Forms properly labeled
- Errors announced
- State changes announced

**Actual Result**: _______________

---

### TC-A11Y-003: Color Contrast
**Priority**: High
**Test Type**: Accessibility

**Steps**:
1. Use contrast checker tool
2. Verify all text/background combinations

**Expected Result**:
- Normal text: ≥ 4.5:1 (WCAG AA)
- Large text: ≥ 3:1 (WCAG AA)
- UI components: ≥ 3:1 (WCAG AA)

**Actual Result**: _______________

---

### TC-A11Y-004: Form Accessibility
**Priority**: Medium
**Test Type**: Accessibility

**Steps**:
1. Navigate to any form
2. Check labels, errors, instructions

**Expected Result**:
- All inputs have labels
- Required fields indicated
- Errors associated with inputs
- Instructions available

**Actual Result**: _______________

---

## Cross-Browser Test Cases

### TC-BROWSER-001: Chrome Compatibility
**Priority**: High
**Test Type**: Compatibility

**Versions**: Chrome 120, 121, Latest

**Focus Areas**:
- All features work
- No console errors
- Performance acceptable

**Actual Result**: _______________

---

### TC-BROWSER-002: Firefox Compatibility
**Priority**: High
**Test Type**: Compatibility

**Versions**: Firefox 120, 121, Latest

**Focus Areas**:
- Same as Chrome
- No Firefox-specific issues

**Actual Result**: _______________

---

### TC-BROWSER-003: Safari Compatibility
**Priority**: High
**Test Type**: Compatibility

**Versions**: Safari 17, Latest

**Focus Areas**:
- Same as Chrome
- No Safari-specific issues
- WebGL/WebSocket support

**Actual Result**: _______________

---

## Test Execution Summary

### Total Test Cases: ___
### Executed: ___
### Passed: ___
### Failed: ___
### Blocked: ___
### Pass Rate: ___%

### Critical Bugs Found:
1.
2.
3.

### Recommendations:
1.
2.
3.

---

**Tester**: _______________
**Test Start Date**: _______________
**Test End Date**: _______________
**Test Environment**: _______________
