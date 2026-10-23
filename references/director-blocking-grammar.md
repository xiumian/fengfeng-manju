# Blocking Grammar

Use this reference when writing detailed prompts or converting raw natural language into low-deviation AI video instructions.

## Text-Grounded Conversion

Start by separating the user's script and assets into:

- script-confirmed facts: directly stated by the script or scene analysis
- asset-confirmed facts: visible in scene images, character assets, prop references, costume references, or set references
- assumptions: useful details inferred from context
- missing decisions: facts that would change blocking, camera, or continuity

Only script-confirmed or asset-confirmed facts can be written as certain. Assumptions must remain labeled until the user approves them.

## Asset Grounding

When assets are provided, use them as concrete evidence under the script framework.

Scene images can define:

- room layout
- entrances and exits
- furniture positions
- practical or natural light sources
- foreground / midground / background depth
- actor marks and safe movement paths
- camera-friendly axes and likely coverage angles

Character assets can define:

- stable face identity
- costume and color
- hairstyle
- body silhouette
- carried props
- age range and performance type

Prop, costume, and set assets can define:

- object appearance
- scale and placement
- material and color
- continuity state
- what must not change between shots

Do not invent a new layout or character look when an asset already defines it. If the asset conflicts with the script, report the conflict and choose the script as story authority unless the user says the asset supersedes it.

## Core Sentence Pattern

Use this pattern for each shot:

```text
A [duration] cinematic shot. Continue from [previous state].
[Character ID and visual anchor] starts at [screen position / set position].
[Action sequence with start, movement, pause, and end].
The camera is [shot size], [angle], [lens feel], and performs [one camera move].
[Composition anchors].
[Lighting and color].
Keep [continuity constraints].
No [negative constraints].
```

## Character IDs

Always assign characters like:

```text
Character A: young woman, white shirt, tied hair, anxious.
Character B: older man, dark coat, gray hair, calm but stern.
Character C: child, yellow raincoat, silent, holding a toy.
```

Rules:

- Use IDs in every shot.
- Pair each ID with a visual anchor the model can preserve.
- Prefer visual anchors from character assets over invented descriptions.
- Avoid renaming IDs mid-sequence.
- If a character exits, say where they exit and whether they remain offscreen.

## Role Scheduling

Role scheduling answers: who moves, where, toward whom, with what prop, and what changes by the end of the beat.

Use this pattern:

```text
Role schedule: Character A starts at [position], [action], keeps eyeline toward [target], and ends at [position]. Character B starts at [position], [action or stillness], keeps eyeline toward [target], and ends at [position]. Prop state: [prop owner/location/change].
```

For each character, define:

- start position
- end position
- movement path
- eyeline target
- visible performance
- prop state
- entry or exit

Keep role scheduling independent from camera wording first. A strong role schedule should still make sense if filmed from a different angle.

## Spatial Language

Use screen geography:

- frame left / frame right
- center frame
- left third / right third
- foreground / midground / background
- background doorway
- foreground table
- behind Character A
- between A and B

Use continuity anchors:

```text
The table remains between A and B.
The door stays in the background center.
A remains frame left; B remains frame right.
The letter stays on the foreground table.
```

## Blocking Verbs

Prefer precise verbs:

- enters from
- crosses behind
- turns toward
- looks down at
- takes two slow steps
- stops before reaching
- leans forward
- reaches for
- pulls back
- remains still
- interrupts
- avoids eye contact

Avoid vague verbs:

- interacts
- moves around
- acts emotional
- cinematic movement
- walks dramatically

## Camera Language

Use one primary camera move:

- static two-shot
- slow dolly-in
- dolly-out
- lateral tracking shot
- over-the-shoulder shot
- slow pan left / right
- tilt up / down
- crane up / down
- handheld follow shot
- slow orbit, only when needed

Constrain unwanted movement:

```text
No orbit, no sudden pan, no handheld shake.
The camera does not cut inside the shot.
The camera keeps A on frame left and B on frame right.
```

Lens feel:

- 24mm: wide, spatial, exaggerated perspective
- 35mm: natural environmental medium shot
- 50mm: intimate natural perspective
- 85mm: close portrait compression

## Camera Description

Camera description answers: how the role schedule is photographed.

Use this pattern:

```text
Camera description: [shot size] at [angle], [lens feel]. The camera [single movement] while keeping [composition anchor]. Start keyframe: [opening image]. End keyframe: [closing image]. Forbidden moves: [constraints].
```

For each shot, define:

- shot size start and end
- angle
- lens feel
- one camera movement
- composition anchor
- start keyframe
- end keyframe
- forbidden movement

The camera description must not contradict the role schedule. If A is supposed to stay frame left, do not describe a camera move that makes A cross to frame right unless the shot explicitly uses a reverse angle.

## Performance Language

Write visible behavior instead of abstract emotion:

Weak:

```text
A is very sad.
```

Strong:

```text
A keeps her shoulders tense, avoids B's eyes, breathes shallowly, and pauses before speaking.
```

## Dialogue and Performance Sync

For dialogue scenes, map each speech unit before writing prompts:

```text
Dialogue beat: Character B speaks while walking from [start] to [end]. Expression: [visible face/body behavior]. Listener A reaction: [head turn / eye movement / stillness]. Timing: B finishes before C enters.
```

Rules:

- A line spoken while walking must include walking path, pace, endpoint, and whether the speaker keeps eye contact.
- A line spoken after stopping should state the stop as the visual punctuation before the line.
- Listener reactions must be visible and limited: head turn, eye shift, held breath, posture change, hand tightening.
- Do not let two characters speak important lines while both perform complex movement unless the user explicitly asks for overlapping action.
- For AI video prompts, keep dialogue text short or summarize intent if the platform does not support accurate lip sync.

## Dialogue Pace and Long-Line Coverage

Long dialogue should be split by performance logic:

- topic shift
- emotional shift
- power shift between characters
- speaker changes eyeline target
- speaker starts, stops, or changes movement
- listener reaction is dramatically important
- a key phrase needs emphasis or a pause

Do not split long dialogue only for visual variety. Every cut needs a reason tied to the script, actor mark, expression, eyeline, or listener reaction.

Use this pattern:

```text
Long dialogue split: Character B speaks at [pace]. Segment 1 stays on B because [reason]. Cut to A after [phrase/beat] because [reaction reason]. Cut to C after [phrase/beat] because [target shift]. Return to B for [final phrase] with [expression/tone]. Pauses: [pause points]. Do not change actor marks, axis, key light, or set layout during the dialogue.
```

Pace vocabulary:

- slow and deliberate
- normal conversational pace
- controlled but urgent
- interrupted or breathless
- quiet and restrained
- defensive, with short pauses
- escalating, with shorter pauses near the end

## Axis, Light, and Set Continuity

For dialogue coverage, define a continuity spine:

```text
Axis: A is seated; the main axis runs between A and the active speaker. Keep B and C on their established screen sides unless a motivated reverse shot is declared.
Light: the script-confirmed key light source keeps its direction, color, shadow behavior, and motivation consistent.
Set: furniture, entry paths, practical lights, windows, doors, props, and standing marks remain fixed unless the script changes them.
Eyeline: A looks toward B when B speaks, then toward C after C stops in front of A.
```

Use these constraints in every shot after the first:

- no left-right position reversal
- no unmotivated axis crossing
- no motivated light-source relocation
- no changing light direction
- no auxiliary light replacing the script-confirmed key source
- no disappearing chair, doorway, or standing mark
- no broken eyeline

## Optional Auxiliary Light Prompt

When the script names or implies a natural, practical, or motivated source, keep it as the confirmed key light. Any fill, bounce, rim, haze, or beauty light must be optional and secondary.

Use this structure:

```text
Confirmed key light: [source] is the natural key light, coming from [direction], with [color/quality].
Optional auxiliary rendering: if needed for face readability, add very soft low-intensity [fill/bounce] from [direction], without changing the key-light direction, shadow logic, or natural-source motivation.
Do not: replace the natural or practical key light, add unmotivated studio lighting, flatten motivated shadows, or change the color/quality of the source between shots.
```

## Multi-Shot Continuity

Each shot after the first should include:

```text
Continue from previous shot: A is now beside the table, B remains near the door, the letter is still in A's right hand.
```

For shot transitions:

- Match action: end one shot with a hand reaching, start next with the hand touching the prop.
- Match eyeline: if A looks right toward B, B should be screen right or offscreen right.
- Match geography: avoid flipping left/right unless explicitly using a reverse shot.

## Negative Constraints

Use targeted negatives:

```text
No character swapping, no identity drift, no extra people, no sudden costume change, no position reversal, no broken eyeline, no jump cuts, no face morphing, no hand distortion, no background flicker, no prop teleporting.
```

Do not overuse generic negatives like:

```text
bad quality, ugly, low resolution
```

## Example Conversion

Raw user scene:

```text
女主角从门口走进来，看到桌上的信，镜头慢慢推近，她很震惊。
```

Structured prompt:

```text
A 6-second cinematic realistic shot. Character A, a young woman in a white shirt with tied hair, enters from the background doorway on frame right. She walks slowly toward the foreground table, stops at center frame, and looks down at a letter on the table. Her performance is restrained shock: frozen posture, widened eyes, shallow breathing, no exaggerated gesture. Eye-level medium shot with a 40mm lens feel. The camera performs a slow dolly-in from medium shot to close-up, no pan, no orbit, no handheld shake. The letter remains on the foreground table, the doorway remains in the background right, and Character A stays centered by the end. Soft interior light, slightly cool shadows, natural skin tone, clean contrast. No jump cuts, no face morphing, no extra characters, no background flicker, no prop teleporting.
```

Role scheduling:

```text
Character A starts at the background doorway on frame right, enters the room, walks toward the foreground table, stops at center frame, looks down at the letter, and ends frozen beside the table. Prop state: the letter remains on the foreground table for the entire shot.
```

Camera description:

```text
Eye-level medium shot with a 40mm lens feel. The camera performs a slow dolly-in from medium shot to close-up while keeping the letter visible in the foreground and the doorway in the background right. Start keyframe: A stands in the background doorway on frame right. End keyframe: A stands center frame beside the table, looking down at the letter. Forbidden moves: no pan, no orbit, no handheld shake, no jump cut inside the shot.
```

## Complex Dialogue Blocking Example

This example uses a fireplace only because the sample script names it. In other scripts, extract the actual light source, actor marks, entry paths, props, and set anchors from the provided text.

Raw user scene:

```text
角色A坐在座位上，左前方是壁炉。角色B在和角色A对话的过程中向角色A的左侧走动，边走边说。角色C在角色B话说完后，从角色A的左后方进入，在角色A的前方站定，以45度背对角色A进行对话。A与C回话完成后，角色B开始对A和C说保护自己的台词。
```

Text confirmation:

```text
Confirmed: A is seated. Fireplace is left-front of A and functions as the scene's natural key light. B speaks while walking toward A's left side. C enters after B finishes. C enters from A's left-rear, stops in front of A, and speaks with a 45-degree back angle to A. B later speaks to both A and C.
Needs confirmation: exact dialogue text, character visual anchors, room size, whether C faces camera or faces away from camera during the 45-degree position.
```

Role scheduling:

```text
Beat 1: A remains seated, torso facing forward, eyeline follows B. Fireplace stays at A's left-front.
Beat 2: B starts near A's front-right or center-front, speaks while walking toward A's left side, slows before reaching A's left-front quadrant, and finishes the line before C enters.
Beat 3: C enters from A's left-rear, crosses into A's front area, stops on a clear standing mark in front of A, body angled 45 degrees away from A, then speaks. A turns head and eyes from B toward C.
Beat 4: After A and C finish their exchange, B addresses both A and C with a self-protection line. B's eyeline alternates between A seated and C standing; A and C react without changing marks.
```

Dialogue rhythm and long-line split:

```text
B's final protection/self-protection line is treated as a long dialogue unit if it exceeds one short sentence. B speaks at a measured, defensive pace. Start on B in a medium shot for the first claim. Cut to A's close reaction when the line first implies danger or responsibility. Cut to C's three-quarter profile when B shifts the warning toward C. Return to B for the final self-protection phrase, with a short breath before the final words. A remains seated; C keeps the 45-degree back-to-A mark; B does not resume walking during the final line unless the script explicitly says so.
```

Camera description plan:

```text
Shot 1: Establishing medium-wide shot. A seated foreground/midground, the script-confirmed key light visible at A's left-front, B's walking path readable. In this example, the key light is the fireplace. Static or very slow lateral adjustment only.
Shot 2: Medium tracking or panning coverage of B while B walks and speaks toward A's left side. Keep A seated in the frame or use A's shoulder as foreground anchor. No axis crossing.
Shot 3: Cut on B's line completion to C entering from A's left-rear. Medium-wide shot shows C's entry path and stop mark in front of A.
Shot 4: Over-A or side-angle two-shot for A/C exchange, preserving C's 45-degree back-to-A orientation and A's seated eyeline.
Shot 5: Three-character coverage when B starts speaking to both A and C. Use a medium-wide triangular composition: A seated, C standing in front of A, B on A's left side. Keep the script-confirmed key light direction, shadow logic, and color consistent.
Shot 6: Long-dialogue coverage if B's protection line is extended. Stay on B for the opening phrase, cut to A for the first emotional impact, cut to C when B targets C, then return to B for the final phrase. All cuts preserve axis, eyelines, actor marks, confirmed key light, and set layout.
```

Prompt constraints:

```text
Keep A seated throughout. Keep the script-confirmed key light source at its established position, with consistent color, shadow direction, and falloff. In this example, the fireplace is that source because the script says so. Optional auxiliary rendering only if needed: very soft low-intensity fill for face readability, secondary to the confirmed key source and never changing the key-light direction. B walks only during B's first line and stops before C enters. C enters only after B finishes speaking. C stops in front of A with a 45-degree back angle toward A. For long dialogue, split coverage by meaning, eyeline target, expression, and listener reaction; preserve speaking pace, pauses, and actor marks. Preserve screen geography, eyelines, actor marks, furniture positions, and light direction. No left-right reversal, no unmotivated axis crossing, no character swapping, no extra people, no broken eyeline, no motivated light-source relocation, no chair movement, no auxiliary light replacing the script-confirmed key source, no arbitrary long-dialogue cuts, no jump cuts inside a shot.
```
