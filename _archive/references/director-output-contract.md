> 历史资料：退出v8默认运行。当前路线见SKILL.md与references/routing.md；不得据此恢复旧固定镜长、动作数或先九格后主稿流程。

# Output Contract

Use this reference when the user wants reusable JSON, a shot list, asset grounding, role scheduling, camera descriptions, keyframe descriptions, or a production-facing format.

## Top-Level JSON

```json
{
  "sequence_id": "seq_001",
  "title": "scene title",
  "source_text_confirmation": {
    "script_confirmed_facts": [],
    "asset_confirmed_facts": [],
    "assumptions": [],
    "needs_user_confirmation": []
  },
  "asset_grounding_map": {
    "scene_images": [],
    "character_assets": [],
    "prop_assets": [],
    "costume_assets": [],
    "set_assets": []
  },
  "scene_objective": "dramatic purpose of the sequence",
  "location": "interior living room at night",
  "visual_style": "cinematic realism, natural skin tone, clean contrast",
  "characters": [],
  "set_map": {},
  "role_schedule": [],
  "camera_description_plan": [],
  "dialogue_performance_map": [],
  "dialogue_rhythm_and_split_plan": [],
  "shots": [],
  "continuity_checklist": []
}
```

## Source Material Confirmation

Before designing shots, confirm what can be derived from the user's script and assets:

```json
{
  "script_confirmed_facts": [
    "A enters from the doorway.",
    "A sees a letter on the table.",
    "A reacts with shock."
  ],
  "asset_confirmed_facts": [
    "The scene image shows a doorway background right and a table foreground center.",
    "Character A asset shows tied hair and a white shirt."
  ],
  "assumptions": [
    "The scene is indoors because the script mentions a doorway and table."
  ],
  "needs_user_confirmation": [
    "Whether Character B is present in this scene."
  ]
}
```

Do not hide invented details inside the prompt. If a detail is not in the script or assets, keep it in `assumptions` or ask for confirmation when it changes the story, layout, character identity, or continuity.

## Asset Grounding Object

Use this when scene images, character references, prop references, costume references, or set references are provided.

```json
{
  "scene_images": [
    {
      "asset_id": "scene_ref_001",
      "usable_facts": [
        "doorway is background right",
        "table is foreground center",
        "primary practical light is frame left"
      ],
      "limits": [
        "exact room dimensions are unknown"
      ]
    }
  ],
  "character_assets": [
    {
      "character_id": "A",
      "asset_id": "char_A_ref_001",
      "visual_anchors": [
        "same face",
        "white shirt",
        "tied hair",
        "slim silhouette"
      ],
      "must_not_change": [
        "face identity",
        "costume color",
        "hairstyle"
      ]
    }
  ],
  "prop_assets": [],
  "costume_assets": [],
  "set_assets": []
}
```

## Character Object

```json
{
  "id": "A",
  "name": "young woman",
  "visual_anchor": "white shirt, tied hair",
  "emotion": "anxious",
  "relationship": "daughter of Character B",
  "start_position": "frame left near the window",
  "must_remain_consistent": [
    "white shirt",
    "tied hair",
    "same face and age"
  ]
}
```

## Set Map Object

```json
{
  "foreground": "wooden table with a sealed letter",
  "midground": "open space between A and B",
  "background": "doorway center, warm lamp frame right",
  "fixed_anchors": [
    "table remains foreground center",
    "door remains background center",
    "lamp remains background right"
  ]
}
```

## Role Schedule Object

Role scheduling is the character-side work. Use it to preserve multi-character blocking before writing camera prompts.

```json
{
  "beat_id": "beat_001",
  "characters_on_screen": ["A", "B"],
  "role_actions": [
    {
      "character_id": "A",
      "start_position": "frame left beside the table",
      "end_position": "center frame, one step closer to B",
      "movement": "takes two slow steps toward B, then stops",
      "eyeline": "looks toward B on frame right",
      "performance": "tense shoulders, controlled breathing",
      "prop_state": "right hand holds the sealed letter"
    },
    {
      "character_id": "B",
      "start_position": "frame right near the doorway",
      "end_position": "same position",
      "movement": "remains still",
      "eyeline": "looks back at A",
      "performance": "calm, stern expression",
      "prop_state": "no prop"
    }
  ],
  "continuity_notes": [
    "A remains frame left-to-center; B remains frame right.",
    "The letter stays in A's right hand."
  ]
}
```

## Camera Description Object

Camera description is the camera-side work. It must support the role schedule.

```json
{
  "beat_id": "beat_001",
  "shot_size_start": "medium two-shot",
  "shot_size_end": "medium close-up on A",
  "angle": "eye-level",
  "lens_feel": "40mm",
  "movement": "slow dolly-in toward A",
  "composition": "A moves from frame left to center; B remains frame right in soft focus",
  "transition": "straight cut from previous shot",
  "start_keyframe": "A stands frame left beside the table, B stands frame right near the doorway.",
  "end_keyframe": "A stops center frame with the letter in her right hand, looking toward B.",
  "forbidden_moves": ["orbit", "sudden pan", "position reversal", "jump cut inside the shot"]
}
```

## Dialogue Performance Object

Use this for dialogue-driven blocking. Each dialogue unit should define the speaker, movement, expression, and listener reaction.

```json
{
  "beat_id": "beat_002",
  "speaker": "B",
  "dialogue_intent": "warns A while walking",
  "line_or_summary": "B speaks to A while moving toward A's left side.",
  "pace": "controlled but urgent",
  "estimated_duration": "5s",
  "pause_points": ["short pause after the warning phrase"],
  "emphasis": ["protect yourself"],
  "speaker_movement_during_line": "B walks from A's front-right toward A's left side, then slows near A.",
  "speaker_expression": "controlled urgency, steady eye contact, restrained hand gesture",
  "listener_reactions": [
    {
      "character_id": "A",
      "reaction": "A remains seated, follows B with his eyes, turns his head slightly left."
    }
  ],
  "timing_note": "B finishes the line before C enters."
}
```

## Dialogue Rhythm and Shot Split Object

Use this when dialogue is long, emotionally layered, or tied to character movement. Split by dramatic function, not by equal length.

```json
{
  "dialogue_unit_id": "du_001",
  "speaker": "B",
  "line_or_summary": "B explains why A and C must protect themselves.",
  "dramatic_function": "self-protection statement addressed to both A and C",
  "pace": "measured, deliberate, slightly defensive",
  "estimated_duration": "10-14s",
  "split_points": [
    {
      "after_phrase_or_beat": "B states the danger",
      "reason_for_cut": "cut to A's reaction because the information lands on A first",
      "recommended_coverage": "A close-up, silent processing"
    },
    {
      "after_phrase_or_beat": "B shifts the warning toward C",
      "reason_for_cut": "C becomes the target of the line",
      "recommended_coverage": "C three-quarter profile or over-A angle"
    }
  ],
  "return_to_speaker": "return to B for the final self-protection phrase",
  "performance_timing": "B does not rush; insert a breath before the final phrase."
}
```

## Shot Object

```json
{
  "shot_id": "shot_001",
  "duration": "6s",
  "continuity_from_previous": "first shot",
  "role_schedule": "A enters from background right, walks to the foreground table, stops center frame, looks down at the letter.",
  "blocking": "A enters from background right, walks to the foreground table, stops center frame, looks down at the letter.",
  "dialogue_performance": {
    "speaker": "A",
    "line_or_summary": "silent reaction",
    "pace": "silent beat",
    "estimated_duration": "2s",
    "pause_or_breath": "one held breath before movement resumes",
    "long_dialogue_split": "not applicable",
    "expression_sync": "shock appears only after A sees the letter",
    "listener_reaction": "none"
  },
  "performance": "restrained shock, widened eyes, shallow breathing, frozen posture",
  "camera_description": {
    "shot_size_start": "medium shot",
    "shot_size_end": "close-up",
    "angle": "eye-level",
    "lens_feel": "40mm",
    "movement": "slow dolly-in",
    "forbidden_moves": ["orbit", "sudden pan", "handheld shake", "jump cut"]
  },
  "composition": "letter in foreground, A centered by the end, doorway remains background right",
  "lighting_color": {
    "confirmed_key_light": "script-confirmed practical, natural, or motivated source, such as window, lamp, fire, neon, candle, sun, moon, screen light, or streetlight",
    "color_and_shadow": "warm key direction and shadow behavior remain consistent",
    "optional_auxiliary_light_prompt": "optional only: very soft low-intensity fill or bounce if needed for facial readability; do not override the natural key light"
  },
  "continuity_protection": {
    "axis": "preserve screen geography; no unmotivated left-right reversal",
    "light": "confirmed key light source direction remains consistent; auxiliary fill is optional and secondary",
    "set": "furniture, doors, windows, practical lights, props, and actor marks remain fixed unless the script changes them",
    "eyeline": "eyelines match character positions"
  },
  "start_keyframe": "A is at the background doorway on frame right, table and letter visible in foreground.",
  "end_keyframe": "A stands center frame beside the table, looking down at the letter.",
  "negative": [
    "no character swapping",
    "no identity drift",
    "no extra people",
    "no face morphing",
    "no background flicker",
    "no prop teleporting"
  ],
  "prompt": "platform-ready prompt goes here"
}
```

## Continuity Checklist

Include a checklist after the shots:

```json
[
  "A remains visually identical across shots.",
  "B remains frame right unless a reverse shot is explicitly stated.",
  "The letter stays on the table until A picks it up.",
  "Eyelines match screen geography.",
  "Dialogue ownership, expression, and body movement match each line.",
  "Speaking pace, pauses, and long-dialogue split points match dramatic intent.",
  "Long dialogue is split for meaning, movement, eyeline, or listener reaction, not arbitrary variety.",
  "The 180-degree axis is preserved unless a motivated axis change is declared.",
  "Confirmed key light direction, shadow density, color, motivation, and set layout remain consistent.",
  "Auxiliary fill, bounce, rim, haze, or beauty light is optional and never replaces the confirmed natural key light.",
  "No shot contains more than two major actions."
]
```

## Platform Prompt Assembly

Construct platform prompts in this order:

1. duration and realism/style
2. continuity inheritance
3. character IDs and visual anchors
4. role schedule and blocking sequence
5. dialogue beat and expression sync
6. speaking pace, pause, and long-dialogue split instruction
7. performance details
8. camera description and lens language
9. composition anchors
10. confirmed natural key light and color
11. axis, eyeline, light, and set continuity constraints
12. optional auxiliary-light rendering block, if needed
13. negative constraints

## Minimal Deliverable

If time is short, output:

- source text confirmation
- asset grounding map, when assets are provided
- character table
- set map
- role schedule
- camera description plan
- dialogue and performance beat map
- dialogue rhythm and shot split plan
- 3-6 shot JSON objects
- one platform prompt per shot
- continuity checklist
